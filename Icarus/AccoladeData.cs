namespace Icarus;

/// <summary>
/// Static lookup for accolade display names, descriptions, and categories.
/// Converts internal RowNames like "StoneMined500" into human-readable text.
/// </summary>
public static class AccoladeData
{
    public enum AccoladeCategory
    {
        Mining,
        Building,
        Combat,
        Exploration,
        Crafting,
        Survival,
        Creatures,
        Progression,
        BossKills,
        Gathering,
        Miscellaneous
    }

    public record AccoladeInfo(string DisplayName, string Description, AccoladeCategory Category);

    private static readonly Dictionary<string, AccoladeInfo> KnownAccolades = new(StringComparer.OrdinalIgnoreCase)
    {
        // === Mining ===
        ["StoneMined500"] = new("Stone Miner I", "Mine 500 stone", AccoladeCategory.Mining),
        ["StoneMined1000"] = new("Stone Miner II", "Mine 1,000 stone", AccoladeCategory.Mining),
        ["StoneMined10000"] = new("Stone Miner III", "Mine 10,000 stone", AccoladeCategory.Mining),
        ["StoneMined50000"] = new("Stone Miner IV", "Mine 50,000 stone", AccoladeCategory.Mining),
        ["StoneMined100000"] = new("Stone Miner V", "Mine 100,000 stone", AccoladeCategory.Mining),
        ["IronMined200"] = new("Iron Miner I", "Mine 200 iron ore", AccoladeCategory.Mining),
        ["IronMined500"] = new("Iron Miner II", "Mine 500 iron ore", AccoladeCategory.Mining),
        ["IronMined1000"] = new("Iron Miner III", "Mine 1,000 iron ore", AccoladeCategory.Mining),
        ["IronMined5000"] = new("Iron Miner IV", "Mine 5,000 iron ore", AccoladeCategory.Mining),
        ["CopperMined200"] = new("Copper Miner I", "Mine 200 copper ore", AccoladeCategory.Mining),
        ["CopperMined500"] = new("Copper Miner II", "Mine 500 copper ore", AccoladeCategory.Mining),
        ["CopperMined1000"] = new("Copper Miner III", "Mine 1,000 copper ore", AccoladeCategory.Mining),
        ["CoalMined200"] = new("Coal Miner I", "Mine 200 coal", AccoladeCategory.Mining),
        ["CoalMined500"] = new("Coal Miner II", "Mine 500 coal", AccoladeCategory.Mining),
        ["CoalMined1000"] = new("Coal Miner III", "Mine 1,000 coal", AccoladeCategory.Mining),
        ["CoalMined5000"] = new("Coal Miner IV", "Mine 5,000 coal", AccoladeCategory.Mining),
        ["SulfurMined200"] = new("Sulfur Miner I", "Mine 200 sulfur", AccoladeCategory.Mining),
        ["SulfurMined500"] = new("Sulfur Miner II", "Mine 500 sulfur", AccoladeCategory.Mining),
        ["SulfurMined1000"] = new("Sulfur Miner III", "Mine 1,000 sulfur", AccoladeCategory.Mining),
        ["SulfurMined5000"] = new("Sulfur Miner IV", "Mine 5,000 sulfur", AccoladeCategory.Mining),
        ["SulfurMined10000"] = new("Sulfur Miner V", "Mine 10,000 sulfur", AccoladeCategory.Mining),
        ["OxiteMined200"] = new("Oxite Miner I", "Mine 200 oxite", AccoladeCategory.Mining),
        ["OxiteMined500"] = new("Oxite Miner II", "Mine 500 oxite", AccoladeCategory.Mining),
        ["OxiteMined1000"] = new("Oxite Miner III", "Mine 1,000 oxite", AccoladeCategory.Mining),
        ["OxiteMined5000"] = new("Oxite Miner IV", "Mine 5,000 oxite", AccoladeCategory.Mining),
        ["OxiteMined10000"] = new("Oxite Miner V", "Mine 10,000 oxite", AccoladeCategory.Mining),
        ["AluminumMined200"] = new("Aluminum Miner I", "Mine 200 aluminum", AccoladeCategory.Mining),
        ["AluminumMined500"] = new("Aluminum Miner II", "Mine 500 aluminum", AccoladeCategory.Mining),
        ["SilicaMined200"] = new("Silica Miner I", "Mine 200 silica", AccoladeCategory.Mining),
        ["SilicaMined500"] = new("Silica Miner II", "Mine 500 silica", AccoladeCategory.Mining),
        ["SilicaMined1000"] = new("Silica Miner III", "Mine 1,000 silica", AccoladeCategory.Mining),
        ["PlatinumMined200"] = new("Platinum Miner I", "Mine 200 platinum", AccoladeCategory.Mining),
        ["PlatinumMined500"] = new("Platinum Miner II", "Mine 500 platinum", AccoladeCategory.Mining),
        ["TitaniumMined200"] = new("Titanium Miner I", "Mine 200 titanium", AccoladeCategory.Mining),
        ["TitaniumMined500"] = new("Titanium Miner II", "Mine 500 titanium", AccoladeCategory.Mining),
        ["MineAllOres"] = new("Ore Connoisseur", "Mine every type of ore", AccoladeCategory.Mining),
        ["VoxelsHit500"] = new("Rock Breaker I", "Destroy 500 terrain voxels", AccoladeCategory.Mining),
        ["VoxelsHit1000"] = new("Rock Breaker II", "Destroy 1,000 terrain voxels", AccoladeCategory.Mining),
        ["VoxelsHit2500"] = new("Rock Breaker III", "Destroy 2,500 terrain voxels", AccoladeCategory.Mining),
        ["VoxelsComplete100"] = new("Voxel Veteran I", "Fully deplete 100 voxels", AccoladeCategory.Mining),
        ["VoxelsComplete250"] = new("Voxel Veteran II", "Fully deplete 250 voxels", AccoladeCategory.Mining),
        ["VoxelsComplete500"] = new("Voxel Veteran III", "Fully deplete 500 voxels", AccoladeCategory.Mining),

        // === Gathering ===
        ["WoodCollected250"] = new("Lumberjack I", "Collect 250 wood", AccoladeCategory.Gathering),
        ["WoodCollected500"] = new("Lumberjack II", "Collect 500 wood", AccoladeCategory.Gathering),
        ["WoodCollected1000"] = new("Lumberjack III", "Collect 1,000 wood", AccoladeCategory.Gathering),
        ["WoodCollected5000"] = new("Lumberjack IV", "Collect 5,000 wood", AccoladeCategory.Gathering),
        ["WoodCollected10000"] = new("Lumberjack V", "Collect 10,000 wood", AccoladeCategory.Gathering),
        ["LeatherCollected100"] = new("Tanner I", "Collect 100 leather", AccoladeCategory.Gathering),
        ["LeatherCollected500"] = new("Tanner II", "Collect 500 leather", AccoladeCategory.Gathering),
        ["LeatherCollected1000"] = new("Tanner III", "Collect 1,000 leather", AccoladeCategory.Gathering),
        ["FurCollected100"] = new("Fur Trader I", "Collect 100 fur", AccoladeCategory.Gathering),
        ["FurCollected500"] = new("Fur Trader II", "Collect 500 fur", AccoladeCategory.Gathering),
        ["FurCollected1000"] = new("Fur Trader III", "Collect 1,000 fur", AccoladeCategory.Gathering),
        ["BoneCollected100"] = new("Bone Collector I", "Collect 100 bone", AccoladeCategory.Gathering),
        ["BoneCollected500"] = new("Bone Collector II", "Collect 500 bone", AccoladeCategory.Gathering),
        ["BoneCollected1000"] = new("Bone Collector III", "Collect 1,000 bone", AccoladeCategory.Gathering),
        ["MeatCollected100"] = new("Butcher I", "Collect 100 meat", AccoladeCategory.Gathering),
        ["MeatCollected500"] = new("Butcher II", "Collect 500 meat", AccoladeCategory.Gathering),
        ["MeatCollected1000"] = new("Butcher III", "Collect 1,000 meat", AccoladeCategory.Gathering),
        ["PrimeMeatCollected100"] = new("Gourmet Hunter I", "Collect 100 prime meat", AccoladeCategory.Gathering),
        ["PrimeMeatCollected500"] = new("Gourmet Hunter II", "Collect 500 prime meat", AccoladeCategory.Gathering),
        ["PrimeMeatCollected1000"] = new("Gourmet Hunter III", "Collect 1,000 prime meat", AccoladeCategory.Gathering),
        ["PickupBasicResource"] = new("First Steps", "Pick up your first resource", AccoladeCategory.Gathering),
        ["CreaturesSkinned20"] = new("Skinner I", "Skin 20 creatures", AccoladeCategory.Gathering),
        ["CreaturesSkinned100"] = new("Skinner II", "Skin 100 creatures", AccoladeCategory.Gathering),

        // === Building ===
        ["ThatchBuildingsCrafted20"] = new("Thatch Builder", "Craft 20 thatch building pieces", AccoladeCategory.Building),
        ["WoodBuildingsCrafted20"] = new("Wood Builder I", "Craft 20 wood building pieces", AccoladeCategory.Building),
        ["WoodBuildingsCrafted50"] = new("Wood Builder II", "Craft 50 wood building pieces", AccoladeCategory.Building),
        ["WoodBuildingsCrafted100"] = new("Wood Builder III", "Craft 100 wood building pieces", AccoladeCategory.Building),
        ["WoodBuildingsCrafted500"] = new("Wood Builder IV", "Craft 500 wood building pieces", AccoladeCategory.Building),
        ["WoodBuildingsCrafted1000"] = new("Wood Builder V", "Craft 1,000 wood building pieces", AccoladeCategory.Building),
        ["StoneBuildingsCrafted20"] = new("Stone Builder I", "Craft 20 stone building pieces", AccoladeCategory.Building),
        ["StoneBuildingsCrafted50"] = new("Stone Builder II", "Craft 50 stone building pieces", AccoladeCategory.Building),
        ["IronBuildingsCrafted20"] = new("Iron Builder I", "Craft 20 iron building pieces", AccoladeCategory.Building),
        ["IronBuildingsCrafted50"] = new("Iron Builder II", "Craft 50 iron building pieces", AccoladeCategory.Building),
        ["IronBuildingsCrafted100"] = new("Iron Builder III", "Craft 100 iron building pieces", AccoladeCategory.Building),
        ["IronBuildingsCrafted500"] = new("Iron Builder IV", "Craft 500 iron building pieces", AccoladeCategory.Building),
        ["ConcreteBuildingsCrafted20"] = new("Concrete Builder I", "Craft 20 concrete building pieces", AccoladeCategory.Building),
        ["ConcreteBuildingsCrafted50"] = new("Concrete Builder II", "Craft 50 concrete building pieces", AccoladeCategory.Building),
        ["ConcreteBuildingsCrafted100"] = new("Concrete Builder III", "Craft 100 concrete building pieces", AccoladeCategory.Building),
        ["ConcreteBuildingsCrafted500"] = new("Concrete Builder IV", "Craft 500 concrete building pieces", AccoladeCategory.Building),
        ["ConcreteBuildingsCrafted1000"] = new("Concrete Builder V", "Craft 1,000 concrete building pieces", AccoladeCategory.Building),
        ["GlassBuildingsCrafted20"] = new("Glass Builder I", "Craft 20 glass building pieces", AccoladeCategory.Building),
        ["GlassBuildingsCrafted50"] = new("Glass Builder II", "Craft 50 glass building pieces", AccoladeCategory.Building),
        ["GlassBuildingsCrafted100"] = new("Glass Builder III", "Craft 100 glass building pieces", AccoladeCategory.Building),

        // === Combat ===
        ["CriticalHitKills50"] = new("Sharpshooter I", "Get 50 critical hit kills", AccoladeCategory.Combat),
        ["CriticalHitKills250"] = new("Sharpshooter II", "Get 250 critical hit kills", AccoladeCategory.Combat),
        ["CriticalHitKills500"] = new("Sharpshooter III", "Get 500 critical hit kills", AccoladeCategory.Combat),
        ["BowKills50"] = new("Archer", "Get 50 bow kills", AccoladeCategory.Combat),
        ["SpearKills50"] = new("Spearman", "Get 50 spear kills", AccoladeCategory.Combat),
        ["KnifeKills50"] = new("Knife Fighter", "Get 50 knife kills", AccoladeCategory.Combat),
        ["AxeKills50"] = new("Axe Warrior", "Get 50 axe kills", AccoladeCategory.Combat),
        ["PickaxeKills50"] = new("Pickaxe Brawler", "Get 50 pickaxe kills", AccoladeCategory.Combat),
        ["FirearmKills50"] = new("Gunslinger I", "Get 50 firearm kills", AccoladeCategory.Combat),
        ["FirearmKills250"] = new("Gunslinger II", "Get 250 firearm kills", AccoladeCategory.Combat),
        ["BulletsFired500"] = new("Trigger Happy", "Fire 500 bullets", AccoladeCategory.Combat),
        ["USeSledgehammer"] = new("Sledgehammer Time", "Use a sledgehammer", AccoladeCategory.Combat),

        // === Creatures ===
        ["WolvesKilled10"] = new("Wolf Hunter I", "Kill 10 wolves", AccoladeCategory.Creatures),
        ["WolvesKilled100"] = new("Wolf Hunter II", "Kill 100 wolves", AccoladeCategory.Creatures),
        ["BearsKilled20"] = new("Bear Slayer", "Kill 20 bears", AccoladeCategory.Creatures),
        ["BoarsKilled20"] = new("Boar Slayer", "Kill 20 boars", AccoladeCategory.Creatures),
        ["DeerKilled10"] = new("Deer Hunter", "Kill 10 deer", AccoladeCategory.Creatures),
        ["RabbitsKilled20"] = new("Rabbit Hunter", "Kill 20 rabbits", AccoladeCategory.Creatures),
        ["LionsKilled20"] = new("Lion Tamer", "Kill 20 lions", AccoladeCategory.Creatures),
        ["CaveWormsKilled10"] = new("Worm Slayer I", "Kill 10 cave worms", AccoladeCategory.Creatures),
        ["CaveWormsKilled100"] = new("Worm Slayer II", "Kill 100 cave worms", AccoladeCategory.Creatures),
        ["KillMutant"] = new("Mutant Killer", "Kill a mutant creature", AccoladeCategory.Creatures),
        ["Pet25"] = new("Animal Friend", "Pet creatures 25 times", AccoladeCategory.Creatures),
        ["Mount50"] = new("Saddle Up", "Mount creatures 50 times", AccoladeCategory.Creatures),
        ["TameHostile"] = new("Whisperer", "Tame a hostile creature", AccoladeCategory.Creatures),
        ["PetDies"] = new("Farewell Friend", "Lose a pet", AccoladeCategory.Creatures),
        ["PetHome"] = new("Welcome Home", "Bring a pet home", AccoladeCategory.Creatures),
        ["OrderChicken"] = new("Chicken Wrangler", "Order a chicken", AccoladeCategory.Creatures),
        ["OrderHorse"] = new("Horse Owner", "Order a horse", AccoladeCategory.Creatures),
        ["LandEly"] = new("Sky Rider", "Land an Ely", AccoladeCategory.Creatures),

        // === Boss Kills ===
        ["DefeatGarganutan"] = new("Garganutan Slayer", "Defeat the Garganutan", AccoladeCategory.BossKills),
        ["DefeatGarganutanHard"] = new("Garganutan Master", "Defeat the Garganutan on hard", AccoladeCategory.BossKills),
        ["DefeatHammerhead"] = new("Hammerhead Slayer", "Defeat the Hammerhead", AccoladeCategory.BossKills),
        ["DefeatHammerheadHard"] = new("Hammerhead Master", "Defeat the Hammerhead on hard", AccoladeCategory.BossKills),
        ["DefeatLavaHunter"] = new("Lava Hunter Slayer", "Defeat the Lava Hunter", AccoladeCategory.BossKills),
        ["DefeatLavaHunterHard"] = new("Lava Hunter Master", "Defeat the Lava Hunter on hard", AccoladeCategory.BossKills),
        ["DefeatQuarrite"] = new("Quarrite Slayer", "Defeat the Quarrite", AccoladeCategory.BossKills),
        ["WolfBossKilled"] = new("Alpha Wolf Slayer", "Kill the Alpha Wolf boss", AccoladeCategory.BossKills),
        ["MammothBossKilled"] = new("Mammoth Slayer", "Kill the Mammoth boss", AccoladeCategory.BossKills),
        ["SandwormBossKilled"] = new("Sandworm Slayer", "Kill the Sandworm boss", AccoladeCategory.BossKills),
        ["JaguarBossKilled"] = new("Jaguar Boss Slayer", "Kill the Jaguar boss", AccoladeCategory.BossKills),
        ["KillAlphaWolfBossOnHardest"] = new("Alpha Wolf Nightmare", "Kill Alpha Wolf on hardest difficulty", AccoladeCategory.BossKills),
        ["KillSandwormBossOnHardest"] = new("Sandworm Nightmare", "Kill Sandworm on hardest difficulty", AccoladeCategory.BossKills),
        ["KillScorpionBossOnHardest"] = new("Scorpion Nightmare", "Kill Scorpion on hardest difficulty", AccoladeCategory.BossKills),
        ["CompleteGarganutanTree"] = new("Garganutan Mastery", "Complete the Garganutan talent tree", AccoladeCategory.BossKills),
        ["CompleteQuarriteTree"] = new("Quarrite Mastery", "Complete the Quarrite talent tree", AccoladeCategory.BossKills),

        // === Exploration ===
        ["DistanceTraveled10"] = new("Explorer I", "Travel 10 km", AccoladeCategory.Exploration),
        ["DistanceTraveled25"] = new("Explorer II", "Travel 25 km", AccoladeCategory.Exploration),
        ["DistanceTraveled50"] = new("Explorer III", "Travel 50 km", AccoladeCategory.Exploration),
        ["DistanceTraveled100"] = new("Explorer IV", "Travel 100 km", AccoladeCategory.Exploration),
        ["DistanceTraveled500"] = new("Explorer V", "Travel 500 km", AccoladeCategory.Exploration),
        ["DistanceTraveledForest10"] = new("Forest Walker I", "Travel 10 km in forest", AccoladeCategory.Exploration),
        ["DistanceTraveledForest25"] = new("Forest Walker II", "Travel 25 km in forest", AccoladeCategory.Exploration),
        ["DistanceTraveledForest50"] = new("Forest Walker III", "Travel 50 km in forest", AccoladeCategory.Exploration),
        ["DistanceTraveledForest100"] = new("Forest Walker IV", "Travel 100 km in forest", AccoladeCategory.Exploration),
        ["DistanceTraveledArctic10"] = new("Arctic Explorer I", "Travel 10 km in arctic", AccoladeCategory.Exploration),
        ["DistanceTraveledArctic25"] = new("Arctic Explorer II", "Travel 25 km in arctic", AccoladeCategory.Exploration),
        ["DistanceTraveledArctic50"] = new("Arctic Explorer III", "Travel 50 km in arctic", AccoladeCategory.Exploration),
        ["DistanceTraveledDesert10"] = new("Desert Wanderer I", "Travel 10 km in desert", AccoladeCategory.Exploration),
        ["DistanceTraveledDesert25"] = new("Desert Wanderer II", "Travel 25 km in desert", AccoladeCategory.Exploration),
        ["DistanceTraveledDesert50"] = new("Desert Wanderer III", "Travel 50 km in desert", AccoladeCategory.Exploration),
        ["DistanceTraveledDesert100"] = new("Desert Wanderer IV", "Travel 100 km in desert", AccoladeCategory.Exploration),
        ["DistanceTraveledCaves1"] = new("Spelunker I", "Travel 1 km in caves", AccoladeCategory.Exploration),
        ["DistanceTraveledCaves2"] = new("Spelunker II", "Travel 2 km in caves", AccoladeCategory.Exploration),
        ["ForestScanComplete"] = new("Forest Surveyed", "Complete forest biome scan", AccoladeCategory.Exploration),
        ["GlacierScanComplete"] = new("Glacier Surveyed", "Complete glacier biome scan", AccoladeCategory.Exploration),
        ["RiverlandsScanComplete"] = new("Riverlands Surveyed", "Complete riverlands biome scan", AccoladeCategory.Exploration),
        ["EnterNullSec"] = new("Null Sector", "Enter the Null Sector", AccoladeCategory.Exploration),
        ["MiddleIceSheet"] = new("Heart of Ice", "Reach the middle of the ice sheet", AccoladeCategory.Exploration),
        ["ViewMeteor"] = new("Stargazer", "Witness a meteor event", AccoladeCategory.Exploration),

        // === Survival ===
        ["TimeSurvived5"] = new("Survivor I", "Survive for 5 hours", AccoladeCategory.Survival),
        ["TimeSurvived10"] = new("Survivor II", "Survive for 10 hours", AccoladeCategory.Survival),
        ["TimeSurvived15"] = new("Survivor III", "Survive for 15 hours", AccoladeCategory.Survival),
        ["TimeSurvived20"] = new("Survivor IV", "Survive for 20 hours", AccoladeCategory.Survival),
        ["TimeSurvived50"] = new("Survivor V", "Survive for 50 hours", AccoladeCategory.Survival),
        ["TimeSurvivedForest5"] = new("Forest Survivor I", "Survive 5 hours in forest", AccoladeCategory.Survival),
        ["TimeSurvivedForest10"] = new("Forest Survivor II", "Survive 10 hours in forest", AccoladeCategory.Survival),
        ["TimeSurvivedForest15"] = new("Forest Survivor III", "Survive 15 hours in forest", AccoladeCategory.Survival),
        ["TimeSurvivedForest20"] = new("Forest Survivor IV", "Survive 20 hours in forest", AccoladeCategory.Survival),
        ["TimeSurvivedForest50"] = new("Forest Survivor V", "Survive 50 hours in forest", AccoladeCategory.Survival),
        ["TimeSurvivedArctic5"] = new("Arctic Survivor", "Survive 5 hours in arctic", AccoladeCategory.Survival),
        ["TimeSurvivedCaves5"] = new("Cave Survivor", "Survive 5 hours in caves", AccoladeCategory.Survival),
        ["TimeSurvivedDesert5"] = new("Desert Survivor I", "Survive 5 hours in desert", AccoladeCategory.Survival),
        ["TimeSurvivedDesert10"] = new("Desert Survivor II", "Survive 10 hours in desert", AccoladeCategory.Survival),
        ["TimeSurvivedDesert15"] = new("Desert Survivor III", "Survive 15 hours in desert", AccoladeCategory.Survival),
        ["TimeSurvivedDesert20"] = new("Desert Survivor IV", "Survive 20 hours in desert", AccoladeCategory.Survival),
        ["FoodConsumed100"] = new("Gourmand", "Consume 100 food items", AccoladeCategory.Survival),
        ["DownedCount1"] = new("Down But Not Out", "Get downed at least once", AccoladeCategory.Survival),
        ["ReviveCount1"] = new("Second Chance", "Get revived at least once", AccoladeCategory.Survival),
        ["Lose80percHealth"] = new("Near Death", "Lose 80% of your health", AccoladeCategory.Survival),
        ["StruckByLightning1"] = new("Lightning Rod", "Get struck by lightning", AccoladeCategory.Survival),
        ["LavaSwim"] = new("Lava Dip", "Enter lava", AccoladeCategory.Survival),
        ["IceBreakerEncounter"] = new("Ice Breaker", "Encounter the ice breaker event", AccoladeCategory.Survival),
        ["EquipFullArmour"] = new("Fully Armoured", "Equip a full set of armour", AccoladeCategory.Survival),
        ["SuitUp"] = new("Suit Up", "Equip a full environmental suit", AccoladeCategory.Survival),
        ["EatCake"] = new("Let Them Eat Cake", "Eat a cake", AccoladeCategory.Survival),
        ["Electroshock"] = new("Electroshock", "Get electrocuted", AccoladeCategory.Survival),

        // === Progression ===
        ["TutorialCompleted"] = new("Tutorial Complete", "Complete the tutorial", AccoladeCategory.Progression),
        ["FirstDropPromStory"] = new("First Drop", "Complete your first story drop", AccoladeCategory.Progression),
        ["ReachMaxLevel"] = new("Max Level", "Reach the maximum character level", AccoladeCategory.Progression),
        ["ReachBottomOfTalentTree"] = new("Talent Tree Master", "Reach the bottom of a talent tree", AccoladeCategory.Progression),
        ["AllBlueprintsUnlockedTier1"] = new("Tier 1 Complete", "Unlock all Tier 1 blueprints", AccoladeCategory.Progression),
        ["AllBlueprintsUnlockedTier2"] = new("Tier 2 Complete", "Unlock all Tier 2 blueprints", AccoladeCategory.Progression),
        ["AllBlueprintsUnlockedTier3"] = new("Tier 3 Complete", "Unlock all Tier 3 blueprints", AccoladeCategory.Progression),
        ["AllBlueprintsUnlockedTier4"] = new("Tier 4 Complete", "Unlock all Tier 4 blueprints", AccoladeCategory.Progression),
        ["UnlockBPT5"] = new("Tier 5 Unlocked", "Unlock Tier 5 blueprints", AccoladeCategory.Progression),
        ["UnlockManu"] = new("Manufacturing Unlocked", "Unlock manufacturing", AccoladeCategory.Progression),
        ["CreditsEarned10000"] = new("Cash Flow", "Earn 10,000 credits", AccoladeCategory.Progression),
        ["ExoticsEarned10000"] = new("Exotic Wealth", "Earn 10,000 exotics", AccoladeCategory.Progression),
        ["100Packs"] = new("Pack Rat", "Open 100 packs", AccoladeCategory.Progression),
        ["ItemsAltered1"] = new("First Alteration", "Alter an item for the first time", AccoladeCategory.Progression),

        // === Crafting & Tech ===
        ["CrudePower"] = new("Crude Power", "Generate power from crude fuel", AccoladeCategory.Crafting),
        ["CraftLegWeapon"] = new("Legendary Craftsman", "Craft a legendary weapon", AccoladeCategory.Crafting),
        ["UpgradeLegWeaponFully"] = new("Legendary Perfection", "Fully upgrade a legendary weapon", AccoladeCategory.Crafting),
        ["UseMiningLaser"] = new("Laser Miner", "Use a mining laser", AccoladeCategory.Crafting),
        ["UseReactor"] = new("Nuclear Age", "Use a reactor", AccoladeCategory.Crafting),
        ["ThumperActivations1"] = new("Ground Pounder", "Activate a thumper", AccoladeCategory.Crafting),
    };

