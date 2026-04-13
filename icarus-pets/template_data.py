"""Default binary templates for new mount creation.

Constructs a minimal valid UE4 binary blob for any species using only
the scalar properties the portal reads and writes. The game initialises
any absent properties (Genetics, Talents, CharacterRecord) to their
defaults when it loads the mount.
"""

from icarus_core.ue4_serializer import props_to_binary_array


def make_template_binary(ai_setup_row, actor_class):
    """Return a default binary blob for a new mount of the given species.

    All stats default to 0 / 'None'; name is left as an empty string
    and must be set by the caller before appending to SavedMounts.
    """
    props = [
        {"name": "MountName",      "type": "StrProperty", "value": ""},
        {"name": "AISetupRowName", "type": "StrProperty", "value": ai_setup_row},
        {"name": "ActorClassName", "type": "StrProperty", "value": actor_class},
        {"name": "Sex",            "type": "IntProperty", "value": 1},
        {"name": "Variation",      "type": "IntProperty", "value": 0},
        {"name": "Lineage",        "type": "StrProperty", "value": "None"},
        {"name": "Experience",     "type": "IntProperty", "value": 0},
        {"name": "FoodLevel",      "type": "IntProperty", "value": 0},
        {"name": "WaterLevel",     "type": "IntProperty", "value": 0},
        {"name": "Stamina",        "type": "IntProperty", "value": 0},
    ]
    return props_to_binary_array(props)
