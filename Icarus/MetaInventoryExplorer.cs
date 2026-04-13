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
        Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        PropertyNameCaseInsensitive = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
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
            Inventory = JsonSerializer.Deserialize<MetaInventory>(json, SerializerOptions);

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

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

/// <summary>
/// A single item in the meta inventory. Items can be either:
/// - Simple workshop items: MetaRow is set (e.g. "Meta_Axe_Shengong_Alpha"), Count > 0
/// - Full item instances: MetaRow is null, identity comes from ItemStaticData.RowName,
///   with full durability, alterations, living item slots, etc.
/// </summary>
public class InventoryItem
{
    /// <summary>
    /// Workshop item row name (e.g. "Meta_Axe_Shengong_Alpha").
    /// NULL for full item instances — use ItemStaticData.RowName instead.
    /// </summary>
    public string? MetaRow { get; set; }

    /// <summary>
    /// Quantity for simple workshop items. 0 for full item instances.
    /// </summary>
    public int Count { get; set; }

    /// <summary>
    /// Static data reference for the item — contains RowName and DataTableName.
    /// This is the primary identifier for full item instances where MetaRow is null.
    /// </summary>
    public ItemStaticDataRef? ItemStaticData { get; set; }

    /// <summary>
    /// Dynamic properties like durability, ammo, stack size, etc.
    /// </summary>
    public List<ItemDynamicProperty>? ItemDynamicData { get; set; }

    /// <summary>
    /// Custom stat overrides.
    /// </summary>
    public List<JsonElement>? ItemCustomStats { get; set; }

    /// <summary>
    /// Custom properties including alterations, living item slots, world stats.
    /// </summary>
    public ItemCustomProperties? CustomProperties { get; set; }

    /// <summary>
    /// Unique identifier for this item instance.
    /// </summary>
    public string? DatabaseGUID { get; set; }

    /// <summary>
    /// Owner lookup ID (-1 = no owner).
    /// </summary>
    public int ItemOwnerLookupId { get; set; } = -1;

    /// <summary>
    /// Runtime gameplay tags.
    /// </summary>
    public RuntimeTagsData? RuntimeTags { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }

    /// <summary>
    /// Gets the best available display name for this item.
    /// Uses MetaRow if set, otherwise falls back to ItemStaticData.RowName.
    /// </summary>
    [JsonIgnore]
    public string DisplayRowName =>
        !string.IsNullOrEmpty(MetaRow) ? MetaRow :
        ItemStaticData?.RowName ?? "Unknown";

    /// <summary>
    /// Gets the stack count — uses Count for workshop items,
    /// or reads ItemableStack from dynamic data for full items.
    /// </summary>
    [JsonIgnore]
    public int EffectiveCount
    {
        get
        {
            if (Count > 0) return Count;
            var stack = ItemDynamicData?.FirstOrDefault(d => d.PropertyType == "ItemableStack");
            return stack?.Value ?? 1;
        }
    }

    /// <summary>
    /// Gets the durability value from dynamic data, or -1 if not present.
    /// </summary>
    [JsonIgnore]
    public int Durability
    {
        get
        {
            var dur = ItemDynamicData?.FirstOrDefault(d => d.PropertyType == "Durability");
            return dur?.Value ?? -1;
        }
    }
}

/// <summary>
/// Reference to a data table row — used by ItemStaticData.
/// </summary>
public class ItemStaticDataRef
{
    public string? RowName { get; set; }
    public string? DataTableName { get; set; }
}

/// <summary>
/// A dynamic property on an item (durability, ammo, stack size, etc.).
/// </summary>
public class ItemDynamicProperty
{
    public string? PropertyType { get; set; }
    public int Value { get; set; }
}

/// <summary>
/// Custom properties block — alterations, living item slots, stats.
/// </summary>
public class ItemCustomProperties
{
    public List<JsonElement>? StaticWorldStats { get; set; }
    public List<JsonElement>? StaticWorldHeldStats { get; set; }
    public List<ItemStatEntry>? Stats { get; set; }
    public List<ItemAlterationEntry>? Alterations { get; set; }
    public List<LivingItemSlot>? LivingItemSlots { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}

public class ItemStatEntry
{
    public ItemStatValue? Stat { get; set; }
    public int Value { get; set; }
}

public class ItemStatValue
{
    public string? Value { get; set; }
}

public class ItemAlterationEntry
{
    public string? Value { get; set; }
}

public class LivingItemSlot
{
    public LivingItemSelection? UpgradeSelection { get; set; }
    public int UnlockProgress { get; set; } = -1;
}

public class LivingItemSelection
{
    public string? Value { get; set; }
}

public class RuntimeTagsData
{
    public List<JsonElement>? GameplayTags { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? ExtensionData { get; set; }
}
