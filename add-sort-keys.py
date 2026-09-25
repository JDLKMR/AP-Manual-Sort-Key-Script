#!/usr/bin/env python3

import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

KEY_NAME = "sort-key"
START = 0
PADDING = 4


def _format_sort_key(value: int, padding: int):
    return str(value).zfill(padding) if padding else value


def _apply_sort_keys(data, key_name: str, start: int, padding: int):
    if not isinstance(data, list):
        raise ValueError(
            f"Expected locations.json to contain a JSON array, "
            f"but found a {type(data).__name__} instead."
        )
    changed = 0
    skipped = 0
    for index, entry in enumerate(data):
        if not isinstance(entry, dict):
            print(f"  Skipping entry #{index}: not a JSON object ({entry!r})")
            skipped += 1
            continue
        new_value = _format_sort_key(index + start, padding)
        if entry.get(key_name) != new_value:
            changed += 1
        entry[key_name] = new_value
    return changed, skipped, len(data)


def add_sort_keys_plain(path: Path, key_name: str = KEY_NAME, start: int = START, padding: int = PADDING):
    data = json.loads(path.read_text(encoding="utf-8"))
    changed, skipped, total = _apply_sort_keys(data, key_name, start, padding)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed, skipped, total


def _find_locations_entry(names):
    normalized = [(n, n.replace("\\", "/").lower()) for n in names]
    for original, norm in normalized:
        if norm.endswith("/data/locations.json"):
            return original
    for original, norm in normalized:
        if norm == "locations.json" or norm.endswith("/locations.json"):
            return original
    raise ValueError("Could not find a locations.json entry inside the archive.")


def add_sort_keys_zip(path: Path, key_name: str = KEY_NAME, start: int = START, padding: int = PADDING):
    with zipfile.ZipFile(path, "r") as zf:
        entry_name = _find_locations_entry(zf.namelist())
        infos = zf.infolist()
        contents = {info.filename: zf.read(info.filename) for info in infos}

    data = json.loads(contents[entry_name].decode("utf-8"))
    changed, skipped, total = _apply_sort_keys(data, key_name, start, padding)
    contents[entry_name] = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

    fd, tmp_path = tempfile.mkstemp(suffix=path.suffix, dir=str(path.parent))
    os.close(fd)
    try:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf_out:
            for info in infos:
                zf_out.writestr(info, contents[info.filename])
        shutil.move(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

    return changed, skipped, total, entry_name


def main():
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = Path("locations.json")

    if not target.exists():
        print(f"Could not find {target}.")
        print("Run this script from your Manual APWorld's data folder,")
        print("or pass the path to locations.json or a .apworld file, e.g.:")
        print(f"    python {Path(sys.argv[0]).name} data/locations.json")
        print(f"    python {Path(sys.argv[0]).name} MyWorld.apworld")
        sys.exit(1)

    is_archive = target.suffix.lower() == ".apworld" or zipfile.is_zipfile(target)

    try:
        if is_archive:
            changed, skipped, total, entry_name = add_sort_keys_zip(target)
            location_desc = f"{entry_name} inside {target}"
        else:
            changed, skipped, total = add_sort_keys_plain(target)
            location_desc = str(target)
    except json.JSONDecodeError as e:
        print(f"locations.json is not valid JSON: {e}")
        sys.exit(1)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    print(f"Done. Processed {total} location(s) in {location_desc}: "
          f"{changed} sort-key value(s) written/updated"
          + (f", {skipped} entry(ies) skipped." if skipped else "."))


if __name__ == "__main__":
    main()
    if sys.platform.startswith("win") and len(sys.argv) <= 1:
        input("Press Enter to close...")
