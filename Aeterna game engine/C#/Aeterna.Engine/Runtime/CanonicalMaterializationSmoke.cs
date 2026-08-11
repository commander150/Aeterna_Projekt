using System.Text.Json;

namespace Aeterna.Engine.Runtime;

internal sealed record CanonicalMaterializationSmokeSuccess(
    string RegistryPackageId,
    string RegistrySchemaVersion,
    string RegistryDataVersion,
    string CardDatabasePackageId,
    string CardDatabaseSchemaVersion,
    string CardDatabaseDataVersion,
    int CardCount,
    int AbilityCount,
    IReadOnlyList<string> Vs1CardIds,
    IReadOnlyList<string> Vs1AbilityCardIds,
    IReadOnlyList<string> Vs1AbilityRuntimeExecutableCardIds);

public static class CanonicalMaterializationSmoke
{
    public const string OutputPrefix = "AETERNA_CANONICAL_MATERIALIZATION_SMOKE ";
    public const int SuccessExitCode = 0;
    public const int ControlledRejectionExitCode = 2;
    public const int UnexpectedFailureExitCode = 3;

    public static int Run(
        IReadOnlyList<string> arguments,
        TextWriter standardOutput,
        TextWriter standardError) => Run(
        arguments,
        standardOutput,
        standardError,
        Materialize);

    internal static int Run(
        IReadOnlyList<string> arguments,
        TextWriter standardOutput,
        TextWriter standardError,
        Func<string, CanonicalPackageValidationMode, CanonicalMaterializationSmokeSuccess> materialize)
    {
        ArgumentNullException.ThrowIfNull(arguments);
        ArgumentNullException.ThrowIfNull(standardOutput);
        ArgumentNullException.ThrowIfNull(standardError);
        ArgumentNullException.ThrowIfNull(materialize);

        try
        {
            var request = Parse(arguments);
            var result = materialize(request.PackageRoot, request.ValidationMode);
            WriteSummary(standardOutput, new
            {
                schema_version = "aeterna-canonical-materialization-smoke-v1",
                status = "success",
                diagnostic_code = (string?)null,
                validation_mode = request.ValidationMode.ToString().ToLowerInvariant(),
                registry = new
                {
                    package_id = result.RegistryPackageId,
                    schema_version = result.RegistrySchemaVersion,
                    data_version = result.RegistryDataVersion,
                },
                carddatabase = new
                {
                    package_id = result.CardDatabasePackageId,
                    schema_version = result.CardDatabaseSchemaVersion,
                    data_version = result.CardDatabaseDataVersion,
                },
                cards = result.CardCount,
                abilities = result.AbilityCount,
                typed_materialization = true,
                vs1 = new
                {
                    membership_authority = "DECKS+DECK_ENTRIES",
                    unique_card_count = result.Vs1CardIds.Count,
                    ability_card_count = result.Vs1AbilityCardIds.Count,
                    ability_runtime_executable_count = result.Vs1AbilityRuntimeExecutableCardIds.Count,
                    card_ids = result.Vs1CardIds,
                    ability_runtime_executable_card_ids = result.Vs1AbilityRuntimeExecutableCardIds,
                },
            });
            return SuccessExitCode;
        }
        catch (EngineInputException exception)
        {
            WriteSummary(standardOutput, new
            {
                schema_version = "aeterna-canonical-materialization-smoke-v1",
                status = "blocked",
                diagnostic_code = exception.Code,
                message = exception.Message,
                typed_materialization = false,
            });
            return ControlledRejectionExitCode;
        }
        catch (Exception exception)
        {
            WriteSummary(standardOutput, new
            {
                schema_version = "aeterna-canonical-materialization-smoke-v1",
                status = "failed",
                diagnostic_code = "CANONICAL_MATERIALIZATION_UNEXPECTED",
                message = exception.Message,
                typed_materialization = false,
            });
            standardError.WriteLine(exception.ToString());
            return UnexpectedFailureExitCode;
        }
    }

