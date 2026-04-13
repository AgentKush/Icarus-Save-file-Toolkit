using Avalonia;
using Avalonia.Media.Imaging;
using Avalonia.Platform.Storage;
using Serilog;

namespace Icarus_Toolkit.Utils;

/// <summary>
/// Resolves item RowNames/MetaRows to icon Bitmaps by fetching from GitHub.
/// Loads an embedded manifest of available icons and downloads them on demand
/// from the raw.githubusercontent.com CDN with in-memory session caching.
/// </summary>
public class IconResolver : IDisposable
{
    private const string GitHubRawBase =
        "https://raw.githubusercontent.com/AgentKush/Icarus-Save-file-Toolkit/main/icarus_icons/";

    private const string ManifestResourceName = "icon_manifest.txt";

    /// <summary>Maps normalised lookup keys → relative icon paths (from manifest).</summary>
    private readonly Dictionary<string, string> _index = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>Maps relative icon path → downloaded Bitmap (session cache).</summary>
    private readonly Dictionary<string, Bitmap?> _cache = new();

    /// <summary>Track paths we already tried and failed so we don't retry.</summary>
    private readonly HashSet<string> _failedPaths = new(StringComparer.OrdinalIgnoreCase);

    private static readonly object CacheLock = new();
    private static readonly HttpClient Http = new() { Timeout = TimeSpan.FromSeconds(10) };
    private bool _disposed;

    public int IndexedCount => _index.Count;
    public bool IsInitialized => _index.Count > 0;

    /// <summary>
    /// Build the lookup index from the embedded icon_manifest.txt resource.
    /// Each line is a relative path like "Tools/Tools_ITEM_Meta_Axe_Shengong_Alpha.png".
    /// </summary>
    public void BuildIndexFromManifest()
    {
        _index.Clear();
        ClearCache();

        try
        {
            var manifestLines = LoadEmbeddedManifest();
            if (manifestLines == null || manifestLines.Length == 0)
            {
                Log.Warning("Icon manifest is empty or not found");
                return;
            }

            foreach (var line in manifestLines)
            {
                var relativePath = line.Trim();
                if (string.IsNullOrEmpty(relativePath)) continue;

                var fileName = Path.GetFileNameWithoutExtension(relativePath);

                // Key 1: Full filename (e.g. "Tools_ITEM_Meta_Axe_Shengong_Alpha")
                _index.TryAdd(fileName, relativePath);

                // Key 2: Strip category prefix (e.g. "ITEM_Meta_Axe_Shengong_Alpha")
                var underscoreIdx = fileName.IndexOf('_');
                if (underscoreIdx > 0 && underscoreIdx < fileName.Length - 1)
                {
                    var afterCategory = fileName[(underscoreIdx + 1)..];
                    _index.TryAdd(afterCategory, relativePath);

                    // Key 3: Strip ITEM_ or T_ITEM_ prefix to get the pure name
                    if (afterCategory.StartsWith("ITEM_", StringComparison.OrdinalIgnoreCase))
                    {
                        var pureName = afterCategory[5..];
                        _index.TryAdd(pureName, relativePath);
                    }
                    else if (afterCategory.StartsWith("T_ITEM_", StringComparison.OrdinalIgnoreCase))
                    {
                        var pureName = afterCategory[7..];
                        _index.TryAdd(pureName, relativePath);
                        _index.TryAdd("ITEM_" + pureName, relativePath);
                    }
                }
            }

            Log.Information("Icon index built from manifest: {Count} entries from {FileCount} icons",
                _index.Count, manifestLines.Length);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to build icon index from manifest");
        }
    }

    /// <summary>
    /// Try to find and download an icon for the given RowName / MetaRow.
    /// Returns a cached Bitmap if already downloaded this session, otherwise fetches from GitHub.
    /// </summary>
    public Bitmap? GetIcon(string? rowName)
    {
        if (string.IsNullOrEmpty(rowName) || _index.Count == 0)
            return null;

        var relativePath = ResolveIconPath(rowName);
        if (relativePath == null)
            return null;

        return LoadBitmapFromGitHub(relativePath);
    }

    /// <summary>
    /// Async version — downloads the icon without blocking the UI thread.
    /// Use this from async contexts for better responsiveness.
    /// </summary>
    public async Task<Bitmap?> GetIconAsync(string? rowName)
    {
        if (string.IsNullOrEmpty(rowName) || _index.Count == 0)
            return null;

        var relativePath = ResolveIconPath(rowName);
        if (relativePath == null)
            return null;

        return await LoadBitmapFromGitHubAsync(relativePath);
    }

