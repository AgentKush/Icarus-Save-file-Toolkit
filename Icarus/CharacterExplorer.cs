namespace Icarus;

using System.Text.Json;
using System.Text.Json.Serialization;
using Serilog;

public class CharacterExplorer
{
    public List<Character> Characters { get; set; } = [];
    private readonly string _charactersFile;

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        WriteIndented = true,
        Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
    };

    public CharacterExplorer(string charactersFile)
    {
        _charactersFile = charactersFile;
        RefreshCharacters();
    }

    /// <summary>
    /// Exports characters to the save file using atomic write (temp file + rename).
    /// </summary>
    public bool ExportCharacters(List<Character> characters)
    {
        var charList = new CharacterList
        {
            CharactersStream = characters
                .Select(ch => JsonSerializer.Serialize(ch, SerializerOptions))
                .ToList()
        };

        var tempPath = _charactersFile + ".tmp";

        try
        {
            var json = JsonSerializer.Serialize(charList, SerializerOptions);

            // Atomic write: write to temp file first, then replace
            File.WriteAllText(tempPath, json);
            File.Move(tempPath, _charactersFile, overwrite: true);

            Log.Information("Exported {CharacterCount} characters to {FilePath}", characters.Count, _charactersFile);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to export characters");

            // Clean up temp file on failure
            try { if (File.Exists(tempPath)) File.Delete(tempPath); }
            catch { /* best effort cleanup */ }

            return false;
        }
    }

    /// <summary>
    /// Reloads characters from the save file. Handles corrupt/missing files gracefully.
    /// </summary>
    public void RefreshCharacters()
    {
        try
        {
            var json = File.ReadAllText(_charactersFile);
            var charList = JsonSerializer.Deserialize<CharacterList>(json);

            Characters.Clear();

            if (charList?.CharactersStream != null)
            {
                foreach (var charJson in charList.CharactersStream)
                {
                    try
                    {
                        var character = JsonSerializer.Deserialize<Character>(charJson);
                        if (character != null)
                            Characters.Add(character);
                    }
                    catch (JsonException ex)
                    {
                        Log.Warning(ex, "Skipped corrupt character entry during refresh");
                    }
                }
            }

            Log.Information("Refreshed {CharacterCount} characters", Characters.Count);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to refresh characters from {FilePath}", _charactersFile);
            Characters.Clear();
        }
    }

    /// <summary>
    /// Duplicates the character at the given index and appends it to the list.
    /// </summary>
    public void AddCharacter(List<Character> characters, int index)
    {
        if (index < 0 || index >= characters.Count)
        {
            Log.Warning("AddCharacter called with invalid index {Index} (count: {Count})", index, characters.Count);
            return;
        }

        var duplicateCharacter = characters[index].DeepClone();
        duplicateCharacter.CharacterName += "2";
        duplicateCharacter.ChrSlot = characters.Count;
        characters.Add(duplicateCharacter);
        ExportCharacters(characters);
    }

    /// <summary>
    /// Removes the character at the given index.
    /// </summary>
    public void RemoveCharacter(List<Character> characters, int index)
    {
        if (index < 0 || index >= characters.Count)
        {
            Log.Warning("RemoveCharacter called with invalid index {Index} (count: {Count})", index, characters.Count);
            return;
        }

        characters.RemoveAt(index);
        ExportCharacters(characters);
    }
}

public class CharacterList
{
    [JsonPropertyName("Characters.json")]
    public List<string> CharactersStream { get; set; } = [];
}

public class Character
{
    public string? CharacterName { get; set; }
    public int ChrSlot { get; set; }
    public int XP { get; set; }
    public int XP_Debt { get; set; }
    public bool IsDead { get; set; }
    public bool IsAbandoned { get; set; }
    public string? LastProspectId { get; set; }
    public string? Location { get; set; }
    public List<int>? UnlockedFlags { get; set; }
    public List<MetaResource>? MetaResources { get; set; }
    public CosmeticData? Cosmetic { get; set; }
    public List<TalentData>? Talents { get; set; }
    public long TimeLastPlayed { get; set; }

    /// <summary>
    /// Captures any unknown JSON properties so they survive round-trip serialization.
    /// This is critical for forward-compatibility with game updates that add new fields.
    /// </summary>
    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

public class CosmeticData
{
    public int Customization_Head { get; set; }
    public int Customization_Hair { get; set; }
    public int Customization_HairColor { get; set; }
    public int Customization_Body { get; set; }
    public int Customization_BodyColor { get; set; }
    public int Customization_SkinTone { get; set; }
    public int Customization_HeadTattoo { get; set; }
    public int Customization_HeadScar { get; set; }
    public int Customization_HeadFacialHair { get; set; }
    public int Customization_CapLogo { get; set; }
    public bool IsMale { get; set; }
    public int Customization_Voice { get; set; }
    public int Customization_EyeColor { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

public class TalentData
{
    public string? RowName { get; set; }
    public int Rank { get; set; }
}
