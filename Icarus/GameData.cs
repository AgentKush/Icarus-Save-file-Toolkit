namespace Icarus;

using Serilog;

public class GameData
{
    private readonly string _gameDataPath;
    private readonly string _charactersPath;
    private readonly string _profilePath;
    private readonly string _metaInventoryPath;
    private readonly string _accoladesPath;
    private readonly string _bestiaryPath;
    private readonly string _loadoutsPath;
    private readonly string _mountsPath;
    private readonly string _prospectsPath;
    private readonly string _mapDataPath;
    private readonly string _binaryFlagsPath;
    private readonly string _backupPath;

    internal const string CharactersFileName = "Characters.json";
    internal const string ProfileFileName = "Profile.json";
    internal const string MetaInventoryFileName = "MetaInventory.json";
    internal const string AccoladesFileName = "Accolades.json";
    internal const string BestiaryFileName = "BestiaryData.json";
    internal const string LoadoutsFileName = "Loadouts.json";
    internal const string MountsFileName = "Mounts.json";
    internal const string ProspectsFilePattern = "AssociatedProspects_Slot_*.json";
    internal const string BackupFolder = "backups";

    public bool ValidGamePath { get; private set; }

    internal string GameDataPath => _gameDataPath;
    internal string CharactersPath => _charactersPath;
    internal string ProfilePath => _profilePath;
    internal string MetaInventoryPath => _metaInventoryPath;
    internal string AccoladesPath => _accoladesPath;
    internal string BestiaryPath => _bestiaryPath;
    internal string LoadoutsPath => _loadoutsPath;
    internal string MountsPath => _mountsPath;
    internal string ProspectsPath => _prospectsPath;
    internal string BackupPath => _backupPath;

    public bool HasMetaInventory => File.Exists(_metaInventoryPath);
    public bool HasAccolades => File.Exists(_accoladesPath);
    public bool HasBestiary => File.Exists(_bestiaryPath);
    public bool HasLoadouts => File.Exists(_loadoutsPath);
    public bool HasMounts => File.Exists(_mountsPath);
    public bool HasProspects => File.Exists(_prospectsPath);
    public bool HasMapData => Directory.Exists(_mapDataPath) && Directory.EnumerateFiles(_mapDataPath, "*.fog").Any();
    public bool HasBinaryFlags => File.Exists(_binaryFlagsPath);

    public GameData(string gameDataPath)
    {
        _gameDataPath = gameDataPath;
        _charactersPath = Path.Combine(gameDataPath, CharactersFileName);
        _profilePath = Path.Combine(gameDataPath, ProfileFileName);
        _metaInventoryPath = Path.Combine(gameDataPath, MetaInventoryFileName);
        _accoladesPath = Path.Combine(gameDataPath, AccoladesFileName);
        _bestiaryPath = Path.Combine(gameDataPath, BestiaryFileName);
        _loadoutsPath = Path.Combine(gameDataPath, LoadoutsFileName);
        _mountsPath = Path.Combine(gameDataPath, MountsFileName);
        _prospectsPath = FindProspectsFile(gameDataPath);
        _mapDataPath = Path.Combine(gameDataPath, "MapData");
        _binaryFlagsPath = FindBinaryFlagsFile(gameDataPath);
        _backupPath = Path.Combine(Directory.GetCurrentDirectory(), BackupFolder);

        if (!ValidateGamePath(gameDataPath))
        {
            ValidGamePath = false;
            Log.Warning("{GameDataPath} was not a valid game data path", gameDataPath);
            return;
        }

        ValidGamePath = true;
        Log.Information("Game data path set to {GameDataPath}", _gameDataPath);
        Log.Information("Character file set to {CharactersPath}", _charactersPath);
        Log.Information("Profile file set to {ProfilePath}", _profilePath);
        Log.Information("MetaInventory file set to {MetaInventoryPath} (exists: {Exists})", _metaInventoryPath, HasMetaInventory);
        Log.Information("Accolades file set to {AccoladesPath} (exists: {Exists})", _accoladesPath, HasAccolades);
        Log.Information("Bestiary file set to {BestiaryPath} (exists: {Exists})", _bestiaryPath, HasBestiary);
        Log.Information("Loadouts file set to {LoadoutsPath} (exists: {Exists})", _loadoutsPath, HasLoadouts);
        Log.Information("Mounts file set to {MountsPath} (exists: {Exists})", _mountsPath, HasMounts);
        Log.Information("Prospects file set to {ProspectsPath} (exists: {Exists})", _prospectsPath, HasProspects);
        Log.Information("MapData path set to {MapDataPath} (exists: {Exists})", _mapDataPath, HasMapData);
        Log.Information("Binary flags file set to {FlagsPath} (exists: {Exists})", _binaryFlagsPath, HasBinaryFlags);
        Log.Information("Backup folder set to {BackupPath}", _backupPath);
    }

    public CharacterExplorer GetCharacters() => new(_charactersPath);

    public ProfileExplorer GetProfile() => new(_profilePath);

    public MetaInventoryExplorer GetMetaInventory() => new(_metaInventoryPath);

    public AccoladesExplorer GetAccolades() => new(_accoladesPath);

    public BestiaryExplorer GetBestiary() => new(_bestiaryPath);

