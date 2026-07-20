using System.Diagnostics;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text.Json.Nodes;
using Aeterna.RuntimeCandidate;

const string prefix = "AETERNA_CSHARP_MINIMAL_PROOF ";
var stopwatch = Stopwatch.StartNew();
var fixturePath = GetOption(args, "--fixture") ?? LocateCanonicalFixture();
var outputPath = GetOption(args, "--canonical-output");
var iterations = ParseIterations(GetOption(args, "--iterations"));

try
{
    RuntimeCandidateResult? firstResult = null;
    var deterministic = true;
    for (var index = 0; index < iterations; index++)
    {
        var current = MinimalRuntimeCandidate.Run(fixturePath);
        firstResult ??= current;
        deterministic &= current.Sha256 == firstResult.Sha256
            && current.CanonicalBytes.AsSpan().SequenceEqual(firstResult.CanonicalBytes);
    }

    var result = firstResult ?? throw new InvalidOperationException("No candidate run completed.");
    if (outputPath is not null)
    {
        var fullOutputPath = Path.GetFullPath(outputPath);
        Directory.CreateDirectory(Path.GetDirectoryName(fullOutputPath)!);
        File.WriteAllBytes(fullOutputPath, result.CanonicalBytes);
    }

    var shaMatch = result.Sha256 == MinimalRuntimeCandidate.ExpectedCanonicalSha256;
    stopwatch.Stop();
    var summary = BuildSummary(
        ok: shaMatch && deterministic,
        result.FixtureId,
        result.CanonicalByteCount,
        result.Sha256,
        iterations,
        deterministic,
        stopwatch.ElapsedMilliseconds,
        errorCode: shaMatch ? null : "CANONICAL_SHA_MISMATCH",
        error: shaMatch ? null : "Calculated canonical SHA does not match the comparison oracle.");
    Console.Out.WriteLine(prefix + CanonicalJson.Compact(summary));
    return shaMatch && deterministic ? 0 : 1;
}
catch (Exception exception)
{
    stopwatch.Stop();
    var errorCode = exception is RuntimeCandidateException runtimeException
        ? runtimeException.Code
        : "CSHARP_PROOF_FAILED";
    var summary = BuildSummary(
        ok: false,
        fixtureId: null,
        canonicalResultBytes: 0,
        actualSha256: null,
        iterations,
        deterministic: false,
        stopwatch.ElapsedMilliseconds,
        errorCode,
        exception.Message);
    Console.Out.WriteLine(prefix + CanonicalJson.Compact(summary));
    return 1;
}

static JsonObject BuildSummary(
    bool ok,
    string? fixtureId,
    int canonicalResultBytes,
    string? actualSha256,
    int deterministicRuns,
    bool deterministic,
    long elapsedMs,
    string? errorCode,
    string? error) => new()
{
    ["ok"] = ok,
    ["schema_version"] = "aeterna-csharp-minimal-proof-v1",
    ["fixture_id"] = fixtureId,
    ["target_framework"] = "net8.0",
    ["runtime_version"] = Environment.Version.ToString(),
    ["architecture"] = RuntimeInformation.ProcessArchitecture.ToString().ToLowerInvariant(),
    ["direct_in_process"] = true,
    ["separate_engine_process"] = false,
    ["python_process_started"] = false,
    ["tcp_listener_used"] = false,
    ["canonical_result_bytes"] = canonicalResultBytes,
    ["actual_sha256"] = actualSha256,
    ["expected_sha256"] = MinimalRuntimeCandidate.ExpectedCanonicalSha256,
    ["sha_match"] = actualSha256 == MinimalRuntimeCandidate.ExpectedCanonicalSha256,
    ["deterministic_runs"] = deterministicRuns,
    ["deterministic"] = deterministic,
    ["elapsed_ms"] = elapsedMs,
    ["assembly_version"] = Assembly.GetExecutingAssembly().GetName().Version?.ToString(),
    ["error_code"] = errorCode,
    ["error"] = error,
};

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

static string LocateCanonicalFixture()
{
    const string relativePath =
        "runtime_comparison/fixtures/minimal_draw_end_turn_v1/fixture.json";
    foreach (var start in new[] { Directory.GetCurrentDirectory(), AppContext.BaseDirectory })
    {
        var directory = new DirectoryInfo(Path.GetFullPath(start));
        while (directory is not null)
        {
            var direct = Path.Combine(directory.FullName, relativePath);
            if (File.Exists(direct))
            {
                return direct;
            }

            var underEngine = Path.Combine(directory.FullName, "Aeterna game engine", relativePath);
            if (File.Exists(underEngine))
            {
                return underEngine;
            }

            directory = directory.Parent;
        }
    }

    throw new FileNotFoundException("Canonical minimal runtime comparison fixture could not be located.");
}
