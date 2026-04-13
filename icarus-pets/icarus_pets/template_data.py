"""Canonical binary template for new mount/pet creation.

Contains a full 46-property UE4 binary blob extracted from a real
game-created creature. The template is stored as a compressed base64
blob and decompressed at import time. Species-specific fields
(AISetupRowName, ActorClassName, MountName, IcarusActorGUID) are
swapped by the caller after deep-copying the parsed properties.

Source creature: Rock (Dog, combat pet) from a live save file.
All identity/owner fields are neutralised to safe defaults.
"""

import base64
import copy
import random
import zlib

from icarus_core.ue4_parser import BinaryReader, parse_properties
from icarus_core.ue4_serializer import props_to_binary_array

# Full 46-property binary blob, zlib-compressed + base64-encoded.
# Extracted from a real game-created Dog (combat pet). All creatures
# (mounts, combat pets, farm animals) share the same property set.
_CANONICAL_BLOB_B64 = (
    "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"
)

# Decompress once at import time — ~7.4 KB in memory.
_CANONICAL_BLOB = list(zlib.decompress(base64.b64decode(_CANONICAL_BLOB_B64)))

# Parse once so we can deep-copy the property tree for each new creature.
_CANONICAL_PROPS = parse_properties(BinaryReader(_CANONICAL_BLOB))


def make_template_binary(ai_setup_row, actor_class, *, max_variation=3):
    """Return a full binary blob for a new creature of the given species.

    Deep-copies the canonical 46-property template and swaps the
    species-specific fields. Name is left empty and IcarusActorGUID
    is set to 0 — both must be set by the caller.

    Args:
        ai_setup_row: Species AI setup row name.
        actor_class: Species actor class name.
        max_variation: Upper bound for random variation index (inclusive).
            Caller can pass the species' actual variation count - 1.
    """
    props = copy.deepcopy(_CANONICAL_PROPS)
    by_name = {p["name"]: p for p in props}

    # Swap species identity
    by_name["AISetupRowName"]["value"] = ai_setup_row
    by_name["ActorClassName"]["value"] = actor_class

    # Clear identity fields (caller sets these)
    by_name["MountName"]["value"] = ""
    by_name["IcarusActorGUID"]["value"] = 0

    # Randomize gender: 1 = Female, 2 = Male
    by_name["Sex"]["value"] = random.choice([1, 2])

    # New creature starts at XP 1 (level 1)
    by_name["Experience"]["value"] = 1

    # Full food/water/stamina/oxygen — healthy newborn
    by_name["FoodLevel"]["value"] = 200
    by_name["WaterLevel"]["value"] = 200
    by_name["Stamina"]["value"] = 100
    by_name["OxygenLevel"]["value"] = 100

    # Randomize variation (appearance) — 0-based index.
    by_name["Variation"]["value"] = random.randint(0, max(0, max_variation))

    # Clear inventories — game creates saddle/cargo slots on first deploy.
    # Leaving stale entries from the source creature (e.g. InventoryID 17)
    # can prevent the game from initialising the full set (saddle + cargo).
    inventories = by_name.get("SavedInventories")
    if inventories:
        inventories["elements"] = []
        inventories["count"] = 0

    # Clear talents — game will initialise species-appropriate defaults
    talents = by_name.get("Talents")
    if talents:
        talents["elements"] = []
        talents["count"] = 0

    # Randomize genetics (1-10 scale per stat)
    _GENETIC_NAMES = [
        "Vitality", "Endurance", "Muscle", "Agility",
        "Toughness", "Hardiness", "Utility",
    ]
    genetics = by_name.get("Genetics")
    if genetics:
        new_elems = []
        for gname in _GENETIC_NAMES:
            new_elems.append([
                {"name": "GeneticValueName", "type": "NameProperty",
                 "data_size": len(gname) + 5, "array_index": 0, "value": gname},
                {"name": "Value", "type": "IntProperty",
                 "data_size": 4, "array_index": 0, "value": random.randint(1, 10)},
            ])
        genetics["elements"] = new_elems
        genetics["count"] = len(new_elems)

    if "bHasGeneratedGenetics" in by_name:
        by_name["bHasGeneratedGenetics"]["value"] = True

    return props_to_binary_array(props)
