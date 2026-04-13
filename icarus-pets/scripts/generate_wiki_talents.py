"""Regenerate per-species talent wiki pages from pak_talents_extracted.json.

Reads the extracted talent data and bestiary, and writes updated
Talents-*.md wiki pages for all 26 creature types.
"""
import json
import os

# Map pak tree names to editor type names
TREE_NAME_MAP = {
    'Creature_Buffalo': 'Buffalo', 'Creature_Horse': 'Horse',
    'Creature_Terrenus': 'HorseStandard', 'Creature_Moa': 'Moa',
    'Creature_ArcticMoa': 'ArcticMoa', 'Creature_Tusker': 'Tusker',
    'Creature_Zebra': 'Zebra', 'Creature_WoolyZebra': 'WoolyZebra',
    'Creature_Blueback': 'Blueback', 'Creature_Swamp_Quadruped': 'SwampQuad',
    'Creature_SwampBird': 'SwampBird', 'Creature_WoollyMammoth': 'WoollyMammoth',
    'Creature_Bull': 'Bull', 'Creature_Chew': 'Chew',
    'Creature_Boar': 'Boar', 'Creature_Wolf': 'Wolf',
    'Creature_Snow_Wolf': 'SnowWolf', 'Creature_Desert_Wolf': 'DesertWolf',
    'Creature_Dog': 'Dog', 'Creature_Cat': 'Cat',
    'Creature_Tundra_Monkey': 'TundraMonkey', 'Creature_Sheep': 'Sheep',
    'Creature_Chicken': 'Chicken', 'Creature_Rooster': 'Rooster',
    'Creature_Cow': 'Cow', 'Creature_Pig': 'Pig',
}

# Display names for wiki page titles
DISPLAY_NAMES = {
    'ArcticMoa': 'Arctic Moa', 'Blueback': 'Blueback', 'Boar': 'Boar',
    'Buffalo': 'Buffalo', 'Bull': 'Bull', 'Cat': 'Cat', 'Chew': 'Dribbo (Chew)',
    'Chicken': 'Chicken', 'Cow': 'Cow', 'DesertWolf': 'Hyena (Desert Wolf)',
    'Dog': 'Dog', 'Horse': 'Terrenus (Horse)', 'HorseStandard': 'Horse (Standard)',
    'Moa': 'Moa', 'Pig': 'Pig', 'Rooster': 'Rooster', 'Sheep': 'Sheep',
    'SnowWolf': 'Snow Wolf', 'SwampBird': 'Ubis (Swamp Bird)',
    'SwampQuad': 'Stryder (Swamp Quad)', 'TundraMonkey': 'Tundra Monkey',
    'Tusker': 'Tusker', 'Wolf': 'Wolf', 'WoollyMammoth': 'Woolly Mammoth',
    'WoolyZebra': 'Shaggy Zebra (Wooly Zebra)', 'Zebra': 'Zebra',
}

CATEGORIES = {
    'Buffalo': 'Mount', 'Horse': 'Mount', 'HorseStandard': 'Mount',
    'Moa': 'Mount', 'ArcticMoa': 'Mount', 'Tusker': 'Mount',
    'Zebra': 'Mount', 'WoolyZebra': 'Mount', 'Blueback': 'Mount',
    'SwampQuad': 'Mount', 'SwampBird': 'Mount', 'WoollyMammoth': 'Mount',
    'Bull': 'Mount', 'Chew': 'Mount',
    'Boar': 'Combat Pet', 'Wolf': 'Combat Pet', 'SnowWolf': 'Combat Pet',
    'DesertWolf': 'Combat Pet', 'Dog': 'Combat Pet', 'Cat': 'Combat Pet',
    'TundraMonkey': 'Combat Pet',
    'Sheep': 'Farm Animal', 'Chicken': 'Farm Animal', 'Rooster': 'Farm Animal',
    'Cow': 'Farm Animal', 'Pig': 'Farm Animal',
}


def is_base_talent(talent_name):
    """Determine if a talent is a base talent (vs specialization)."""
    return (talent_name.startswith('Creature_Base_') or
            talent_name.startswith('CombatPet_'))


def format_values(vals):
    """Format values as arrow-separated string."""
    formatted = []
    for v in vals:
        if v == int(v):
            formatted.append(str(int(v)))
        else:
            formatted.append(str(v))
    return ' → '.join(formatted)


