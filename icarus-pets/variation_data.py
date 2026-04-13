"""Icarus creature phenotype variation data.

Auto-generated from pak file extraction (pak_variation_extract.py).
Contains variation tables for all creature types, extracted from the
IcarusMount DataTable in data.pak.

7 of 31 creature types have color variations via the Variations
system (Buffalo, Chew, Moa, Raptor, RaptorDesert, TundraMonkey, Wolf).
The remaining types have a single fixed appearance.
"""


# ── Rarity Tiers ─────────────────────────────────────────────────────────────

RARITY_THRESHOLDS = [
    (1000, "Common"),
    (100,  "Uncommon"),
    (25,   "Rare"),
    (5,    "Legendary"),
    (0,    "Ultra-Rare"),
]


def get_rarity_tier(weighting):
    """Determine rarity tier from spawn weighting.

    Thresholds: >=1000 Common, >=100 Uncommon, >=25 Rare,
    >=5 Legendary, <5 Ultra-Rare.
    """
    for threshold, tier in RARITY_THRESHOLDS:
        if weighting >= threshold:
            return tier
    return "Ultra-Rare"


# ── Variation Tables ─────────────────────────────────────────────────────────
# Each entry: index, mesh_material (short name), fur_material, weighting, rarity
# Source: D_Mounts DataTable via extract_variations.py (pak JSON parsing)

_VARIATIONS_BUFFALO = [
    {"index": 0, "mesh_material": "MI_CRE_Buffalo", "fur_material": "MI_CRE_Buffalo_fur", "weighting": 2000, "rarity": "Common"},
    {"index": 1, "mesh_material": "MI_CRE_Buffalo_Rare_VarC", "fur_material": "MI_CRE_Buffalo_Rare_VarC_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 2, "mesh_material": "MI_CRE_Buffalo_Rare_VarD", "fur_material": "MI_CRE_Buffalo_Rare_VarD_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 3, "mesh_material": "MI_CRE_Buffalo_Rare_VarG", "fur_material": "MI_CRE_Buffalo_Rare_VarG_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 4, "mesh_material": "MI_CRE_Buffalo_Rare_VarH", "fur_material": "MI_CRE_Buffalo_Rare_VarH_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 5, "mesh_material": "MI_CRE_Buffalo_White", "fur_material": "MI_CRE_Buffalo_White_fur", "weighting": 5, "rarity": "Legendary"},
    {"index": 6, "mesh_material": "MI_CRE_Buffalo_Legendary_VarA", "fur_material": "MI_CRE_Buffalo_Legendary_VarA_Fur", "weighting": 5, "rarity": "Legendary"},
    {"index": 7, "mesh_material": "MI_CRE_Buffalo_Legendary_VarB", "fur_material": "MI_CRE_Buffalo_Legendary_VarB_Fur", "weighting": 5, "rarity": "Legendary"},
]

_VARIATIONS_SLINKER = [
    {"index": 0, "mesh_material": "M_CRE_Slinker", "fur_material": "M_CRE_Slinker_Fur", "weighting": 2000, "rarity": "Common"},
    {"index": 1, "mesh_material": "M_CRE_Slinker_Rare_VarA", "fur_material": "M_CRE_Slinker_Fur_Rare_VarA", "weighting": 50, "rarity": "Rare"},
    {"index": 2, "mesh_material": "M_CRE_Slinker_Rare_VarB", "fur_material": "M_CRE_Slinker_Fur_Rare_VarB", "weighting": 50, "rarity": "Rare"},
    {"index": 3, "mesh_material": "M_CRE_Slinker_Rare_VarC", "fur_material": "M_CRE_Slinker_Fur_Rare_VarC", "weighting": 5, "rarity": "Legendary"},
    {"index": 4, "mesh_material": "M_CRE_Slinker_Rare_VarD", "fur_material": "M_CRE_Slinker_Fur_Rare_VarD", "weighting": 50, "rarity": "Rare"},
    {"index": 5, "mesh_material": "M_CRE_Slinker_Rare_VarE", "fur_material": "M_CRE_Slinker_Fur_Rare_VarE", "weighting": 50, "rarity": "Rare"},
    {"index": 6, "mesh_material": "M_CRE_Slinker_Legendary_VarA", "fur_material": "M_CRE_Slinker_Fur_Legendary_VarA", "weighting": 5, "rarity": "Legendary"},
]

