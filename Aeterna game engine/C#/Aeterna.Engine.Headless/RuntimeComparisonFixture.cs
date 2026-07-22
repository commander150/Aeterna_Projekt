using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine.Contracts;

namespace Aeterna.Engine.Headless;

public sealed record RuntimeComparisonFixture(
    string SchemaVersion,
    string FixtureId,
    string FixturePath,
    string RuntimePackagePath,
    int Seed,
    string MatchId,
    ImmutableArray<PlayerSetup> Players,
    int StartingHandSize,
    string StepPlanId)
{
    private const string SupportedSchema = "aeterna-runtime-comparison-fixture-v1";
    private const string SupportedFixtureId = "minimal_draw_end_turn_v1";

    public static RuntimeComparisonFixture Load(string fixturePath)
    {
        if (string.IsNullOrWhiteSpace(fixturePath))
        {
            throw new RuntimeComparisonFixtureException("FIXTURE_PATH_INVALID", "Fixture path is empty.");
        }

        var fullFixturePath = Path.GetFullPath(fixturePath);
        if (!File.Exists(fullFixturePath))
        {
            throw new RuntimeComparisonFixtureException("FIXTURE_NOT_FOUND", "Fixture file was not found.");
        }

        JsonDocument document;
        try
        {
            document = JsonDocument.Parse(File.ReadAllBytes(fullFixturePath));
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or JsonException)
        {
            throw new RuntimeComparisonFixtureException(
                "FIXTURE_JSON_INVALID",
                "Fixture JSON could not be read or parsed.",
                exception);
        }

        using (document)
        {
            var root = document.RootElement;
            Require(root.ValueKind == JsonValueKind.Object, "FIXTURE_SHAPE_INVALID", "Fixture root must be an object.");
            var schemaVersion = ReadRequiredString(root, "schema_version");
            var fixtureId = ReadRequiredString(root, "fixture_id");
            Require(schemaVersion == SupportedSchema, "FIXTURE_SCHEMA_INVALID", "Fixture schema is not supported.");
            Require(fixtureId == SupportedFixtureId, "FIXTURE_ID_INVALID", "Fixture ID is not supported.");
            var fixtureDirectory = Path.GetDirectoryName(fullFixturePath)
                ?? throw new RuntimeComparisonFixtureException("FIXTURE_PATH_INVALID", "Fixture directory is unavailable.");
            var runtimePackageRef = ReadRequiredString(root, "runtime_package_ref");
            Require(!Path.IsPathRooted(runtimePackageRef), "FIXTURE_PATH_INVALID", "Runtime package reference must be relative.");
            var runtimePackagePath = Path.GetFullPath(Path.Combine(fixtureDirectory, runtimePackageRef));
            Require(IsWithin(runtimePackagePath, fixtureDirectory), "FIXTURE_PATH_INVALID", "Runtime package reference escapes the fixture directory.");

            var playerIds = ReadStringArray(root, "player_ids");
            var deckIds = ReadStringArray(root, "deck_ids");
            Require(playerIds.Length == 2 && deckIds.Length == 2, "FIXTURE_SHAPE_INVALID", "Fixture must define two players and two decks.");
            Require(playerIds.Distinct(StringComparer.Ordinal).Count() == playerIds.Length, "FIXTURE_SHAPE_INVALID", "Fixture player IDs must be distinct.");
            var setup = ReadRequiredArray(root, "player_setup");
            Require(setup.GetArrayLength() == playerIds.Length, "FIXTURE_SHAPE_INVALID", "Fixture player setup count is invalid.");
            var players = ImmutableArray.CreateBuilder<PlayerSetup>();
            for (var index = 0; index < setup.GetArrayLength(); index++)
            {
                var playerId = ReadRequiredString(setup[index], "player_id");
                var deckId = ReadRequiredString(setup[index], "deck_id");
                Require(playerId == playerIds[index] && deckId == deckIds[index], "FIXTURE_SHAPE_INVALID", "Fixture player setup order is invalid.");
                players.Add(new PlayerSetup(playerId, deckId));
            }

            var stepPlan = ReadRequiredObject(root, "step_plan");
            var stepPlanId = ReadRequiredString(stepPlan, "step_plan_id");
            Require(stepPlanId == fixtureId, "FIXTURE_SHAPE_INVALID", "Fixture step plan is invalid.");
            return new RuntimeComparisonFixture(
                schemaVersion,
                fixtureId,
                fullFixturePath,
                runtimePackagePath,
                ReadRequiredInt(root, "seed"),
                ReadRequiredString(root, "match_id"),
                players.ToImmutable(),
                ReadRequiredInt(root, "starting_hand_size"),
                stepPlanId);
        }
    }

    public CreateMatchRequest CreateMatchRequest() => new(
        ContractSchemas.CreateMatchRequest,
        MatchId,
        Seed,
        Players,
        StartingHandSize,
        new RuntimePackageSource(RuntimePackagePath));

    private static ImmutableArray<string> ReadStringArray(JsonElement root, string propertyName)
    {
        var values = ImmutableArray.CreateBuilder<string>();
        foreach (var item in ReadRequiredArray(root, propertyName).EnumerateArray())
        {
            Require(item.ValueKind == JsonValueKind.String && !string.IsNullOrWhiteSpace(item.GetString()), "FIXTURE_SHAPE_INVALID", $"{propertyName} must contain non-empty strings.");
            values.Add(item.GetString()!);
        }

        return values.ToImmutable();
    }

    private static JsonElement ReadRequiredObject(JsonElement root, string propertyName)
    {
        Require(root.TryGetProperty(propertyName, out var value) && value.ValueKind == JsonValueKind.Object, "FIXTURE_SHAPE_INVALID", $"Required object is missing: {propertyName}");
        return value;
    }

    private static JsonElement ReadRequiredArray(JsonElement root, string propertyName)
    {
        Require(root.TryGetProperty(propertyName, out var value) && value.ValueKind == JsonValueKind.Array, "FIXTURE_SHAPE_INVALID", $"Required array is missing: {propertyName}");
        return value;
    }

    private static string ReadRequiredString(JsonElement root, string propertyName)
    {
        Require(root.TryGetProperty(propertyName, out var value)
                && value.ValueKind == JsonValueKind.String
                && !string.IsNullOrWhiteSpace(value.GetString()),
            "FIXTURE_SHAPE_INVALID",
            $"Required string is missing: {propertyName}");
        return value.GetString()!;
    }

    private static int ReadRequiredInt(JsonElement root, string propertyName)
    {
        Require(root.TryGetProperty(propertyName, out var value)
                && value.ValueKind == JsonValueKind.Number
                && value.TryGetInt32(out _),
            "FIXTURE_SHAPE_INVALID",
            $"Required integer is missing: {propertyName}");
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
            throw new RuntimeComparisonFixtureException(code, message);
        }
    }
}

public sealed class RuntimeComparisonFixtureException : Exception
{
    public RuntimeComparisonFixtureException(string code, string message, Exception? innerException = null)
        : base(message, innerException)
    {
        Code = code;
    }

    public string Code { get; }
}
