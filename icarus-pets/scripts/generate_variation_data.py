"""Generate variation_data.py from pak_variations_extracted.json.

Reads the extracted variation data and produces a complete Python module
with variation tables, rarity tiers, and lookup functions.

Pipeline:
  pak_extract.py → pak_variation_extract.py → generate_variation_data.py
"""
import json
import os

# Normalize extracted type names to editor type names
TYPE_NAME_MAP = {
    "Horse_Standard": "HorseStandard",
    "Arctic_Moa": "ArcticMoa",
    "Snow_Wolf": "SnowWolf",
    "Desert_Wolf": "DesertWolf",
    "Wooly_Zebra": "WoolyZebra",
    "Woolly_Mammoth": "WoollyMammoth",
    "Mini_Hippo": "Chew",
    "Snow_Striker": "SnowWolf",
}

# All known editor type names (for the ALL_CREATURE_TYPES list)
ALL_TYPES = [
    "ArcticMoa", "Blueback", "Boar", "Buffalo", "Bull", "Cat", "Chew",
    "Chicken", "Cow", "DesertWolf", "Dog", "Horse", "HorseStandard",
    "Moa", "Orka", "Pig", "Raptor", "RaptorDesert", "Rooster", "Sheep",
    "Slinker", "SnowWolf", "Storca", "SwampBird", "SwampQuad",
    "TundraMonkey", "Tusker", "Wolf", "WoollyMammoth", "WoolyZebra", "Zebra",
]


def normalize_type(name):
    """Normalize extracted type names to editor convention."""
    return TYPE_NAME_MAP.get(name, name)


