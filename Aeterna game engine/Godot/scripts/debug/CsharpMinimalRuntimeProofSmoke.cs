using Aeterna.GodotRuntime.RuntimeComparison;
using Aeterna.RuntimeCandidate;
using Godot;

namespace Aeterna.GodotRuntime.DebugProof;

public partial class CsharpMinimalRuntimeProofSmoke : Node
{
    public override void _Ready()
    {
        var exitCode = 1;
        try
        {
            var proof = CsharpRuntimeCandidateBridge.Run();
            var summary = CsharpRuntimeCandidateBridge.BuildSummary(proof);
            GD.Print(CsharpRuntimeCandidateBridge.HeadlessProofPrefix + CanonicalJson.Compact(summary));
            exitCode = proof.ShaMatch ? 0 : 1;
        }
        catch (Exception exception)
        {
            var summary = new System.Text.Json.Nodes.JsonObject
            {
                ["ok"] = false,
                ["schema_version"] = "aeterna-godot-csharp-minimal-proof-v1",
                ["direct_in_process"] = true,
                ["separate_engine_process"] = false,
                ["python_process_started"] = false,
                ["tcp_listener_used"] = false,
                ["final_result"] = "FAIL",
                ["error_code"] = exception is RuntimeCandidateException runtimeException
                    ? runtimeException.Code
                    : "GODOT_CSHARP_PROOF_FAILED",
                ["error"] = exception.Message,
            };
            GD.Print(CsharpRuntimeCandidateBridge.HeadlessProofPrefix + CanonicalJson.Compact(summary));
        }

        GetTree().Quit(exitCode);
    }
}