    private static CanonicalMaterializationSmokeSuccess Materialize(
        string packageRoot,
        CanonicalPackageValidationMode validationMode)
    {
        var fullRoot = Path.GetFullPath(packageRoot);
        var registry = CanonicalPackageLoader.LoadRegistry(
            Path.Combine(fullRoot, "REGISTRY"),
            validationMode);
        var cardDatabase = CanonicalPackageLoader.LoadCardDatabase(
            Path.Combine(fullRoot, "CARDDATABASE"),
            registry,
            validationMode);
        var cards = CanonicalCardMaterializer.Materialize(cardDatabase);
        var abilities = CanonicalAbilityMaterializer.Materialize(cardDatabase);
        var vs1CardIds = ResolveVs1CardIds(cardDatabase);
        var vs1AbilityCardIds = vs1CardIds
            .Where(abilities.AbilitiesByCardId.ContainsKey)
            .ToArray();
        var vs1ExecutableCardIds = vs1AbilityCardIds
            .Where(cardId => abilities.AbilitiesByCardId[cardId].All(CanonicalEffectExecutor.IsSupportedGraph))
            .ToArray();
        return new CanonicalMaterializationSmokeSuccess(
            registry.PackageId,
            registry.SchemaVersion,
            registry.DataVersion,
            cardDatabase.PackageId,
            cardDatabase.SchemaVersion,
            cardDatabase.DataVersion,
            cards.Definitions.Length,
            abilities.AbilitiesById.Count,
            vs1CardIds,
            vs1AbilityCardIds,
            vs1ExecutableCardIds);
    }

    private static string[] ResolveVs1CardIds(CanonicalCardDatabasePackage cardDatabase)
    {
        var deckIds = new HashSet<string>(StringComparer.Ordinal)
        {
            "DECK-IGN-HAM-VS1-001",
            "DECK-AQU-MOR-VS1-001",
        };
        if (!cardDatabase.Tables.TryGetValue("decks", out var decks)
            || !cardDatabase.Tables.TryGetValue("deck_entries", out var entries))
        {
            throw new EngineInputException(
                "CANONICAL_VS1_MEMBERSHIP_TABLE_MISSING",
                "VS1 membership requires canonical DECKS and DECK_ENTRIES tables.");
        }

        var activeDeckIds = decks.Records
            .Where(record => string.Equals(record.GetRequiredString("status"), "active", StringComparison.Ordinal))
            .Select(record => record.GetRequiredString("deck_id"))
            .Where(deckIds.Contains)
            .ToHashSet(StringComparer.Ordinal);
        if (activeDeckIds.Count != deckIds.Count)
        {
            throw new EngineInputException(
                "CANONICAL_VS1_DECK_MISSING",
                "Both fixed VS1 decks must be active for runtime coverage audit.");
        }

        return entries.Records
            .Where(record => string.Equals(record.GetRequiredString("status"), "active", StringComparison.Ordinal)
                && activeDeckIds.Contains(record.GetRequiredString("deck_id")))
            .Select(record => record.GetRequiredString("card_id"))
            .Distinct(StringComparer.Ordinal)
            .OrderBy(cardId => cardId, StringComparer.Ordinal)
            .ToArray();
    }

    private static CanonicalMaterializationSmokeRequest Parse(IReadOnlyList<string> arguments)
    {
        string? packageRoot = null;
        var validationMode = CanonicalPackageValidationMode.Development;
        for (var index = 0; index < arguments.Count; index += 1)
        {
            var argument = arguments[index];
            if (string.Equals(argument, "--package-root", StringComparison.Ordinal))
            {
                packageRoot = ReadValue(arguments, ref index, argument, packageRoot is null);
            }
            else if (string.Equals(argument, "--validation-mode", StringComparison.Ordinal))
            {
                var value = ReadValue(arguments, ref index, argument, true);
                validationMode = value switch
                {
                    "development" => CanonicalPackageValidationMode.Development,
                    "production" => CanonicalPackageValidationMode.Production,
                    _ => throw InvalidArguments("--validation-mode must be development or production."),
                };
            }
            else if (!argument.StartsWith("-", StringComparison.Ordinal) && packageRoot is null)
            {
                packageRoot = argument;
            }
            else
            {
                throw InvalidArguments($"Unknown or duplicate argument: {argument}");
            }
        }

        if (string.IsNullOrWhiteSpace(packageRoot))
        {
            throw InvalidArguments("Canonical package root is required.");
        }

        return new CanonicalMaterializationSmokeRequest(packageRoot, validationMode);
    }

    private static string ReadValue(
        IReadOnlyList<string> arguments,
        ref int index,
        string option,
        bool allowed)
    {
        if (!allowed
            || index + 1 >= arguments.Count
            || string.IsNullOrWhiteSpace(arguments[index + 1])
            || arguments[index + 1].StartsWith("--", StringComparison.Ordinal))
        {
            throw InvalidArguments($"Missing or duplicate value for {option}.");
        }

        index += 1;
        return arguments[index];
    }

    private static void WriteSummary(TextWriter writer, object summary) =>
        writer.WriteLine(OutputPrefix + JsonSerializer.Serialize(summary));

    private static EngineInputException InvalidArguments(string message) =>
        new("CANONICAL_MATERIALIZATION_ARGUMENT_INVALID", message);

    private sealed record CanonicalMaterializationSmokeRequest(
        string PackageRoot,
        CanonicalPackageValidationMode ValidationMode);
}
