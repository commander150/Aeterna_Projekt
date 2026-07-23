using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine.Contracts;

namespace Aeterna.Engine.Runtime;

public sealed record RuntimeCardDefinition(
    string CardId,
    int Magnitude,
    int PrintedAuraCost,
    string Realm,
    string CardType);

public sealed record RuntimeDeckDefinition(
    string DeckId,
    ImmutableArray<string> OrderedCardIds);

public sealed record RuntimePackageCatalog(
    string PackageId,
    ImmutableDictionary<string, RuntimeCardDefinition> Cards,
    ImmutableDictionary<string, RuntimeDeckDefinition> Decks,
    RuntimeLookupCatalog Lookups);

public static class RuntimePackageLoader
{
    private static readonly string[] RequiredFiles =
    [
        "manifest.json",
        "cards.jsonl",
        "decks.jsonl",
        "lookups.json",
    ];

    private static readonly string[] RequiredLookupGroups =
    [
        "realm",
        "card_type",
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

        var runtimeLookups = ReadRuntimeLookupCatalog(Path.Combine(packageDirectory, "lookups.json"));
        var cards = ImmutableDictionary.CreateBuilder<string, RuntimeCardDefinition>(StringComparer.Ordinal);
        foreach (var card in ReadJsonLines(Path.Combine(packageDirectory, "cards.jsonl")))
        {
            var cardId = ReadRequiredString(card, "card_id");
            var magnitude = ReadRequiredMagnitude(card);
            var printedAuraCost = ReadRequiredAuraCost(card);
            var realm = ReadAndResolveCardLookup(
                card,
                propertyName: "realm",
                lookupGroup: "realm",
                errorCode: "RUNTIME_PACKAGE_CARD_REALM_INVALID",
                runtimeLookups);
            var cardType = ReadAndResolveCardLookup(
                card,
                propertyName: "card_type",
                lookupGroup: "card_type",
                errorCode: "RUNTIME_PACKAGE_CARD_TYPE_INVALID",
                runtimeLookups);
            var definition = new RuntimeCardDefinition(
                cardId,
                magnitude,
                printedAuraCost,
                realm,
                cardType);
            if (!cards.TryAdd(cardId, definition))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_DUPLICATE_CARD",
                    "Runtime package contains a duplicate card_id.");
            }
        }

        if (cards.Count == 0)
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

                if (!cards.ContainsKey(cardId))
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

        var catalog = new RuntimePackageCatalog(
            packageId,
            cards.ToImmutable(),
            decks.ToImmutable(),
            runtimeLookups);
        ValidateCatalog(catalog);
        return catalog;
    }

    internal static void ValidateCatalog(RuntimePackageCatalog? catalog)
    {
        if (catalog is null
            || string.IsNullOrWhiteSpace(catalog.PackageId)
            || catalog.Cards is null
            || catalog.Decks is null
            || catalog.Lookups is null)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_CATALOG_INVALID",
                "Runtime package catalog is missing required data.");
        }

        if (catalog.Cards.Count == 0)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_EMPTY_CARDS",
                "Runtime package card registry is empty.");
        }

        ValidateLookupCatalog(catalog.Lookups);
        foreach (var (cardId, definition) in catalog.Cards)
        {
            if (definition is null
                || string.IsNullOrWhiteSpace(cardId)
                || !string.Equals(cardId, definition.CardId, StringComparison.Ordinal)
                || definition.Magnitude < 0
                || definition.PrintedAuraCost < 0
                || string.IsNullOrWhiteSpace(definition.Realm)
                || !catalog.Lookups.ContainsCanonicalValue("realm", definition.Realm)
                || string.IsNullOrWhiteSpace(definition.CardType)
                || !catalog.Lookups.ContainsCanonicalValue("card_type", definition.CardType))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_CATALOG_INVALID",
                    "Runtime package card definition is invalid.");
            }
        }

        foreach (var (deckId, deck) in catalog.Decks)
        {
            if (deck is null
                || string.IsNullOrWhiteSpace(deckId)
                || !string.Equals(deckId, deck.DeckId, StringComparison.Ordinal)
                || deck.OrderedCardIds.Any(cardId => !catalog.Cards.ContainsKey(cardId)))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_CATALOG_INVALID",
                    "Runtime package deck definition is invalid.");
            }
        }
    }

    private static RuntimeLookupCatalog ReadRuntimeLookupCatalog(string path)
    {
        using var document = ParseJsonFile(path);
        if (document.RootElement.ValueKind != JsonValueKind.Object)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_LOOKUPS_ROOT_INVALID",
                "Runtime lookups root must be an object.");
        }

        if (!document.RootElement.TryGetProperty("lookups", out var records)
            || records.ValueKind != JsonValueKind.Array)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_LOOKUPS_ARRAY_INVALID",
                "Runtime lookups must contain a lookups array.");
        }

        var aliasesByGroup = new Dictionary<string, ImmutableDictionary<string, string>.Builder>(
            StringComparer.Ordinal);
        foreach (var groupName in RequiredLookupGroups)
        {
            aliasesByGroup.Add(
                groupName,
                ImmutableDictionary.CreateBuilder<string, string>(StringComparer.Ordinal));
        }

        foreach (var record in records.EnumerateArray())
        {
            if (record.ValueKind != JsonValueKind.Object)
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_LOOKUP_RECORD_INVALID",
                    "Runtime lookup record must be an object.");
            }

            var lookupGroup = ReadRequiredLookupRecordString(record, "lookup_group");
            var alias = ReadRequiredLookupRecordString(record, "value");
            var status = ReadRequiredLookupRecordString(record, "status");
            var canonicalValue = ReadRequiredLookupRecordString(record, "canonical_value");
            if (!aliasesByGroup.TryGetValue(lookupGroup, out var aliases))
            {
                continue;
            }

            if (!IsStableRuntimeToken(canonicalValue))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_LOOKUP_RECORD_INVALID",
                    "Runtime lookup canonical_value must be a stable lowercase runtime token.");
            }

            if (!string.Equals(status, "active", StringComparison.Ordinal))
            {
                continue;
            }

            if (aliases.TryGetValue(alias, out var existingCanonicalValue))
            {
                if (!string.Equals(existingCanonicalValue, canonicalValue, StringComparison.Ordinal))
                {
                    throw new EngineInputException(
                        "RUNTIME_PACKAGE_LOOKUP_ALIAS_CONFLICT",
                        "Runtime lookup alias maps to conflicting canonical values.");
                }

                continue;
            }

            aliases.Add(alias, canonicalValue);
        }

        var groups = ImmutableDictionary.CreateBuilder<string, RuntimeLookupGroup>(StringComparer.Ordinal);
        foreach (var groupName in RequiredLookupGroups)
        {
            var aliases = aliasesByGroup[groupName];
            if (aliases.Count == 0)
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_LOOKUP_GROUP_MISSING",
                    $"Required active runtime lookup group is missing or empty: {groupName}");
            }

            groups.Add(groupName, new RuntimeLookupGroup(groupName, aliases.ToImmutable()));
        }

        return new RuntimeLookupCatalog(groups.ToImmutable());
    }

    private static void ValidateLookupCatalog(RuntimeLookupCatalog lookups)
    {
        if (lookups.Groups is null
            || !Equals(lookups.Groups.KeyComparer, StringComparer.Ordinal))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_CATALOG_INVALID",
                "Runtime lookup catalog is missing required data or ordinal comparison.");
        }

        foreach (var requiredGroup in RequiredLookupGroups)
        {
            if (!lookups.Groups.TryGetValue(requiredGroup, out var group)
                || group is null
                || !string.Equals(requiredGroup, group.LookupGroup, StringComparison.Ordinal)
                || group.ActiveAliases is null
                || group.ActiveAliases.Count == 0
                || !Equals(group.ActiveAliases.KeyComparer, StringComparer.Ordinal))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_CATALOG_INVALID",
                    $"Required runtime lookup group is invalid: {requiredGroup}");
            }
        }

        foreach (var (groupName, group) in lookups.Groups)
        {
            if (group is null
                || string.IsNullOrWhiteSpace(groupName)
                || !string.Equals(groupName, group.LookupGroup, StringComparison.Ordinal)
                || group.ActiveAliases is null
                || !Equals(group.ActiveAliases.KeyComparer, StringComparer.Ordinal)
                || group.ActiveAliases.Any(pair =>
                    string.IsNullOrWhiteSpace(pair.Key)
                    || string.IsNullOrWhiteSpace(pair.Value)
                    || !IsStableRuntimeToken(pair.Value)))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_CATALOG_INVALID",
                    "Runtime lookup catalog is internally inconsistent.");
            }
        }
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

    private static int ReadRequiredMagnitude(JsonElement root)
    {
        if (!root.TryGetProperty("magnitude", out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var magnitude)
            || magnitude < 0)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_CARD_MAGNITUDE_INVALID",
                "Runtime card magnitude must be a non-negative Int32 JSON number.");
        }

        return magnitude;
    }

    private static int ReadRequiredAuraCost(JsonElement root)
    {
        if (!root.TryGetProperty("aura_cost", out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var auraCost)
            || auraCost < 0)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_CARD_AURA_COST_INVALID",
                "Runtime card aura_cost must be a non-negative Int32 JSON number.");
        }

        return auraCost;
    }

    private static string ReadAndResolveCardLookup(
        JsonElement root,
        string propertyName,
        string lookupGroup,
        string errorCode,
        RuntimeLookupCatalog lookups)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw new EngineInputException(
                errorCode,
                $"Runtime card {propertyName} must be a non-empty string.");
        }

        var alias = value.GetString()!;
        if (!lookups.TryResolve(lookupGroup, alias, out var canonicalValue))
        {
            throw new EngineInputException(
                errorCode,
                $"Runtime card {propertyName} is not an active lookup alias.");
        }

        return canonicalValue;
    }

    private static string ReadRequiredLookupRecordString(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_LOOKUP_RECORD_INVALID",
                $"Runtime lookup record string is missing or empty: {propertyName}");
        }

        return value.GetString()!;
    }

    private static bool IsStableRuntimeToken(string value)
    {
        if (value.Length == 0 || value[0] is < 'a' or > 'z')
        {
            return false;
        }

        return value.Skip(1).All(character =>
            character is >= 'a' and <= 'z'
            or >= '0' and <= '9'
            or '_');
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
