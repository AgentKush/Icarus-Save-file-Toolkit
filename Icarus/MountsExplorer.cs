namespace Icarus;

using System.Text.Json;
using System.Text.Json.Serialization;
using Serilog;

public class MountsExplorer
{
    public MountsData? MountsData { get; private set; }
    private readonly string _mountsPath;

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        WriteIndented = true,
        Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
    };

    public MountsExplorer(string mountsPath)
    {
        _mountsPath = mountsPath;
        RefreshMounts();
    }

    public bool ExportMounts(MountsData mountsData)
    {
        var tempPath = _mountsPath + ".tmp";

        try
        {
            var json = JsonSerializer.Serialize(mountsData, SerializerOptions);
            File.WriteAllText(tempPath, json);
            File.Move(tempPath, _mountsPath, overwrite: true);

            Log.Information("Exported mounts to {FilePath}", _mountsPath);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to export mounts");
            try { if (File.Exists(tempPath)) File.Delete(tempPath); }
            catch { /* best effort cleanup */ }
            return false;
        }
    }

    public void RefreshMounts()
    {
        try
        {
            if (!File.Exists(_mountsPath))
            {
                MountsData = null;
                return;
            }

            var json = File.ReadAllText(_mountsPath);
            MountsData = JsonSerializer.Deserialize<MountsData>(json);

            if (MountsData == null)
                Log.Warning("Mounts deserialization returned null from {Path}", _mountsPath);
            else
                Log.Information("Refreshed mounts with {Count} entries", MountsData.SavedMounts?.Count ?? 0);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to refresh mounts from {Path}", _mountsPath);
            MountsData = null;
        }
    }
}

