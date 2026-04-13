"""Insert BESTIARY_DATA into talent_data.py after the aliases section."""

lines = open('talent_data.py', 'r', encoding='utf-8').readlines()

# Find insertion point: after 'get_talents_for_type = get_talent_tree'
insert_after = None
for i, line in enumerate(lines):
    if 'get_talents_for_type = get_talent_tree' in line:
        insert_after = i
        break

if insert_after is None:
    print("ERROR: Could not find insertion point")
    exit(1)

print(f"Inserting after line {insert_after+1}: {lines[insert_after].rstrip()}")

BESTIARY_BLOCK = '''

# -- Bestiary Data (extracted from pak files) ------------------------------------

BESTIARY_DATA = {
    "ArcticMoa": {"name": "Arctic Moa", "lore": "Found in icy terrazone environments. This previously extinct creature had many variants. Specifically found on Icarus is the Dinornis novaezealandiae, the second largest moa species in recorded history."},
    "Blueback": {"name": "Blueback", "lore": "The Blueback is an Icarus native, while mostly docile it will defend itself when provoked. Displays a symbiotic relationship with local and introduced fauna."},
    "BluebackDaisy": {"name": "Redback", "lore": "The Redback is an Icarus native, evolved for volcanic environments. Believed to be a distant cousin of the Blueback."},
    "Boar": {"name": "Boar", "lore": "Wild boar are medium-sized mammals with a stocky build, short legs, and bristly hair. They are typically brown or black in color and have curved tusks."},
    "Buffalo": {"name": "Buffalo", "lore": "Buffalo are large, muscular mammals with shaggy brown fur and a distinctive hump on their shoulders. They have short, curved horns and a broad, flat face."},
    "Bull": {"name": "Bull", "lore": "A powerful bovine mount, prized for its strength and resilience."},
    "Cat": {"name": "Cat", "lore": "These cats are felines that have been cryogenically preserved, their sleek fur untouched by their time spent in space. They retain their natural grace and keen senses."},
    "Chew": {"name": "Chew", "lore": "A curious creature with powerful jaws, useful as a harvesting companion."},
    "Chicken": {"name": "Chicken", "lore": "Chickens thrive under the care of competent prospectors. They have an uncanny ability to recognize humans, and hold grudges."},
    "Cow": {"name": "Cattle", "lore": "Cattle are hardy, domesticated herbivores renowned for their strength and adaptability, that thrive in grassy areas. Valued for their milk, meat, and labor."},
    "DesertWolf": {"name": "Hyena", "lore": "These medium-sized carnivores have distinctive spotted fur and powerful jaws. They are often thought of as scavengers but they are also skilled hunters."},
    "Dog": {"name": "Dog", "lore": "Dogs are loyal and beloved domesticated mammals known for their unwavering devotion. With a keen sense of smell and boundless energy, they are faithful companions."},
    "Horse": {"name": "Terrenus", "lore": "The Terrenus is an engineered descendant of Earth's horses. Its compact, sturdy build allows for swift movement. Unlike their predecessors, the Terrenus uses its tusks to defend itself."},
    "HorseStandard": {"name": "Horse", "lore": "Horses are large, herbivorous mammals renowned for their domestication and utility. Upon Icarus, they are a welcome and familiar sight in a place of peril."},
    "Moa": {"name": "Moa", "lore": "Found in moderate terrazone environments. This large flightless bird is the result of genetic experimentation, preserved Moa DNA was found in amber near Tekapo, New Zealand."},
    "Pig": {"name": "Pig", "lore": "A sturdy farm animal, useful for food production on Icarus."},
    "Raptor": {"name": "Raptor", "lore": "A swift and agile predatory mount, well-suited for desert environments."},
    "Rooster": {"name": "Rooster", "lore": "Can be specialized into aura bonuses or become more well-rounded."},
    "Sheep": {"name": "Sheep", "lore": "The humble Sheep is a mostly peaceful herbivore characterized by its thick fleece, providing insulation against the ever-changing weather of Icarus."},
    "Slinker": {"name": "Slinker", "lore": "A stealthy mount with low profile, ideal for navigating dense terrain."},
    "SnowWolf": {"name": "Snow Wolf", "lore": "Genetically engineered Eurasian wolf, designed for a harsh and cold climate. The most common predator within terraformed environments."},
    "Storca": {"name": "Storca", "lore": "A large flightless bird mount, adapted to diverse environments."},
    "Striker": {"name": "Snow Stalker", "lore": "The Stalker has a strong pack mentality, oriented around small family groups. Strong, agile and smart - the perfect hunter."},
    "SwampBird": {"name": "Ubis", "lore": "The genetics team didn't quite get the size of the Ubis right, but many prospectors are more than happy about the mistake. A genetic descendant of the Earth Flamingo."},
    "SwampQuad": {"name": "Stryder", "lore": "With their long legs and height these creatures move surprisingly swiftly when in marshy areas. Believed to be endemic to Icarus."},
    "TundraMonkey": {"name": "Tundra Monkey", "lore": "A primate adapted to cold climates, capable of assisting prospectors as a combat companion."},
    "Tusker": {"name": "Tusker", "lore": "The Tusker's four eyes help detect threats at far greater accuracy. Capable of fighting off aggressive wildlife with increased stamina and deadly protrusions."},
    "Wolf": {"name": "Wolf", "lore": "Genetically engineered Eurasian wolf, designed for various climates. Most common predator within terraformed environments."},
    "WoollyMammoth": {"name": "Mammoth", "lore": "Revived ancient earth species. A well preserved sample was found deep in the Le Brea tar pits. Due to ethics debate, the experiment had to be conducted on Icarus."},
    "WoolyZebra": {"name": "Shaggy Zebra", "lore": "These odd-looking creatures are believed to be a mutation resulting from integrating the Zebra into the Icarus food chain."},
    "Zebra": {"name": "Zebra", "lore": "Zebras are social animals that live in herds. They are herbivores and use their stripes as a form of camouflage to confuse predators."},
}


def get_bestiary_info(type_name):
    """Get bestiary display name and lore for a species type."""
    return BESTIARY_DATA.get(type_name, {"name": type_name, "lore": ""})

'''

lines.insert(insert_after + 1, BESTIARY_BLOCK)
open('talent_data.py', 'w', encoding='utf-8').write(''.join(lines))
print("BESTIARY_DATA inserted successfully")
print(f"File now has {len(lines)} lines")
