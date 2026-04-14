namespace Icarus;

using Serilog;

/// <summary>
/// Reads and writes fog-of-war .fog files in the MapData directory.
/// Format: int32 entryCount + entryCount * (int32 x, int32 y, int32 state) triplets.
/// Each file represents explored tiles for a terrain zone (e.g. Terrain_016 = Olympus Forest).
/// State 4 = fully revealed.
/// </summary>
public class FogExplorer
{
    public List<FogFile> FogFiles { get; private set; } = [];
    private readonly string _mapDataPath;

    /// <summary>
    /// Known terrain zone names (best-effort mapping).
    /// </summary>
    private static readonly Dictionary<string, string> TerrainNames = new()
    {
        ["Terrain_016"] = "Olympus - Forest",
        ["Terrain_017"] = "Olympus - Arctic",
        ["Terrain_019"] = "Styx - Desert",
        ["Terrain_021"] = "Prometheus - Open World",
        ["Terrain_018"] = "Olympus - Riverlands",
        ["Terrain_020"] = "Styx - Volcanic",
        ["Terrain_022"] = "Prometheus - Glacier",
    };

    public FogExplorer(string mapDataPath)
    {
        _mapDataPath = mapDataPath;
        RefreshFog();
    }

    public void RefreshFog()
    {
        FogFiles.Clear();

        try
        {
            if (!Directory.Exists(_mapDataPath)) return;

            foreach (var filePath in Directory.EnumerateFiles(_mapDataPath, "*.fog"))
            {
                try
                {
                    var data = File.ReadAllBytes(filePath);
                    if (data.Length < 4) continue;

                    var entryCount = BitConverter.ToInt32(data, 0);
                    var entries = new List<FogEntry>();
                    var offset = 4;

                    for (var i = 0; i < entryCount && offset + 12 <= data.Length; i++)
                    {
                        entries.Add(new FogEntry
                        {
                            X = BitConverter.ToInt32(data, offset),
                            Y = BitConverter.ToInt32(data, offset + 4),
                            State = BitConverter.ToInt32(data, offset + 8)
                        });
                        offset += 12;
                    }

                    var baseName = Path.GetFileNameWithoutExtension(filePath);
                    TerrainNames.TryGetValue(baseName, out var zoneName);

                    FogFiles.Add(new FogFile
                    {
                        FileName = Path.GetFileName(filePath),
                        FilePath = filePath,
                        TerrainId = baseName,
                        ZoneName = zoneName ?? baseName,
                        Entries = entries
                    });

                    Log.Information("Loaded fog file {File}: {Count} explored tiles", Path.GetFileName(filePath), entryCount);
                }
                catch (Exception ex)
                {
                    Log.Warning(ex, "Failed to read fog file {File}", filePath);
                }
            }
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to enumerate fog files in {Path}", _mapDataPath);
        }
    }

    /// <summary>
    /// Exports a single fog file back to disk.
    /// </summary>
    public bool ExportFogFile(FogFile fogFile)
    {
        var tempPath = fogFile.FilePath + ".tmp";

        try
        {
            using var ms = new MemoryStream();
            using var writer = new BinaryWriter(ms);

            writer.Write(fogFile.Entries.Count);
            foreach (var entry in fogFile.Entries)
            {
                writer.Write(entry.X);
                writer.Write(entry.Y);
                writer.Write(entry.State);
            }

            File.WriteAllBytes(tempPath, ms.ToArray());
            File.Move(tempPath, fogFile.FilePath, overwrite: true);

            Log.Information("Exported fog file {File}: {Count} entries", fogFile.FileName, fogFile.Entries.Count);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to export fog file {File}", fogFile.FileName);
            try { if (File.Exists(tempPath)) File.Delete(tempPath); }
            catch { /* best effort cleanup */ }
            return false;
        }
    }

    /// <summary>
    /// Deletes a fog file (resets exploration for that zone).
    /// </summary>
    public bool DeleteFogFile(FogFile fogFile)
    {
        try
        {
            if (File.Exists(fogFile.FilePath))
            {
                File.Delete(fogFile.FilePath);
                FogFiles.Remove(fogFile);
                Log.Information("Deleted fog file {File}", fogFile.FileName);
                return true;
            }
            return false;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to delete fog file {File}", fogFile.FileName);
            return false;
        }
    }
}

public class FogFile
{
    public string FileName { get; set; } = "";
    public string FilePath { get; set; } = "";
    public string TerrainId { get; set; } = "";
    public string ZoneName { get; set; } = "";
    public List<FogEntry> Entries { get; set; } = [];
}

public class FogEntry
{
    public int X { get; set; }
    public int Y { get; set; }
    public int State { get; set; }
}
