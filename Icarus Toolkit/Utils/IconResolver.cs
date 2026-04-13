using Avalonia.Media.Imaging;
using Serilog;

namespace Icarus_Toolkit.Utils;

/// <summary>
/// Resolves item RowNames/MetaRows to icon Bitmaps by scanning an icons folder.
/// Builds an index of all PNG files and matches items using multiple strategies.
/// </summary>
public class IconResolver : IDisposable
{
    private readonly Dictionary<string, string> _index = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, Bitmap> _cache = new();
    private static readonly object CacheLock = new();
    private bool _disposed;

    public string? IconFolder { get; private set; }
    public int IndexedCount => _index.Count;

    /// <summary>
    /// Scan an icons folder and build the lookup index.
    /// Icons are named like "Category_ITEM_Meta_Axe_Shengong_Alpha.png"
    /// or "Category_T_ITEM_Lithium_Axe.png".
    /// </summary>
    public void BuildIndex(string iconFolder)
    {
        _index.Clear();
        ClearCache();
        IconFolder = iconFolder;

        if (string.IsNullOrEmpty(iconFolder) || !Directory.Exists(iconFolder))
        {
            Log.Warning("Icon folder not found: {Folder}", iconFolder);
            return;
        }

        // Recursively find all .png files
        var pngFiles = Directory.GetFiles(iconFolder, "*.png", SearchOption.AllDirectories);

        foreach (var file in pngFiles)
        {
            var stem = Path.GetFileNameWithoutExtension(file);

            // Add full filename as key (e.g. "Tools_ITEM_Meta_Axe_Shengong_Alpha")
            _index.TryAdd(stem, file);

            // Extract the item name portion by stripping the category prefix
            // e.g. "Tools_ITEM_Meta_Axe_Shengong_Alpha" -> "ITEM_Meta_Axe_Shengong_Alpha"
            var underscoreIdx = stem.IndexOf('_');
            if (underscoreIdx > 0 && underscoreIdx < stem.Length - 1)
            {
                var afterCategory = stem[(underscoreIdx + 1)..];
                _index.TryAdd(afterCategory, file);

                // Also strip ITEM_ or T_ITEM_ prefix to get the pure name
                // "ITEM_Meta_Axe_Shengong_Alpha" -> "Meta_Axe_Shengong_Alpha"
                // "T_ITEM_Lithium_Axe" -> "Lithium_Axe"
                if (afterCategory.StartsWith("ITEM_", StringComparison.OrdinalIgnoreCase))
                {
                    var pureName = afterCategory[5..];
                    _index.TryAdd(pureName, file);
                }
                else if (afterCategory.StartsWith("T_ITEM_", StringComparison.OrdinalIgnoreCase))
                {
                    var pureName = afterCategory[7..];
                    _index.TryAdd(pureName, file);
                    // Also add with ITEM_ prefix for cross-matching
                    _index.TryAdd("ITEM_" + pureName, file);
                }
            }
        }

        Log.Information("Icon index built: {Count} entries from {FileCount} files in {Folder}",
            _index.Count, pngFiles.Length, iconFolder);
    }

    /// <summary>
    /// Try to find an icon for the given RowName / MetaRow.
    /// Tries multiple matching strategies in order of specificity.
    /// </summary>
    public Bitmap? GetIcon(string? rowName)
    {
        if (string.IsNullOrEmpty(rowName) || _index.Count == 0)
            return null;

        var path = ResolveIconPath(rowName);
        if (path == null)
            return null;

        return LoadBitmap(path);
    }

    /// <summary>
    /// Find the icon file path for a given RowName, or null if not found.
    /// </summary>
    public string? ResolveIconPath(string rowName)
    {
        // Strategy 1: Direct match (e.g. "Meta_Axe_Shengong_Alpha" or "ITEM_Wood")
        if (_index.TryGetValue(rowName, out var path))
            return path;

        // Strategy 2: Try with "Meta_" prefix stripped (some items stored without it)
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

        // Strategy 5: Fuzzy — search for any key that ends with the rowName
        foreach (var kvp in _index)
        {
            if (kvp.Key.EndsWith("_" + rowName, StringComparison.OrdinalIgnoreCase) ||
                kvp.Key.EndsWith(rowName, StringComparison.OrdinalIgnoreCase))
                return kvp.Value;
        }

        return null;
    }

    private Bitmap? LoadBitmap(string path)
    {
        lock (CacheLock)
        {
            if (_cache.TryGetValue(path, out var cached))
                return cached;
        }

        try
        {
            if (!File.Exists(path))
                return null;

            var bitmap = new Bitmap(path);

            lock (CacheLock)
            {
                _cache.TryAdd(path, bitmap);
            }

            return bitmap;
        }
        catch (Exception ex)
        {
            Log.Warning("Failed to load icon: {Path} — {Error}", path, ex.Message);
            return null;
        }
    }

    public void ClearCache()
    {
        lock (CacheLock)
        {
            foreach (var bmp in _cache.Values)
                bmp.Dispose();
            _cache.Clear();
        }
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        ClearCache();
        GC.SuppressFinalize(this);
    }
}
