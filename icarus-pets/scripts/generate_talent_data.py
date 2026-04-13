"""Generate talent_data.py from pak_talents_extracted.json.

Reads the extracted talent definitions and produces a complete
Python module with all talent trees, genetics, lineage data,
species swap data, bestiary data, and backward-compatible aliases.

NOTE: This generator must emit ALL sections that talent_data.py needs.
If you add new data to talent_data.py, add the generation here too
so that running refresh_talent_data.py won't destroy manual additions.
"""
import json
import os

# Tree aliases: sub-types that use a parent tree's row names at runtime.
# The game defines separate D_Talents trees for these in the pak, but at runtime
# it uses the parent tree's talent row names in save files.
# Discovered via in-game testing (e.g., Desert Raptor uses Raptor_* row names).
TREE_ALIAS = {
    'Creature_Raptor_Desert': 'Creature_Raptor',
    'Creature_Chew': 'Creature_Slinker',
}

# Map pak tree names to editor type names  
TREE_NAME_MAP = {
    'Creature_Buffalo': 'Buffalo',
    'Creature_Horse': 'Horse',
    'Creature_Terrenus': 'HorseStandard',
    'Creature_Moa': 'Moa',
    'Creature_ArcticMoa': 'ArcticMoa',
    'Creature_Tusker': 'Tusker',
    'Creature_Zebra': 'Zebra',
    'Creature_WoolyZebra': 'WoolyZebra',
    'Creature_Blueback': 'Blueback',
    'Creature_Swamp_Quadruped': 'SwampQuad',
    'Creature_SwampBird': 'SwampBird',
    'Creature_WoollyMammoth': 'WoollyMammoth',
    'Creature_Bull': 'Bull',
    'Creature_Chew': 'Chew',
    'Creature_Boar': 'Boar',
    'Creature_Wolf': 'Wolf',
    'Creature_Snow_Wolf': 'SnowWolf',
    'Creature_Desert_Wolf': 'DesertWolf',
    'Creature_Dog': 'Dog',
    'Creature_Cat': 'Cat',
    'Creature_Tundra_Monkey': 'TundraMonkey',
    'Creature_Sheep': 'Sheep',
    'Creature_Chicken': 'Chicken',
    'Creature_Rooster': 'Rooster',
    'Creature_Cow': 'Cow',
    'Creature_Pig': 'Pig',
    'Creature_Raptor': 'Raptor',
    'Creature_Raptor_Desert': 'RaptorDesert',
    'Creature_Orka': 'Orka',
    'Creature_Slinker': 'Slinker',
    'Creature_Storca': 'Storca',
}

# Category for each type
CATEGORIES = {
    'Buffalo': 'mount', 'Horse': 'mount', 'HorseStandard': 'mount',
    'Moa': 'mount', 'ArcticMoa': 'mount', 'Tusker': 'mount',
    'Zebra': 'mount', 'WoolyZebra': 'mount', 'Blueback': 'mount',
    'SwampQuad': 'mount', 'SwampBird': 'mount', 'WoollyMammoth': 'mount',
    'Bull': 'mount', 'Chew': 'mount',
    'Boar': 'combatpet', 'Wolf': 'combatpet', 'SnowWolf': 'combatpet',
    'DesertWolf': 'combatpet', 'Dog': 'combatpet', 'Cat': 'combatpet',
    'TundraMonkey': 'combatpet',
    'Sheep': 'farm', 'Chicken': 'farm', 'Rooster': 'farm',
    'Cow': 'farm', 'Pig': 'farm',
    'Raptor': 'mount', 'RaptorDesert': 'mount', 'Slinker': 'mount',
    'Storca': 'mount', 'Orka': 'combatpet',
}


def format_values(vals):
    """Format a list of values as Python code."""
    formatted = []
    for v in vals:
        if v == int(v):
            formatted.append(str(int(v)))
        else:
            formatted.append(str(v))
    return '[' + ', '.join(formatted) + ']'


