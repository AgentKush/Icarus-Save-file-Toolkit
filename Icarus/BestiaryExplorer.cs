namespace Icarus;

using System.Text.Json;
using System.Text.Json.Serialization;
using Serilog;

public class BestiaryExplorer
{
    public BestiaryData? Bestiary { get; private set; }
    private readonly string _bestiaryPath;

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        WriteIndented = true,
        Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
    };

    public BestiaryExplorer(string bestiaryPath)
    {
        _bestiaryPath = bestiaryPath;
        RefreshBestiary();
    }

    public bool ExportBestiary(BestiaryData bestiary)
    {
        var tempPath = _bestiaryPath + ".tmp";

        try
        {
            var json = JsonSerializer.Serialize(bestiary, SerializerOptions);
            File.WriteAllText(tempPath, json);
            File.Move(tempPath, _bestiaryPath, overwrite: true);

            Log.Information("Exported bestiary data to {FilePath}", _bestiaryPath);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to export bestiary data");
            try { if (File.Exists(tempPath)) File.Delete(tempPath); }
            catch { /* best effort cleanup */ }
            return false;
        }
    }

    public void RefreshBestiary()
    {
        try
        {
            if (!File.Exists(_bestiaryPath))
            {
                Bestiary = null;
                return;
            }

            var json = File.ReadAllText(_bestiaryPath);
            Bestiary = JsonSerializer.Deserialize<BestiaryData>(json);

            if (Bestiary == null)
                Log.Warning("Bestiary deserialization returned null from {Path}", _bestiaryPath);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to refresh bestiary from {Path}", _bestiaryPath);
            Bestiary = null;
        }
    }
}

public class BestiaryData
{
    public List<BestiaryEntry>? Entries { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

public class BestiaryEntry
{
    public string? RowName { get; set; }
    public int NumPoints { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}