    /// <summary>
    /// Find the relative icon path for a given RowName, or null if not in manifest.
    /// </summary>
    public string? ResolveIconPath(string rowName)
    {
        // Strategy 1: Direct match (e.g. "Meta_Axe_Shengong_Alpha" or "ITEM_Wood")
        if (_index.TryGetValue(rowName, out var path))
            return path;

        // Strategy 2: Try with "Meta_" prefix stripped
        if (rowName.StartsWith("Meta_", StringComparison.OrdinalIgnoreCase))
        {
            var stripped = rowName[5..];
            if (_index.TryGetValue(stripped, out path))
                return path;
        }

        // Strategy 3: Try adding ITEM_ prefix
        if (_index.TryGetValue("ITEM_" + rowName, out path))
            return path;

        // Strategy 4: Try adding ITEM_Meta_ for workshop items
        if (!rowName.StartsWith("Meta_", StringComparison.OrdinalIgnoreCase))
        {
            if (_index.TryGetValue("ITEM_Meta_" + rowName, out path))
                return path;
        }

        // Strategy 5: Fuzzy — search for any key ending with the rowName
        foreach (var kvp in _index)
        {
            if (kvp.Key.EndsWith("_" + rowName, StringComparison.OrdinalIgnoreCase) ||
                kvp.Key.EndsWith(rowName, StringComparison.OrdinalIgnoreCase))
                return kvp.Value;
        }

        return null;
    }

    /// <summary>
    /// Synchronous download — blocks the calling thread. Used during batch loading.
    /// </summary>
    private Bitmap? LoadBitmapFromGitHub(string relativePath)
    {
        lock (CacheLock)
        {
            if (_cache.TryGetValue(relativePath, out var cached))
                return cached;
            if (_failedPaths.Contains(relativePath))
                return null;
        }

        try
        {
            var url = GitHubRawBase + relativePath.Replace('\\', '/');
            var data = Http.GetByteArrayAsync(url).GetAwaiter().GetResult();

            using var ms = new MemoryStream(data);
            var bitmap = new Bitmap(ms);

            lock (CacheLock)
            {
                _cache.TryAdd(relativePath, bitmap);
            }

            return bitmap;
        }
        catch (Exception ex)
        {
            Log.Debug("Failed to download icon: {Path} — {Error}", relativePath, ex.Message);
            lock (CacheLock)
            {
                _failedPaths.Add(relativePath);
            }
            return null;
        }
    }

    /// <summary>
    /// Async download — non-blocking. Preferred for UI contexts.
    /// </summary>
    private async Task<Bitmap?> LoadBitmapFromGitHubAsync(string relativePath)
    {
        lock (CacheLock)
        {
            if (_cache.TryGetValue(relativePath, out var cached))
                return cached;
            if (_failedPaths.Contains(relativePath))
                return null;
        }

        try
        {
            var url = GitHubRawBase + relativePath.Replace('\\', '/');
            var data = await Http.GetByteArrayAsync(url);

            using var ms = new MemoryStream(data);
            var bitmap = new Bitmap(ms);

            lock (CacheLock)
            {
                _cache.TryAdd(relativePath, bitmap);
            }

            return bitmap;
        }
        catch (Exception ex)
        {
            Log.Debug("Failed to download icon: {Path} — {Error}", relativePath, ex.Message);
            lock (CacheLock)
            {
                _failedPaths.Add(relativePath);
            }
            return null;
        }
    }

    /// <summary>
    /// Load the icon_manifest.txt embedded resource from the Assets folder.
    /// Uses the calling assembly to resolve the avares:// URI correctly regardless of spaces in the name.
    /// </summary>
    private static string[]? LoadEmbeddedManifest()
    {
        try
        {
            // Resolve assembly name at runtime to handle spaces correctly
            var assembly = System.Reflection.Assembly.GetExecutingAssembly();
            var assemblyName = assembly.GetName().Name ?? "Icarus Toolkit";
            var uri = new Uri($"avares://{assemblyName}/Assets/{ManifestResourceName}");
            using var stream = AssetLoader.Open(uri);
            using var reader = new StreamReader(stream);
            var content = reader.ReadToEnd();
            return content.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        }
        catch (Exception ex)
        {
            Log.Warning("Could not load embedded icon manifest: {Error}", ex.Message);
            return null;
        }
    }

    public void ClearCache()
    {
        List<Bitmap?> toDispose;
        lock (CacheLock)
        {
            toDispose = new List<Bitmap?>(_cache.Values);
            _cache.Clear();
            _failedPaths.Clear();
        }

        // Dispose outside lock to avoid holding it during potentially slow Dispose calls
        foreach (var bmp in toDispose)
            bmp?.Dispose();
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        ClearCache();
        GC.SuppressFinalize(this);
    }
}