def main():
    with open('pak_talents_extracted.json') as f:
        data = json.load(f)
    
    lines = []
    lines.append('"""Icarus mount/pet talent and genetics data.')
    lines.append('')
    lines.append('Auto-generated from pak file extraction (pak_talent_extract.py).')
    lines.append(f'Contains {data["entry_count"]} talents across {data["tree_count"]} trees.')
    lines.append('"""')
    lines.append('')
    lines.append('# ── Genetics ──────────────────────────────────────────────────────────────────')
    lines.append('')
    lines.append('GENETICS = [')
    genetics = [
        ('Vitality', 'Vigor', 'VIR', 'Increases Maximum Health'),
        ('Endurance', 'Fitness', 'FIT', 'Increases Maximum Stamina'),
        ('Muscle', 'Physique', 'PHY', 'Increases Melee Damage & Weight Capacity'),
        ('Agility', 'Reflex', 'REF', 'Increases Movement Speed'),
        ('Toughness', 'Toughness', 'TGH', 'Increases Physical Damage Resistance'),
        ('Hardiness', 'Adaptation', 'ADP', 'Increases Cold & Heat Resistance'),
        ('Utility', 'Instinct', 'INS', 'Increases Production Speed & Cargo Slots'),
    ]
    for internal, display, short, effect in genetics:
        lines.append(f'    {{"internal": "{internal}", "display": "{display}", "short": "{short}", "effect": "{effect}"}},')
    lines.append(']')
    lines.append('')
    
    lines.append('# ── Lineages ─────────────────────────────────────────────────────────────────')
    lines.append('')
    lines.append('LINEAGES = {')
    lineages = [
        ('Wild', 'Common', '+5% Water/Food consumption', 'Attacks cause Minor Hemorrhage'),
        ('Brave', 'Uncommon', '-10% Max Stamina', '+Melee Damage per level'),
        ('Careful', 'Uncommon', '-10% Movement Speed', '-Animal Threat per level'),
        ('Timid', 'Uncommon', '-10% Melee Damage', '+Movement Speed per level'),
        ('Bold', 'Uncommon', '-10% Physical Resistance', '+Max Stamina per level'),
        ('Hardy', 'Uncommon', '+10% Food Consumption', '+Max Health & Stamina Regen per level'),
        ('Stout', 'Uncommon', '+10% Animal Threat', '+Weight Capacity per level'),
        ('Ambitious', 'Uncommon', '+50% Experience gain', 'No growth bonuses'),
        ('Resolute', 'Rare', '-10% Max Health', '+Fertilization Recovery & Stamina Regen per level'),
        ('Fierce', 'Rare', '-50% Fertilization Recovery', '+Genetics & Cosmetic Mutation Chance'),
        ('Savage', 'Rare', '-50% Health Regen', 'Attacks Leech Health per level'),
        ('Alpha', 'Very Rare', '+20% Creature Size', '+Melee Damage & Max Health per level'),
    ]
    for name, rarity, penalty, bonus in lineages:
        lines.append(f'    "{name}": {{"rarity": "{rarity}", "penalty": "{penalty}", "bonus": "{bonus}"}},')
    lines.append('}')
    lines.append('')
    
    lines.append('# ── Type Detection ────────────────────────────────────────────────────────────')
    lines.append('')
    lines.append('# Keywords checked against AISetupRowName and ActorClassName (case-insensitive)')
    lines.append('# More specific patterns first')
    lines.append('_TYPE_KEYWORDS = [')
    type_keywords = [
        ('SnowWolf', ['snow_wolf', 'snowwolf', 'wolf_snow']),
        ('DesertWolf', ['desert_wolf', 'desertwolf', 'hyena', 'wolf_desert']),
        ('ArcticMoa', ['arcticmoa', 'arctic_moa']),
        ('WoolyZebra', ['woolyzebra', 'woolly_zebra', 'wooly_zebra']),
        ('HorseStandard', ['horse_standard']),
        ('SwampBird', ['swampbird', 'swamp_bird']),
        ('SwampQuad', ['swampquad', 'swamp_quad', 'stryder']),
        ('WoollyMammoth', ['mammoth', 'woollymammoth']),
        ('TundraMonkey', ['tundramonkey', 'tundra_monkey']),
        ('RaptorDesert', ['raptor_desert']),
        ('Raptor', ['raptor']),
        ('Storca', ['storca']),
        ('Orka', ['orka']),
        ('Slinker', ['slinker_new', 'bp_mount_slinker']),
        ('Chew', ['chew', 'mini_hippo', 'mount_slinker', 'bp_slinker_mount']),
        ('Buffalo', ['buffalo']),
        ('Horse', ['horse']),
        ('Moa', ['moa']),
        ('Tusker', ['tusker']),
        ('Zebra', ['zebra']),
        ('Blueback', ['blueback']),
        ('Bull', ['bull']),
        ('Wolf', ['wolf']),
        ('Boar', ['boar']),
        ('Dog', ['dog', 'labrador']),
        ('Cat', ['cat']),
        ('Sheep', ['sheep', 'ram']),
        ('Chicken', ['chicken']),
        ('Rooster', ['rooster']),
        ('Cow', ['cow']),
        ('Pig', ['pig']),
    ]
    for type_name, keywords in type_keywords:
        lines.append(f'    ("{type_name}", {keywords}),')
    lines.append(']')
    lines.append('')
    
    lines.append('_CATEGORIES = {')
    for type_name, cat in sorted(CATEGORIES.items()):
        lines.append(f'    "{type_name}": "{cat}",')
    lines.append('}')
    lines.append('')
    
    lines.append('')
    lines.append('def detect_type(ai_setup="", actor_class=""):')
    lines.append('    """Detect creature type from AI setup row name and actor class name."""')
    lines.append('    combined = (ai_setup + " " + actor_class).lower()')
    lines.append('    for type_name, keywords in _TYPE_KEYWORDS:')
    lines.append('        if any(kw in combined for kw in keywords):')
    lines.append('            return type_name')
    lines.append('    return "Unknown"')
    lines.append('')
    lines.append('')
    lines.append('def get_category(type_name):')
    lines.append('    """Get creature category: mount, combatpet, or farm."""')
    lines.append('    return _CATEGORIES.get(type_name, "unknown")')
    lines.append('')
    
    # Generate talent trees
    lines.append('')
    lines.append('# ── Talent Trees ─────────────────────────────────────────────────────────────')
    lines.append('')
    
    for tree_key in sorted(data['trees'].keys()):
        editor_name = TREE_NAME_MAP.get(tree_key)
        if not editor_name:
            continue
        
        # If this tree is aliased, use the parent tree's talents instead.
        # The game uses the parent's row names at runtime even though D_Talents
        # defines a separate tree for this sub-type.
        source_key = TREE_ALIAS.get(tree_key, tree_key)
        if source_key != tree_key:
            tlist = data['trees'].get(source_key, [])
        else:
            tlist = data['trees'][tree_key]
        
        category = CATEGORIES.get(editor_name, 'unknown')
        
        # Separate base/root talents from actual rankable talents
        talents = [t for t in tlist if t['max_rank'] > 0]
        root = [t for t in tlist if t['max_rank'] == 0]
        
        # Skip trees with no rankable talents (WIP creatures)
        if not talents:
            continue
        
        var_name = f'_TREE_{editor_name.upper()}'
        alias_note = f' (aliased from {source_key})' if source_key != tree_key else ''
        lines.append(f'# {editor_name} ({category}) - {len(talents)} rankable talents{alias_note}')
        if root:
            lines.append(f'# Root: {root[0]["display"]} - {root[0]["desc"]}')
        lines.append(f'{var_name} = [')
        
        for t in talents:
            vals = format_values(t['values'])
            stat = t['stat'] if t['stat'] else ''
            lines.append(f'    {{')
            lines.append(f'        "name": "{t["name"]}",')
            lines.append(f'        "display": "{t["display"]}",')
            desc_escaped = t['desc'].replace('"', '\\"')
            lines.append(f'        "desc": "{desc_escaped}",')
            lines.append(f'        "max_rank": {t["max_rank"]},')
            lines.append(f'        "stat": "{stat}",')
            lines.append(f'        "values": {vals},')
            lines.append(f'    }},')
        
        lines.append(f']')
        lines.append('')
    
    # Build TALENT_TREES dict
    lines.append('')
    lines.append('# ── Combined Lookup ──────────────────────────────────────────────────────────')
    lines.append('')
    lines.append('TALENT_TREES = {')
    for tree_key in sorted(data['trees'].keys()):
        editor_name = TREE_NAME_MAP.get(tree_key)
        if not editor_name:
            continue
        # Only include trees that have rankable talents
        tlist = data['trees'][tree_key]
        talents = [t for t in tlist if t['max_rank'] > 0]
        if not talents:
            continue
        var_name = f'_TREE_{editor_name.upper()}'
        lines.append(f'    "{editor_name}": {var_name},')
    lines.append('}')
    lines.append('')
    
    # Helper functions
    lines.append('')
    lines.append('def get_talent_tree(type_name):')
    lines.append('    """Get the talent tree for a creature type, or empty list."""')
    lines.append('    return TALENT_TREES.get(type_name, [])')
    lines.append('')
    lines.append('')
    lines.append('def get_all_types():')
    lines.append('    """Get list of all creature types with talent trees."""')
    lines.append('    return list(TALENT_TREES.keys())')
    lines.append('')

    # ── Derived Constants ────────────────────────────────────────────────
    lines.append('')
    lines.append('# ── Derived Constants ────────────────────────────────────────────────────────')
    lines.append('')
    lines.append('GENETIC_ORDER = [g["internal"] for g in GENETICS]')
    lines.append('LINEAGE_NAMES = list(LINEAGES.keys())')
    lines.append('')

    # ── Backward-Compatible Aliases ──────────────────────────────────────
    lines.append('')
    lines.append('# ── Backward-Compatible Aliases ──────────────────────────────────────────────')
    lines.append('')
    lines.append('detect_mount_type = detect_type')
    lines.append('get_mount_category = get_category')
    lines.append('get_talents_for_type = get_talent_tree')
    lines.append('')

    # ── Species Data ─────────────────────────────────────────────────────
    species_data = {
        # Mounts
        "ArcticMoa":      {"actor_class": "BP_Mount_Arctic_Moa_C",       "ai_setup": "Mount_Arctic_Moa",     "mount_type": "Arctic_Moa"},
        "Blueback":       {"actor_class": "BP_Mount_Blueback_Daisy_C",   "ai_setup": "Mount_Blueback_Daisy", "mount_type": "Blueback"},
        "Buffalo":        {"actor_class": "BP_Mount_Buffalo_C",          "ai_setup": "Mount_Buffalo",         "mount_type": "Buffalo"},
        "Bull":           {"actor_class": "BP_Mount_Bull_C",             "ai_setup": "Mount_Bull",            "mount_type": "Bull"},
        "Chew":           {"actor_class": "BP_Slinker_Mount_C",          "ai_setup": "Mount_Slinker",         "mount_type": "Slinker"},
        "Horse":          {"actor_class": "BP_Mount_Horse_C",            "ai_setup": "Mount_Horse",           "mount_type": "Horse"},
        "HorseStandard":  {"actor_class": "BP_Mount_Horse_Standard_C",   "ai_setup": "Mount_Horse_Standard",  "mount_type": "Horse_Standard"},
        "Moa":            {"actor_class": "BP_Mount_Moa_C",              "ai_setup": "Mount_Moa",             "mount_type": "Moa"},
        "SwampBird":      {"actor_class": "BP_Mount_SwampBird_C",        "ai_setup": "Mount_SwampBird",       "mount_type": "SwampBird"},
        "SwampQuad":      {"actor_class": "BP_Swamp_Quadruped_Mount_C",  "ai_setup": "Mount_SwampQuad",       "mount_type": "SwampQuad"},
        "Tusker":         {"actor_class": "BP_Mount_Tusker_C",           "ai_setup": "Mount_Tusker",          "mount_type": "Tusker"},
        "WoollyMammoth":  {"actor_class": "BP_Mount_WoollyMammoth_C",    "ai_setup": "Mount_WoollyMammoth",   "mount_type": "WoollyMammoth"},
        "WoolyZebra":     {"actor_class": "BP_Mount_Wooly_Zebra_C",     "ai_setup": "Mount_Wooly_Zebra",     "mount_type": "Wooly_Zebra"},
        "Zebra":          {"actor_class": "BP_Mount_Zebra_C",            "ai_setup": "Mount_Zebra",           "mount_type": "Zebra"},
        # Combat pets
        "Boar":           {"actor_class": "BP_Tame_Boar_C",             "ai_setup": "Tamed_Wild_Boar",       "mount_type": "Wild_Boar"},
        "Cat":            {"actor_class": "BP_Tame_Cat_C",              "ai_setup": "Mount_Cat",             "mount_type": "Cat"},
        "DesertWolf":     {"actor_class": "BP_Tamed_Wolf_Desert_C",     "ai_setup": "Tamed_Desert_Wolf",     "mount_type": "Desert_Wolf"},
        "Dog":            {"actor_class": "BP_Tame_Dog_C",              "ai_setup": "Mount_Dog",             "mount_type": "Dog"},
        "SnowWolf":       {"actor_class": "BP_Tamed_Wolf_Snow_C",       "ai_setup": "Tamed_Snow_Wolf",       "mount_type": "Snow_Wolf"},
        "TundraMonkey":   {"actor_class": "BP_Tundra_Monkey_C",         "ai_setup": "Tamed_Tundra_Monkey",   "mount_type": "Tundra_Monkey"},
        "Wolf":           {"actor_class": "BP_Tamed_Wolf_C",            "ai_setup": "Tamed_Forest_Wolf",     "mount_type": "Wolf"},
        # Farm animals
        "Chicken":        {"actor_class": "BP_Tame_Chicken_C",          "ai_setup": "Mount_Chicken",         "mount_type": "Chicken"},
        "Cow":            {"actor_class": "BP_Tame_Cow_C",              "ai_setup": "Mount_Cow",             "mount_type": "Cow"},
        "Pig":            {"actor_class": "BP_Tame_Pig_C",              "ai_setup": "Mount_Pig",             "mount_type": "Pig"},
        "Rooster":        {"actor_class": "BP_Tame_Rooster_C",          "ai_setup": "Mount_Rooster",         "mount_type": "Rooster"},
        "Sheep":          {"actor_class": "BP_Tame_Sheep_C",            "ai_setup": "Mount_Sheep",           "mount_type": "Sheep"},
        # New mounts (Elysium update)
        "Raptor":         {"actor_class": "BP_Mount_Raptor_C",           "ai_setup": "Mount_Raptor",          "mount_type": "Raptor"},
        "RaptorDesert":   {"actor_class": "BP_Mount_Raptor_Desert_C",    "ai_setup": "Mount_Raptor_Desert",   "mount_type": "Raptor_Desert"},
        "Slinker":        {"actor_class": "BP_Mount_Slinker_C",          "ai_setup": "Mount_Slinker_New",     "mount_type": "Slinker_New"},
        "Storca":         {"actor_class": "BP_Mount_Storca_C",           "ai_setup": "Mount_Storca",          "mount_type": "Storca"},
        "Orka":           {"actor_class": "BP_Tamed_Orka_C",             "ai_setup": "Tamed_Orka",            "mount_type": "Orka"},
    }

    lines.append('')
    lines.append('# ── Species Data (binary field lookup for species swaps) ─────────────────────')
    lines.append('# Each entry maps a type name to the binary/JSON field values needed.')
    lines.append('# Fields: actor_class, ai_setup, mount_type (JSON MountType field)')
    lines.append('')
    lines.append('SPECIES_DATA = {')
    for sname in sorted(species_data.keys()):
        s = species_data[sname]
        lines.append(f'    "{sname}": {{"actor_class": "{s["actor_class"]}", "ai_setup": "{s["ai_setup"]}", "mount_type": "{s["mount_type"]}"}},')
    lines.append('}')
    lines.append('')

    # ── Bestiary Data ────────────────────────────────────────────────────
    # Load from bestiary_data.json if available
    bestiary = {}
    bestiary_path = 'bestiary_data.json'
    if os.path.isfile(bestiary_path):
        with open(bestiary_path, encoding='utf-8') as f:
            raw_bestiary = json.load(f)
        # Map bestiary keys to editor type names
        bestiary_key_map = {
            'Arctic_Moa': 'ArcticMoa', 'Blueback': 'Blueback', 'Wild_Boar': 'Boar',
            'Buffalo': 'Buffalo', 'Cat': 'Cat', 'MiniHippo': 'Chew',
            'Chicken': 'Chicken', 'Cattle': 'Cow', 'Desert_Wolf': 'DesertWolf',
            'Dog': 'Dog', 'Horse': 'Horse', 'Horse_Standard': 'HorseStandard',
            'Mammoth': 'WoollyMammoth',
            'Moa': 'Moa', 'Pig': 'Pig', 'Rooster': 'Rooster', 'Sheep': 'Sheep',
            'Snow_Wolf': 'SnowWolf', 'Swamp_Bird': 'SwampBird',
            'Swamp_Quadruped': 'SwampQuad', 'Tusker': 'Tusker',
            'Wooly_Zebra': 'WoolyZebra', 'Zebra': 'Zebra',
            'Forest_Wolf': 'Wolf', 'Tundra_Monkey': 'TundraMonkey',
            'Raptor': 'Raptor', 'Raptor_Desert': 'RaptorDesert',
            'Orka': 'Orka', 'Slinker': 'Slinker', 'Storca': 'Storca',
        }
        for bkey, bval in raw_bestiary.items():
            editor_type = bestiary_key_map.get(bkey)
            if editor_type:
                bestiary[editor_type] = {
                    'name': bval.get('CreatureName', editor_type),
                    'lore': bval.get('Lore1', ''),
                    'lore2': bval.get('Lore2', ''),
                }
    # Manual entries for types without bestiary data
    manual_bestiary = {
        'Bull': {'name': 'Bull', 'lore': 'A powerful bovine mount, prized for its strength and resilience.', 'lore2': ''},
        'Chew': {'name': 'Chew', 'lore': 'A curious creature with powerful jaws, useful as a harvesting companion.', 'lore2': ''},
        'Pig': {'name': 'Pig', 'lore': 'A sturdy farm animal, useful for food production on Icarus.', 'lore2': ''},
        'Rooster': {'name': 'Rooster', 'lore': 'Can be specialized into aura bonuses or become more well-rounded.', 'lore2': ''},
        'TundraMonkey': {'name': 'Tundra Monkey', 'lore': 'A primate adapted to cold climates, capable of assisting prospectors as a combat companion.', 'lore2': ''},
        'Raptor': {'name': 'Raptor', 'lore': 'A swift predatory mount found in geothermal regions.', 'lore2': ''},
        'RaptorDesert': {'name': 'Desert Raptor', 'lore': 'A desert-adapted variant of the Raptor, built for arid environments.', 'lore2': ''},
        'Orka': {'name': 'Orka', 'lore': 'A formidable combat companion.', 'lore2': ''},
        'Slinker': {'name': 'Slinker', 'lore': 'A stealthy mount with a low profile.', 'lore2': ''},
        'Storca': {'name': 'Storca', 'lore': 'A large flightless bird mount.', 'lore2': ''},
    }
    for k, v in manual_bestiary.items():
        if k not in bestiary:
            bestiary[k] = v

    lines.append('')
    lines.append('# ── Bestiary Data (extracted from pak files) ────────────────────────────────')
    lines.append('')
    lines.append('BESTIARY_DATA = {')
    for bname in sorted(bestiary.keys()):
        b = bestiary[bname]
        name_esc = b['name'].replace("'", "\\'")
        lore_esc = b['lore'].replace('"', '\\"').replace("'", "\\'")
        lore2_esc = b['lore2'].replace('"', '\\"').replace("'", "\\'")
        lines.append(f'    "{bname}": {{"name": "{b["name"]}", "lore": "{lore_esc}", "lore2": "{lore2_esc}"}},')
    lines.append('}')
    lines.append('')

    # get_bestiary_info function
    lines.append('')
    lines.append('def get_bestiary_info(type_name):')
    lines.append('    """Get bestiary display name and lore for a species type."""')
    lines.append('    return BESTIARY_DATA.get(type_name, {"name": type_name, "lore": ""})')
    lines.append('')

    # ── Species Swap Logic ───────────────────────────────────────────────
    lines.append('')
    lines.append('# ── Species Swap Logic ───────────────────────────────────────────────────────')
    lines.append('')
    lines.append('def get_swap_targets(current_type):')
    lines.append('    """Get valid species swap targets (same category only).')
    lines.append('')
    lines.append('    Returns list of type names, excluding the current type.')
    lines.append('    """')
    lines.append('    cat = get_category(current_type)')
    lines.append('    if cat == "unknown":')
    lines.append('        return []')
    lines.append('    return sorted(')
    lines.append('        t for t, c in _CATEGORIES.items()')
    lines.append('        if c == cat and t != current_type')
    lines.append('    )')
    lines.append('')
    lines.append('')
    lines.append('def remap_talents(old_talents, old_type, new_type):')
    lines.append('    """Remap talent points from old species to new species.')
    lines.append('')
    lines.append('    Matches by display name. Returns (new_talents, lost_points):')
    lines.append('    - new_talents: dict {talent_row_name: rank} for the new species')
    lines.append('    - lost_points: int, total points that couldn\'t be mapped (refunded)')
    lines.append('    """')
    lines.append('    old_tree = get_talent_tree(old_type)')
    lines.append('    new_tree = get_talent_tree(new_type)')
    lines.append('')
    lines.append('    # Build display_name → talent mapping for both trees')
    lines.append('    old_by_display = {t["display"]: t for t in old_tree}')
    lines.append('    new_by_display = {t["display"]: t for t in new_tree}')
    lines.append('')
    lines.append('    new_talents = {}')
    lines.append('    lost_points = 0')
    lines.append('')
    lines.append('    for old_row, rank in old_talents.items():')
    lines.append('        if rank <= 0:')
    lines.append('            continue')
    lines.append('')
    lines.append('        # Find the display name for this old talent')
    lines.append('        old_talent = old_by_display.get(')
    lines.append('            next((t["display"] for t in old_tree if t["name"] == old_row), None)')
    lines.append('        )')
    lines.append('        if not old_talent:')
    lines.append('            # Unknown old talent — refund all points')
    lines.append('            lost_points += rank')
    lines.append('            continue')
    lines.append('')
    lines.append('        display = old_talent["display"]')
    lines.append('')
    lines.append('        # Find matching talent in new tree by display name')
    lines.append('        new_talent = new_by_display.get(display)')
    lines.append('        if not new_talent:')
    lines.append('            # No equivalent in new tree — refund')
    lines.append('            lost_points += rank')
    lines.append('            continue')
    lines.append('')
    lines.append('        # Clamp rank to new talent\'s max_rank')
    lines.append('        new_rank = min(rank, new_talent["max_rank"])')
    lines.append('        lost_points += rank - new_rank  # refund overflow')
    lines.append('        if new_rank > 0:')
    lines.append('            new_talents[new_talent["name"]] = new_rank')
    lines.append('')
    lines.append('    return new_talents, lost_points')
    lines.append('')

    # Write output
    output = '\n'.join(lines) + '\n'
    with open('talent_data.py', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Generated talent_data.py:")
    print(f"  {len(data['trees'])} trees mapped to {len(TREE_NAME_MAP)} editor types")
    tree_count = sum(1 for k in data['trees'] if k in TREE_NAME_MAP)
    talent_count = sum(
        len([t for t in data['trees'][k] if t['max_rank'] > 0])
        for k in data['trees'] if k in TREE_NAME_MAP
    )
    print(f"  {tree_count} trees with {talent_count} rankable talents")
    print(f"  File size: {len(output):,} bytes")


if __name__ == "__main__":
    main()
