# Talent & Genetics Data

## Genetics (7 stats, 0-10 range each)
| Internal | Display | Short | Effect |
|----------|---------|-------|--------|
| Vitality | Vigor | VIR | Max Health |
| Endurance | Fitness | FIT | Max Stamina |
| Muscle | Physique | PHY | Melee Damage & Weight Capacity |
| Agility | Reflex | REF | Movement Speed |
| Toughness | Toughness | TGH | Physical Damage Resistance |
| Hardiness | Adaptation | ADP | Cold & Heat Resistance |
| Utility | Instinct | INS | Production Speed & Cargo Slots |

Storage: ArrayProperty<StructProperty> with 7 elements, each having GeneticValueName (StrProperty) + Value (IntProperty 0-10)

## Lineages
| Lineage | Rarity | Penalty | Growth Bonus |
|---------|--------|---------|-------------|
| Wild | Common | +5% Water/Food consumption | Minor Hemorrhage attacks |
| Brave | Uncommon | -10% Max Stamina | +Melee Damage/level |
| Careful | Uncommon | -10% Movement Speed | -Animal Threat/level |
| Timid | Uncommon | -10% Melee Damage | +Movement Speed/level |
| Bold | Uncommon | -10% Physical Resistance | +Max Stamina/level |
| Hardy | Uncommon | +10% Food Consumption | +Max Health & Stamina Regen/level |
| Stout | Uncommon | +10% Animal Threat | +Weight Capacity/level |
| Ambitious | Uncommon | +50% Experience gain | No growth bonuses |
| Resolute | Rare | -10% Max Health | +Fertilization Recovery & Stamina Regen/level |
| Fierce | Rare | -50% Fertilization Recovery | +Genetics & Cosmetic Mutation Chance |
| Savage | Rare | -50% Health Regen | Leech Health attacks/level |
| Alpha | Very Rare | +20% Creature Size | +Melee Damage & Max Health/level |

Storage: NameProperty string e.g. "Bold", "Wild", "Alpha"

## Talent Storage
ArrayProperty<StructProperty>. Each element: TalentRowName (StrProperty) + TalentRank (IntProperty). Only learned talents stored.

## Level Caps
- Mounts: 50
- Combat Pets: 25
- Farm Animals: 25
