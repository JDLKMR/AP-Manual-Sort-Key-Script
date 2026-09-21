# Archipelago Manual Sort-Key Adding Script
A Python script that adds sort-keys to all entries in an Archipelago Manual world's `location.json`, in the order that the locations appear in the file. A fairly recent change to the Manual Client changed how ordering works, no longer using the order of entries as they appear in the file, but rather, alphabetizes them. This script is useful for ensuring the locations always appear in the Manual client in the order that they appear directly in the file, if desired.

## Usage
With the script in the same location as either the `.apworld` or `locations.json` file (no extraction needed), and run:

```
python add-sort-keys.py <.apworld name/locations.json>
```

Re-running the script is safe and overwrites previous sort-keys with new ones according to the new location order, in case you change things around.

You can also adjust the digit padding that the added sort-keys use (default `4`).

Currently only applies to `locations.json`. I might add the ability to do the same for items and categories later.

## AI Disclosure
All programming of the script is done by Claude. Testing, documentation, and other writing is all done by me.
