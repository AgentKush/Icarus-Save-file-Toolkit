"""Copy ALL creature/pet/farm talent icons from data-catalog to pets assets.

Includes Creature_*, CombatPet_*, NonCombatPet_*, Raptor_*, RaptorDesert_*,
Slinker_*, Storca_*, Orka_* prefixed talents.
"""
import json
import shutil
import os
import sys

DATA_CATALOG = os.path.join(os.path.dirname(__file__), '..', '..', 'icarus-data-catalog')
DEST = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons', 'talents')
os.makedirs(DEST, exist_ok=True)

# Load the full icon map from data-catalog
m = json.load(open(os.path.join(DATA_CATALOG, 'catalog', 'icon_map.json')))

# Also load the pet editor's talent trees to know which talents we need
PETS_DATA = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, PETS_DATA)
from talent_data import get_talent_tree, SPECIES_DATA

# Collect ALL talent names used in any creature's talent tree
needed_talents = set()
for species in SPECIES_DATA:
    tree = get_talent_tree(species)
    for t in tree:
        if 'name' in t:
            needed_talents.add(t['name'])

print(f"Total talents across all species: {len(needed_talents)}")

# Build lookup: talent_name -> icon_filename
lookup = {}
filenames_needed = set()

for talent_name in needed_talents:
    if talent_name in m['talents']:
        icon_fn = m['talents'][talent_name]['icon_filename']
        if icon_fn:
            lookup[talent_name] = icon_fn
            filenames_needed.add(icon_fn)

print(f"Talents with icons: {len(lookup)}")
print(f"Unique icon files: {len(filenames_needed)}")

# Copy icon files
copied = 0
missing = 0
total_size = 0
for fn in sorted(filenames_needed):
    src = os.path.join(DATA_CATALOG, 'icons', 'web', '128', f'{fn}.webp')
    dst = os.path.join(DEST, f'{fn}.webp')
    if os.path.exists(src):
        shutil.copy2(src, dst)
        total_size += os.path.getsize(dst)
        copied += 1
    else:
        missing += 1
        print(f"  WARNING: {fn}.webp not found in data-catalog icons")

# Write lookup JSON
lookup_path = os.path.join(DEST, '..', 'talent_icon_map.json')
json.dump(lookup, open(lookup_path, 'w'), indent=2, sort_keys=True)

print(f"\nCopied {copied} icon files ({missing} missing)")
print(f"Total size: {total_size/1024:.0f} KB")
print(f"Generated lookup: {os.path.abspath(lookup_path)} ({len(lookup)} entries)")

# Coverage report
unmapped = needed_talents - set(lookup.keys())
if unmapped:
    print(f"\nTalents without icons ({len(unmapped)}):")
    for name in sorted(unmapped)[:10]:
        print(f"  {name}")
    if len(unmapped) > 10:
        print(f"  ... and {len(unmapped) - 10} more")