_VARIATIONS_MOA = [
    {"index": 0, "mesh_material": "M_CRE_Moa_MI", "fur_material": "M_CRE_Moa_fur", "weighting": 2000, "rarity": "Common"},
    {"index": 1, "mesh_material": "M_CRE_Moa_Var5", "fur_material": "M_CRE_Moa_Var5_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 2, "mesh_material": "M_CRE_Moa_Var8", "fur_material": "M_CRE_Moa_Var8_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 3, "mesh_material": "M_CRE_Moa_Var9", "fur_material": "M_CRE_Moa_Var9_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 4, "mesh_material": "M_CRE_Moa_Var10", "fur_material": "M_CRE_Moa_Var10_Fur", "weighting": 25, "rarity": "Rare"},
    {"index": 5, "mesh_material": "M_CRE_Moa_Var11", "fur_material": "M_CRE_Moa_Var11_Fur", "weighting": 25, "rarity": "Rare"},
    {"index": 6, "mesh_material": "M_CRE_Moa_Var12", "fur_material": "M_CRE_Moa_Var12_Fur", "weighting": 25, "rarity": "Rare"},
    {"index": 7, "mesh_material": "M_CRE_Moa_Var13", "fur_material": "M_CRE_Moa_Var13_Fur", "weighting": 5, "rarity": "Legendary"},
]

_VARIATIONS_RAPTOR = [
    {"index": 0, "mesh_material": "M_CRE_Raptor", "fur_material": "", "weighting": 2000, "rarity": "Common"},
    {"index": 1, "mesh_material": "M_CRE_Raptor_Geothermal_Rare_VarA", "fur_material": "", "weighting": 50, "rarity": "Rare"},
    {"index": 2, "mesh_material": "M_CRE_Raptor_Geothermal_Rare_VarB", "fur_material": "", "weighting": 50, "rarity": "Rare"},
    {"index": 3, "mesh_material": "M_CRE_Raptor_Geothermal_Rare_VarC", "fur_material": "", "weighting": 50, "rarity": "Rare"},
    {"index": 4, "mesh_material": "M_CRE_Raptor_Geothermal_Rare_VarD", "fur_material": "", "weighting": 50, "rarity": "Rare"},
    {"index": 5, "mesh_material": "M_CRE_Raptor_Geothermal_Rare_VarE", "fur_material": "", "weighting": 50, "rarity": "Rare"},
    {"index": 6, "mesh_material": "M_CRE_Raptor_Geothermal_Rare_VarF", "fur_material": "", "weighting": 5, "rarity": "Legendary"},
    {"index": 7, "mesh_material": "M_CRE_Raptor_Geothermal_Legendary_VarA", "fur_material": "", "weighting": 5, "rarity": "Legendary"},
]

_VARIATIONS_RAPTORDESERT = [
    {"index": 0, "mesh_material": "M_CRE_Raptor_Desert", "fur_material": "", "weighting": 2000, "rarity": "Common"},
    {"index": 1, "mesh_material": "M_CRE_Raptor_Desert_Rare_VarA", "fur_material": "", "weighting": 50, "rarity": "Rare"},
    {"index": 2, "mesh_material": "M_CRE_Raptor_Desert_Rare_VarB", "fur_material": "", "weighting": 50, "rarity": "Rare"},
    {"index": 3, "mesh_material": "M_CRE_Raptor_Desert_Rare_VarC", "fur_material": "", "weighting": 50, "rarity": "Rare"},
    {"index": 4, "mesh_material": "M_CRE_Raptor_Desert_Rare_VarD", "fur_material": "", "weighting": 50, "rarity": "Rare"},
    {"index": 5, "mesh_material": "M_CRE_Raptor_Desert_Rare_VarE", "fur_material": "", "weighting": 50, "rarity": "Rare"},
    {"index": 6, "mesh_material": "M_CRE_Raptor_Desert_Legendary_VarA", "fur_material": "", "weighting": 5, "rarity": "Legendary"},
    {"index": 7, "mesh_material": "M_CRE_Raptor_Desert_Legendary_VarB", "fur_material": "", "weighting": 5, "rarity": "Legendary"},
]

_VARIATIONS_TUNDRAMONKEY = [
    {"index": 0, "mesh_material": "M_CRE_Tundra_Monkey_FurCards", "fur_material": "M_CRE_Tundra_Monkey_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 1, "mesh_material": "M_CRE_Tundra_Monkey_Rare_VarA_FurCards", "fur_material": "M_CRE_Tundra_Monkey_Rare_VarA_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 2, "mesh_material": "M_CRE_Tundra_Monkey_Rare_VarB_FurCards", "fur_material": "M_CRE_Tundra_Monkey_Rare_VarB_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 3, "mesh_material": "M_CRE_Tundra_Monkey_Rare_VarC_FurCards", "fur_material": "M_CRE_Tundra_Monkey_Rare_VarC_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 4, "mesh_material": "M_CRE_Tundra_Monkey_Rare_VarD_FurCards", "fur_material": "M_CRE_Tundra_Monkey_Rare_VarD_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 5, "mesh_material": "M_CRE_Tundra_Monkey_Rare_VarE_FurCards", "fur_material": "M_CRE_Tundra_Monkey_Rare_VarE_Fur", "weighting": 50, "rarity": "Rare"},
    {"index": 6, "mesh_material": "M_CRE_Tundra_Monkey_Legendary_VarA_FurCards", "fur_material": "M_CRE_Tundra_Monkey_Legendary_VarA_Fur", "weighting": 5, "rarity": "Legendary"},
    {"index": 7, "mesh_material": "M_CRE_Tundra_Monkey_Legendary_VarB_FurCards", "fur_material": "M_CRE_Tundra_Monkey_Legendary_VarB_Fur", "weighting": 5, "rarity": "Legendary"},
]

_VARIATIONS_WOLF = [
    {"index": 0, "mesh_material": "M_CRE_Wolf", "fur_material": "M_CRE_Wolf_fur", "weighting": 2000, "rarity": "Common"},
    {"index": 1, "mesh_material": "M_CRE_Wolf_Rare_VarA", "fur_material": "M_CRE_Wolf_Rare_VarA_fur", "weighting": 50, "rarity": "Rare"},
    {"index": 2, "mesh_material": "M_CRE_Wolf_Rare_VarB", "fur_material": "M_CRE_Wolf_Rare_VarB_fur", "weighting": 50, "rarity": "Rare"},
    {"index": 3, "mesh_material": "M_CRE_Wolf_Rare_VarC", "fur_material": "M_CRE_Wolf_Rare_VarC_fur", "weighting": 50, "rarity": "Rare"},
    {"index": 4, "mesh_material": "M_CRE_Wolf_Rare_VarD", "fur_material": "M_CRE_Wolf_Rare_VarD_fur", "weighting": 50, "rarity": "Rare"},
    {"index": 5, "mesh_material": "M_CRE_Wolf_Rare_VarE", "fur_material": "M_CRE_Wolf_Rare_VarE_fur", "weighting": 50, "rarity": "Rare"},
    {"index": 6, "mesh_material": "M_CRE_Wolf_Legendary_VarA", "fur_material": "M_CRE_Wolf_Legendary_VarA_fur", "weighting": 5, "rarity": "Legendary"},
    {"index": 7, "mesh_material": "M_CRE_Wolf_Legendary_VarB", "fur_material": "M_CRE_Wolf_Legendary_VarB_fur", "weighting": 5, "rarity": "Legendary"},
]


# ── Combined Lookup ──────────────────────────────────────────────────────────

VARIATION_DATA = {
    "Buffalo": _VARIATIONS_BUFFALO,
    "Slinker": _VARIATIONS_SLINKER,
    "Moa": _VARIATIONS_MOA,
    "Raptor": _VARIATIONS_RAPTOR,
    "RaptorDesert": _VARIATIONS_RAPTORDESERT,
    "TundraMonkey": _VARIATIONS_TUNDRAMONKEY,
    "Wolf": _VARIATIONS_WOLF,
}

# All known creature types — types not in VARIATION_DATA have no variations
ALL_CREATURE_TYPES = [
    "ArcticMoa", "Blueback", "Boar", "Buffalo", "Bull", "Cat", "Chew", "Chicken",
    "Cow", "DesertWolf", "Dog", "Horse", "HorseStandard", "Moa", "Orka",
    "Pig", "Raptor", "RaptorDesert", "Rooster", "Sheep", "Slinker", "SnowWolf",
    "Storca", "SwampBird", "SwampQuad", "TundraMonkey", "Tusker", "Wolf",
    "WoollyMammoth", "WoolyZebra", "Zebra",
]

# Types that use the Variation system (Variations array in IcarusMount DataTable)
TYPES_WITH_VARIATIONS = sorted(VARIATION_DATA.keys())


# ── Public API ───────────────────────────────────────────────────────────────

def get_variations(type_name):
    """Get the variation list for a creature type.

    Returns list of dicts with keys: index, mesh_material, fur_material,
    weighting, rarity.  Returns empty list for types without variations.
    """
    return VARIATION_DATA.get(type_name, [])


def get_variation_count(type_name):
    """Get the number of variations for a creature type (0 if none)."""
    return len(VARIATION_DATA.get(type_name, []))


def has_variations(type_name):
    """Check if a creature type has color variations."""
    return type_name in VARIATION_DATA


def get_variation_label(type_name, index):
    """Get a human-readable label for a specific variation index.

    Returns a string like 'Common \u2014 MI_CRE_Buffalo' or
    'Rare \u2014 MI_CRE_Buffalo_Rare_VarC'.
    For types without variations, returns 'Default'.
    """
    variations = get_variations(type_name)
    if not variations:
        return "Default"
    if 0 <= index < len(variations):
        v = variations[index]
        return f"{v['rarity']} \u2014 {v['mesh_material']}"
    return f"Unknown (index {index})"


def get_variation_labels(type_name):
    """Get all variation labels for dropdown display.

    Returns list of strings like:
      ['0: Common \u2014 MI_CRE_Buffalo', '1: Rare \u2014 MI_CRE_Buffalo_Rare_VarC', ...]
    For types without variations, returns ['Default (single appearance)'].
    """
    variations = get_variations(type_name)
    if not variations:
        return ["Default (single appearance)"]
    labels = []
    for v in variations:
        labels.append(f"{v['index']}: {v['rarity']} \u2014 {v['mesh_material']}")
    return labels


def validate_variation_index(type_name, index):
    """Check if a variation index is valid for the given creature type.

    Returns True if valid, False otherwise.
    For types without variations, only index 0 is valid.
    """
    count = get_variation_count(type_name)
    if count == 0:
        return index == 0
    return 0 <= index < count

