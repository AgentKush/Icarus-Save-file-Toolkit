# Icarus Mount Talent & Genetics Reference
*Extracted from game data tables (data.pak)*

---

## Talent Rank System
All creature talent trees use the same rank gate system:
- **Novice** - Starting rank (no investment needed)
- **Apprentice** - Requires 4 talent points invested
- **Journeyman** - Requires 8 talent points invested
- **Master** - Requires 12 talent points invested

Each individual talent typically has **3-5 ranks** (number of reward tiers).

---

## Genetic Stats (7 total)
These are the genetic values stored in the save data under `GeneticValues`:

| Internal Name | Display Name | Short | Stat Effect |
|---|---|---|---|
| Vitality | Vigor | VIR | BaseMaximumHealth |
| Endurance | Fitness | FIT | BaseMaximumStamina |
| Muscle | Physique | PHY | BaseMeleeDamage, BaseWeightCapacity |
| Agility | Reflex | REF | BaseMovementSpeed |
| Toughness | Toughness | TGH | BasePhysicalDamageResistance |
| Hardiness | Adaptation | ADP | BaseColdResistance, BaseHeatResistance |
| Utility | Instinct | INS | BaseCowTimeBetweenMilk, BaseChickenTimeBetweenEggs, BaseSheepSecondsBetweenWoolTick, BaseMountCargoSlots |

Genetic values are stored as integers in the save file (the `GeneticValues` map property).
The actual stat bonus is looked up from a CurveFloat based on the genetic value.

---

## Genetic Lineages (12 total)
Each mount has a lineage that gives bonuses/penalties:

| Lineage | Weight | Starting Bonus | Starting Penalty | Growth Per Level |
|---|---|---|---|---|
| **Wild** | 300 | +5% Water/Food consumption | - | Attacks cause Minor Hemorrhage |
| **Brave** | 50 | - | -10% Max Stamina | +Melee Damage |
| **Careful** | 50 | - | -10% Movement Speed | -Animal Threat |
| **Timid** | 50 | - | -10% Melee Damage | +Movement Speed |
| **Bold** | 50 | - | -10% Physical Resistance | +Max Stamina |
| **Hardy** | 50 | +10% Food Consumption | - | +Max Health, +Stamina Regen |
| **Stout** | 50 | +10% Animal Threat | - | +Weight Capacity |
| **Ambitious** | 50 | +50% Experience | - | *(none)* |
| **Resolute** | 25 | - | -10% Max Health | +Fertilization Recovery, +Stamina Regen |
| **Fierce** | 25 | - | -50% Fertilization Recovery | +Genetics Mutation Chance, +Cosmetic Mutation Chance |
| **Savage** | 25 | - | -50% Health Regen | Attacks Leech Health |
| **Alpha** | 10 | +20% Creature Size | - | +Melee Damage, +Max Health |

---

## BUFFALO TALENT TREE (Mounts)

### Base Talents (shared mount talents, Buffalo version)
| Talent Name | Display | Effect | Stat | Ranks |
|---|---|---|---|---|
| Creature_Base_Buffalo | Buffalo | Specialization root | BaseMaximumStamina_+% | 4 |
| Creature_Base_Health_Buffalo | Wild Fortitude | +Max Health | BaseMaximumHealth_+% | 4 (2→5→10→20) |
| Creature_Base_Stamina_Buffalo | Natural Endurance | +Max Stamina | BaseMaximumStamina_+% | 4 (2→5→10→20) |
| Creature_Base_HealthRegeneration_Buffalo | Nurtured Recovery | +Health Regen | BaseHealthRegen_+% | 4 (5→15→30→60) |
| Creature_Base_StaminaRegeneration_Buffalo | Roaming Vitality | +Stamina Regen | BaseStaminaRegen_+% | 4 (2→5→10→20) |
| Creature_Base_WeightCapacity_Buffalo | Strong Back | +Weight Capacity | BaseWeightCapacity_+% | 4 (2→5→10→20) |
| Creature_Base_MovementSpeed_Buffalo | Racing Ready | +Movement Speed | BaseMovementSpeed_+% | 3 (2→5→10) |
| Creature_Base_FallDamageReduction_Buffalo | Catlike Grace | +Fall Damage Reduction | BaseFallDamageResistance_% | 4 (5→10→20→40) |
| Creature_Base_SlowResistance_Buffalo | Riding Forward | +Slow Resistance | BaseSlowResistance_% | 4 (5→10→20→40) |
| Creature_Base_DamageReduction_Buffalo | Tough as Leather | +Physical DR | BasePhysicalDamageResistance_% | 3 (2→5→10) |
| Creature_Base_ReducedThreat_Buffalo | Soft Padding | -Animal Threat | BaseAnimalThreatModifier_+% | 4 (-2→-5→-10→-20) |
| Creature_Base_ReducedFoodConsumption_Buffalo | Metabolic Preservation | -Food Usage | BaseFoodConsumption_+% | 4 (-2→-5→-10→-20) |
| Creature_Base_ReducedWaterUsage_Buffalo | Hydration Elasticity | -Water Usage | BaseWaterConsumption_+% | 4 (-2→-5→-10→-20) |
| Creature_Base_FoodSlot_Buffalo | Large Stomach | +Food Effectiveness & Slots | BaseFruitAndVegeModifierEffectiveness_+% | 3 (5→12→15) |
| Creature_Base_FoodBuffDuration_Buffalo | Perfect Pasturage | +Food Duration | BaseFoodModifierDuration_+% | 4 (2→5→10→20) |
| Creature_Base_InventorySlots_Buffalo | Balanced Pack | +Inventory Slots | BaseMountCargoSlots_+ | 3 (1→2→4) |
| Creature_Base_Jumping_Buffalo | Springful Step | -Jump Stamina Cost | BaseJumpingStaminaActionCost_+% | 4 (-5→-10→-20→-40) |