    public LoadoutsExplorer GetLoadouts() => new(_loadoutsPath);

    public MountsExplorer GetMounts() => new(_mountsPath);

    public ProspectsExplorer GetProspects() => new(_prospectsPath);

    public FogExplorer GetFog() => new(_mapDataPath);

    public BinaryFlagsExplorer GetBinaryFlags() => new(_binaryFlagsPath);

    private static string FindBinaryFlagsFile(string gameDataPath)
    {
        try
        {
            var match = Directory.EnumerateFiles(gameDataPath, "flags_*.dat").FirstOrDefault();
            return match ?? Path.Combine(gameDataPath, "flags.dat");
        }
        catch
        {
            return Path.Combine(gameDataPath, "flags.dat");
        }
    }

    private static string FindProspectsFile(string gameDataPath)
    {
        try
        {
            // Prefer Slot_0 explicitly, then fall back to first match
            var slot0 = Path.Combine(gameDataPath, "AssociatedProspects_Slot_0.json");
            if (File.Exists(slot0)) return slot0;

            var match = Directory.EnumerateFiles(gameDataPath, ProspectsFilePattern).FirstOrDefault();
            return match ?? slot0;
        }
        catch
        {
            return Path.Combine(gameDataPath, "AssociatedProspects_Slot_0.json");
        }
    }

    public static bool ValidateGamePath(string gamePath)
    {
        if (string.IsNullOrEmpty(gamePath))
            return false;

        if (!Directory.Exists(gamePath))
            return false;

        var files = Directory.EnumerateFiles(gamePath, "*.json")
            .Select(Path.GetFileName)
            .ToHashSet();

        return files.Contains(CharactersFileName) && files.Contains(ProfileFileName);
    }

    /// <summary>
    /// Auto-detects the Icarus player save data folder.
    /// Searches %LocalAppData%\Icarus\Saved\PlayerData\{SteamID}\ for valid save data.
    /// Returns the first valid folder found, or null if none found.
    /// </summary>
    public static string? AutoDetectSavePath()
    {
        try
        {
            var localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            var playerDataRoot = Path.Combine(localAppData, "Icarus", "Saved", "PlayerData");

            if (!Directory.Exists(playerDataRoot))
            {
                Log.Information("Icarus PlayerData root not found at {Path}", playerDataRoot);
                return null;
            }

            // Each subfolder is a Steam ID — find one with valid save files
            foreach (var steamIdFolder in Directory.GetDirectories(playerDataRoot))
            {
                if (ValidateGamePath(steamIdFolder))
                {
                    Log.Information("Auto-detected save path: {Path}", steamIdFolder);
                    return steamIdFolder;
                }
            }

            Log.Information("No valid save data found under {Path}", playerDataRoot);
            return null;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to auto-detect save path");
            return null;
        }
    }

    /// <summary>
    /// Checks if a path appears to be inside the game installation rather than the player save folder.
    /// This is a common mistake — editing Content\Data won't affect actual saves.
    /// </summary>
    public static bool IsGameInstallPath(string path)
    {
        var normalized = path.Replace('\\', '/').ToLowerInvariant();
        return normalized.Contains("/steamapps/common/icarus") ||
               normalized.Contains("/content/data") ||
               normalized.Contains("/icarus/icarus/content");
    }

    /// <summary>
    /// Creates a timestamped backup of all game data files.
    /// </summary>
    public bool BackupData()
    {
        var timestamp = DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss");
        var currentBackupPath = Path.Combine(_backupPath, timestamp);

        try
        {
            if (Directory.Exists(currentBackupPath))
                Directory.Delete(currentBackupPath, recursive: true);

            Directory.CreateDirectory(currentBackupPath);

            foreach (var file in Directory.GetFiles(_gameDataPath, "*.json"))
            {
                File.Copy(file, Path.Combine(currentBackupPath, Path.GetFileName(file)));
            }

            Log.Information("Backup created at {BackupPath}", currentBackupPath);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to create backup");
            return false;
        }
    }

    /// <summary>
    /// Returns a list of available backup directories.
    /// </summary>
    public List<string> GetBackups()
    {
        try
        {
            if (!Directory.Exists(_backupPath))
                return [];

            return Directory.GetDirectories(_backupPath)
                .OrderByDescending(d => d)
                .ToList();
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to retrieve backups");
            return [];
        }
    }

    /// <summary>
    /// Restores game data files from a backup directory.
    /// </summary>
    public bool RestoreBackup(string backupPath)
    {
        if (!Directory.Exists(backupPath))
        {
            Log.Warning("Backup path does not exist: {BackupPath}", backupPath);
            return false;
        }

        try
        {
            var jsonFiles = Directory.GetFiles(backupPath, "*.json");

            if (jsonFiles.Length == 0)
            {
                Log.Warning("No JSON files found in backup: {BackupPath}", backupPath);
                return false;
            }

            foreach (var file in jsonFiles)
            {
                var fileName = Path.GetFileName(file);
                var destinationPath = Path.Combine(_gameDataPath, fileName);

                File.Copy(file, destinationPath, overwrite: true);
            }

            Log.Information("Restored backup from {BackupPath}", backupPath);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to restore backup");
            return false;
        }
    }
}
