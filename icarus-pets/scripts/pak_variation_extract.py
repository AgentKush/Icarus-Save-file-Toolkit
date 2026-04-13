"""Extract creature variation tables from pak-extracted bin files.

Reads the zlib-decompressed chunks from pak-files/ that contain
the IcarusMount DataTable, reassembles them, and parses out
the Variations array for each creature type.

Outputs pak_variations_extracted.json with per-creature variation data.

Pipeline:
  pak_extract.py → pak_variation_extract.py → generate_variation_data.py
"""
import os
import re
import json

PAK_DIR = "pak-files"

# AISetup RowName → editor type name mapping
AISETUP_TO_TYPE = {
    "Mount_Arctic_Moa": "ArcticMoa",
    "Mount_Blueback_Daisy": "Blueback",
    "Tamed_Wild_Boar": "Boar",
    "Mount_Buffalo": "Buffalo",
    "Mount_Bull": "Bull",
    "Mount_Cat": "Cat",
    "Mount_Slinker": "Chew",
    "Mount_Chicken": "Chicken",
    "Mount_Cow": "Cow",
    "Tamed_Desert_Wolf": "DesertWolf",
    "Mount_Dog": "Dog",
    "Mount_Horse": "Horse",
    "Mount_Horse_Standard": "HorseStandard",
    "Mount_Moa": "Moa",
    "Mount_Pig": "Pig",
    "Mount_Rooster": "Rooster",
    "Mount_Sheep": "Sheep",
    "Tamed_Snow_Wolf": "SnowWolf",
    "Mount_SwampBird": "SwampBird",
    "Mount_SwampQuad": "SwampQuad",
    "Tamed_Tundra_Monkey": "TundraMonkey",
    "Mount_Tusker": "Tusker",
    "Mount_Wolf": "Wolf",
    "Tamed_Forest_Wolf": "Wolf",
    "Mount_WoollyMammoth": "WoollyMammoth",
    "Mount_Wooly_Zebra": "WoolyZebra",
    "Mount_Zebra": "Zebra",
    "Mount_Raptor": "Raptor",
    "Mount_Raptor_Desert": "RaptorDesert",
    "Mount_Storca": "Storca",
    "Tamed_Orka": "Orka",
}

# D_Mounts Name → editor type name (for rows where AISetup doesn't match)
ROW_NAME_TO_TYPE = {
    "Mount_Horse_Standard_A1": "HorseStandard",
    "Mount_Horse_Standard_A2": "HorseStandard",
    "Mount_Horse_Standard_A3": "HorseStandard",
    "Chicken": "Chicken",
    "Chicken_A2": "Chicken",
    "Chicken_A3": "Chicken",
    "Tame_Dog_A1": "Dog", "Tame_Dog_A2": "Dog",
    "Tame_Dog_B1": "Dog", "Tame_Dog_B2": "Dog",
    "Tame_Dog_C1": "Dog", "Tame_Dog_C2": "Dog",
    "Tame_Dog_D1": "Dog", "Tame_Dog_D2": "Dog",
    "Tame_Dog_E": "Dog",
    "Tame_Cat_A1": "Cat", "Tame_Cat_A2": "Cat", "Tame_Cat_A3": "Cat",
    "Tame_Cat_B1": "Cat", "Tame_Cat_C1": "Cat",
    "Mini_Hippo": "Chew",
    "Snow_Striker": "SnowWolf",
}


def load_mount_chunks():
    """Load and concatenate chunks containing the IcarusMount DataTable.

    Scans all extracted .bin files for IcarusMount or MeshMaterial
    keywords, then concatenates matching chunks in offset order.
    """
    chunks = []
    for fname in sorted(os.listdir(PAK_DIR)):
        if not fname.endswith('.bin'):
            continue
        fpath = os.path.join(PAK_DIR, fname)
        with open(fpath, 'rb') as f:
            data = f.read()
        text = data.decode('utf-8', errors='replace')
        if ('IcarusMount' in text or 'MeshMaterial' in text
                or 'GFurMaterial' in text):
            offset = int(fname.replace('extracted_', '').replace('.bin', ''))
            chunks.append((offset, data))

    if not chunks:
        raise RuntimeError(
            f"No IcarusMount chunks found in {PAK_DIR}/. "
            "Run pak_extract.py first."
        )

    chunks.sort()
    combined = b''.join(d for _, d in chunks)
    return combined.decode('utf-8', errors='replace')


def extract_material_name(full_path):
    """Extract short material name from UE4 asset path.

    '/Game/ASS/CRE/Buffalo/MI_CRE_Buffalo.MI_CRE_Buffalo'
    → 'MI_CRE_Buffalo'
    """
    if not full_path or full_path == "None":
        return ""
    # Take the part after the last dot (the asset name)
    if '.' in full_path:
        return full_path.rsplit('.', 1)[-1]
    # Fallback: take the part after the last slash
    if '/' in full_path:
        return full_path.rsplit('/', 1)[-1]
    return full_path


def get_rarity_tier(weighting):
    """Determine rarity tier from spawn weighting."""
    if weighting >= 1000:
        return "Common"
    if weighting >= 100:
        return "Uncommon"
    if weighting >= 25:
        return "Rare"
    if weighting >= 5:
        return "Legendary"
    return "Ultra-Rare"


