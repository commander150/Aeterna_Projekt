using System.Text.Json;

namespace Aeterna.RuntimeCandidate;

internal static class FixtureContract
{
    private const string FixtureSchemaVersion = "aeterna-runtime-comparison-fixture-v1";
    private const string FixtureId = "minimal_draw_end_turn_v1";

    public static FixtureDefinition Load(string fixturePath)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(fixturePath);
        var fullFixturePath = Path.GetFullPath(fixturePath);
        if (!File.Exists(fullFixturePath))
        {
            throw new RuntimeCandidateException("FIXTURE_NOT_FOUND", "Fixture file was not found.");
        }

        using var fixtureDocument = ParseJsonFile(fullFixturePath, "FIXTURE_JSON_INVALID");
        var root = fixtureDocument.RootElement;
        Require(root.ValueKind == JsonValueKind.Object, "FIXTURE_SHAPE_INVALID", "Fixture root must be an object.");

        var schemaVersion = ReadRequiredString(root, "schema_version");
        var fixtureId = ReadRequiredString(root, "fixture_id");
        Require(schemaVersion == FixtureSchemaVersion, "FIXTURE_SCHEMA_INVALID", "Fixture schema is not supported.");
        Require(fixtureId == FixtureId, "FIXTURE_ID_INVALID", "Fixture ID is not supported.");

        var runtimePackageRef = ReadRequiredString(root, "runtime_package_ref");
        Require(!Path.IsPathRooted(runtimePackageRef), "FIXTURE_SHAPE_INVALID", "Runtime package reference must be relative.");
        Require(
            !runtimePackageRef.Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                .Any(part => part == ".."),
            "FIXTURE_SHAPE_INVALID",
            "Runtime package reference cannot traverse its fixture directory.");

        var fixtureDirectory = Path.GetDirectoryName(fullFixturePath)
            ?? throw new RuntimeCandidateException("FIXTURE_SHAPE_INVALID", "Fixture directory is unavailable.");
        var runtimePackagePath = Path.GetFullPath(Path.Combine(fixtureDirectory, runtimePackageRef));
        Require(
            IsWithin(runtimePackagePath, fixtureDirectory),
            "FIXTURE_SHAPE_INVALID",
            "Runtime package must stay under the fixture directory.");

        var playerIds = ReadStringArray(root, "player_ids");
        var deckIds = ReadStringArray(root, "deck_ids");
        Require(playerIds.Count == 2 && playerIds.Distinct(StringComparer.Ordinal).Count() == 2,
            "FIXTURE_SHAPE_INVALID", "Fixture must define two distinct players.");
        Require(deckIds.Count == 2, "FIXTURE_SHAPE_INVALID", "Fixture must define two decks.");
        Require(playerIds.SequenceEqual(["player_1", "player_2"], StringComparer.Ordinal),
            "FIXTURE_SHAPE_INVALID", "Fixture player order is invalid.");

        var startingHandSize = ReadRequiredInt(root, "starting_hand_size");
        Require(startingHandSize == 1, "FIXTURE_SHAPE_INVALID", "Fixture starting hand size must be one.");
        var seed = ReadRequiredInt(root, "seed");
        var matchId = ReadRequiredString(root, "match_id");
        var stepPlan = ReadRequiredObject(root, "step_plan");
        var stepPlanId = ReadRequiredString(stepPlan, "step_plan_id");
        Require(stepPlanId == FixtureId, "FIXTURE_SHAPE_INVALID", "Fixture step plan is invalid.");