def main():
    json_path = "pak_variations_extracted.json"
    if not os.path.isfile(json_path):
        print(f"Error: {json_path} not found. Run pak_variation_extract.py first.")
        return

    with open(json_path) as f:
        data = json.load(f)

    creatures = data["creatures"]

    # Separate types with variations from those without
    with_vars = {}
    for type_name, info in creatures.items():
        norm = normalize_type(type_name)
        if info["variation_count"] > 0:
            with_vars[norm] = info["variations"]

    lines = []
    lines.append('"""Icarus creature phenotype variation data.')
    lines.append('')
    lines.append('Auto-generated from pak file extraction (pak_variation_extract.py).')
    lines.append('Contains variation tables for all creature types, extracted from the')
    lines.append('IcarusMount DataTable in data.pak.')
    lines.append('')
    lines.append(f'Only {len(with_vars)} of {len(ALL_TYPES)} creature types have color variations via the Variations')
    lines.append('system. The remaining types have a single fixed appearance.')
    lines.append('"""')
    lines.append('')
    lines.append('')
    lines.append('# ── Rarity Tiers ─────────────────────────────────────────────────────────────')
    lines.append('')
    lines.append('RARITY_THRESHOLDS = [')
    lines.append('    (1000, "Common"),')
    lines.append('    (100,  "Uncommon"),')
    lines.append('    (25,   "Rare"),')
    lines.append('    (5,    "Legendary"),')
    lines.append('    (0,    "Ultra-Rare"),')
    lines.append(']')
    lines.append('')
    lines.append('')
    lines.append('def get_rarity_tier(weighting):')
    lines.append('    """Determine rarity tier from spawn weighting.')
    lines.append('')
    lines.append('    Thresholds: >=1000 Common, >=100 Uncommon, >=25 Rare,')
    lines.append('    >=5 Legendary, <5 Ultra-Rare.')
    lines.append('    """')
    lines.append('    for threshold, tier in RARITY_THRESHOLDS:')
    lines.append('        if weighting >= threshold:')
    lines.append('            return tier')
    lines.append('    return "Ultra-Rare"')
    lines.append('')
    lines.append('')
    lines.append('# ── Variation Tables ─────────────────────────────────────────────────────────')
    lines.append('# Each entry: index, mesh_material (short name), fur_material, weighting, rarity')
    lines.append('')

    # Generate per-type variation arrays
    for type_name in sorted(with_vars.keys()):
        variations = with_vars[type_name]
        var_name = f"_VARIATIONS_{type_name.upper()}"
        lines.append(f'{var_name} = [')
        for v in variations:
            mesh = v["mesh_material"]
            fur = v["fur_material"]
            wt = v["weighting"]
            rarity = v["rarity"]
            idx = v["index"]
            lines.append(f'    {{"index": {idx}, "mesh_material": "{mesh}", '
                         f'"fur_material": "{fur}", '
                         f'"weighting": {wt}, "rarity": "{rarity}"}},')
        lines.append(']')
        lines.append('')

    # Combined lookup dict
    lines.append('')
    lines.append('# ── Combined Lookup ──────────────────────────────────────────────────────────')
    lines.append('')
    lines.append('VARIATION_DATA = {')
    for type_name in sorted(with_vars.keys()):
        var_name = f"_VARIATIONS_{type_name.upper()}"
        lines.append(f'    "{type_name}": {var_name},')
    lines.append('}')
    lines.append('')

    # All creature types list
    lines.append('# All known creature types — types not in VARIATION_DATA have no variations')
    lines.append('ALL_CREATURE_TYPES = [')
    type_strs = ', '.join(f'"{t}"' for t in ALL_TYPES)
    # Wrap at ~80 chars
    chunk = []
    for t in ALL_TYPES:
        chunk.append(f'"{t}"')
        if len(', '.join(chunk)) > 65:
            lines.append(f'    {", ".join(chunk)},')
            chunk = []
    if chunk:
        lines.append(f'    {", ".join(chunk)},')
    lines.append(']')
    lines.append('')

    # Types with variations
    lines.append('# Types that use the Variation system (Variations array in IcarusMount DataTable)')
    lines.append('TYPES_WITH_VARIATIONS = sorted(VARIATION_DATA.keys())')
    lines.append('')
    lines.append('')

    # Public API functions
    lines.append('# ── Public API ───────────────────────────────────────────────────────────────')
    lines.append('')
    lines.append('def get_variations(type_name):')
    lines.append('    """Get the variation list for a creature type.')
    lines.append('')
    lines.append('    Returns list of dicts with keys: index, mesh_material, fur_material,')
    lines.append('    weighting, rarity.  Returns empty list for types without variations.')
    lines.append('    """')
    lines.append('    return VARIATION_DATA.get(type_name, [])')
    lines.append('')
    lines.append('')
    lines.append('def get_variation_count(type_name):')
    lines.append('    """Get the number of variations for a creature type (0 if none)."""')
    lines.append('    return len(VARIATION_DATA.get(type_name, []))')
    lines.append('')
    lines.append('')
    lines.append('def has_variations(type_name):')
    lines.append('    """Check if a creature type has color variations."""')
    lines.append('    return type_name in VARIATION_DATA')
    lines.append('')
    lines.append('')
    lines.append('def get_variation_label(type_name, index):')
    lines.append('    """Get a human-readable label for a specific variation index.')
    lines.append('')
    lines.append('    Returns a string like \'Common \\u2014 MI_CRE_Buffalo\' or')
    lines.append('    \'Rare \\u2014 MI_CRE_Buffalo_Rare_VarC\'.')
    lines.append('    For types without variations, returns \'Default\'.')
    lines.append('    """')
    lines.append('    variations = get_variations(type_name)')
    lines.append('    if not variations:')
    lines.append('        return "Default"')
    lines.append('    if 0 <= index < len(variations):')
    lines.append('        v = variations[index]')
    lines.append('        return f"{v[\'rarity\']} \\u2014 {v[\'mesh_material\']}"')
    lines.append('    return f"Unknown (index {index})"')
    lines.append('')
    lines.append('')
    lines.append('def get_variation_labels(type_name):')
    lines.append('    """Get all variation labels for dropdown display.')
    lines.append('')
    lines.append('    Returns list of strings like:')
    lines.append('      [\'0: Common \\u2014 MI_CRE_Buffalo\', \'1: Rare \\u2014 MI_CRE_Buffalo_Rare_VarC\', ...]')
    lines.append('    For types without variations, returns [\'Default (single appearance)\'].')
    lines.append('    """')
    lines.append('    variations = get_variations(type_name)')
    lines.append('    if not variations:')
    lines.append('        return ["Default (single appearance)"]')
    lines.append('    labels = []')
    lines.append('    for v in variations:')
    lines.append('        labels.append(f"{v[\'index\']}: {v[\'rarity\']} \\u2014 {v[\'mesh_material\']}")')
    lines.append('    return labels')
    lines.append('')
    lines.append('')
    lines.append('def validate_variation_index(type_name, index):')
    lines.append('    """Check if a variation index is valid for the given creature type.')
    lines.append('')
    lines.append('    Returns True if valid, False otherwise.')
    lines.append('    For types without variations, only index 0 is valid.')
    lines.append('    """')
    lines.append('    count = get_variation_count(type_name)')
    lines.append('    if count == 0:')
    lines.append('        return index == 0')
    lines.append('    return 0 <= index < count')
    lines.append('')

    # Write output
    output = '\n'.join(lines) + '\n'
    with open('variation_data.py', 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Generated variation_data.py:")
    print(f"  {len(with_vars)} types with variations")
    total = sum(len(v) for v in with_vars.values())
    print(f"  {total} total variant entries")
    print(f"  {len(ALL_TYPES)} creature types in catalog")
    print(f"  File size: {len(output):,} bytes")


if __name__ == "__main__":
    main()
