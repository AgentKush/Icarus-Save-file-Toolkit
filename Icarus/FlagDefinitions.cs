namespace Icarus;

/// <summary>
/// Known flag definitions extracted from Icarus game data tables.
/// Character flags are per-character (D_CharacterFlags), Account flags are per-profile (D_AccountFlags).
/// The integer IDs in save files map to the index in these tables.
/// </summary>
public static class FlagDefinitions
{
    /// <summary>
    /// D_CharacterFlags — 45 entries. Index = flag ID used in Character.UnlockedFlags.
    /// </summary>
    public static readonly Dictionary<int, string> CharacterFlags = new()
    {
        { 0, "TestDataFlag" },
        { 1, "TutorialTestFlag" },
        { 2, "FirstScanComplete" },
        { 3, "Talent_RepairBench" },
        { 4, "Talent_WaterBomb" },
        { 5, "Talent_Ghillie_Armor" },
        { 6, "Talent_Trophy_Bench" },
        { 7, "Talent_Solo_Blueprints1" },
        { 8, "Talent_Solo_Blueprints2" },
        { 9, "Talent_SkinningBench" },
        { 10, "Talent_Wood_Sticks" },
        { 11, "Talent_Polarbear_Armor" },
        { 12, "Talent_Leather_Rope" },
        { 13, "Talent_CropPlot" },
        { 14, "Talent_Rifle_Bulk_Ammo" },
        { 15, "Talent_Shotgun_Bulk_Ammo" },
        { 16, "Talent_Pistol_Bulk_Ammo" },
        { 17, "Voxel_Meta_Resources_Visible [Deprecated]" },
        { 18, "Deposit_Meta_Resources_Visible [Deprecated]" },
        { 19, "Unlocked_Bait [Deprecated]" },
        { 20, "Talent_GunpowderRecipe" },
        { 21, "Talent_ShotgunRecipe" },
        { 22, "Mission_Cave_Worm_Analyser [Deprecated]" },
        { 23, "Mission_Handheld_Scanners [Deprecated]" },
        { 24, "Mission_Scorpion_Item_Analyzer [Deprecated]" },
        { 25, "Mission_Sandworm_Items [Deprecated]" },
        { 26, "Mission_Scorpion_Armor_Items [Deprecated]" },
        { 27, "Mission_Olympus_Unlock" },
        { 28, "Mission_BlackWolf_Items [Deprecated]" },
        { 29, "Mission_Targets [Deprecated]" },
        { 30, "Communicator_T2" },
        { 31, "Communicator_T3" },
        { 32, "Communicator_T4" },
        { 33, "Mission_AlienFossil [Deprecated]" },
        { 34, "StyxBlocker_B_TooltipOnly" },
        { 35, "StyxBlocker_C_TooltipOnly" },
        { 36, "StyxBlocker_D_TooltipOnly" },
        { 37, "StyxBlocker_E_TooltipOnly" },
        { 38, "RefundOnly_Repairable" },
        { 39, "GreatHunt_IntroPlayed" },
        { 40, "NPC_Farmer_TooltipOnly" },
        { 41, "NPC_Norex_TooltipOnly" },
        { 42, "NPC_Hunter_TooltipOnly" },
        { 43, "NPC_Fisher_TooltipOnly" },
        { 44, "Sandwyrm_Queen_TooltipOnly" }
    };

