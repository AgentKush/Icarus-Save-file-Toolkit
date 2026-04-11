using Serilog;
using System.Text.Json;

namespace Icarus_Toolkit.Utils;

public static class SettingsManager
{
    private static readonly string SettingsDir = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "IcarusToolkit");

    private static readonly string SettingsPath = Path.Combine(SettingsDir, "settings.json");
    private static readonly string LogPath = Path.Combine(SettingsDir, "logs", "icarus_toolkit.log");

    private static Dictionary<string, object> _settings = new();
    private static bool _isLogInitialized = false;

    static SettingsManager()
    {
        LoadSettings();
    }

    public static void InitLog()
    {
        if (_isLogInitialized)
            return;

        try
        {
            var logDir = Path.GetDirectoryName(LogPath)!;
            if (!Directory.Exists(logDir))
                Directory.CreateDirectory(logDir);

            Log.Logger = new LoggerConfiguration()
                .MinimumLevel.Debug()
                .WriteTo.File(LogPath, rollingInterval: RollingInterval.Day, retainedFileCountLimit: 10, shared: true)
                .CreateLogger();

            _isLogInitialized = true;
            Log.Information("");
            Log.Information("LOG INIT");
            Log.Information("");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Failed to initialize logging: {ex.Message}");
        }
    }

    public static string? GetSetting(string key)
    {
        if (_settings.TryGetValue(key, out var value))
        {
            return value.ToString();
        }
        return null;
    }

    public static void SetSetting(string key, string value)
    {
        _settings[key] = value;
        SaveSettings();
    }

    private static void LoadSettings()
    {
        try
        {
            if (File.Exists(SettingsPath))
            {
                var json = File.ReadAllText(SettingsPath);
                var loaded = JsonSerializer.Deserialize<Dictionary<string, object>>(json);
                if (loaded != null)
                {
                    _settings = loaded;
                }
            }
        }
        catch (Exception ex)
        {
            Log.Warning($"Failed to load settings: {ex.Message}");
        }
    }

    private static void SaveSettings()
    {
        try
        {
            if (!Directory.Exists(SettingsDir))
                Directory.CreateDirectory(SettingsDir);

            var json = JsonSerializer.Serialize(_settings, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(SettingsPath, json);
        }
        catch (Exception ex)
        {
            Log.Error($"Failed to save settings: {ex.Message}");
        }
    }
}
