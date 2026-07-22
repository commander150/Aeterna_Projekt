using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text.Json.Nodes;
using Aeterna.RuntimeCandidate;
using Godot;

namespace Aeterna.GodotRuntime.RuntimeComparison;

public static class CsharpRuntimeCandidateBridge
{
    public const string HeadlessProofPrefix = "AETERNA_GODOT_CSHARP_MINIMAL_PROOF ";
    public const string VisualProofPrefix = "AETERNA_GODOT_CSHARP_VISUAL_PROOF ";

    public static GodotProofResult Run()
    {
        var stopwatch = Stopwatch.StartNew();
        var fixturePath = ResolveFixturePath();
        var candidate = MinimalRuntimeCandidate.Run(fixturePath);
        stopwatch.Stop();
        return new GodotProofResult(candidate, stopwatch.ElapsedMilliseconds);
    }

    public static JsonObject BuildSummary(GodotProofResult proof, int runCount = 1) => new()
    {
        ["ok"] = proof.ShaMatch,
        ["schema_version"] = "aeterna-godot-csharp-minimal-proof-v1",
        ["fixture_id"] = proof.Candidate.FixtureId,
        ["godot_pid"] = System.Environment.ProcessId,
        ["managed_process_id"] = System.Environment.ProcessId,
        ["godot_version"] = Godot.Engine.GetVersionInfo()["string"].AsString(),
        ["dotnet_runtime"] = System.Environment.Version.ToString(),
        ["target_framework"] = "net8.0",
        ["architecture"] = RuntimeInformation.ProcessArchitecture.ToString().ToLowerInvariant(),
        ["direct_in_process"] = true,
        ["separate_engine_process"] = false,
        ["python_process_started"] = false,
        ["tcp_listener_used"] = false,
        ["canonical_result_bytes"] = proof.Candidate.CanonicalByteCount,
        ["actual_sha256"] = proof.Candidate.Sha256,
        ["expected_sha256"] = MinimalRuntimeCandidate.ExpectedCanonicalSha256,
        ["sha_match"] = proof.ShaMatch,
        ["run_count"] = runCount,
        ["elapsed_ms"] = proof.ElapsedMilliseconds,
        ["final_result"] = proof.ShaMatch ? "PASS" : "FAIL",
        ["error_code"] = proof.ShaMatch ? null : "CANONICAL_SHA_MISMATCH",
        ["error"] = proof.ShaMatch ? null : "Calculated canonical SHA does not match the comparison oracle.",
    };

    public static string ResolveFixturePath()
    {
        var godotProjectRoot = ProjectSettings.GlobalizePath("res://");
        var fixturePath = Path.GetFullPath(Path.Combine(
            godotProjectRoot,
            "..",
            "runtime_comparison",
            "fixtures",
            "minimal_draw_end_turn_v1",
            "fixture.json"));
        if (!File.Exists(fixturePath))
        {
            throw new FileNotFoundException(
                "Canonical minimal runtime comparison fixture was not found relative to res://.");
        }

        return fixturePath;
    }
}

public sealed record GodotProofResult(RuntimeCandidateResult Candidate, long ElapsedMilliseconds)
{
    public bool ShaMatch =>
        string.Equals(
            Candidate.Sha256,
            MinimalRuntimeCandidate.ExpectedCanonicalSha256,
            StringComparison.Ordinal);
}
