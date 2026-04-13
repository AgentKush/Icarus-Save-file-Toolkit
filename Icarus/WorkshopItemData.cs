namespace Icarus;

/// <summary>
/// Workshop item data sourced from D_WorkshopItems (331 rows).
/// Data extracted from the Icarus game data catalog.
/// Used for autocomplete/dropdown when adding items to inventory or loadouts.
/// </summary>
public static class WorkshopItemData
{
    /// <summary>
    /// All workshop items with their MetaRow names, display names, and categories.
    /// The MetaRow is the key used in MetaInventory.json and Loadouts.json.
    /// </summary>
    public static readonly List<(string MetaRow, string DisplayName, string Category)> KnownItems =
    [
        // ===== Envirosuits =====
        ("Meta_Envirosuit_Basic", "Basic Envirosuit", "Envirosuits"),
        ("Meta_Envirosuit", "Envirosuit", "Envirosuits"),
        ("Meta_Envirosuit2", "Envirosuit MK2", "Envirosuits"),
        ("Meta_Envirosuit3", "Envirosuit MK3", "Envirosuits"),
        ("Meta_Envirosuit4", "Envirosuit MK4", "Envirosuits"),
        ("Meta_Envirosuit5", "Envirosuit MK5", "Envirosuits"),
        ("Meta_Envirosuit6", "Envirosuit MK6", "Envirosuits"),
        ("Meta_Deluxe_Envirosuit", "Deluxe Envirosuit", "Envirosuits"),
        ("Meta_Shengong_Envirosuit", "Shengong Envirosuit", "Envirosuits"),
        ("Meta_Shengong_Envirosuit_2", "Shengong Envirosuit MK2", "Envirosuits"),
        ("Meta_Envirosuit_Inaris", "Inaris Envirosuit", "Envirosuits"),
        ("Meta_Envirosuit_Larkell_Alpha", "Larkwell Envirosuit Alpha", "Envirosuits"),
        ("Meta_Envirosuit_Larkell_Bravo", "Larkwell Envirosuit Bravo", "Envirosuits"),
        ("Meta_Envirosuit_Larkell_White", "Larkwell Envirosuit White", "Envirosuits"),

        // ===== Consumables =====
        ("Meta_Ration", "Ration", "Consumables"),
        ("Meta_Super_Ration", "Super Ration", "Consumables"),
        ("Meta_Soda", "Soda", "Consumables"),
        ("Meta_Oxygen_Gel", "Oxygen Gel", "Consumables"),
        ("Meta_Stamina_Gel", "Stamina Gel", "Consumables"),
        ("Meta_Purification_Tablet", "Purification Tablet", "Consumables"),
        ("Meta_Kiwi_Fruit", "Kiwi Fruit", "Consumables"),

        // ===== Modules =====
        ("Meta_Module_Tracker", "Tracker Module", "Modules"),
        ("Meta_Module_MovementSpeed", "Movement Speed Module", "Modules"),
        ("Meta_Module_Carry_Weight", "Carry Weight Module", "Modules"),
        ("Meta_Module_Poison_Resistance", "Poison Resistance Module", "Modules"),
        ("Meta_Module_Fire_Resistance", "Fire Resistance Module", "Modules"),
        ("Meta_Module_Inventory_Slots_1", "Inventory Slots Module MK1", "Modules"),
        ("Meta_Module_Inventory_Slots_2", "Inventory Slots Module MK2", "Modules"),
        ("Meta_Module_Consumption", "Consumption Module", "Modules"),
        ("Meta_Module_Fall_Damage", "Fall Damage Module", "Modules"),
        ("Meta_Module_Animal_Healthbar", "Animal Healthbar Module", "Modules"),
        ("Meta_Module_Animal_Highlighting", "Animal Highlighting Module", "Modules"),
        ("Meta_Module_Alpha", "Module Alpha", "Modules"),
        ("Meta_Module_Beta", "Module Beta", "Modules"),
        ("Meta_Module_World_Boss", "World Boss Module", "Modules"),
        ("Meta_Module_Temperature", "Temperature Module", "Modules"),
        ("Meta_Module_Caving", "Caving Module", "Modules"),
        ("Meta_Module_Extremes", "Extremes Module", "Modules"),
        ("Meta_Module_Fishing", "Fishing Module", "Modules"),
        ("Meta_Module_Wounds", "Wounds Module", "Modules"),
        ("Meta_Module_Taming", "Taming Module", "Modules"),
        ("Meta_Module_Food", "Food Module", "Modules"),
        ("Meta_Module_Oxygen", "Oxygen Module", "Modules"),
        ("Meta_Module_Water", "Water Module", "Modules"),
        ("Meta_Module_TamedDamage", "Tamed Damage Module", "Modules"),
        ("Meta_Module_Melee", "Melee Module", "Modules"),
        ("Meta_Module_HeatResist", "Heat Resistance Module", "Modules"),
        ("Meta_Module_ColdResist", "Cold Resistance Module", "Modules"),
        ("Meta_Module_ExposureResist", "Exposure Resistance Module", "Modules"),
        ("Meta_Module_ItemWear", "Item Wear Module", "Modules"),
        ("Meta_Module_Night", "Night Vision Module", "Modules"),
        ("Meta_Module_Highlight", "Highlight Module", "Modules"),
        ("Meta_Module_StaminaRegen", "Stamina Regen Module", "Modules"),
        ("Meta_Module_Radiation", "Radiation Module", "Modules"),

        // ===== Shengong Tools =====
        ("Meta_Axe_Shengong_Alpha", "Shengong Axe Alpha", "Shengong Tools"),
        ("Meta_Axe_Shengong_Beta", "Shengong Axe Beta", "Shengong Tools"),
        ("Meta_Axe_Shengong_Charlie", "Shengong Axe Charlie", "Shengong Tools"),
        ("Meta_Axe_Shengong_Delta", "Shengong Axe Delta", "Shengong Tools"),
        ("Meta_Axe_Shengong_Echo", "Shengong Axe Echo", "Shengong Tools"),
        ("Meta_Pickaxe_Shengong_Alpha", "Shengong Pickaxe Alpha", "Shengong Tools"),
        ("Meta_Pickaxe_Shengong_Beta", "Shengong Pickaxe Beta", "Shengong Tools"),
        ("Meta_Pickaxe_Shengong_Charlie", "Shengong Pickaxe Charlie", "Shengong Tools"),
        ("Meta_Pickaxe_Shengong_Delta", "Shengong Pickaxe Delta", "Shengong Tools"),
        ("Meta_Pickaxe_Shengong_Echo", "Shengong Pickaxe Echo", "Shengong Tools"),
        ("Meta_Spear_Shengong_Alpha", "Shengong Spear Alpha", "Shengong Tools"),
        ("Meta_Spear_Shengong_Beta", "Shengong Spear Beta", "Shengong Tools"),
        ("Meta_Spear_Shengong_Charlie", "Shengong Spear Charlie", "Shengong Tools"),
        ("Meta_Spear_Shengong_Delta", "Shengong Spear Delta", "Shengong Tools"),
        ("Meta_Spear_Shengong_Echo", "Shengong Spear Echo", "Shengong Tools"),
        ("Meta_Knife_Shengong_Alpha", "Shengong Knife Alpha", "Shengong Tools"),
        ("Meta_Knife_Shengong_Beta", "Shengong Knife Beta", "Shengong Tools"),
        ("Meta_Knife_Shengong_Charlie", "Shengong Knife Charlie", "Shengong Tools"),
        ("Meta_Knife_Shengong_Delta", "Shengong Knife Delta", "Shengong Tools"),
        ("Meta_Knife_Shengong_Echo", "Shengong Knife Echo", "Shengong Tools"),
        ("Meta_Hammer_Shengong_Alpha", "Shengong Hammer Alpha", "Shengong Tools"),
        ("Meta_Hammer_Shengong_Beta", "Shengong Hammer Beta", "Shengong Tools"),
        ("Meta_Hammer_Shengong_Charlie", "Shengong Hammer Charlie", "Shengong Tools"),
        ("Meta_Hammer_Shengong_Delta", "Shengong Hammer Delta", "Shengong Tools"),
        ("Meta_Hammer_Shengong_Echo", "Shengong Hammer Echo", "Shengong Tools"),
        ("Meta_Sickle_Shengong_01", "Shengong Sickle MK1", "Shengong Tools"),
        ("Meta_Sickle_Shengong_02", "Shengong Sickle MK2", "Shengong Tools"),

        // ===== Shengong Ranged =====
        ("Meta_Bow_Shengong_Alpha", "Shengong Bow Alpha", "Shengong Ranged"),
        ("Meta_Bow_Shengong_Beta", "Shengong Bow Beta", "Shengong Ranged"),
        ("Meta_Bow_Shengong_Charlie", "Shengong Bow Charlie", "Shengong Ranged"),
        ("Meta_Bow_Shengong_Delta", "Shengong Bow Delta", "Shengong Ranged"),
        ("Meta_Bow_Shengong_Echo", "Shengong Bow Echo", "Shengong Ranged"),
        ("Meta_Arrow_Set_Shengong", "Shengong Arrow Set", "Shengong Ranged"),
        ("Meta_Bandage_Shengong", "Shengong Bandage", "Shengong Medical"),
        ("Meta_Canteen_Shengong", "Shengong Canteen", "Shengong Equipment"),
        ("Meta_Oxygen_Tank_Shengong", "Shengong Oxygen Tank", "Shengong Equipment"),

        // ===== Printed Tools & Items =====
        ("Meta_Axe_Printed", "Printed Axe", "Printed Items"),
        ("Meta_Knife_Printed", "Printed Knife", "Printed Items"),
        ("Meta_Pickaxe_Printed", "Printed Pickaxe", "Printed Items"),
        ("Meta_Spear_Printed", "Printed Spear", "Printed Items"),
        ("Meta_Sickle_Printed", "Printed Sickle", "Printed Items"),
        ("Meta_Firewhacker_Printed", "Printed Firewhacker", "Printed Items"),
        ("Meta_Hammer_Printed", "Printed Hammer", "Printed Items"),
        ("Meta_Cot_Printed", "Printed Cot", "Printed Items"),
        ("Meta_Campfire_Printed", "Printed Campfire", "Printed Items"),
        ("Meta_Furnace_Printed", "Printed Furnace", "Printed Items"),
        ("Meta_Crate_Printed", "Printed Crate", "Printed Items"),

        // ===== Printed Arrow Sets =====
        ("Meta_Arrow_Set_Printed_Alpha", "Printed Arrow Set Alpha", "Printed Items"),
        ("Meta_Arrow_Set_Printed_Beta", "Printed Arrow Set Beta", "Printed Items"),
        ("Meta_Arrow_Set_Printed_Charlie", "Printed Arrow Set Charlie", "Printed Items"),

        // ===== Vaccines =====
        ("Meta_Antibiotic_Vaccine_Alpha", "Antibiotic Vaccine Alpha", "Vaccines"),
        ("Meta_Antibiotic_Vaccine_Beta", "Antibiotic Vaccine Beta", "Vaccines"),
        ("Meta_Antibiotic_Vaccine_Charlie", "Antibiotic Vaccine Charlie", "Vaccines"),
        ("Meta_Antiparasitic_Vaccine_Alpha", "Antiparasitic Vaccine Alpha", "Vaccines"),
        ("Meta_Antiparasitic_Vaccine_Beta", "Antiparasitic Vaccine Beta", "Vaccines"),
        ("Meta_Antiparasitic_Vaccine_Charlie", "Antiparasitic Vaccine Charlie", "Vaccines"),
        ("Meta_Antipoison_Vaccine_Alpha", "Antipoison Vaccine Alpha", "Vaccines"),
        ("Meta_Antipoison_Vaccine_Beta", "Antipoison Vaccine Beta", "Vaccines"),
        ("Meta_Antipoison_Vaccine_Charlie", "Antipoison Vaccine Charlie", "Vaccines"),
        ("Meta_Blood_Thinning_Vaccine_Alpha", "Blood Thinning Vaccine Alpha", "Vaccines"),
        ("Meta_Blood_Thinning_Vaccine_Beta", "Blood Thinning Vaccine Beta", "Vaccines"),
        ("Meta_Blood_Thinning_Vaccine_Charlie", "Blood Thinning Vaccine Charlie", "Vaccines"),

        // ===== Carbon Armor =====
        ("Meta_Carbon_Armor_Head", "Carbon Armor Head", "Carbon Armor"),
        ("Meta_Carbon_Armor_Chest", "Carbon Armor Chest", "Carbon Armor"),
        ("Meta_Carbon_Armor_Arms", "Carbon Armor Arms", "Carbon Armor"),
        ("Meta_Carbon_Armor_Legs", "Carbon Armor Legs", "Carbon Armor"),
        ("Meta_Carbon_Armor_Feet", "Carbon Armor Feet", "Carbon Armor"),
        ("Meta_Carbon_Armor_Head_Alpha", "Carbon Armor Head Alpha", "Carbon Armor"),
        ("Meta_Carbon_Armor_Chest_Alpha", "Carbon Armor Chest Alpha", "Carbon Armor"),
        ("Meta_Carbon_Armor_Arms_Alpha", "Carbon Armor Arms Alpha", "Carbon Armor"),
        ("Meta_Carbon_Armor_Legs_Alpha", "Carbon Armor Legs Alpha", "Carbon Armor"),
        ("Meta_Carbon_Armor_Feet_Alpha", "Carbon Armor Feet Alpha", "Carbon Armor"),
        ("Meta_Carbon_Armor_Head_Beta", "Carbon Armor Head Beta", "Carbon Armor"),
        ("Meta_Carbon_Armor_Chest_Beta", "Carbon Armor Chest Beta", "Carbon Armor"),
        ("Meta_Carbon_Armor_Arms_Beta", "Carbon Armor Arms Beta", "Carbon Armor"),
        ("Meta_Carbon_Armor_Legs_Beta", "Carbon Armor Legs Beta", "Carbon Armor"),
        ("Meta_Carbon_Armor_Feet_Beta", "Carbon Armor Feet Beta", "Carbon Armor"),

        // ===== Larkwell Armor =====
        ("Meta_Larkwell_Armor_Alpha_Head", "Larkwell Armor Alpha Head", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_Alpha_Chest", "Larkwell Armor Alpha Chest", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_Alpha_Arms", "Larkwell Armor Alpha Arms", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_Alpha_Legs", "Larkwell Armor Alpha Legs", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_Alpha_Feet", "Larkwell Armor Alpha Feet", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_Black_Head", "Larkwell Armor Black Head", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_Black_Chest", "Larkwell Armor Black Chest", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_Black_Arms", "Larkwell Armor Black Arms", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_Black_Legs", "Larkwell Armor Black Legs", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_Black_Feet", "Larkwell Armor Black Feet", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_White_Head", "Larkwell Armor White Head", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_White_Chest", "Larkwell Armor White Chest", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_White_Arms", "Larkwell Armor White Arms", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_White_Legs", "Larkwell Armor White Legs", "Larkwell Armor"),
        ("Meta_Larkwell_Armor_White_Feet", "Larkwell Armor White Feet", "Larkwell Armor"),

        // ===== Bulky Armor =====
        ("Meta_Bulky_Armor_Head", "Bulky Armor Head", "Bulky Armor"),
        ("Meta_Bulky_Armor_Chest", "Bulky Armor Chest", "Bulky Armor"),
        ("Meta_Bulky_Armor_Arms", "Bulky Armor Arms", "Bulky Armor"),
        ("Meta_Bulky_Armor_Legs", "Bulky Armor Legs", "Bulky Armor"),
        ("Meta_Bulky_Armor_Feet", "Bulky Armor Feet", "Bulky Armor"),

        // ===== Coal =====
        ("Meta_Coal", "Coal", "Resources"),

        // ===== Backpacks =====
        ("Meta_Backpack_Mining", "Mining Backpack", "Backpacks"),
        ("Meta_Backpack_Quiver", "Quiver Backpack", "Backpacks"),
        ("Meta_Backpack_Survival", "Survival Backpack", "Backpacks"),
        ("Meta_Backpack_Larkwell_Alpha", "Larkwell Backpack Alpha", "Backpacks"),
        ("Meta_Backpack_Larkwell_Beta", "Larkwell Backpack Beta", "Backpacks"),
        ("Meta_Farmers_Backpack", "Farmer's Backpack", "Backpacks"),
        ("Meta_Explorers_Backpack", "Explorer's Backpack", "Backpacks"),
        ("Meta_Tech_Backpack", "Tech Backpack", "Backpacks"),
        ("Meta_Hunters_Backpack", "Hunter's Backpack", "Backpacks"),
        ("Meta_Medic_Backpack", "Medic Backpack", "Backpacks"),
        ("Meta_Chefs_Backpack", "Chef's Backpack", "Backpacks"),
        ("Meta_Solar_Backpack", "Solar Backpack", "Backpacks"),

        // ===== Seeds =====
        ("Meta_Corn_Seed", "Corn Seed", "Seeds"),
        ("Meta_Pumpkin_Seed", "Pumpkin Seed", "Seeds"),
        ("Meta_Squash_Seed", "Squash Seed", "Seeds"),
        ("Meta_Carrot_Seed", "Carrot Seed", "Seeds"),
        ("Meta_Mushroom_Seed", "Mushroom Seed", "Seeds"),
        ("Meta_Berry_Seed", "Berry Seed", "Seeds"),
        ("Meta_Wheat_Seed", "Wheat Seed", "Seeds"),
        ("Meta_Watermelon_Seed", "Watermelon Seed", "Seeds"),
        ("Meta_Bean_Seed", "Bean Seed", "Seeds"),
        ("Meta_Rhubarb_Seed", "Rhubarb Seed", "Seeds"),
        ("Meta_Kumara_Seed", "Kumara Seed", "Seeds"),
        ("Meta_Avocado_Seed", "Avocado Seed", "Seeds"),
        ("Meta_Stawberry_Seed", "Strawberry Seed", "Seeds"),
        ("Meta_Reed_Seed", "Reed Seed", "Seeds"),
        ("Meta_Yeast_Seed", "Yeast Seed", "Seeds"),
        ("Meta_Lily_Seed", "Lily Seed", "Seeds"),
        ("Meta_Cocao_Seed", "Cocoa Seed", "Seeds"),
        ("Meta_Coffee_Seed", "Coffee Seed", "Seeds"),
        ("Meta_GreenTea_Seed", "Green Tea Seed", "Seeds"),
        ("Meta_WildTea_Seed", "Wild Tea Seed", "Seeds"),
        ("Meta_Fiber_Seed", "Fiber Seed", "Seeds"),
        ("Meta_Tomato_Seed", "Tomato Seed", "Seeds"),
        ("Meta_Potato_Seed", "Potato Seed", "Seeds"),
        ("Meta_SugarCane_Seed", "Sugar Cane Seed", "Seeds"),
        ("Meta_Coconut_Seed", "Coconut Seed", "Seeds"),
        ("Meta_Bramble_Seed", "Bramble Seed", "Seeds"),
        ("Meta_Banana_Seed", "Banana Seed", "Seeds"),
        ("Meta_Onion_Seed", "Onion Seed", "Seeds"),
        ("Meta_Agave_Seed", "Agave Seed", "Seeds"),
        ("Meta_PricklyPear_Seed", "Prickly Pear Seed", "Seeds"),
        ("Meta_Garlic_Seed", "Garlic Seed", "Seeds"),
        ("Meta_Truffle_Seed", "Truffle Seed", "Seeds"),

        // ===== Inaris Tools =====
        ("Meta_Axe_Inaris_Alpha", "Inaris Axe Alpha", "Inaris Tools"),
        ("Meta_Axe_Inaris_Bravo", "Inaris Axe Bravo", "Inaris Tools"),
        ("Meta_Axe_Inaris_Charlie", "Inaris Axe Charlie", "Inaris Tools"),
        ("Meta_Axe_Inaris_Delta", "Inaris Axe Delta", "Inaris Tools"),
        ("Meta_Knife_Inaris_Alpha", "Inaris Knife Alpha", "Inaris Tools"),
        ("Meta_Knife_Inaris_Bravo", "Inaris Knife Bravo", "Inaris Tools"),
        ("Meta_Knife_Inaris_Charlie", "Inaris Knife Charlie", "Inaris Tools"),
        ("Meta_Knife_Inaris_Delta", "Inaris Knife Delta", "Inaris Tools"),
        ("Meta_Pickaxe_Inaris_Alpha", "Inaris Pickaxe Alpha", "Inaris Tools"),
        ("Meta_Pickaxe_Inaris_Bravo", "Inaris Pickaxe Bravo", "Inaris Tools"),
        ("Meta_Pickaxe_Inaris_Charlie", "Inaris Pickaxe Charlie", "Inaris Tools"),
        ("Meta_Pickaxe_Inaris_Delta", "Inaris Pickaxe Delta", "Inaris Tools"),
        ("Meta_Spear_Inaris_Alpha", "Inaris Spear Alpha", "Inaris Tools"),
        ("Meta_Spear_Inaris_Bravo", "Inaris Spear Bravo", "Inaris Tools"),
        ("Meta_Spear_Inaris_Charlie", "Inaris Spear Charlie", "Inaris Tools"),
        ("Meta_Spear_Inaris_Delta", "Inaris Spear Delta", "Inaris Tools"),
        ("Meta_Sickle_Inaris_00", "Inaris Sickle MK0", "Inaris Tools"),
        ("Meta_Sickle_Inaris_01", "Inaris Sickle MK1", "Inaris Tools"),
        ("Meta_Sickle_Inaris_02", "Inaris Sickle MK2", "Inaris Tools"),
        ("Meta_Sickle_Inaris_03", "Inaris Sickle MK3", "Inaris Tools"),

        // ===== Inaris Ranged =====
        ("Meta_Arrow_Set_Inaris", "Inaris Arrow Set", "Inaris Ranged"),
        ("Meta_Arrow_Inaris_Bravo", "Inaris Arrow Bravo", "Inaris Ranged"),
        ("Meta_Arrow_Inaris_Charlie", "Inaris Arrow Charlie", "Inaris Ranged"),
        ("Meta_Arrow_Inaris_Delta", "Inaris Arrow Delta", "Inaris Ranged"),
        ("Meta_Crossbow_Inaris_A", "Inaris Crossbow A", "Inaris Ranged"),
        ("Meta_Crossbow_Inaris_B", "Inaris Crossbow B", "Inaris Ranged"),
        ("Meta_Crossbow_Inaris_C", "Inaris Crossbow C", "Inaris Ranged"),
        ("Meta_Crossbow_Inaris_D", "Inaris Crossbow D", "Inaris Ranged"),

        // ===== Larkwell Tools =====
        ("Meta_Axe_Larkwell", "Larkwell Axe", "Larkwell Tools"),
        ("Meta_Pickaxe_Larkwell", "Larkwell Pickaxe", "Larkwell Tools"),
        ("Meta_Hammer_Larkwell", "Larkwell Hammer", "Larkwell Tools"),
        ("Meta_Spear_Larkwell", "Larkwell Spear", "Larkwell Tools"),
        ("Meta_Knife_Larkwell", "Larkwell Knife", "Larkwell Tools"),
        ("Meta_Sickle_Larkwell", "Larkwell Sickle", "Larkwell Tools"),
        ("Meta_Bow_Larkwell", "Larkwell Bow", "Larkwell Ranged"),

        // ===== Larkwell Ammo =====
        ("Meta_Arrow_Set_Larkwell_Standard", "Larkwell Arrow Set Standard", "Larkwell Ranged"),
        ("Meta_Arrow_Set_Larkwell_Ballistic", "Larkwell Arrow Set Ballistic", "Larkwell Ranged"),
        ("Meta_Arrow_Set_Larkwell_Bleed", "Larkwell Arrow Set Bleed", "Larkwell Ranged"),
        ("Meta_Arrow_Set_Larkwell_Tazer", "Larkwell Arrow Set Tazer", "Larkwell Ranged"),
        ("Meta_Bolt_Set_Larkwell_Standard", "Larkwell Bolt Set Standard", "Larkwell Ranged"),
        ("Meta_Bolt_Set_Larkwell_Electroshock", "Larkwell Bolt Set Electroshock", "Larkwell Ranged"),
        ("Meta_Bolt_Set_Larkwell_Explosive", "Larkwell Bolt Set Explosive", "Larkwell Ranged"),
        ("Meta_Bolt_Set_Larkwell_Piercing", "Larkwell Bolt Set Piercing", "Larkwell Ranged"),

        // ===== Larkwell Equipment =====
        ("Meta_Heated_Canteen_Larkwell", "Larkwell Heated Canteen", "Larkwell Equipment"),
        ("Meta_Heated_Canteen_Inaris", "Inaris Heated Canteen", "Inaris Equipment"),
        ("Meta_Oxygen_Tank_Larkwell", "Larkwell Oxygen Tank", "Larkwell Equipment"),

        // ===== Scanners & Utility =====
        ("Meta_Scanner_DeepOre", "Deep Ore Scanner", "Scanners"),
        ("Meta_Scanner_Creatures", "Creature Scanner", "Scanners"),
        ("Meta_Fishfinder", "Fishfinder", "Scanners"),

        // ===== Deployables =====
        ("Meta_Repair_Item_Pack", "Repair Item Pack", "Deployables"),
        ("Meta_Extractor", "Extractor", "Deployables"),
        ("Meta_Radar", "Radar", "Deployables"),
        ("Meta_Biofuel_Can", "Biofuel Can", "Deployables"),
        ("Meta_Power_Source", "Power Source", "Deployables"),
        ("Meta_Dropship_Beacon", "Dropship Beacon", "Deployables"),
        ("Meta_CropPlot", "Crop Plot", "Deployables"),
        ("Meta_Shovel", "Shovel", "Deployables"),
        ("Meta_Beehive_Starter_Kit", "Beehive Starter Kit", "Deployables"),
        ("Meta_Oil_Can", "Oil Can", "Deployables"),
        ("Meta_Hydrazine_Cooker", "Hydrazine Cooker", "Deployables"),
        ("Meta_Hydrazine_Heater", "Hydrazine Heater", "Deployables"),
        ("Meta_Hydrazine_Canister", "Hydrazine Canister", "Deployables"),

        // ===== Resource Packs =====
        ("Meta_Resource_Pack_Wood", "Wood Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Stone", "Stone Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Oxite", "Oxite Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Sulfur", "Sulfur Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Silica", "Silica Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Iron", "Iron Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Copper", "Copper Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Gold", "Gold Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Limestone", "Limestone Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Aluminium", "Aluminium Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Platinum", "Platinum Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Titanium", "Titanium Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Dirt", "Dirt Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Scoria", "Scoria Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Obsidian", "Obsidian Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Clay", "Clay Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Synthetic_Enzymes", "Synthetic Enzymes Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Lithium", "Lithium Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Ruby", "Ruby Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Uranium_Rod", "Uranium Rod Resource Pack", "Resource Packs"),
        ("Meta_Resource_Pack_Ren", "Ren Resource Pack", "Resource Packs"),

        // ===== CHAC Firearms =====
        ("Meta_CHAC_Shotgun", "CHAC Shotgun", "Firearms"),
        ("Meta_CHAC_Pistol", "CHAC Pistol", "Firearms"),
        ("Meta_CHAC_Rifle", "CHAC Rifle", "Firearms"),

        // ===== Ammo =====
        ("Meta_Pistol_Ammo", "Pistol Ammo", "Ammo"),
        ("Meta_Shotgun_Ammo", "Shotgun Ammo", "Ammo"),
        ("Meta_Rifle_Ammo", "Rifle Ammo", "Ammo"),
        ("Meta_AssaultRifle_Ammo", "Assault Rifle Ammo", "Ammo"),
        ("Meta_Sniper_Ammo", "Sniper Ammo", "Ammo"),
        ("Meta_Sniper_Explosive_Ammo", "Sniper Explosive Ammo", "Ammo"),
        ("Meta_Sniper_Incendiary_Ammo", "Sniper Incendiary Ammo", "Ammo"),

        // ===== Shield =====
        ("Meta_Shield_9Diamonds", "9 Diamonds Shield", "Equipment"),

        // ===== Pets — Dogs =====
        ("Meta_Dog_A1", "Dog A1", "Pets"),
        ("Meta_Dog_A2", "Dog A2", "Pets"),
        ("Meta_Dog_B1", "Dog B1", "Pets"),
        ("Meta_Dog_B2", "Dog B2", "Pets"),
        ("Meta_Dog_C1", "Dog C1", "Pets"),
        ("Meta_Dog_C2", "Dog C2", "Pets"),
        ("Meta_Dog_D1", "Dog D1", "Pets"),
        ("Meta_Dog_D2", "Dog D2", "Pets"),
        ("Meta_Dog_E", "Dog E", "Pets"),

        // ===== Pets — Cats =====
        ("Meta_Cat_A1", "Cat A1", "Pets"),
        ("Meta_Cat_A2", "Cat A2", "Pets"),
        ("Meta_Cat_A3", "Cat A3", "Pets"),
        ("Meta_Cat_B", "Cat B", "Pets"),
        ("Meta_Cat_C", "Cat C", "Pets"),

        // ===== Pets — Horses =====
        ("Meta_Horse_A1", "Horse A1", "Pets"),
        ("Meta_Horse_A2", "Horse A2", "Pets"),
        ("Meta_Horse_A3", "Horse A3", "Pets"),

        // ===== Farm Animals =====
        ("Meta_Chicken", "Chicken", "Farm Animals"),
        ("Meta_Sheep", "Sheep", "Farm Animals"),
        ("Meta_Calf", "Calf", "Farm Animals"),
        ("Meta_Chick", "Chick", "Farm Animals"),
        ("Meta_Lamb", "Lamb", "Farm Animals"),
        ("Meta_Lamb_Male", "Lamb (Male)", "Farm Animals"),
        ("Meta_Chick_Male", "Chick (Male)", "Farm Animals"),
        ("Meta_Calf_Male", "Calf (Male)", "Farm Animals"),
        ("Meta_Piglet_Male", "Piglet (Male)", "Farm Animals"),
        ("Meta_Piglet_Female", "Piglet (Female)", "Farm Animals"),

        // ===== Medical =====
        ("Meta_Dressing_Kit", "Dressing Kit", "Medical"),
        ("Meta_Splint", "Splint", "Medical"),
        ("Meta_AntiRadiation_Injection", "Anti-Radiation Injection", "Medical"),

        // ===== Saddles =====
        ("Meta_Saddle_QuickTrainer", "Quick Trainer Saddle", "Saddles"),
        ("Meta_Saddle_Overrider", "Overrider Saddle", "Saddles"),
        ("Meta_Saddle_Carrier", "Carrier Saddle", "Saddles"),

        // ===== Biolab Inhalers =====
        ("Meta_Biolab_Inhaler_Sandworm", "Sandworm Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_AlphaWolf", "Alpha Wolf Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_Scorpion", "Scorpion Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_IceMammoth", "Ice Mammoth Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_LavaHunter", "Lava Hunter Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_Hammerhead", "Hammerhead Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_RockGolem", "Rock Golem Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_SwampApe", "Swamp Ape Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_Scyther", "Scyther Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_Thornet", "Thornet Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_PlantBoss", "Plant Boss Inhaler", "Biolab Inhalers"),
        ("Meta_Biolab_Inhaler_GiantCat", "Giant Cat Inhaler", "Biolab Inhalers"),
    ];

    /// <summary>
    /// Fast lookup dictionary for MetaRow -> display info. Case-insensitive.
    /// </summary>
    private static readonly Dictionary<string, (string DisplayName, string Category)> _lookup;

    static WorkshopItemData()
    {
        _lookup = new Dictionary<string, (string, string)>(StringComparer.OrdinalIgnoreCase);
        foreach (var item in KnownItems)
        {
            _lookup.TryAdd(item.MetaRow, (item.DisplayName, item.Category));
        }
    }

    /// <summary>
    /// Gets all unique categories from the known items list.
    /// </summary>
    public static List<string> GetCategories()
    {
        return KnownItems.Select(i => i.Category).Distinct().ToList();
    }

    /// <summary>
    /// Gets items filtered by category.
    /// </summary>
    public static List<(string MetaRow, string DisplayName, string Category)> GetItemsByCategory(string category)
    {
        return KnownItems.Where(i => i.Category == category).ToList();
    }

    /// <summary>
    /// Tries to get a display name for a MetaRow. Returns a cleaned-up version of the MetaRow if not found.
    /// </summary>
    public static string GetDisplayName(string? metaRow)
    {
        if (metaRow == null) return "Unknown";
        if (_lookup.TryGetValue(metaRow, out var info))
            return info.DisplayName;

        // Generate a readable name from the MetaRow by removing Meta_ prefix and replacing underscores
        var cleaned = metaRow;
        if (cleaned.StartsWith("Meta_", StringComparison.OrdinalIgnoreCase))
            cleaned = cleaned[5..];
        return cleaned.Replace('_', ' ');
    }

    /// <summary>
    /// Tries to get the category for a MetaRow.
    /// </summary>
    public static string GetCategory(string? metaRow)
    {
        if (metaRow == null) return "Unknown";
        if (_lookup.TryGetValue(metaRow, out var info))
            return info.Category;
        return "Unknown";
    }
}