    /// <summary>
    /// D_AccountFlags — 100 entries. Index = flag ID used in Profile.UnlockedFlags.
    /// </summary>
    public static readonly Dictionary<int, string> AccountFlags = new()
    {
        { 0, "Mission_Communicator_T2_Upgrade" },
        { 1, "Mission_Communicator_T3_Upgrade" },
        { 2, "Mission_Communicator_T4_Upgrade" },
        { 3, "Styx_Level_Boost_Claimed" },
        { 4, "Prometheus_Level_Boost_Claimed" },
        { 5, "Has_Seen_NewGame_Prompt" },
        { 6, "GrantedTalent_Nullsector_Story" },
        { 7, "GrantedBlueprint_Medical_Device" },
        { 8, "GrantedTalent_Olympus_Nightfall" },
        { 9, "GrantedTalent_Styx_Ironclad" },
        { 10, "GrantedBlueprint_Bait" },
        { 11, "GrantedBlueprint_CavewormMelee" },
        { 12, "GrantedBlueprint_CavewormRange" },
        { 13, "GrantedBlueprint_ScorpionTrap" },
        { 14, "GrantedBlueprint_SandwormMelee" },
        { 15, "GrantedBlueprint_SandwormRange" },
        { 16, "GrantedBlueprint_SandwormArmor" },
        { 17, "GrantedBlueprint_ScorpionArmor" },
        { 18, "GrantedBlueprint_BlackWolfKnifeArrow" },
        { 19, "GrantedBlueprint_AlienDecorations" },
        { 20, "GrantedBlueprint_TargetDummy" },
        { 21, "GrantedBlueprint_DrillArrows" },
        { 22, "GrantedBlueprint_EDSRounds" },
        { 23, "GrantedBlueprint_ResearchEquipment" },
        { 24, "GrantedBlueprint_Recovery_Beacon_Device" },
        { 25, "GrantedBlueprint_EnzymeElixir" },
        { 26, "Has_Seen_GreatHunts_Prompt" },
        { 27, "GrantedWorkshop_BananaPack" },
        { 28, "GrantedTalent_GH_RG" },
        { 29, "GrantedTalent_GH_IM" },
        { 30, "GrantedTalent_GH_APE" },
        { 31, "GrantedBlueprint_SandArmor" },
        { 32, "GrantedBlueprint_SandArmor_Backpack" },
        { 33, "GrantedBlueprint_ArcticArmor" },
        { 34, "GrantedBlueprint_MinerArmor" },
        { 35, "GrantedBlueprint_MiniThumper" },
        { 36, "GrantedBlueprint_Ape_FishingTrap" },
        { 37, "GrantedBlueprint_Ape_Grenade" },
        { 38, "GrantedBlueprint_Ape_Tonic" },
        { 39, "GrantedBlueprint_Ape_Attractor" },
        { 40, "GrantedBlueprint_Ape_Module" },
        { 41, "GrantedBlueprint_Ape_Attachment" },
        { 42, "GrantedBlueprint_Ape_Armor" },
        { 43, "GrantedBlueprint_Ape_Trophy" },
        { 44, "GrantedBlueprint_IM_Module" },
        { 45, "GrantedBlueprint_IM_Attachment" },
        { 46, "GrantedBlueprint_IM_Trap" },
        { 47, "GrantedBlueprint_IM_Spear" },
        { 48, "GrantedBlueprint_IM_Shield" },
        { 49, "GrantedBlueprint_IM_Armor" },
        { 50, "GrantedBlueprint_IM_Trophies" },
        { 51, "GrantedBlueprint_RG_Grenade" },
        { 52, "GrantedBlueprint_RG_Attachment" },
        { 53, "GrantedBlueprint_RG_Module" },
        { 54, "GrantedBlueprint_RG_Gun" },
        { 55, "GrantedBlueprint_RG_Sledgehammer" },
        { 56, "GrantedBlueprint_RG_Trophies" },
        { 57, "GrantedBlueprint_LH_Trophies" },
        { 58, "GrantedBlueprint_LH_Trap" },
        { 59, "GrantedBlueprint_LH_Backpack" },
        { 60, "GrantedBlueprint_LH_Sickle" },
        { 61, "GrantedBlueprint_LH_Module" },
        { 62, "GrantedBlueprint_LH_Attachment" },
        { 63, "GrantedBlueprint_SL_Axe" },
        { 64, "GrantedBlueprint_SL_Module" },
        { 65, "GrantedBlueprint_SL_Attachment" },
        { 66, "GrantedBlueprint_SL_Grenade" },
        { 67, "GrantedBlueprint_SL_Trophies" },
        { 68, "GrantedBlueprint_SL_Epoxy" },
        { 69, "GrantedBlueprint_SC_Module" },
        { 70, "GrantedBlueprint_SC_Attachment" },
        { 71, "GrantedBlueprint_SC_Rod" },
        { 72, "GrantedBlueprint_SC_Crossbow" },
        { 73, "GrantedBlueprint_SC_Trophies" },
        { 74, "GrantedBlueprint_BW_Attachment" },
        { 75, "GrantedBlueprint_BW_Shield" },
        { 76, "GrantedBlueprint_BW_Armor" },
        { 77, "GrantedBlueprint_BW_Trap" },
        { 78, "GrantedBlueprint_BW_Module" },
        { 79, "GrantedBlueprint_BW_Trophies" },
        { 80, "GrantedBlueprint_SW_Trophies" },
        { 81, "GrantedBlueprint_SW_Building" },
        { 82, "GrantedBlueprint_SW_Building2" },
        { 83, "GrantedBlueprint_SW_Module" },
        { 84, "GrantedBlueprint_SW_Attachment" },
        { 85, "GrantedBlueprint_CavewormArmor" },
        { 86, "Homestead_Passive_Talent_Refund" },
        { 87, "GrantedBlueprint_YetiArticArmor" },
        { 88, "GrantedTalent_ELY_SQ" },
        { 89, "GrantedTalent_ELY_Story_6" },
        { 90, "GrantedBlueprint_Hasmat" },
        { 91, "GrantedBlueprint_Sandwyrm" },
        { 92, "GrantedBlueprint_Sandwyrm_Trophies" },
        { 93, "GrantedWorkshop_ELY_Seeds" },
        { 94, "GrantedWorkshop_LandingPads" },
        { 95, "Elysium_Level_Boost_Claimed" },
        { 96, "GrantedBlueprint_Speeder" },
        { 97, "GrantedBlueprint_ScoutSuit" },
        { 98, "GrantedBlueprint_ScoutSmg" },
        { 99, "GrantedBlueprint_UraniumAmmo" }
    };

    /// <summary>
    /// Gets the display name for a character flag ID. Returns "Unknown (ID)" for unrecognized flags.
    /// </summary>
    public static string GetCharacterFlagName(int id)
    {
        return CharacterFlags.TryGetValue(id, out var name) ? name : $"Unknown ({id})";
    }

    /// <summary>
    /// Gets the display name for an account flag ID. Returns "Unknown (ID)" for unrecognized flags.
    /// </summary>
    public static string GetAccountFlagName(int id)
    {
        return AccountFlags.TryGetValue(id, out var name) ? name : $"Unknown ({id})";
    }
}