    /// <summary>
    /// Look up the display info for an accolade RowName.
    /// Falls back to auto-generated name from the RowName if unknown.
    /// </summary>
    public static AccoladeInfo GetInfo(string? rowName)
    {
        if (string.IsNullOrEmpty(rowName))
            return new AccoladeInfo("Unknown", "", AccoladeCategory.Miscellaneous);

        if (KnownAccolades.TryGetValue(rowName, out var info))
            return info;

        // Auto-generate a readable name from the RowName
        var displayName = GenerateDisplayName(rowName);
        var category = GuessCategory(rowName);
        return new AccoladeInfo(displayName, "", category);
    }

    /// <summary>
    /// Convert "StoneMined500" → "Stone Mined 500", "DefeatGarganutanHard" → "Defeat Garganutan Hard"
    /// </summary>
    private static string GenerateDisplayName(string rowName)
    {
        var result = new System.Text.StringBuilder();
        for (int i = 0; i < rowName.Length; i++)
        {
            var c = rowName[i];
            if (i > 0 && char.IsUpper(c) && !char.IsUpper(rowName[i - 1]))
                result.Append(' ');
            else if (i > 0 && char.IsDigit(c) && !char.IsDigit(rowName[i - 1]))
                result.Append(' ');
            result.Append(c);
        }
        return result.ToString();
    }