def parse_creature_entries(text):
    """Parse creature entries from the IcarusMount DataTable text.

    Finds each creature's Name and Variations array, extracting
    MeshMaterial, GFurMaterial, and Weighting per variation.
    """
    # Find all "Name": "..." entries that look like D_Mounts rows
    name_pattern = r'"Name":\s*"([^"]+)"'
    creatures = {}

    for m in re.finditer(name_pattern, text):
        row_name = m.group(1)
        start = m.start()

        # Determine the block end (next "Name": or end of text)
        next_name = re.search(name_pattern, text[m.end():])
        end = m.end() + next_name.start() if next_name else len(text)
        block = text[start:end]

        # Check for AISetup to confirm this is a D_Mounts entry
        ai_match = re.search(r'"AISetup":\s*\{\s*"RowName":\s*"([^"]*)"', block)
        if not ai_match:
            continue

        ai_setup = ai_match.group(1)

        # Look up the editor type name — try AISetup first, then row name
        editor_type = AISETUP_TO_TYPE.get(ai_setup)
        if not editor_type:
            editor_type = ROW_NAME_TO_TYPE.get(row_name)
        if not editor_type:
            # Try partial matching on row name
            for rn, et in ROW_NAME_TO_TYPE.items():
                if rn.lower() in row_name.lower():
                    editor_type = et
                    break
        if not editor_type:
            # Unknown creature — record with raw name
            editor_type = row_name

        # Parse Variations array if present
        variations = []
        var_match = re.search(r'"Variations":\s*\[', block)
        if var_match:
            # Find the closing ] of the Variations array
            arr_start = var_match.end()
            depth = 1
            arr_end = arr_start
            for ci, ch in enumerate(block[arr_start:], arr_start):
                if ch == '[':
                    depth += 1
                elif ch == ']':
                    depth -= 1
                if depth == 0:
                    arr_end = ci + 1
                    break

            var_text = block[var_match.start():arr_end]

            # Parse each variation entry
            for entry_match in re.finditer(
                r'\{[^}]*"MeshMaterial":\s*"([^"]*)"[^}]*'
                r'"GFurMaterial":\s*"([^"]*)"[^}]*'
                r'"Weighting":\s*(\d+)',
                var_text
            ):
                mesh_full = entry_match.group(1)
                fur_full = entry_match.group(2)
                weighting = int(entry_match.group(3))

                mesh_name = extract_material_name(mesh_full)
                fur_name = extract_material_name(fur_full)

                variations.append({
                    "index": len(variations),
                    "mesh_material": mesh_name,
                    "mesh_path": mesh_full,
                    "fur_material": fur_name,
                    "fur_path": fur_full,
                    "weighting": weighting,
                    "rarity": get_rarity_tier(weighting),
                })

        # Also try alternate Variations ordering (GFurMaterial before MeshMaterial)
        if not variations and var_match:
            var_text = block[var_match.start():arr_end]
            for entry_match in re.finditer(
                r'\{[^}]*"GFurMaterial":\s*"([^"]*)"[^}]*'
                r'"MeshMaterial":\s*"([^"]*)"[^}]*'
                r'"Weighting":\s*(\d+)',
                var_text
            ):
                fur_full = entry_match.group(1)
                mesh_full = entry_match.group(2)
                weighting = int(entry_match.group(3))

                mesh_name = extract_material_name(mesh_full)
                fur_name = extract_material_name(fur_full)

                variations.append({
                    "index": len(variations),
                    "mesh_material": mesh_name,
                    "mesh_path": mesh_full,
                    "fur_material": fur_name,
                    "fur_path": fur_full,
                    "weighting": weighting,
                    "rarity": get_rarity_tier(weighting),
                })

        creatures[editor_type] = {
            "row_name": row_name,
            "ai_setup": ai_setup,
            "editor_type": editor_type,
            "variation_count": len(variations),
            "variations": variations,
        }

    return creatures


def main():
    print("Loading IcarusMount DataTable chunks...")
    text = load_mount_chunks()
    print(f"  Total text: {len(text):,} chars")

    print("Parsing creature entries...")
    creatures = parse_creature_entries(text)
    print(f"  Found {len(creatures)} creature types")

    # Summary
    with_vars = {k: v for k, v in creatures.items() if v["variation_count"] > 0}
    without_vars = {k: v for k, v in creatures.items() if v["variation_count"] == 0}
    total_variants = sum(v["variation_count"] for v in with_vars.values())

    print(f"\n{'=' * 60}")
    print(f"VARIATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Types with variations: {len(with_vars)}")
    print(f"  Types without variations: {len(without_vars)}")
    print(f"  Total variant entries: {total_variants}")

    for type_name in sorted(with_vars.keys()):
        c = with_vars[type_name]
        print(f"\n  {type_name} ({c['row_name']}): {c['variation_count']} variations")
        for v in c["variations"]:
            print(f"    [{v['index']}] {v['mesh_material']} "
                  f"(wt={v['weighting']}, {v['rarity']})")

    print(f"\n  Single-appearance types:")
    for type_name in sorted(without_vars.keys()):
        print(f"    {type_name}")

    # Save JSON
    output = {
        "creature_count": len(creatures),
        "types_with_variations": len(with_vars),
        "total_variants": total_variants,
        "creatures": creatures,
    }
    with open("pak_variations_extracted.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to pak_variations_extracted.json")


if __name__ == "__main__":
    main()