### Buffalo-Specific Talents
| Talent Name | Display | Effect | Stat | Ranks |
|---|---|---|---|---|
| Creature_Buffalo_DamageReduction | Thick Hide | +Physical DR | BasePhysicalDamageResistance_% | 3 (2→5→10) |
| Creature_Buffalo_ExtraCarry | Cargo Hauling | +Inventory & Bulky Slot | BaseMountCargoSlots_+ | 3 (1→2→3) |
| Creature_Buffalo_Weaken | Thump Thump | Blunt Trauma on attack | BaseAttacksCauseBluntTrauma_% | 3 (15→40→80) |
| Creature_Buffalo_AuraHeatResist | Fever Control | -Desert Water Use, Hyperthermia Aura | BaseDesertWaterConsumption_+% | 3 (-2→-5→-7) |
| Creature_Buffalo_FireResist | Flaming Defiance | +Fire/Heat Resistance | BaseFireDamageResistance_+% | 3 (10→20→40) |
| Creature_Buffalo_CartMovement | Heavy Payload | +Speed while hauling cart | BaseMovementSpeedWhilePullingCart_+% | 3 (4→10→20) |

---

## BOAR TALENT TREE (Combat Pets)

### Base Combat Pet Talents (Boar version)
| Talent Name | Display | Effect | Stat | Ranks |
|---|---|---|---|---|
| CombatPet_Base_Boar | Boar | Specialization root | BaseMeleeDamage_+% | 4-5 (5→15→30→60) |
| CombatPet_Health_Boar | Wild Fortitude | +Max Health | BaseMaximumHealth_+% | 4 (2→5→10→20) |
| CombatPet_Damage_Boar | Natural Ferocity | +Melee Damage | BaseMeleeDamage_+% | 4 (5→15→30→60) |
| CombatPet_HealthRegeneration_Boar | Nurtured Recovery | +Health Regen | BaseHealthRegen_+% | 4 (5→15→30→60) |
| CombatPet_DamageReduction_Boar | Tough as Leather | +Physical DR | BasePhysicalDamageResistance_% | 4 |
| CombatPet_ReducedFoodConsumption_Boar | Metabolic Preservation | -Food Usage | BaseFoodConsumption_+% | 4 (-2→-5→-10→-20) |
| CombatPet_ReducedWaterUsage_Boar | Hydration Elasticity | -Water Usage | BaseWaterConsumption_+% | 4 |
| CombatPet_FoodSlot_Boar | Large Stomach | +Food Effectiveness & Slots | BaseFruitAndVegeModifierEffectiveness_+% | 4 |
| CombatPet_FoodBuffDuration_Boar | Perfect Pasturage | +Food Duration | BaseFoodModifierDuration_+% | 4 |