        ValidatePlayerSetup(root, playerIds, deckIds);
        var package = LoadRuntimePackage(runtimePackagePath, deckIds);
        return new FixtureDefinition(
            schemaVersion,
            fixtureId,
            package.PackageId,
            seed,
            matchId,
            playerIds,
            deckIds,
            startingHandSize,
            stepPlanId,
            package.Decks,
            package.CardIds);
    }

    private static RuntimePackageDefinition LoadRuntimePackage(
        string packagePath,
        IReadOnlyList<string> requiredDeckIds)
    {
        foreach (var fileName in new[] { "manifest.json", "cards.jsonl", "decks.jsonl", "lookups.json" })
        {
            Require(File.Exists(Path.Combine(packagePath, fileName)),
                "RUNTIME_PACKAGE_INVALID", $"Runtime package file is missing: {fileName}");
        }

        using var manifestDocument = ParseJsonFile(Path.Combine(packagePath, "manifest.json"), "RUNTIME_PACKAGE_INVALID");
        var packageId = ReadRequiredString(manifestDocument.RootElement, "package_id");

        var cardIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var card in ReadJsonLines(Path.Combine(packagePath, "cards.jsonl")))
        {
            var cardId = ReadRequiredString(card, "card_id");
            Require(cardIds.Add(cardId), "RUNTIME_PACKAGE_INVALID", "Runtime package contains a duplicate card_id.");
        }

        Require(cardIds.Count > 0, "RUNTIME_PACKAGE_INVALID", "Runtime package card registry is empty.");
        var decks = new Dictionary<string, DeckDefinition>(StringComparer.Ordinal);
        foreach (var deck in ReadJsonLines(Path.Combine(packagePath, "decks.jsonl")))
        {
            var deckId = ReadRequiredString(deck, "deck_id");
            var orderedCardIds = new List<string>();
            var entries = ReadRequiredArray(deck, "card_entries");
            foreach (var entry in entries.EnumerateArray())
            {
                var cardId = ReadRequiredString(entry, "card_id");
                var count = ReadRequiredInt(entry, "count");
                Require(count > 0, "RUNTIME_PACKAGE_INVALID", "Deck entry count must be positive.");
                Require(cardIds.Contains(cardId), "RUNTIME_PACKAGE_INVALID", "Deck references an unknown card_id.");
                for (var index = 0; index < count; index++)
                {
                    orderedCardIds.Add(cardId);
                }
            }

            Require(decks.TryAdd(deckId, new DeckDefinition(deckId, orderedCardIds)),
                "RUNTIME_PACKAGE_INVALID", "Runtime package contains a duplicate deck_id.");
        }

        foreach (var deckId in requiredDeckIds)
        {
            Require(decks.ContainsKey(deckId), "RUNTIME_PACKAGE_INVALID", "Fixture references an unknown deck_id.");
        }

        using var lookupsDocument = ParseJsonFile(Path.Combine(packagePath, "lookups.json"), "RUNTIME_PACKAGE_INVALID");
        Require(lookupsDocument.RootElement.ValueKind == JsonValueKind.Object,
            "RUNTIME_PACKAGE_INVALID", "Runtime lookups root must be an object.");
        return new RuntimePackageDefinition(packageId, decks, cardIds);
    }

    private static void ValidatePlayerSetup(
        JsonElement root,
        IReadOnlyList<string> playerIds,
        IReadOnlyList<string> deckIds)
    {
        var setup = ReadRequiredArray(root, "player_setup");
        Require(setup.GetArrayLength() == 2, "FIXTURE_SHAPE_INVALID", "Fixture player setup is invalid.");
        for (var index = 0; index < setup.GetArrayLength(); index++)
        {
            var record = setup[index];
            Require(ReadRequiredString(record, "player_id") == playerIds[index],
                "FIXTURE_SHAPE_INVALID", "Player setup order is invalid.");
            Require(ReadRequiredString(record, "deck_id") == deckIds[index],
                "FIXTURE_SHAPE_INVALID", "Player setup deck is invalid.");
        }
    }

    private static JsonDocument ParseJsonFile(string path, string code)
    {
        try
        {
            return JsonDocument.Parse(File.ReadAllBytes(path));
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or JsonException)
        {
            throw new RuntimeCandidateException(code, "JSON input could not be read or parsed.", exception);
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
            throw new RuntimeCandidateException("RUNTIME_PACKAGE_INVALID", "JSONL input could not be read.", exception);
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
                throw new RuntimeCandidateException("RUNTIME_PACKAGE_INVALID", "JSONL record is invalid.", exception);
            }

            using (document)
            {
                Require(document.RootElement.ValueKind == JsonValueKind.Object,
                    "RUNTIME_PACKAGE_INVALID", "JSONL record must be an object.");
                yield return document.RootElement.Clone();
            }
        }
    }

    private static IReadOnlyList<string> ReadStringArray(JsonElement root, string propertyName)
    {
        var array = ReadRequiredArray(root, propertyName);
        var values = new List<string>();
        foreach (var item in array.EnumerateArray())
        {
            Require(item.ValueKind == JsonValueKind.String && !string.IsNullOrWhiteSpace(item.GetString()),
                "FIXTURE_SHAPE_INVALID", $"{propertyName} must contain non-empty strings.");
            values.Add(item.GetString()!);
        }

        return values;
    }

    private static JsonElement ReadRequiredObject(JsonElement root, string propertyName)
    {
        Require(root.TryGetProperty(propertyName, out var value) && value.ValueKind == JsonValueKind.Object,
            "FIXTURE_SHAPE_INVALID", $"Required object is missing: {propertyName}");
        return value;
    }

    private static JsonElement ReadRequiredArray(JsonElement root, string propertyName)
    {
        Require(root.TryGetProperty(propertyName, out var value) && value.ValueKind == JsonValueKind.Array,
            "FIXTURE_SHAPE_INVALID", $"Required array is missing: {propertyName}");
        return value;
    }

    private static string ReadRequiredString(JsonElement root, string propertyName)
    {
        Require(root.TryGetProperty(propertyName, out var value)
                && value.ValueKind == JsonValueKind.String
                && !string.IsNullOrWhiteSpace(value.GetString()),
            "FIXTURE_SHAPE_INVALID", $"Required string is missing: {propertyName}");
        return value.GetString()!;
    }

    private static int ReadRequiredInt(JsonElement root, string propertyName)
    {
        Require(root.TryGetProperty(propertyName, out var value)
                && value.ValueKind == JsonValueKind.Number
                && value.TryGetInt32(out _),
            "FIXTURE_SHAPE_INVALID", $"Required integer is missing: {propertyName}");
        return value.GetInt32();
    }

    private static bool IsWithin(string path, string parent)
    {
        var relative = Path.GetRelativePath(Path.GetFullPath(parent), Path.GetFullPath(path));
        return !Path.IsPathRooted(relative)
               && !relative.Equals("..", StringComparison.Ordinal)
               && !relative.StartsWith($"..{Path.DirectorySeparatorChar}", StringComparison.Ordinal);
    }

    private static void Require(bool condition, string code, string message)
    {
        if (!condition)
        {
            throw new RuntimeCandidateException(code, message);
        }
    }

    private sealed record RuntimePackageDefinition(
        string PackageId,
        IReadOnlyDictionary<string, DeckDefinition> Decks,
        IReadOnlySet<string> CardIds);
}

public sealed class RuntimeCandidateException : Exception
{
    public RuntimeCandidateException(string code, string message, Exception? innerException = null)
        : base(message, innerException)
    {
        Code = code;
    }

    public string Code { get; }
}
