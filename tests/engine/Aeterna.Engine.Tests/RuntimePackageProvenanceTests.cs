using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Nodes;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Runtime;

internal static class RuntimePackageProvenanceTests
{
    internal static void LegacyPackageWithoutProvenanceIsAccepted()
    {
        using var fixture = CanonicalFixture.Create(legacy: true);
        var catalog = RuntimePackageLoader.Load(new RuntimePackageSource(fixture.Directory, fixture.PackageId));
        Equal(null, catalog.Provenance, "Legacy runtime package unexpectedly acquired provenance.");
    }

    internal static void CanonicalPackageWithValidProvenanceIsAccepted()
    {
        using var fixture = CanonicalFixture.Create();
        var catalog = RuntimePackageLoader.Load(new RuntimePackageSource(fixture.Directory, fixture.PackageId));
        True(catalog.Provenance is not null, "Canonical runtime provenance was not exposed.");
        Equal(fixture.PackageId, catalog.Provenance!.RuntimePackageId, "Runtime provenance ID differs.");
        Equal("canonical-runtime-materializer", catalog.Provenance.MaterializerId, "Materializer ID differs.");
        True(catalog.Provenance.Readiness.MaterializationValid, "Materialization readiness was not exposed.");
        True(!catalog.Provenance.Readiness.ProductionReady, "Fixture unexpectedly became production-ready.");
        True(!catalog.Provenance.Readiness.PublishAllowed, "Fixture unexpectedly became publishable.");
    }

