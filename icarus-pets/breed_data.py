"""Icarus pet breed data.

Maps creature types that have breed/color sub-variants to their D_AIRelationships
row entries. Verified against data.pak (D_AIRelationships.json, 2026-03-06).

Three sub-variant patterns exist across pet types:

  True Breeds     — each variant has a unique ActorClass (Dogs, Cat B/C)
  Color Variants  — variants share an ActorClass, differ by AISetupRowName
                    (Cat A, Chickens, HorseStandard)
  No Variants     — single fixed appearance (Horse, and all other types)

Friendly breed names (the 'label' field) are sourced from the icarus/pets
wiki (Species-and-Types.md). All names pending final confirmation via
in-game verification (#81). Row names and ActorClasses are confirmed from
pak data.
"""


# ── Dogs ─────────────────────────────────────────────────────────────────────
# 9 entries across 5 breed groups (A–E), each with a unique ActorClass.
# Pattern: True Breeds — ActorClass swap required for each variant.

_BREEDS_DOG = [
    {
        "ai_setup": "Tame_Dog_A1",
        "actor_class": "BP_Tame_Dog_A1_C",
        "label": "Golden Labrador",
    },
    {
        "ai_setup": "Tame_Dog_A2",
        "actor_class": "BP_Tame_Dog_A2_C",
        "label": "Chocolate Labrador",
    },
    {
        "ai_setup": "Tame_Dog_B1",
        "actor_class": "BP_Tame_Dog_B1_C",
        "label": "German Shepherd",
    },
    {
        "ai_setup": "Tame_Dog_B2",
        "actor_class": "BP_Tame_Dog_B2_C",
        "label": "Panda German Shepherd",
    },
    {
        "ai_setup": "Tame_Dog_C1",
        "actor_class": "BP_Tame_Dog_C1_C",
        "label": "Pug",
    },
    {
        "ai_setup": "Tame_Dog_C2",
        "actor_class": "BP_Tame_Dog_C2_C",
        "label": "French Bulldog",
    },
    {
        "ai_setup": "Tame_Dog_D1",
        "actor_class": "BP_Tame_Dog_D1_C",
        "label": "Tan Laika",
    },
    {
        "ai_setup": "Tame_Dog_D2",
        "actor_class": "BP_Tame_Dog_D2_C",
        "label": "Brown Laika",
    },
    {
        "ai_setup": "Tame_Dog_E",
        "actor_class": "BP_Tame_Dog_E_C",
        "label": "Border Collie",
    },
]


# ── Cats ─────────────────────────────────────────────────────────────────────
# 5 entries across 3 breed groups.
# Pattern: Mixed — Cat A is Color Variants (shared ActorClass), Cat B and C
# are True Breeds (unique ActorClass each). All three groups share the same
# talent tree.

_BREEDS_CAT = [
    {
        "ai_setup": "Tame_Cat_A1",
        "actor_class": "BP_Tame_Cat_C",
        "label": "Grey Tabby",
    },
    {
        "ai_setup": "Tame_Cat_A2",
        "actor_class": "BP_Tame_Cat_C",
        "label": "Orange Tabby",
    },
    {
        "ai_setup": "Tame_Cat_A3",
        "actor_class": "BP_Tame_Cat_C",
        "label": "Black Cat",
    },
    {
        "ai_setup": "Tame_Cat_B1",
        "actor_class": "BP_Tame_Cat_B_C",
        "label": "Himalayan Seal Point",
    },
    {
        "ai_setup": "Tame_Cat_C1",
        "actor_class": "BP_Tame_Cat_C_C",
        "label": "Tortoise Shell Ragdoll",
    },
]


# ── Chickens ─────────────────────────────────────────────────────────────────
# 3 entries, all sharing a single ActorClass.
# Pattern: Color Variants — AISetupRowName distinguishes the colors.

_BREEDS_CHICKEN = [
    {
        "ai_setup": "Chicken",
        "actor_class": "BP_Tame_Chicken_C",
        "label": "Chicken (default)",
    },
    {
        "ai_setup": "Chicken_A2",
        "actor_class": "BP_Tame_Chicken_C",
        "label": "Chicken (color 2)",
    },
    {
        "ai_setup": "Chicken_A3",
        "actor_class": "BP_Tame_Chicken_C",
        "label": "Chicken (color 3)",
    },
]


# ── Horse Standard ────────────────────────────────────────────────────────────
# 3 color variants of the HorseStandard type, all sharing a single ActorClass.
# Pattern: Color Variants — AISetupRowName distinguishes the colors.
# Note: Mount_Horse (the 'Horse' type) is a separate True Breed with its own
# ActorClass (BP_Mount_Horse_C) and has no sub-variants.

_BREEDS_HORSE_STANDARD = [
    {
        "ai_setup": "Mount_Horse_Standard_A1",
        "actor_class": "BP_Mount_Horse_Standard_C",
        "label": "Brown",
    },
    {
        "ai_setup": "Mount_Horse_Standard_A2",
        "actor_class": "BP_Mount_Horse_Standard_C",
        "label": "Black",
    },
    {
        "ai_setup": "Mount_Horse_Standard_A3",
        "actor_class": "BP_Mount_Horse_Standard_C",
        "label": "White",
    },
]


# ── Combined Lookup ───────────────────────────────────────────────────────────

BREED_DATA = {
    "Cat": _BREEDS_CAT,
    "Chicken": _BREEDS_CHICKEN,
    "Dog": _BREEDS_DOG,
    "HorseStandard": _BREEDS_HORSE_STANDARD,
}

# Creature types that have breed/color sub-variants
TYPES_WITH_BREEDS = sorted(BREED_DATA.keys())


# ── Public API ────────────────────────────────────────────────────────────────

def get_breeds(type_name):
    """Return the breed list for a creature type, or [] if none."""
    return BREED_DATA.get(type_name, [])


def has_breeds(type_name):
    """Return True if the creature type has breed/color sub-variants."""
    return type_name in BREED_DATA


def get_breed_labels(type_name):
    """Return a list of label strings for dropdown display.

    Returns ['Default (single appearance)'] for types without breeds.
    """
    breeds = get_breeds(type_name)
    if not breeds:
        return ["Default (single appearance)"]
    return [b["label"] for b in breeds]


def get_breed_by_ai_setup(type_name, ai_setup_row):
    """Look up a breed entry by its AISetupRowName.

    Returns the matching breed dict, or None if not found.
    """
    for b in get_breeds(type_name):
        if b["ai_setup"] == ai_setup_row:
            return b
    return None


def get_breed_actor_class(type_name, ai_setup_row):
    """Return the ActorClass for a breed identified by AISetupRowName.

    Returns None if the type has no breeds or the row is not found.
    """
    b = get_breed_by_ai_setup(type_name, ai_setup_row)
    return b["actor_class"] if b else None
