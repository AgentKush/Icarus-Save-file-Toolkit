"""Quick verification that the refresh produced valid data for all creature types."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import talent_data as td
import variation_data as vd

NEW_TYPES = ['Raptor', 'RaptorDesert', 'Orka', 'Slinker', 'Storca']

print("=== Talent Data Verification ===")
types = td.get_all_types()
print(f"Total types: {len(types)}")
for t in sorted(types):
    tree = td.get_talent_tree(t)
    cat = td.get_category(t)
    bestiary = td.get_bestiary_info(t)
    marker = " ★ NEW" if t in NEW_TYPES else ""
    print(f"  {t:20s}  {cat:10s}  {len(tree):2d} talents  \"{bestiary['name']}\"{marker}")

print()
missing = [t for t in NEW_TYPES if t not in types]
if missing:
    print(f"⚠ Missing new types: {missing}")
else:
    print("✅ All 5 new creature types present in talent trees")

print()
print("=== Type Detection Spot-Check ===")
# Chew backward compat (existing saves have Mount_Slinker)
chew = td.detect_type("Mount_Slinker", "BP_Slinker_Mount_C")
print(f"  Chew (legacy ai_setup):  detect_type('Mount_Slinker', 'BP_Slinker_Mount_C') → {chew}  {'✅' if chew == 'Chew' else '❌'}")

raptor = td.detect_type("Mount_Raptor", "BP_Mount_Raptor_C")
print(f"  Raptor:                  detect_type('Mount_Raptor', 'BP_Mount_Raptor_C') → {raptor}  {'✅' if raptor == 'Raptor' else '❌'}")

raptor_d = td.detect_type("Mount_Raptor_Desert", "BP_Mount_Raptor_Desert_C")
print(f"  RaptorDesert:            detect_type('Mount_Raptor_Desert', ...) → {raptor_d}  {'✅' if raptor_d == 'RaptorDesert' else '❌'}")

orka = td.detect_type("Tamed_Orka", "BP_Tamed_Orka_C")
print(f"  Orka:                    detect_type('Tamed_Orka', ...) → {orka}  {'✅' if orka == 'Orka' else '❌'}")

storca = td.detect_type("Mount_Storca", "BP_Mount_Storca_C")
print(f"  Storca:                  detect_type('Mount_Storca', ...) → {storca}  {'✅' if storca == 'Storca' else '❌'}")

print()
print("=== Variation Data Verification ===")
print(f"  ALL_CREATURE_TYPES: {len(vd.ALL_CREATURE_TYPES)}")
print(f"  Types with variations: {len(vd.TYPES_WITH_VARIATIONS)}")
new_in_vd = [t for t in NEW_TYPES if t in vd.ALL_CREATURE_TYPES]
print(f"  New types in catalog: {new_in_vd}")

print()
print("=== Bestiary Coverage ===")
bestiary_count = len(td.BESTIARY_DATA)
print(f"  Bestiary entries: {bestiary_count}")
for t in NEW_TYPES:
    b = td.get_bestiary_info(t)
    print(f"  {t:20s}  → \"{b['name']}\"  lore={len(b.get('lore',''))} chars")

print()
print("=== Species Swap Coverage ===")
for t in NEW_TYPES:
    targets = td.get_swap_targets(t)
    sd = td.SPECIES_DATA.get(t, {})
    print(f"  {t:20s}  swap targets: {len(targets)}  species_data: {'✅' if sd else '❌'}")