    internal static void CanonicalPackageWithoutProvenanceIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        File.Delete(Path.Combine(fixture.Directory, "provenance.json"));
        Rejects("RUNTIME_PACKAGE_PROVENANCE_MISSING", fixture);
    }

    internal static void RuntimePackageIdentityMismatchIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        fixture.MutateManifest(root => root["runtime_package_id"] = Sha('9'));
        Rejects("RUNTIME_PACKAGE_PROVENANCE_ID_MISMATCH", fixture);
    }

    internal static void CandidateIdentityMismatchIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        fixture.MutateProvenance(root => root["candidate_id"] = Sha('9'));
        Rejects("RUNTIME_PACKAGE_PROVENANCE_ID_MISMATCH", fixture);
    }

    internal static void PackageSetIdentityMismatchIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        fixture.MutateProvenance(root => root["package_set_id"] = Sha('9'));
        Rejects("RUNTIME_PACKAGE_PROVENANCE_ID_MISMATCH", fixture);
    }

    internal static void WrongMaterializerIdentityIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        fixture.MutateProvenance(root => root["materializer"]!["id"] = "other-materializer");
        Rejects("RUNTIME_PACKAGE_MATERIALIZER_CONTRACT_INVALID", fixture);
    }

    internal static void WrongMaterializationPolicyIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        fixture.MutateProvenance(root => root["materialization_policy_id"] = "other-policy");
        Rejects("RUNTIME_PACKAGE_MATERIALIZER_CONTRACT_INVALID", fixture);
    }

    internal static void MalformedHashIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        fixture.MutateProvenance(root => root["file_hashes"]!["cards.jsonl"] = "sha256:BAD");
        Rejects("RUNTIME_PACKAGE_HASH_INVALID", fixture);
    }

    internal static void PayloadTamperIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        File.AppendAllText(Path.Combine(fixture.Directory, "cards.jsonl"), "tamper");
        Rejects("RUNTIME_PACKAGE_HASH_MISMATCH", fixture);
    }

    internal static void MissingHashedFileIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        File.Delete(Path.Combine(fixture.Directory, "aliases.json"));
        Rejects("RUNTIME_PACKAGE_HASHED_FILE_MISSING", fixture);
    }

    internal static void UnsafeProvenancePathIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        fixture.MutateProvenance(root => root["file_hashes"]!["../escape.json"] = Sha('1'));
        Rejects("RUNTIME_PACKAGE_HASH_PATH_INVALID", fixture);
    }

    internal static void DuplicateManifestPathIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        fixture.MutateManifest(root => root["files"]!.AsArray().Add(
            new JsonObject { ["path"] = "cards.jsonl" }));
        Rejects("RUNTIME_PACKAGE_HASH_PATH_DUPLICATE", fixture);
    }

    internal static void ExpectedPackageIdentityMismatchIsRejected()
    {
        using var fixture = CanonicalFixture.Create();
        var exception = Throws(() => RuntimePackageLoader.Load(
            new RuntimePackageSource(fixture.Directory, Sha('9'))));
        Equal("RUNTIME_PACKAGE_ID_MISMATCH", exception.Code, "Expected package ID gate changed.");
    }

    private static void Rejects(string expectedCode, CanonicalFixture fixture)
    {
        var exception = Throws(() => RuntimePackageLoader.Load(
            new RuntimePackageSource(fixture.Directory, fixture.PackageId)));
        Equal(expectedCode, exception.Code, "Unexpected provenance diagnostic code.");
    }

    private static EngineInputException Throws(Action action)
    {
        try
        {
            action();
        }
        catch (EngineInputException exception)
        {
            return exception;
        }

        throw new InvalidOperationException("Expected EngineInputException was not thrown.");
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

    private static string Sha(char character) => "sha256:" + new string(character, 64);

    private sealed class CanonicalFixture : IDisposable
    {
        private const string MaterializerId = "canonical-runtime-materializer";
        private const string PolicyId = "canonical-runtime-materialization-policy-v1";
        private const string ProfileId = "runtime-package-source-compatible-v1";
        private const string FileHashScope = "all package files except self-referential provenance.json";

        private CanonicalFixture(string directory, string packageId)
        {
            Directory = directory;
            PackageId = packageId;
        }

        internal string Directory { get; }
        internal string PackageId { get; }

        internal static CanonicalFixture Create(bool legacy = false)
        {
            var directory = Path.Combine(Path.GetTempPath(), "aeterna-runtime-provenance-tests", Guid.NewGuid().ToString("N"));
            System.IO.Directory.CreateDirectory(directory);
            var packageId = legacy ? "legacy-runtime-package" : Sha('1');
            File.WriteAllText(Path.Combine(directory, "cards.jsonl"),
                "{\"card_id\":\"CARD-1\",\"magnitude\":1,\"aura_cost\":1,\"realm\":\"aqua\",\"card_type\":\"entity\"}\n");
            File.WriteAllText(Path.Combine(directory, "decks.jsonl"),
                "{\"deck_id\":\"DECK-1\",\"card_entries\":[{\"card_id\":\"CARD-1\",\"count\":1}]}\n");
            File.WriteAllText(Path.Combine(directory, "lookups.json"),
                "{\"lookups\":[{\"lookup_group\":\"realm\",\"value\":\"aqua\",\"status\":\"active\",\"canonical_value\":\"aqua\"},{\"lookup_group\":\"card_type\",\"value\":\"entity\",\"status\":\"active\",\"canonical_value\":\"entity\"}]}");
            File.WriteAllText(Path.Combine(directory, "aliases.json"), "{}\n");

            if (legacy)
            {
                WriteJson(Path.Combine(directory, "manifest.json"), new Dictionary<string, object?>
                {
                    ["package_id"] = packageId,
                });
                return new CanonicalFixture(directory, packageId);
            }

            var identityPayloadPaths = new[] { "aliases.json", "cards.jsonl", "decks.jsonl", "lookups.json" };
            var identityPayloadHashes = identityPayloadPaths.ToDictionary(
                path => path,
                path => Hash(Path.Combine(directory, path)),
                StringComparer.Ordinal);
            var readiness = new Dictionary<string, object?>
            {
                ["materialization_valid"] = true,
                ["production_ready"] = false,
                ["publish_allowed"] = false,
            };
            var candidateId = Sha('2');
            var packageSetId = Sha('3');
            var cardDatabaseIdentity = Sha('4');
            var registryIdentity = Sha('5');
            var manifest = new Dictionary<string, object?>
            {
                ["build_profile"] = ProfileId,
                ["files"] = new object[]
                {
                    new Dictionary<string, object?> { ["path"] = "manifest.json" },
                    new Dictionary<string, object?> { ["path"] = "cards.jsonl" },
                    new Dictionary<string, object?> { ["path"] = "decks.jsonl" },
                    new Dictionary<string, object?> { ["path"] = "lookups.json" },
                    new Dictionary<string, object?> { ["path"] = "aliases.json" },
                    new Dictionary<string, object?> { ["path"] = "provenance.json" },
                },
                ["identity_payload_file_hashes"] = identityPayloadHashes,
                ["metadata"] = new Dictionary<string, object?>
                {
                    ["generator"] = MaterializerId,
                    ["materialization_policy_id"] = PolicyId,
                },
                ["package_id"] = packageId,
                ["readiness"] = readiness,
                ["runtime_package_id"] = packageId,
                ["source_components"] = new object[]
                {
                    new Dictionary<string, object?>
                    {
                        ["component_kind"] = "CARDDATABASE",
                        ["component_identity"] = cardDatabaseIdentity,
                    },
                    new Dictionary<string, object?>
                    {
                        ["component_kind"] = "REGISTRY",
                        ["component_identity"] = registryIdentity,
                    },
                },
                ["source_identity"] = new Dictionary<string, object?>
                {
                    ["candidate_id"] = candidateId,
                    ["package_set_id"] = packageSetId,
                },
            };
            WriteJson(Path.Combine(directory, "manifest.json"), manifest);
            var fileHashes = identityPayloadHashes.ToDictionary(pair => pair.Key, pair => pair.Value, StringComparer.Ordinal);
            fileHashes.Add("manifest.json", Hash(Path.Combine(directory, "manifest.json")));
            var provenance = new Dictionary<string, object?>
            {
                ["candidate_id"] = candidateId,
                ["file_hash_scope"] = FileHashScope,
                ["file_hashes"] = fileHashes,
                ["identity_payload_file_hashes"] = identityPayloadHashes,
                ["materialization_policy_id"] = PolicyId,
                ["materialization_profile_id"] = ProfileId,
                ["materializer"] = new Dictionary<string, object?>
                {
                    ["contract_version"] = "1",
                    ["id"] = MaterializerId,
                },
                ["package_set_id"] = packageSetId,
                ["read_audit"] = new Dictionary<string, object?>
                {
                    ["candidate_only"] = true,
                    ["legacy_source_read_count"] = 0,
                },
                ["readiness"] = readiness,
                ["runtime_package_id"] = packageId,
                ["source_components"] = new Dictionary<string, object?>
                {
                    ["CARDDATABASE"] = new Dictionary<string, object?>
                    {
                        ["component_identity"] = cardDatabaseIdentity,
                        ["content_hash"] = Sha('6'),
                    },
                    ["REGISTRY"] = new Dictionary<string, object?>
                    {
                        ["component_identity"] = registryIdentity,
                        ["content_hash"] = Sha('7'),
                    },
                },
            };
            WriteJson(Path.Combine(directory, "provenance.json"), provenance);
            return new CanonicalFixture(directory, packageId);
        }

        internal void MutateManifest(Action<JsonObject> mutation) => Mutate("manifest.json", mutation);
        internal void MutateProvenance(Action<JsonObject> mutation) => Mutate("provenance.json", mutation);

        public void Dispose()
        {
            if (System.IO.Directory.Exists(Directory))
            {
                System.IO.Directory.Delete(Directory, recursive: true);
            }
        }

        private void Mutate(string fileName, Action<JsonObject> mutation)
        {
            var path = Path.Combine(Directory, fileName);
            var root = JsonNode.Parse(File.ReadAllText(path))!.AsObject();
            mutation(root);
            File.WriteAllText(path, root.ToJsonString());
        }

        private static void WriteJson(string path, object value) =>
            File.WriteAllText(path, JsonSerializer.Serialize(value));

        private static string Hash(string path) =>
            "sha256:" + Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();
    }
}
