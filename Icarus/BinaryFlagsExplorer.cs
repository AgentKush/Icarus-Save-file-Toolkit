namespace Icarus;

using Serilog;

/// <summary>
/// Reads and writes the binary flags_{SteamID}.dat file.
/// Format: int32 strLen + null-terminated SteamID string + int32 flagCount + flagCount * int32 flagIDs.
/// These are separate from the JSON-based UnlockedFlags in Profile/Characters.
/// </summary>
public class BinaryFlagsExplorer
{
    public BinaryFlagsData? FlagsData { get; private set; }
    private readonly string _flagsPath;

    public BinaryFlagsExplorer(string flagsPath)
    {
        _flagsPath = flagsPath;
        RefreshFlags();
    }

    public bool ExportFlags(BinaryFlagsData flagsData)
    {
        var tempPath = _flagsPath + ".tmp";

        try
        {
            using var ms = new MemoryStream();
            using var writer = new BinaryWriter(ms);

            // Write SteamID as null-terminated string with length prefix
            var steamBytes = System.Text.Encoding.ASCII.GetBytes(flagsData.SteamID + '\0');
            writer.Write(steamBytes.Length); // int32 length including null
            writer.Write(steamBytes);

            // Write flags
            var flags = flagsData.FlagIDs ?? [];
            writer.Write(flags.Count); // int32 count
            foreach (var flag in flags)
                writer.Write(flag); // int32 each

            File.WriteAllBytes(tempPath, ms.ToArray());
            File.Move(tempPath, _flagsPath, overwrite: true);

            Log.Information("Exported binary flags to {FilePath} ({Count} flags)", _flagsPath, flags.Count);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to export binary flags");
            try { if (File.Exists(tempPath)) File.Delete(tempPath); }
            catch { /* best effort cleanup */ }
            return false;
        }
    }

    public void RefreshFlags()
    {
        try
        {
            if (!File.Exists(_flagsPath))
            {
                FlagsData = null;
                return;
            }

            var data = File.ReadAllBytes(_flagsPath);
            if (data.Length < 8)
            {
                FlagsData = null;
                return;
            }

            var offset = 0;

            // Read string length
            var strLen = BitConverter.ToInt32(data, offset);
            offset += 4;

            if (offset + strLen > data.Length)
            {
                Log.Warning("Binary flags file truncated at SteamID");
                FlagsData = null;
                return;
            }

            // Read SteamID (null-terminated)
            var steamId = System.Text.Encoding.ASCII.GetString(data, offset, strLen).TrimEnd('\0');
            offset += strLen;

            // Read flag count
            if (offset + 4 > data.Length)
            {
                FlagsData = new BinaryFlagsData { SteamID = steamId, FlagIDs = [] };
                return;
            }

            var flagCount = BitConverter.ToInt32(data, offset);
            offset += 4;

            var flags = new List<int>();
            for (var i = 0; i < flagCount && offset + 4 <= data.Length; i++)
            {
                flags.Add(BitConverter.ToInt32(data, offset));
                offset += 4;
            }

            FlagsData = new BinaryFlagsData
            {
                SteamID = steamId,
                FlagIDs = flags
            };

            Log.Information("Loaded binary flags: SteamID={SteamID}, {Count} flags", steamId, flags.Count);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to read binary flags from {Path}", _flagsPath);
            FlagsData = null;
        }
    }
}

public class BinaryFlagsData
{
    public string SteamID { get; set; } = "";
    public List<int> FlagIDs { get; set; } = [];
}
