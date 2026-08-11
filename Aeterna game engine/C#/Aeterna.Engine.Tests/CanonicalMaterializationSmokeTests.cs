using System.Text.Json;
using Aeterna.Engine.Runtime;

internal static class CanonicalMaterializationSmokeTests
{
    internal static void EntryPointContractsAreControlledAndDiagnostic()
    {
        var success = Run((_, _) => new CanonicalMaterializationSmokeSuccess(
            "aeterna_registry",
            "0.5.1",
            "0.16.7",
            "aeterna_carddatabase",
            "0.7.0",
            "0.19.2",
            814,
            26,
            Enumerable.Range(1, 32).Select(index => $"CARD-{index:000}").ToArray(),
            Enumerable.Range(1, 19).Select(index => $"CARD-{index:000}").ToArray(),
            Enumerable.Range(1, 13).Select(index => $"CARD-{index:000}").ToArray()));
        Equal(CanonicalMaterializationSmoke.SuccessExitCode, success.ExitCode, "Positive smoke exit code is invalid.");
        Equal("success", success.Summary.GetProperty("status").GetString(), "Positive smoke status is invalid.");
        Equal(814, success.Summary.GetProperty("cards").GetInt32(), "Positive smoke card count is invalid.");
        Equal(26, success.Summary.GetProperty("abilities").GetInt32(), "Positive smoke ability count is invalid.");
        Equal(32, success.Summary.GetProperty("vs1").GetProperty("unique_card_count").GetInt32(), "Positive smoke VS1 membership count is invalid.");
        Equal(13, success.Summary.GetProperty("vs1").GetProperty("ability_runtime_executable_count").GetInt32(), "Positive smoke VS1 executable count is invalid.");
        Equal(string.Empty, success.StandardError, "Positive smoke wrote unexpected stderr.");

        var controlled = Run((_, _) => throw new EngineInputException(
            "CANONICAL_TBD_FORBIDDEN",
            "#TBD is forbidden in production materialization."));
        Equal(CanonicalMaterializationSmoke.ControlledRejectionExitCode, controlled.ExitCode, "Controlled rejection exit code is invalid.");
        Equal("blocked", controlled.Summary.GetProperty("status").GetString(), "Controlled rejection status is invalid.");
        Equal("CANONICAL_TBD_FORBIDDEN", controlled.Summary.GetProperty("diagnostic_code").GetString(), "Controlled diagnostic code is invalid.");
        Equal(string.Empty, controlled.StandardError, "Controlled rejection wrote unexpected stderr.");

        var unexpected = Run((_, _) => throw new InvalidOperationException(
            "outer failure",
            new FormatException("inner failure")));
        Equal(CanonicalMaterializationSmoke.UnexpectedFailureExitCode, unexpected.ExitCode, "Unexpected failure exit code is invalid.");
        Equal("failed", unexpected.Summary.GetProperty("status").GetString(), "Unexpected failure status is invalid.");
        Equal("CANONICAL_MATERIALIZATION_UNEXPECTED", unexpected.Summary.GetProperty("diagnostic_code").GetString(), "Unexpected diagnostic code is invalid.");
        True(unexpected.StandardError.Contains("InvalidOperationException: outer failure", StringComparison.Ordinal), "Unexpected exception type/message is absent from stderr.");
        True(unexpected.StandardError.Contains("FormatException: inner failure", StringComparison.Ordinal), "Unexpected inner exception is absent from stderr.");
        True(unexpected.StandardError.Contains(nameof(EntryPointContractsAreControlledAndDiagnostic), StringComparison.Ordinal), "Unexpected managed stack trace is absent from stderr.");
    }

    private static SmokeInvocation Run(
        Func<string, CanonicalPackageValidationMode, CanonicalMaterializationSmokeSuccess> materialize)
    {
        using var output = new StringWriter();
        using var error = new StringWriter();
        var exitCode = CanonicalMaterializationSmoke.Run(
            ["--package-root", "fixture", "--validation-mode", "development"],
            output,
            error,
            materialize);
        var line = output.ToString().Trim();
        True(line.StartsWith(CanonicalMaterializationSmoke.OutputPrefix, StringComparison.Ordinal), "Smoke output prefix is missing.");
        var json = line[CanonicalMaterializationSmoke.OutputPrefix.Length..];
        return new SmokeInvocation(
            exitCode,
            JsonDocument.Parse(json).RootElement.Clone(),
            error.ToString());
    }

    private static void True(bool condition, string message)
    {
        if (!condition)
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected={expected}; Actual={actual}");
        }
    }

    private sealed record SmokeInvocation(
        int ExitCode,
        JsonElement Summary,
        string StandardError);
}