### Boar-Specific Talents
| Talent Name | Display | Effect | Stat | Ranks |
|---|---|---|---|---|
| Creature_Boar_Bleed | Rip and Tear | Bleed on hit | BaseAttacksCauseBleed_% | 3 (25→60→100) |
| Creature_Boar_Mark | Hunter | Mark target on hit | BaseAttacksCauseMarkedTarget_% | 3 (25→60→100) |
| Creature_Boar_HealOnKill | Endless Hunger | Heal on kill | BaseTotalHealthRestoredOnKill_% | 3 (5→15→30) |
| Creature_Boar_MovementSpeed | Charge! | +Movement Speed | BaseMovementSpeed_+% | 3 (5→10→20) |
| Creature_Boar_Trauma | Thump Thump | Blunt Trauma | BaseAttacksCauseBluntTrauma_% | 3 (15→40→80) |

---

## WOLF TALENT TREE (Combat Pets)

### Base Combat Pet Talents (Wolf version)
| Talent Name | Display | Effect | Stat | Ranks |
|---|---|---|---|---|
| CombatPet_Base_Wolf | Wolf | Specialization root | BaseMeleeDamage_+% | 4-5 (5→15→30→60) |
| CombatPet_Health_Wolf | Wild Fortitude | +Max Health | BaseMaximumHealth_+% | 4 (2→5→10→20) |
| CombatPet_Damage_Wolf | Natural Ferocity | +Melee Damage | BaseMeleeDamage_+% | 4 (5→15→30→60) |
| CombatPet_HealthRegeneration_Wolf | Nurtured Recovery | +Health Regen | BaseHealthRegen_+% | 4 (5→15→30→60) |
| CombatPet_DamageReduction_Wolf | Tough as Leather | +Physical DR | BasePhysicalDamageResistance_% | 4 |
| CombatPet_ReducedFoodConsumption_Wolf | Metabolic Preservation | -Food Usage | BaseFoodConsumption_+% | 4 (-2→-5→-10→-20) |
| CombatPet_ReducedWaterUsage_Wolf | Hydration Elasticity | -Water/+Heat Resist | BaseWaterConsumption_+% | 4 |
| CombatPet_FoodSlot_Wolf | Large Stomach | +Food Effectiveness & Slots | BaseFruitAndVegeModifierEffectiveness_+% | 4 |
| CombatPet_FoodBuffDuration_Wolf | Perfect Pasturage | +Food Duration/+Cold Resist | BaseFoodModifierDuration_+% | 4 |

### Wolf-Specific Talents
| Talent Name | Display | Effect | Stat | Ranks |
|---|---|---|---|---|
| Creature_Wolf_Bleed | Rip and Tear | Bleed on hit | BaseAttacksCauseBleed_% | 3 (25→60→100) |
| Creature_Wolf_Mark | Hunter | Mark target on hit | BaseAttacksCauseMarkedTarget_% | 3 (25→60→100) |
| Creature_Wolf_HealOnKill | Endless Hunger | Heal on kill | BaseTotalHealthRestoredOnKill_% | 3 (5→15→30) |
| Creature_Wolf_Slow | Slowing Strikes | Slow on hit | *(slow effect)* | 4 |
| Creature_Wolf_Highlight | Coordinated Attacks | Highlights hit targets | BaseAttacksCauseHighlightedTarget_% | 3 (25→60→100) |

### Snow Wolf Unique Talents
| Talent Name | Display | Effect | Stat | Ranks |
|---|---|---|---|---|
| Creature_SnowWolf_Freeze | Arctic Mutation | Freeze on hit + Cold Resist | BaseAttacksCauseFreeze_% | 3 (5→15→25) |
| Creature_SnowWolf_ArcticHealthRegeneration | Aura of Warmth | +Arctic Health Regen, Hypothermia Resist Aura | BaseArcticHealthRegen_+% | 3 (10→25→35) |
| Creature_SnowWolf_Mark | Hunter | Mark target | BaseAttacksCauseMarkedTarget_% | 3 (25→60→100) |
| Creature_SnowWolf_HealOnKill | Endless Hunger | Heal on kill | BaseTotalHealthRestoredOnKill_% | 3 (5→15→30) |
| Creature_SnowWolf_Highlight | Coordinated Attacks | Highlights targets | BaseAttacksCauseHighlightedTarget_% | 3 (25→60→100) |

