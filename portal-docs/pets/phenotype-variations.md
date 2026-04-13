# Phenotype & Variations

Only 3 of 28 creature types have color variations: Buffalo, Moa, Wolf (8 variants each, 24 total)

Variation field: IntProperty, 0-based index into IcarusMount DataTable Variations array.

## Rarity Tiers (by spawn weighting)
| Weighting | Rarity |
|-----------|--------|
| >= 1000 | Common |
| 100-999 | Uncommon |
| 25-99 | Rare |
| 5-24 | Legendary |
| < 5 | Ultra-Rare |

## Buffalo (8 variations)
0: MI_CRE_Buffalo (2000, Common)
1-4: MI_CRE_Buffalo_Rare_VarC/D/G/H (50 each, Rare)
5: MI_CRE_Buffalo_White (5, Legendary)
6-7: MI_CRE_Buffalo_Legendary_VarA/B (5 each, Legendary)

## Moa (8 variations)
0: M_CRE_Moa_MI (2000, Common)
1-3: M_CRE_Moa_Var5/8/9 (50 each, Rare)
4-6: M_CRE_Moa_Var10/11/12 (25 each, Rare)
7: M_CRE_Moa_Var13 (5, Legendary)

## Wolf (8 variations)
0: M_CRE_Wolf (2000, Common)
1-5: M_CRE_Wolf_Rare_VarA-E (50 each, Rare)
6-7: M_CRE_Wolf_Legendary_VarA/B (5 each, Legendary)

## Three Visual Mechanisms
1. Variation Array (Buffalo/Moa/Wolf) - IntProperty index
2. Breed/ActorClass (Dog 9 breeds, Cat 3, Horse Standard 3, Chicken 3)
3. Biome/Separate CreatureType (Arctic Moa, Snow Wolf, Desert Wolf)
