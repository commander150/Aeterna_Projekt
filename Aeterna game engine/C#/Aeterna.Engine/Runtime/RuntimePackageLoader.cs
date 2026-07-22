using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine.Contracts;

namespace Aeterna.Engine.Runtime;

public sealed record RuntimeDeckDefinition(
    string DeckId,
    ImmutableArray<string> OrderedCardIds);

public sealed record RuntimePackageCatalog(
    string PackageId,
    ImmutableHashSet<string> CardIds,
    ImmutableDictionary<string, RuntimeDeckDefinition> Decks);

public static class RuntimePackageLoader
{
    private static readonly string[] RequiredFiles =
    [
        "manifest.json",
        "cards.jsonl",
        "decks.jsonl",
        "lookups.json",
    ];

    public static RuntimePackageCatalog Load(RuntimePackageSource? source)
    {
        if (source is null)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_SOURCE_MISSING",
                "Runtime package source is missing.");
        }

        if (string.IsNullOrWhiteSpace(source.PackageDirectory))
        {
            throw new EngineInputException("RUNTIME_PACKAGE_PATH_INVALID", "Runtime package directory is empty.");
        }

        var packageDirectory = Path.GetFullPath(source.PackageDirectory);
        if (!Directory.Exists(packageDirectory))
        {
            throw new EngineInputException("RUNTIME_PACKAGE_NOT_FOUND", "Runtime package directory was not found.");
        }

        foreach (var fileName in RequiredFiles)
        {
            if (!File.Exists(Path.Combine(packageDirectory, fileName)))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_FILE_MISSING",
                    $"Runtime package file is missing: {fileName}");
            }
        }

        using var manifest = ParseJsonFile(Path.Combine(packageDirectory, "manifest.json"));
        RequireObject(manifest.RootElement, "Runtime package manifest must be an object.");
        var packageId = ReadRequiredString(manifest.RootElement, "package_id");
        if (source.ExpectedPackageId is not null
            && !string.Equals(source.ExpectedPackageId, packageId, StringComparison.Ordinal))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_ID_MISMATCH",
                "Runtime package ID does not match the requested package.");
        }

        var cardIds = ImmutableHashSet.CreateBuilder<string>(StringComparer.Ordinal);
        foreach (var card in ReadJsonLines(Path.Combine(packageDirectory, "cards.jsonl")))
        {
            var cardId = ReadRequiredString(card, "card_id");
            if (!cardIds.Add(cardId))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_DUPLICATE_CARD",
                    "Runtime package contains a duplicate card_id.");
            }
        }

        if (cardIds.Count == 0)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_EMPTY_CARDS",
                "Runtime package card registry is empty.");
        }

        var decks = ImmutableDictionary.CreateBuilder<string, RuntimeDeckDefinition>(StringComparer.Ordinal);
        foreach (var deck in ReadJsonLines(Path.Combine(packageDirectory, "decks.jsonl")))
        {
            var deckId = ReadRequiredString(deck, "deck_id");
            var cardEntries = ReadRequiredArray(deck, "card_entries");
            var orderedCardIds = ImmutableArray.CreateBuilder<string>();
            foreach (var entry in cardEntries.EnumerateArray())
            {
                RequireObject(entry, "Deck card entry must be an object.");
                var cardId = ReadRequiredString(entry, "card_id");
                var count = ReadRequiredInt(entry, "count");
                if (count <= 0)
                {
                    throw new EngineInputException(
                        "RUNTIME_PACKAGE_DECK_COUNT_INVALID",
                        "Deck entry count must be positive.");
                }

                if (!cardIds.Contains(cardId))
                {
                    throw new EngineInputException(
                        "RUNTIME_PACKAGE_UNKNOWN_CARD",
                        "Deck references an unknown card_id.");
                }

                for (var index = 0; index < count; index++)
                {
                    orderedCardIds.Add(cardId);
                }
            }

            if (!decks.TryAdd(deckId, new RuntimeDeckDefinition(deckId, orderedCardIds.ToImmutable())))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_DUPLICATE_DECK",
                    "Runtime package contains a duplicate deck_id.");
            }
        }

        using var lookups = ParseJsonFile(Path.Combine(packageDirectory, "lookups.json"));
        RequireObject(lookups.RootElement, "Runtime lookups root must be an object.");
        return new RuntimePackageCatalog(packageId, cardIds.ToImmutable(), decks.ToImmutable());
    }

    private static JsonDocument ParseJsonFile(string path)
    {
        try
        {
            return JsonDocument.Parse(File.ReadAllBytes(path));
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or JsonException)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_JSON_INVALID",
                "Runtime package JSON could not be read or parsed.",
                exception);
        }
    }

    private static IEnumerable<JsonElement> ReadJsonLines(string path)
    {
        string[] lines;
        try
        {
            lines = File.ReadAllLines(path);
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_JSONL_INVALID",
                "Runtime package JSONL could not be read.",
                exception);
        }

        foreach (var line in lines.Where(line => !string.IsNullOrWhiteSpace(line)))
        {
            JsonDocument document;
            try
            {
                document = JsonDocument.Parse(line);
            }
            catch (JsonException exception)
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_JSONL_INVALID",
                    "Runtime package JSONL record is invalid.",
                    exception);
            }

            using (document)
            {
                RequireObject(document.RootElement, "Runtime package JSONL record must be an object.");
                yield return document.RootElement.Clone();
            }
        }
    }

    private static string ReadRequiredString(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_FIELD_INVALID",
                $"Required runtime package string is missing: {propertyName}");
        }

        return value.GetString()!;
    }

    private static int ReadRequiredInt(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var result))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_FIELD_INVALID",
                $"Required runtime package integer is missing: {propertyName}");
        }

        return result;
    }

    private static JsonElement ReadRequiredArray(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value) || value.ValueKind != JsonValueKind.Array)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_FIELD_INVALID",
                $"Required runtime package array is missing: {propertyName}");
        }

        return value;
    }

    private static void RequireObject(JsonElement value, string message)
    {
        if (value.ValueKind != JsonValueKind.Object)
        {
            throw new EngineInputException("RUNTIME_PACKAGE_SHAPE_INVALID", message);
        }
    }
}

public sealed class EngineInputException : Exception
{
    public EngineInputException(string code, string message, Exception? innerException = null)
        : base(message, innerException)
    {
        Code = code;
    }

    public string Code { get; }
}
