namespace Icarus;

using System.Text.Json;
using System.Text.Json.Serialization;

internal static class ExtensionMethods
{
    /// <summary>
    /// Creates a deep copy of an object using JSON serialization.
    /// This approach works with .NET 8+ and avoids the deprecated BinaryFormatter.
    /// </summary>
    internal static T DeepClone<T>(this T source) where T : notnull
    {
        var json = JsonSerializer.Serialize(source);
        return JsonSerializer.Deserialize<T>(json)
            ?? throw new InvalidOperationException("Failed to deserialize cloned object");
    }
}