/// <summary>
/// Top-level Mounts.json structure.
/// </summary>
public class MountsData
{
    public List<MountEntry>? SavedMounts { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

/// <summary>
/// A single pet/mount entry. JSON-level fields are directly editable;
/// the RecorderBlob contains UE4 binary data (genetics, talents, stats, etc.)
/// which is preserved as-is during round-trip serialization.
/// </summary>
public class MountEntry
{
    public string? DatabaseGUID { get; set; }
    public string? MountName { get; set; }
    public int MountLevel { get; set; }
    public string? MountType { get; set; }
    public int MountIconName { get; set; }
    public RecorderBlob? RecorderBlob { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

/// <summary>
/// Contains the UE4 binary property data for a mount.
/// BinaryData is a raw byte array containing serialized UE4 properties
/// (genetics, lineage, talents, position, stats, inventory, etc.)
/// </summary>
public class RecorderBlob
{
    public string? ComponentClassName { get; set; }
    public List<int>? BinaryData { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

/// <summary>
/// Known creature types with display names and categories.
/// </summary>
public static class CreatureData
{
    public enum CreatureCategory
    {
        Mount,
        CombatPet,
        FarmAnimal
    }

    /// <summary>
    /// All known tameable creature types. Includes BOTH naming conventions used by the game:
    /// PascalCase (talent_data canonical) and underscore variants (Mounts.json MountType field).
    /// </summary>
    public static readonly Dictionary<string, (string DisplayName, CreatureCategory Category)> CreatureTypes = new(StringComparer.OrdinalIgnoreCase)
    {
        // ===== Mounts =====
        { "ArcticMoa", ("Arctic Moa", CreatureCategory.Mount) },
        { "Arctic_Moa", ("Arctic Moa", CreatureCategory.Mount) },
        { "Blueback", ("Blueback", CreatureCategory.Mount) },
        { "Buffalo", ("Buffalo", CreatureCategory.Mount) },
        { "Bull", ("Bull", CreatureCategory.Mount) },
        { "Chew", ("Chew", CreatureCategory.Mount) },
        { "Horse", ("Horse", CreatureCategory.Mount) },
        { "Horse_Standard", ("Standard Horse", CreatureCategory.Mount) },
        { "HorseStandard", ("Standard Horse", CreatureCategory.Mount) },
        { "Moa", ("Moa", CreatureCategory.Mount) },
        { "Raptor", ("Raptor", CreatureCategory.Mount) },
        { "RaptorDesert", ("Desert Raptor", CreatureCategory.Mount) },
        { "Raptor_Desert", ("Desert Raptor", CreatureCategory.Mount) },
        { "Storca", ("Storca", CreatureCategory.Mount) },
        { "SwampBird", ("Swamp Bird", CreatureCategory.Mount) },
        { "Swamp_Bird", ("Swamp Bird", CreatureCategory.Mount) },
        { "SwampQuad", ("Swamp Quad / Stryder", CreatureCategory.Mount) },
        { "Swamp_Quad", ("Swamp Quad / Stryder", CreatureCategory.Mount) },
        { "Tusker", ("Tusker", CreatureCategory.Mount) },
        { "WoollyMammoth", ("Woolly Mammoth", CreatureCategory.Mount) },
        { "Woolly_Mammoth", ("Woolly Mammoth", CreatureCategory.Mount) },
        { "WoolyZebra", ("Woolly Zebra", CreatureCategory.Mount) },
        { "Wooly_Zebra", ("Woolly Zebra", CreatureCategory.Mount) },
        { "Zebra", ("Zebra", CreatureCategory.Mount) },
        { "Orka", ("Orka", CreatureCategory.Mount) },
        { "Slinker", ("Slinker", CreatureCategory.Mount) },

        // ===== Combat Pets =====
        { "Boar", ("Boar", CreatureCategory.CombatPet) },
        { "Wild_Boar", ("Boar", CreatureCategory.CombatPet) },
        { "Cat", ("Cat", CreatureCategory.CombatPet) },
        { "DesertWolf", ("Desert Wolf", CreatureCategory.CombatPet) },
        { "Desert_Wolf", ("Desert Wolf", CreatureCategory.CombatPet) },
        { "Dog", ("Dog", CreatureCategory.CombatPet) },
        { "SnowWolf", ("Snow Wolf", CreatureCategory.CombatPet) },
        { "Snow_Wolf", ("Snow Wolf", CreatureCategory.CombatPet) },
        { "TundraMonkey", ("Tundra Monkey", CreatureCategory.CombatPet) },
        { "Tundra_Monkey", ("Tundra Monkey", CreatureCategory.CombatPet) },
        { "Wolf", ("Wolf", CreatureCategory.CombatPet) },
        { "Forest_Wolf", ("Wolf", CreatureCategory.CombatPet) },

        // ===== Farm Animals =====
        { "Chicken", ("Chicken", CreatureCategory.FarmAnimal) },
        { "Cow", ("Cow", CreatureCategory.FarmAnimal) },
        { "Pig", ("Pig", CreatureCategory.FarmAnimal) },
        { "Rooster", ("Rooster", CreatureCategory.FarmAnimal) },
        { "Sheep", ("Sheep", CreatureCategory.FarmAnimal) }
    };

    /// <summary>
    /// Known lineages with rarity. Lineage affects starting bonuses/penalties and per-level growth.
    /// </summary>
    public static readonly Dictionary<string, string> Lineages = new()
    {
        { "Wild", "Common" },
        { "Brave", "Uncommon" },
        { "Careful", "Uncommon" },
        { "Timid", "Uncommon" },
        { "Bold", "Uncommon" },
        { "Hardy", "Uncommon" },
        { "Stout", "Uncommon" },
        { "Ambitious", "Uncommon" },
        { "Resolute", "Rare" },
        { "Fierce", "Rare" },
        { "Savage", "Rare" },
        { "Alpha", "Very Rare" }
    };

    /// <summary>
    /// Gets a friendly display name for a mount type string, or returns the raw type if unknown.
    /// </summary>
    public static string GetDisplayName(string? mountType)
    {
        if (mountType == null) return "Unknown";
        return CreatureTypes.TryGetValue(mountType, out var info) ? info.DisplayName : mountType;
    }

    /// <summary>
    /// Gets the category label for a mount type.
    /// </summary>
    public static string GetCategoryLabel(string? mountType)
    {
        if (mountType == null) return "Unknown";
        if (!CreatureTypes.TryGetValue(mountType, out var info)) return "Unknown";
        return info.Category switch
        {
            CreatureCategory.Mount => "Mount",
            CreatureCategory.CombatPet => "Combat Pet",
            CreatureCategory.FarmAnimal => "Farm Animal",
            _ => "Unknown"
        };
    }
}
