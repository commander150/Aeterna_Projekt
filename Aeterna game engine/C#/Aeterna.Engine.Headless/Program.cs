using System.Text.Json.Nodes;
using Aeterna.Engine.Headless;
using Aeterna.Engine.Serialization;

try
{
    var fixturePath = GetOption(args, "--fixture") ?? FixtureLocator.LocateCanonicalFixture();
    var iterations = ParseIterations(GetOption(args, "--iterations"));
    RuntimeComparisonRunResult? first = null;
    var deterministic = true;
    for (var index = 0; index < iterations; index++)
    {
        var current = RuntimeComparisonFixtureRunner.Run(fixturePath);
        first ??= current;
        deterministic &= current.Sha256 == first.Sha256
            && current.CanonicalBytes.AsSpan().SequenceEqual(first.CanonicalBytes);
    }

    var result = first ?? throw new InvalidOperationException("No production engine run completed.");
    var summary = RuntimeComparisonFixtureRunner.BuildProofSummary(result, iterations, deterministic);
    Console.Out.WriteLine(CanonicalJson.Compact(summary));
    return summary["ok"]!.GetValue<bool>() ? 0 : 1;
}
catch (Exception exception)
{
    var code = exception switch
    {
        RuntimeComparisonFixtureException fixtureException => fixtureException.Code,
        RuntimeComparisonRunException runException => runException.Code,
        _ => "CSHARP_PRODUCTION_HEADLESS_FAILED",
    };
    var summary = new JsonObject
    {
        ["ok"] = false,
        ["schema_version"] = "aeterna-csharp-production-headless-proof-v1",
        ["actual_sha256"] = null,
        ["expected_sha256"] = RuntimeComparisonFixtureRunner.ExpectedCanonicalSha256,
        ["sha_match"] = false,
        ["error_code"] = code,
        ["error"] = exception.Message,
    };
    Console.Out.WriteLine(CanonicalJson.Compact(summary));
    return 1;
}

static int ParseIterations(string? value)
{
    if (value is null)
    {
        return 1;
    }

    if (!int.TryParse(value, out var iterations) || iterations < 1 || iterations > 10_000)
    {
        throw new ArgumentException("--iterations must be an integer from 1 through 10000.");
    }

    return iterations;
}

static string? GetOption(IReadOnlyList<string> arguments, string option)
{
    for (var index = 0; index < arguments.Count; index++)
    {
        if (!string.Equals(arguments[index], option, StringComparison.Ordinal))
        {
            continue;
        }

        if (index + 1 >= arguments.Count || arguments[index + 1].StartsWith("--", StringComparison.Ordinal))
        {
            throw new ArgumentException($"Missing value for {option}.");
        }

        return arguments[index + 1];
    }

    return null;
}
