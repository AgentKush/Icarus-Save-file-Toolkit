"""Extract bestiary data from pak files."""
import re
import json
import glob

all_entries = {}

for f in glob.glob('pak-files/*.bin'):
    try:
        data = open(f, 'rb').read()
        text = data.decode('latin-1')
    except:
        continue

    # Match: NSLOCTEXT(\"D_BestiaryData\", \"Key\", \"Value\")
    # In the file the quotes are escaped as \"
    pattern = r'NSLOCTEXT\(\\"D_BestiaryData\\",\s*\\"([^"\\]+)\\",\s*\\"((?:[^"\\]|\\\\.)*)\\"\)'
    for m in re.finditer(pattern, text):
        key = m.group(1)
        val = m.group(2).replace("\\'", "'").replace("\\n", "\n")
        parts = key.split('-', 1)
        creature = parts[0]
        field = parts[1] if len(parts) > 1 else 'unknown'
        if creature not in all_entries:
            all_entries[creature] = {}
        all_entries[creature][field] = val

print(f"Found {len(all_entries)} creatures with bestiary data\n")

# Show mount/pet-relevant ones
mount_keys = [
    'Buffalo', 'Horse', 'Horse_Standard', 'Zebra', 'Wooly_Zebra',
    'Moa', 'Arctic_Moa', 'Tusker', 'Bull', 'Swamp_Bird', 'Swamp_Quadruped',
    'Blueback', 'WoollyMammoth', 'Wolf', 'Desert_Wolf', 'Snow_Wolf',
    'Wild_Boar', 'Dog', 'Cat', 'Chicken', 'Cattle', 'Sheep', 'Pig',
    'Tundra_Monkey', 'Mammoth',
    'Raptor', 'Raptor_Desert', 'Orka', 'Slinker', 'Storca',
]

print("=== ALL CREATURES ===")
for name in sorted(all_entries.keys()):
    c = all_entries[name]
    cname = c.get('CreatureName', '?')
    lore1 = c.get('Lore1', '')[:120]
    marker = " ★" if name in mount_keys else ""
    print(f"  {name}: \"{cname}\"{marker}")
    if lore1:
        print(f"    {lore1}...")
    print()

# Save full data as JSON
with open('bestiary_data.json', 'w') as f:
    json.dump(all_entries, f, indent=2)
print("\nFull data saved to bestiary_data.json")
