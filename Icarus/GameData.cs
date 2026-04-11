namespace Icarus;

using Serilog;

public class GameData
{
    private readonly string _gameDataPath;
    private readonly string _charactersPath;
    private readonly string _profilePath;
    private readonly string _metaInventoryPath;
    private readonly string _backupPath;

    internal const string CharactersFileName = "Characters.json";
    internal const string ProfileFileName = "Profile.json";
    internal const string MetaInventoryFileName = "MetaInventory.json";
    internal const string BackupFolder = "backups";

    public bool ValidGamePath { get; private set; }

    internal string GameDataPath => _gameDataPath;
    internal string CharactersPath => _charactersPath;
    internal string ProfilePath => _profilePath;
    internal string MetaInventoryPath => _metaInventoryPath;
    internal string BackupPath => _backupPath;

    /// <summary>
    /// Whether a MetaInventory.json file exists in the game data path.
    /// </summary>
    public bool HasMetaInventory => File.Exists(_metaInventoryPath);

    public GameData(string gameDataPath)
    {
        _gameDataPath = gameDataPath;
        _charactersPath = Path.Combine(gameDataPath, CharactersFileName);
        _profilePath = Path.Combine(gameDataPath, ProfileFileName);
        _metaInventoryPath = Path.Combine(gameDataPath, MetaInventoryFileName);
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
        Log.Information("Backup folder set to {BackupPath}", _backupPath);
    }

    public CharacterExplorer GetCharacters() => new(_charactersPath);

    public ProfileExplorer GetProfile() => new(_profilePath);

    public MetaInventoryExplorer GetMetaInventory() => new(_metaInventoryPath);

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
