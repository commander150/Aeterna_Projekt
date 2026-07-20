using System.Text.Json.Nodes;

namespace Aeterna.RuntimeCandidate;

public sealed class RuntimeCandidateResult
{
    internal RuntimeCandidateResult(
        string fixtureId,
        JsonObject result,
        byte[] canonicalBytes,
        string sha256)
    {
        FixtureId = fixtureId;
        Result = result;
        CanonicalBytes = canonicalBytes;
        Sha256 = sha256;
    }

    public string FixtureId { get; }

    public JsonObject Result { get; }

    public byte[] CanonicalBytes { get; }

    public string Sha256 { get; }

    public int CanonicalByteCount => CanonicalBytes.Length;
}
