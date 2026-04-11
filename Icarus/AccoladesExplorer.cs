namespace Icarus;

using System.Text.Json;
using System.Text.Json.Serialization;
using Serilog;

public class AccoladesExplorer
{
    public AccoladesData? Accolades { get; private set; }
    private readonly string _accoladesPath;

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        WriteIndented = true,
        Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
    };

    public AccoladesExplorer(string accoladesPath)
    {
        _accoladesPath = accoladesPath;
        RefreshAccolades();
    }

    public bool ExportAccolades(AccoladesData accolades)
    {
        var tempPath = _accoladesPath + ".tmp";

        try
        {
            var json = JsonSerializer.Serialize(accolades, SerializerOptions);
            File.WriteAllText(tempPath, json);
            File.Move(tempPath, _accoladesPath, overwrite: true);

            Log.Information("Exported accolades to {FilePath}", _accoladesPath);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to export accolades");
            try { if (File.Exists(tempPath)) File.Delete(tempPath); }
            catch { /* best effort cleanup */ }
            return false;
        }
    }

    public void RefreshAccolades()
    {
        try
        {
            if (!File.Exists(_accoladesPath))
            {
                Accolades = null;
                return;
            }

            var json = File.ReadAllText(_accoladesPath);
            Accolades = JsonSerializer.Deserialize<AccoladesData>(json);

            if (Accolades == null)
                Log.Warning("Accolades deserialization returned null from {Path}", _accoladesPath);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to refresh accolades from {Path}", _accoladesPath);
            Accolades = null;
        }
    }
}

public class AccoladesData
{
    public List<AccoladeEntry>? Accolades { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

public class AccoladeEntry
{
    public string? RowName { get; set; }
    public int NumPoints { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}