def generate_page(editor_name, talents, bestiary):
    """Generate a wiki page for a creature type."""
    display = DISPLAY_NAMES.get(editor_name, editor_name)
    category = CATEGORIES.get(editor_name, 'Unknown')

    rankable = [t for t in talents if t['max_rank'] > 0]
    base = [t for t in rankable if is_base_talent(t['name'])]
    spec = [t for t in rankable if not is_base_talent(t['name'])]

    lines = []
    lines.append(f'# {display}')
    lines.append('')
    lines.append(f'**Type:** {category} · **Internal Key:** `{editor_name}` · **Talents:** {len(rankable)} ({len(base)} base + {len(spec)} specialization)')
    lines.append('')

    # Bestiary lore
    b = bestiary.get(editor_name, {})
    lore1 = b.get('lore', '')
    lore2 = b.get('lore2', '')
    if lore1:
        lines.append(f'> {lore1}')
        if lore2:
            lines.append(f'>')
            lines.append(f'> *{lore2}*')
        lines.append('')

    # Base Talents
    if base:
        lines.append('## Base Talents')
        lines.append('')
        lines.append('| Display Name | Description | Stat | Max Rank | Values per Rank |')
        lines.append('|-------------|-------------|------|----------|----------------|')
        for t in base:
            vals = format_values(t['values'])
            lines.append(f'| {t["display"]} | {t["desc"]} | `{t["stat"]}` | {t["max_rank"]} | {vals} |')
        lines.append('')

    # Specialization Talents
    if spec:
        lines.append('## Specialization Talents')
        lines.append('')
        lines.append('| Display Name | Description | Stat | Max Rank | Values per Rank |')
        lines.append('|-------------|-------------|------|----------|----------------|')
        for t in spec:
            vals = format_values(t['values'])
            lines.append(f'| {t["display"]} | {t["desc"]} | `{t["stat"]}` | {t["max_rank"]} | {vals} |')
        lines.append('')

    # Full Talent Reference
    lines.append('## Full Talent Reference')
    lines.append('')
    lines.append('| # | Display Name | Internal Name | Type | Ranks | Stat | Values |')
    lines.append('|---|-------------|--------------|------|-------|------|--------|')
    for i, t in enumerate(rankable, 1):
        ttype = 'Base' if is_base_talent(t['name']) else '⭐ Spec'
        vals = format_values(t['values'])
        lines.append(f'| {i} | {t["display"]} | `{t["name"]}` | {ttype} | {t["max_rank"]} | `{t["stat"]}` | {vals} |')
    lines.append('')

    lines.append('---')
    lines.append('')
    lines.append('[← Back to All Talent Trees](Talent-and-Genetics-Data) · [Species & Types](Species-and-Types)')

    return '\n'.join(lines) + '\n'


def load_bestiary():
    """Load bestiary data from talent_data.py or bestiary_data.json."""
    bestiary = {}
    # Try bestiary_data.json
    if os.path.isfile('bestiary_data.json'):
        with open('bestiary_data.json', encoding='utf-8') as f:
            raw = json.load(f)
        key_map = {
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
        }
        for bkey, bval in raw.items():
            editor_type = key_map.get(bkey)
            if editor_type:
                bestiary[editor_type] = {
                    'lore': bval.get('Lore1', ''),
                    'lore2': bval.get('Lore2', ''),
                }
    # Manual entries
    manual = {
        'Bull': {'lore': 'A powerful bovine mount, prized for its strength and resilience.', 'lore2': ''},
        'Chew': {'lore': 'A curious creature with powerful jaws, useful as a harvesting companion.', 'lore2': ''},
        'Pig': {'lore': 'A sturdy farm animal, useful for food production on Icarus.', 'lore2': ''},
        'Rooster': {'lore': 'Can be specialized into aura bonuses or become more well-rounded.', 'lore2': ''},
        'TundraMonkey': {'lore': 'A primate adapted to cold climates, capable of assisting prospectors as a combat companion.', 'lore2': ''},
    }
    for k, v in manual.items():
        if k not in bestiary:
            bestiary[k] = v
    return bestiary


def main():
    with open('pak_talents_extracted.json') as f:
        data = json.load(f)

    bestiary = load_bestiary()
    wiki_dir = 'wiki'

    total_talents = 0
    pages_written = 0

    for tree_key in sorted(TREE_NAME_MAP.keys()):
        editor_name = TREE_NAME_MAP[tree_key]
        if tree_key not in data['trees']:
            print(f"  WARNING: {tree_key} not in extracted data")
            continue

        talents = data['trees'][tree_key]
        rankable = [t for t in talents if t['max_rank'] > 0]
        total_talents += len(rankable)

        page = generate_page(editor_name, talents, bestiary)
        out_path = os.path.join(wiki_dir, f'Talents-{editor_name}.md')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(page)
        pages_written += 1
        print(f"  {editor_name}: {len(rankable)} talents → {out_path}")

    print(f"\nGenerated {pages_written} wiki pages with {total_talents} total rankable talents")


if __name__ == '__main__':
    main()