    private static AccoladeCategory GuessCategory(string rowName)
    {
        var lower = rowName.ToLowerInvariant();
        if (lower.Contains("mined") || lower.Contains("voxel")) return AccoladeCategory.Mining;
        if (lower.Contains("building") || lower.Contains("crafted")) return AccoladeCategory.Building;
        if (lower.Contains("kill") || lower.Contains("fired") || lower.Contains("hit")) return AccoladeCategory.Combat;
        if (lower.Contains("distance") || lower.Contains("travel") || lower.Contains("scan")) return AccoladeCategory.Exploration;
        if (lower.Contains("survived") || lower.Contains("food") || lower.Contains("health")) return AccoladeCategory.Survival;
        if (lower.Contains("collected") || lower.Contains("skinned") || lower.Contains("wood")) return AccoladeCategory.Gathering;
        if (lower.Contains("defeat") || lower.Contains("boss")) return AccoladeCategory.BossKills;
        if (lower.Contains("wolf") || lower.Contains("bear") || lower.Contains("deer") || lower.Contains("pet") || lower.Contains("mount")) return AccoladeCategory.Creatures;
        if (lower.Contains("unlock") || lower.Contains("level") || lower.Contains("tier") || lower.Contains("blueprint")) return AccoladeCategory.Progression;
        return AccoladeCategory.Miscellaneous;
    }

    /// <summary>Total number of known accolades in the database.</summary>
    public static int KnownCount => KnownAccolades.Count;
}
