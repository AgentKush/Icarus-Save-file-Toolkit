namespace Icarus;

using System.Text.Json;
using System.Text.Json.Serialization;
using Serilog;

public class ProspectsExplorer
{
    public ProspectData? Prospect { get; private set; }
    private readonly string _prospectsPath;

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        WriteIndented = true,
        Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
    };

    public ProspectsExplorer(string prospectsPath)
    {
        _prospectsPath = prospectsPath;
        RefreshProspects();
    }

    public bool ExportProspects(ProspectData prospect)
    {
        var tempPath = _prospectsPath + ".tmp";

        try
        {
            // Re-wrap: the file stores JSON as { "AssociatedProspects_Slot_0.json": [ "<json string>" ] }
            var innerJson = JsonSerializer.Serialize(prospect, SerializerOptions);
            var fileName = Path.GetFileName(_prospectsPath);
            var wrapper = new Dictionary<string, List<string>>
            {
                [fileName] = [innerJson]
            };
            var json = JsonSerializer.Serialize(wrapper, SerializerOptions);

            File.WriteAllText(tempPath, json);
            File.Move(tempPath, _prospectsPath, overwrite: true);

            Log.Information("Exported prospects to {FilePath}", _prospectsPath);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to export prospects");
            try { if (File.Exists(tempPath)) File.Delete(tempPath); }
            catch { /* best effort cleanup */ }
            return false;
        }
    }

    public void RefreshProspects()
    {
        try
        {
            if (!File.Exists(_prospectsPath))
            {
                Prospect = null;
                return;
            }

            var json = File.ReadAllText(_prospectsPath);
            var wrapper = JsonSerializer.Deserialize<Dictionary<string, List<string>>>(json);

            if (wrapper == null || wrapper.Count == 0)
            {
                Prospect = null;
                return;
            }

            // Get the first (and only) key's value list
            var prospectJsonList = wrapper.Values.First();
            if (prospectJsonList.Count == 0)
            {
                Prospect = null;
                return;
            }

            Prospect = JsonSerializer.Deserialize<ProspectData>(prospectJsonList[0]);

            if (Prospect == null)
                Log.Warning("Prospect deserialization returned null from {Path}", _prospectsPath);
            else
                Log.Information("Loaded prospect: {ProspectID} ({State}, {MemberCount} members)",
                    Prospect.AssociatedProspect?.ProspectID ?? "unknown",
                    Prospect.AssociatedProspect?.ProspectState ?? "unknown",
                    Prospect.AssociatedProspect?.AssociatedMembers?.Count ?? 0);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to refresh prospects from {Path}", _prospectsPath);
            Prospect = null;
        }
    }
}

public class ProspectData
{
    public AssociatedProspect? AssociatedProspect { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

public class AssociatedProspect
{
    public string? ProspectID { get; set; }
    public string? ClaimedAccountID { get; set; }
    public int ClaimedAccountCharacter { get; set; }
    public string? ProspectDTKey { get; set; }
    public string? FactionMissionDTKey { get; set; }
    public string? LobbyName { get; set; }
    public int ExpireTime { get; set; }
    public string? ProspectState { get; set; }
    public List<ProspectMember>? AssociatedMembers { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

public class ProspectMember
{
    public string? AccountName { get; set; }
    public string? CharacterName { get; set; }
    public int ChrSlot { get; set; }
    public string? Status { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}
