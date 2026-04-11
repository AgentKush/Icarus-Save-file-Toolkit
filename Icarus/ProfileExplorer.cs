namespace Icarus;

using System.Text.Json;
using System.Text.Json.Serialization;
using Serilog;

public class ProfileExplorer
{
    public Profile? PlayerProfile { get; private set; }
    private readonly string _profilePath;

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        WriteIndented = true,
        Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
    };

    public ProfileExplorer(string profilePath)
    {
        _profilePath = profilePath;
        RefreshProfile();
    }

    /// <summary>
    /// Exports profile to the save file using atomic write (temp file + rename).
    /// </summary>
    public bool ExportProfile(Profile profile)
    {
        var tempPath = _profilePath + ".tmp";

        try
        {
            var json = JsonSerializer.Serialize(profile, SerializerOptions);

            // Atomic write: write to temp file first, then replace
            File.WriteAllText(tempPath, json);
            File.Move(tempPath, _profilePath, overwrite: true);

            Log.Information("Exported profile");
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to export profile");

            try { if (File.Exists(tempPath)) File.Delete(tempPath); }
            catch { /* best effort cleanup */ }

            return false;
        }
    }

    /// <summary>
    /// Reloads profile from the save file. Handles corrupt/missing files gracefully.
    /// </summary>
    public void RefreshProfile()
    {
        try
        {
            var json = File.ReadAllText(_profilePath);
            PlayerProfile = JsonSerializer.Deserialize<Profile>(json);

            if (PlayerProfile == null)
                Log.Warning("Profile deserialization returned null from {ProfilePath}", _profilePath);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to refresh profile from {ProfilePath}", _profilePath);
            PlayerProfile = null;
        }
    }
}

public class Profile
{
    public string? UserID { get; set; }
    public List<MetaResource>? MetaResources { get; set; }
    public List<int>? UnlockedFlags { get; set; }
    public List<Talent>? Talents { get; set; }
    public int NextChrSlot { get; set; }
    public int DataVersion { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

public class MetaResource
{
    public string? MetaRow { get; set; }
    public int Count { get; set; }
}

public class Talent
{
    public string? RowName { get; set; }
    public int Rank { get; set; }
}
