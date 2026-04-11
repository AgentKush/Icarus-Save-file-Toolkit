namespace Icarus;

using System.Text.Json;
using System.Text.Json.Serialization;
using Serilog;

public class MetaInventoryExplorer
{
    public MetaInventory? Inventory { get; private set; }
    private readonly string _inventoryPath;

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        WriteIndented = true,
        Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
    };

    public MetaInventoryExplorer(string inventoryPath)
    {
        _inventoryPath = inventoryPath;
        RefreshInventory();
    }

    /// <summary>
    /// Exports meta inventory to the save file using atomic write.
    /// </summary>
    public bool ExportInventory(MetaInventory inventory)
    {
        var tempPath = _inventoryPath + ".tmp";

        try
        {
            var json = JsonSerializer.Serialize(inventory, SerializerOptions);

            File.WriteAllText(tempPath, json);
            File.Move(tempPath, _inventoryPath, overwrite: true);

            Log.Information("Exported meta inventory to {FilePath}", _inventoryPath);
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to export meta inventory");

            try { if (File.Exists(tempPath)) File.Delete(tempPath); }
            catch { /* best effort cleanup */ }

            return false;
        }
    }

    /// <summary>
    /// Reloads meta inventory from the save file.
    /// </summary>
    public void RefreshInventory()
    {
        try
        {
            if (!File.Exists(_inventoryPath))
            {
                Log.Information("MetaInventory file not found at {Path}, creating empty inventory", _inventoryPath);
                Inventory = new MetaInventory();
                return;
            }

            var json = File.ReadAllText(_inventoryPath);
            Inventory = JsonSerializer.Deserialize<MetaInventory>(json);

            if (Inventory == null)
            {
                Log.Warning("MetaInventory deserialization returned null from {Path}", _inventoryPath);
                Inventory = new MetaInventory();
            }
            else
            {
                var itemCount = Inventory.Items?.Count ?? 0;
                Log.Information("Refreshed meta inventory with {ItemCount} items", itemCount);
            }
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to refresh meta inventory from {Path}", _inventoryPath);
            Inventory = new MetaInventory();
        }
    }
}

/// <summary>
/// Represents the MetaInventory.json file — the player's orbital workshop stash.
/// Contains items crafted in the workshop that can be taken on drops.
/// </summary>
public class MetaInventory
{
    public string? InventoryID { get; set; }
    public List<InventoryItem>? Items { get; set; }

    /// <summary>
    /// Captures unknown fields for forward-compatibility with game updates.
    /// </summary>
    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

/// <summary>
/// A single item in the meta inventory (workshop orbital stash).
/// </summary>
public class InventoryItem
{
    /// <summary>
    /// The item's data table row name (e.g. "MXC_OxygenTank", "Pickaxe_Iron").
    /// </summary>
    public string? MetaRow { get; set; }

    /// <summary>
    /// Quantity of this item.
    /// </summary>
    public int Count { get; set; }

    /// <summary>
    /// Captures any additional item properties (durability, mods, etc.).
    /// </summary>
    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}
