"""Phenotype analysis — compare same-type creatures with different Variation values."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from collections import defaultdict
from ue4_parser import BinaryReader, parse_properties

with open("Mounts.json", "r") as f:
    data = json.load(f)

print(f"Total mounts: {len(data['SavedMounts'])}")
print()

# Parse all mounts
mounts = []
for mount in data["SavedMounts"]:
    binary = mount["RecorderBlob"]["BinaryData"]
    reader = BinaryReader(binary)
    props = parse_properties(reader)
    by_name = {p["name"]: p for p in props}

    # Extract key phenotype fields
    variation = by_name.get("Variation", {}).get("value", "N/A")

    # IntVariables
    int_vars = {}
    iv = by_name.get("IntVariables")
    if iv:
        for elem in iv.get("elements", []):
            if len(elem) >= 2:
                int_vars[elem[0]["value"]] = elem[1]["value"]

    # LinearColorVariables
    color_vars = []
    lcv = by_name.get("LinearColorVariables")
    if lcv:
        for elem in lcv.get("elements", []):
            entry = {}
            for p in elem:
                entry[p["name"]] = p.get("value")
            color_vars.append(entry)

    mounts.append({
        "name": mount["MountName"],
        "type": mount["MountType"],
        "by_name": by_name,
        "json": mount,
        "variation": variation,
        "cosmetic_skin": int_vars.get("CosmeticSkinIndex", "N/A"),
        "int_vars": int_vars,
        "color_vars": color_vars,
    })

    print(f"  {mount['MountName']:20s} ({mount['MountType']:15s}) "
          f"Variation={variation}  CosmeticSkin={int_vars.get('CosmeticSkinIndex', 'N/A')}  "
          f"Colors={len(color_vars)}")

# Group by type
by_type = defaultdict(list)
for m in mounts:
    by_type[m["type"]].append(m)

# Full diff on pairs of same-type creatures
for mtype, group in sorted(by_type.items()):
    if len(group) < 2:
        continue

    a, b = group[0], group[1]
    print(f"\n{'=' * 70}")
    print(f"FULL DIFF: {a['name']} vs {b['name']} (both {mtype})")
    print(f"{'=' * 70}")

    all_keys = sorted(set(a["by_name"].keys()) | set(b["by_name"].keys()))

    for key in all_keys:
        pa = a["by_name"].get(key)
        pb = b["by_name"].get(key)

        if pa is None:
            print(f"  ONLY {b['name']}: {key}")
            continue
        if pb is None:
            print(f"  ONLY {a['name']}: {key}")
            continue

        ptype = pa["type"]

        if ptype in ("IntProperty", "UInt32Property", "BoolProperty"):
            if pa.get("value") != pb.get("value"):
                print(f"  DIFF {key} ({ptype}): {pa['value']} vs {pb['value']}")

        elif ptype in ("StrProperty", "NameProperty"):
            va = pa.get("value", "") or ""
            vb = pb.get("value", "") or ""
            if va != vb:
                print(f"  DIFF {key} ({ptype}): \"{va[:60]}\" vs \"{vb[:60]}\"")

        elif ptype == "EnumProperty":
            if pa.get("value") != pb.get("value"):
                print(f"  DIFF {key}: {pa['value'].split('::')[-1]} vs {pb['value'].split('::')[-1]}")

        elif ptype == "StructProperty":
            if "value" in pa and "value" in pb:
                if pa["value"] != pb["value"]:
                    print(f"  DIFF {key} (Struct): values differ")
            elif "properties" in pa:
                for sp in pa.get("properties", []):
                    for sp2 in pb.get("properties", []):
                        if sp2["name"] == sp["name"]:
                            if sp.get("value") != sp2.get("value"):
                                print(f"  DIFF {key}.{sp['name']}: {sp.get('value')} vs {sp2.get('value')}")
                            break

        elif ptype == "ArrayProperty":
            ea = pa.get("elements", [])
            eb = pb.get("elements", [])
            ca = pa.get("count", 0)
            cb = pb.get("count", 0)

            if key == "IntVariables":
                a_vars = {e[0]["value"]: e[1]["value"] for e in ea if len(e) >= 2}
                b_vars = {e[0]["value"]: e[1]["value"] for e in eb if len(e) >= 2}
                for vk in sorted(set(a_vars.keys()) | set(b_vars.keys())):
                    if a_vars.get(vk) != b_vars.get(vk):
                        print(f"  DIFF IntVars.{vk}: {a_vars.get(vk)} vs {b_vars.get(vk)}")
            elif key == "Talents":
                if ca != cb:
                    print(f"  DIFF Talents: {ca} vs {cb} talents (different builds)")
            elif key == "Genetics":
                for i in range(min(len(ea), len(eb))):
                    gname = ea[i][0]["value"]
                    gval_a = ea[i][1]["value"]
                    gval_b = eb[i][1]["value"]
                    if gval_a != gval_b:
                        print(f"  DIFF Genetics.{gname}: {gval_a} vs {gval_b}")
            elif key in ("BoolVariables", "NameVariables", "TextVariables",
                         "LinearColorVariables", "StomachContents", "Modifiers"):
                if ca != cb:
                    print(f"  DIFF {key}: {ca} vs {cb} elements")
            elif key == "SavedInventories":
                if ca != cb:
                    print(f"  DIFF SavedInventories: {ca} vs {cb}")
            else:
                if ca != cb:
                    print(f"  DIFF {key}: {ca} vs {cb} elements")

    # JSON envelope diffs
    for jk in sorted(a["json"].keys()):
        if jk == "RecorderBlob":
            continue
        va = a["json"].get(jk)
        vb = b["json"].get(jk)
        if va != vb:
            print(f"  DIFF json.{jk}: {str(va)[:60]} vs {str(vb)[:60]}")

    print()

# Cross-reference with pak data
print("\n" + "=" * 70)
print("VARIATION INDEX → D_MOUNTS PAK DATA MAPPING")
print("=" * 70)
print()
print("Buffalo Variations (from D_Mounts DataTable):")
print("  [0] MI_CRE_Buffalo                    (Common, wt=2000)")
print("  [1] MI_CRE_Buffalo_Rare_VarC          (Rare, wt=50)")
print("  [2] MI_CRE_Buffalo_Rare_VarD          (Rare, wt=50)")
print("  [3] MI_CRE_Buffalo_Rare_VarG          (Rare, wt=50)")
print("  [4] MI_CRE_Buffalo_Rare_VarH          (Rare, wt=50)")
print("  [5] MI_CRE_Buffalo_White              (Legendary, wt=5)")
print("  [6] MI_CRE_Buffalo_Legendary_VarA     (Legendary, wt=5)")
print("  [7] MI_CRE_Buffalo_Legendary_VarB     (Legendary, wt=5)")
print()
print("Moa Variations (from D_Mounts DataTable):")
print("  [0] M_CRE_Moa                         (Common, wt=2000)")
print("  [1] M_CRE_Moa_Var5                    (Rare, wt=50)")
print("  [2] M_CRE_Moa_Var8                    (Rare, wt=50)")
print("  [3] M_CRE_Moa_Var9                    (Rare, wt=50)")
print("  [4] M_CRE_Moa_Var10                   (Rare, wt=25)")
print("  [5] M_CRE_Moa_Var11                   (Rare, wt=25)")
print("  [6] M_CRE_Moa_Var12                   (Rare, wt=25)")
print("  [7] M_CRE_Moa_Var13                   (Legendary, wt=5)")
print()
print("CONCLUSION:")
print("  The 'Variation' IntProperty is a 0-based index into the creature's")
print("  Variations array in D_Mounts. Changing this value should change the")
print("  creature's visual appearance (mesh material + groom/fur material).")
print("  CosmeticSkinIndex and LinearColorVariables are unused (-1 / empty).")