### Desert Wolf (Hyena) Unique Talents
| Talent Name | Display | Effect | Stat | Ranks |
|---|---|---|---|---|
| Creature_DesertWolf_PoisonResistance | Scavenger | +Poison Resistance | BasePoisonDamageResistance_+% | 3 (10→20→40) |
| Creature_DesertWolf_AuraHeatResist | Fever Control | -Desert Water Use, Hyperthermia Aura | BaseDesertWaterConsumption_+% | 3 (-2→-5→-7) |
| Creature_DesertWolf_DamageReduction | Thick Hide | +Physical DR | BasePhysicalDamageResistance_% | 3 (2→5→10) |
| Creature_DesertWolf_Mark | Hunter | Mark target | BaseAttacksCauseMarkedTarget_% | 3 (25→60→100) |
| Creature_SnowWolf_DesertWolf | Endless Hunger | Heal on kill | BaseTotalHealthRestoredOnKill_% | 3 (5→15→30) |

---

## Save File Data Structure (Actual from Mounts.json)

In the Mounts.json save file, each mount's BinaryData contains UE4 serialized properties:

### Talents
- **Talents** (Array<StructProperty>): List of unlocked talents
  - Each element is a struct with:
    - `TalentRowName` (StrProperty): The talent internal name (matches tables above)
    - `TalentRank` (IntProperty): Current rank invested (1 = rank 1, 4 = max for most)
  - Example: `TalentRowName="CombatPet_Damage_Boar", TalentRank=4`

### Genetics
- **Genetics** (Array<StructProperty>): 7 genetic stat values
  - Each element is a struct with:
    - `GeneticValueName` (NameProperty): Stat name (Vitality, Endurance, Muscle, Agility, Toughness, Hardiness, Utility)
    - `Value` (IntProperty): Integer level (observed range 1-5+)
  - Example: `GeneticValueName="Muscle", Value=5`

### Lineage & Identity
- **Lineage** (NameProperty): The lineage type (Wild, Brave, Stout, Alpha, etc.)
- **MountName** (StrProperty): Display name (also in JSON metadata)
- **AISetupRowName** (NameProperty): Creature type (e.g., "Tamed_Wild_Boar", "Tamed_Buffalo", "Tamed_Wolf")
- **ActorClassName** (NameProperty): Blueprint class (e.g., "BP_Tame_Boar_C")
- **Sex** (IntProperty): 0 or 1
- **Variation** (IntProperty): Visual variation

### Combat & Stats
- **Experience** (IntProperty): Total XP earned
- **FoodLevel** (IntProperty): Current food level
- **WaterLevel** (IntProperty): Current water level
- **OxygenLevel** (IntProperty): Current oxygen level
- **Stamina** (IntProperty): Current stamina
- **CharacterRecord** → **CurrentHealth** (IntProperty): Current HP
- **CombatBehaviourState** (EnumProperty): NeutralEngagement, Aggressive, etc.
- **MovementBehaviourState** (EnumProperty): Follow, Stay, Wander
- **ConsumptionBehaviourState** (EnumProperty): Any, None, etc.

### Breeding
- **ChildDNA** (Struct): Pending offspring data with Genetics, Sex, LineageName, MotherName, FatherName
- **GestationProgress** (IntProperty): Breeding progress
- **MotherName** / **FatherName** (StrProperty): Parent names

### Position
- **ActorTransform** (Struct<Transform>): Location in world
  - Rotation (Quat), Translation (Vector), Scale3D (Vector)

### Inventory
- **SavedInventories** (Array<StructProperty>): Mount's carried items

---

## Example: Cypress (Tame Boar) from Save Data

```
Talents:
  CombatPet_HealthRegeneration_Boar  rank 4
  CombatPet_DamageReduction_Boar     rank 4
  CombatPet_Damage_Boar              rank 4

Genetics:
  Vitality=4, Endurance=5, Muscle=5, Agility=3, Toughness=1, Hardiness=5, Utility=3

Lineage: Stout (+10% Animal Threat, +Weight Capacity per level)
Experience: 41459
AISetup: Tamed_Wild_Boar
```

---

## Notes on Editing

When editing talents in the save via the mount_editor.py GUI:
1. Each talent entry stores the **TalentRowName** and **TalentRank** as a pair
2. TalentRank is the number of ranks invested (typically 1-4 for base, 1-3 for specialization)
3. To max a talent, set its TalentRank to the max rank from the tables above
4. You can add new talent entries by expanding the Talents array
5. Genetic values are integer levels - higher values give better stat bonuses via game curves
6. Lineage can be changed to any of the 12 lineage names (Wild, Brave, Careful, Timid, Bold, Hardy, Stout, Ambitious, Resolute, Fierce, Savage, Alpha)
