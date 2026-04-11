namespace Icarus;

using System.Text.Json;
using System.Text.Json.Serialization;
using Serilog;

public class LoadoutsExplorer
{
    public LoadoutsData? Loadouts { get; private set; }
    private readonly string _loadoutsPath;

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        WriteIndented = true,
        Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
    };

    public LoadoutsExplorer(string loadoutsPath)
    {
        _loadoutsPath = loadoutsPath;
        RefreshLoadouts();
    }

    public bool ExportLoadouts(LoadoutsData loadouts)
    {
        var tempPath = _loadoutsPath + ".tmp";

        try
        {
            var json = JsonSerializer.Serialize(loadouts, SerializerOptions);
            File.WriteAllText(tempPath, json);
            File.Move(tempPath, _loadoutsPath, overwrite: true);

            Log.Information("Exported loadouts to {FilePath}", _loadoutsPath);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to export loadouts");
            try { if (File.Exists(tempPath)) File.Delete(tempPath); }
            catch { /* best effort cleanup */ }
            return false;
        }
    }

    public void RefreshLoadouts()
    {
        try
        {
            if (!File.Exists(_loadoutsPath))
            {
                Loadouts = null;
                return;
            }

            var json = File.ReadAllText(_loadoutsPath);
            Loadouts = JsonSerializer.Deserialize<LoadoutsData>(json);

            if (Loadouts == null)
                Log.Warning("Loadouts deserialization returned null from {Path}", _loadoutsPath);
            else
                Log.Information("Refreshed loadouts with {Count} entries", Loadouts.Loadouts?.Count ?? 0);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to refresh loadouts from {Path}", _loadoutsPath);
            Loadouts = null;
        }
    }
}

/// <summary>
/// Represents the Loadouts.json file — saved equipment loadout presets.
/// The file structure uses ExtensionData to preserve all unknown fields.
/// </summary>
public class LoadoutsData
{
    public List<LoadoutEntry>? Loadouts { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

/// <summary>
/// A single loadout preset with a name and list of item slots.
/// </summary>
public class LoadoutEntry
{
    public string? LoadoutName { get; set; }
    public List<LoadoutSlot>? Slots { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

/// <summary>
/// A single slot in a loadout (an item reference).
/// </summary>
public class LoadoutSlot
{
    public string? MetaRow { get; set; }
    public int SlotIndex { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}
