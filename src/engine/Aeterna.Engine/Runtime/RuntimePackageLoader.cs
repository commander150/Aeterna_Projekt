using System.Collections.Immutable;
using System.Security.Cryptography;
using System.Text.Json;
using Aeterna.Engine.Contracts;

namespace Aeterna.Engine.Runtime;

public sealed record RuntimeCardDefinition(
    string CardId,
    int Magnitude,
    int PrintedAuraCost,
    string Realm,
    string CardType);

public sealed record RuntimeDeckDefinition(
    string DeckId,
    ImmutableArray<string> OrderedCardIds);

public sealed record RuntimePackageReadiness(
    bool MaterializationValid,
    bool ProductionReady,
    bool PublishAllowed);

public sealed record RuntimeSourceComponentProvenance(
    string ComponentIdentity,
    string ContentHash);

public sealed record RuntimePackageProvenance(
    string RuntimePackageId,
    string CandidateId,
    string PackageSetId,
    string MaterializerId,
    string MaterializerContractVersion,
    string MaterializationProfileId,
    string MaterializationPolicyId,
    bool CandidateOnly,
    int LegacySourceReadCount,
    ImmutableDictionary<string, RuntimeSourceComponentProvenance> SourceComponents,
    RuntimePackageReadiness Readiness,
    ImmutableDictionary<string, string> FileHashes,
    ImmutableDictionary<string, string> IdentityPayloadFileHashes);

public sealed record RuntimePackageCatalog(
    string PackageId,
    ImmutableDictionary<string, RuntimeCardDefinition> Cards,
    ImmutableDictionary<string, RuntimeDeckDefinition> Decks,
    RuntimeLookupCatalog Lookups,
    RuntimePackageProvenance? Provenance = null);

public static class RuntimePackageLoader
{
    private const string CanonicalMaterializerId = "canonical-runtime-materializer";
    private const string CanonicalMaterializerContractVersion = "1";
    private const string CanonicalMaterializationPolicyId = "canonical-runtime-materialization-policy-v1";
    private const string CanonicalMaterializationProfileId = "runtime-package-source-compatible-v1";
    private const string CanonicalFileHashScope = "all package files except self-referential provenance.json";

    private static readonly string[] RequiredFiles =
    [
        "manifest.json",
        "cards.jsonl",
        "decks.jsonl",
        "lookups.json",
    ];

    private static readonly string[] RequiredLookupGroups =
    [
        "realm",
        "card_type",
    ];

    public static RuntimePackageCatalog Load(RuntimePackageSource? source)
    {
        if (source is null)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_SOURCE_MISSING",
                "Runtime package source is missing.");
        }

        if (string.IsNullOrWhiteSpace(source.PackageDirectory))
        {
            throw new EngineInputException("RUNTIME_PACKAGE_PATH_INVALID", "Runtime package directory is empty.");
        }

        var packageDirectory = Path.GetFullPath(source.PackageDirectory);
        if (!Directory.Exists(packageDirectory))
        {
            throw new EngineInputException("RUNTIME_PACKAGE_NOT_FOUND", "Runtime package directory was not found.");
        }

        foreach (var fileName in RequiredFiles)
        {
            if (!File.Exists(Path.Combine(packageDirectory, fileName)))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_FILE_MISSING",
                    $"Runtime package file is missing: {fileName}");
            }
        }

        using var manifest = ParseJsonFile(Path.Combine(packageDirectory, "manifest.json"));
        RequireObject(manifest.RootElement, "Runtime package manifest must be an object.");
        var packageId = ReadRequiredString(manifest.RootElement, "package_id");
        if (source.ExpectedPackageId is not null
            && !string.Equals(source.ExpectedPackageId, packageId, StringComparison.Ordinal))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_ID_MISMATCH",
                "Runtime package ID does not match the requested package.");
        }

        var provenance = IsCanonicalDerived(manifest.RootElement)
            ? ReadAndValidateCanonicalProvenance(packageDirectory, manifest.RootElement, packageId)
            : null;

        var runtimeLookups = ReadRuntimeLookupCatalog(Path.Combine(packageDirectory, "lookups.json"));
        var cards = ImmutableDictionary.CreateBuilder<string, RuntimeCardDefinition>(StringComparer.Ordinal);
        foreach (var card in ReadJsonLines(Path.Combine(packageDirectory, "cards.jsonl")))
        {
            var cardId = ReadRequiredString(card, "card_id");
            var magnitude = ReadRequiredMagnitude(card);
            var printedAuraCost = ReadRequiredAuraCost(card);
            var realm = ReadAndResolveCardLookup(
                card,
                propertyName: "realm",
                lookupGroup: "realm",
                errorCode: "RUNTIME_PACKAGE_CARD_REALM_INVALID",
                runtimeLookups);
            var cardType = ReadAndResolveCardLookup(
                card,
                propertyName: "card_type",
                lookupGroup: "card_type",
                errorCode: "RUNTIME_PACKAGE_CARD_TYPE_INVALID",
                runtimeLookups);
            var definition = new RuntimeCardDefinition(
                cardId,
                magnitude,
                printedAuraCost,
                realm,
                cardType);
            if (!cards.TryAdd(cardId, definition))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_DUPLICATE_CARD",
                    "Runtime package contains a duplicate card_id.");
            }
        }

        if (cards.Count == 0)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_EMPTY_CARDS",
                "Runtime package card registry is empty.");
        }

        var decks = ImmutableDictionary.CreateBuilder<string, RuntimeDeckDefinition>(StringComparer.Ordinal);
        foreach (var deck in ReadJsonLines(Path.Combine(packageDirectory, "decks.jsonl")))
        {
            var deckId = ReadRequiredString(deck, "deck_id");
            var cardEntries = ReadRequiredArray(deck, "card_entries");
            var orderedCardIds = ImmutableArray.CreateBuilder<string>();
            foreach (var entry in cardEntries.EnumerateArray())
            {
                RequireObject(entry, "Deck card entry must be an object.");
                var cardId = ReadRequiredString(entry, "card_id");
                var count = ReadRequiredInt(entry, "count");
                if (count <= 0)
                {
                    throw new EngineInputException(
                        "RUNTIME_PACKAGE_DECK_COUNT_INVALID",
                        "Deck entry count must be positive.");
                }

                if (!cards.ContainsKey(cardId))
                {
                    throw new EngineInputException(
                        "RUNTIME_PACKAGE_UNKNOWN_CARD",
                        "Deck references an unknown card_id.");
                }

                for (var index = 0; index < count; index++)
                {
                    orderedCardIds.Add(cardId);
                }
            }

            if (!decks.TryAdd(deckId, new RuntimeDeckDefinition(deckId, orderedCardIds.ToImmutable())))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_DUPLICATE_DECK",
                    "Runtime package contains a duplicate deck_id.");
            }
        }

        var catalog = new RuntimePackageCatalog(
            packageId,
            cards.ToImmutable(),
            decks.ToImmutable(),
            runtimeLookups,
            provenance);
        ValidateCatalog(catalog);
        return catalog;
    }

    private static bool IsCanonicalDerived(JsonElement manifest)
    {
        if (manifest.TryGetProperty("metadata", out var metadata)
            && metadata.ValueKind == JsonValueKind.Object
            && metadata.TryGetProperty("generator", out var generator)
            && generator.ValueKind == JsonValueKind.String
            && string.Equals(generator.GetString(), CanonicalMaterializerId, StringComparison.Ordinal))
        {
            return true;
        }

        return manifest.TryGetProperty("runtime_package_id", out _)
            || manifest.TryGetProperty("source_identity", out _)
            || manifest.TryGetProperty("source_components", out _)
            || manifest.TryGetProperty("identity_payload_file_hashes", out _)
            || manifest.TryGetProperty("build_profile", out _)
            || (manifest.TryGetProperty("metadata", out metadata)
                && metadata.ValueKind == JsonValueKind.Object
                && metadata.TryGetProperty("materialization_policy_id", out _));
    }

    private static RuntimePackageProvenance ReadAndValidateCanonicalProvenance(
        string packageDirectory,
        JsonElement manifest,
        string packageId)
    {
        var provenancePath = Path.Combine(packageDirectory, "provenance.json");
        if (!File.Exists(provenancePath))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_MISSING",
                "Canonical-derived runtime package provenance is missing.");
        }

        using var provenanceDocument = ParseJsonFile(provenancePath);
        var provenance = provenanceDocument.RootElement;
        RequireProvenanceObject(provenance, "Canonical runtime provenance must be an object.");

        var manifestRuntimeId = ReadProvenanceString(manifest, "runtime_package_id");
        var provenanceRuntimeId = ReadProvenanceString(provenance, "runtime_package_id");
        var manifestSourceIdentity = ReadProvenanceObject(manifest, "source_identity");
        var manifestCandidateId = ReadProvenanceString(manifestSourceIdentity, "candidate_id");
        var manifestPackageSetId = ReadProvenanceString(manifestSourceIdentity, "package_set_id");
        var provenanceCandidateId = ReadProvenanceString(provenance, "candidate_id");
        var provenancePackageSetId = ReadProvenanceString(provenance, "package_set_id");

        foreach (var identity in new[]
                 {
                     packageId,
                     manifestRuntimeId,
                     provenanceRuntimeId,
                     manifestCandidateId,
                     manifestPackageSetId,
                     provenanceCandidateId,
                     provenancePackageSetId,
                 })
        {
            RequireSha256Identity(identity);
        }

        if (!string.Equals(packageId, manifestRuntimeId, StringComparison.Ordinal)
            || !string.Equals(packageId, provenanceRuntimeId, StringComparison.Ordinal)
            || !string.Equals(manifestCandidateId, provenanceCandidateId, StringComparison.Ordinal)
            || !string.Equals(manifestPackageSetId, provenancePackageSetId, StringComparison.Ordinal))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_ID_MISMATCH",
                "Canonical runtime manifest and provenance identities do not agree.");
        }

        var metadata = ReadProvenanceObject(manifest, "metadata");
        var manifestGenerator = ReadProvenanceString(metadata, "generator");
        var manifestPolicy = ReadProvenanceString(metadata, "materialization_policy_id");
        var manifestProfile = ReadProvenanceString(manifest, "build_profile");
        var materializer = ReadProvenanceObject(provenance, "materializer");
        var materializerId = ReadProvenanceString(materializer, "id");
        var materializerContractVersion = ReadProvenanceString(materializer, "contract_version");
        var provenancePolicy = ReadProvenanceString(provenance, "materialization_policy_id");
        var provenanceProfile = ReadProvenanceString(provenance, "materialization_profile_id");
        if (!string.Equals(manifestGenerator, CanonicalMaterializerId, StringComparison.Ordinal)
            || !string.Equals(materializerId, CanonicalMaterializerId, StringComparison.Ordinal)
            || !string.Equals(materializerContractVersion, CanonicalMaterializerContractVersion, StringComparison.Ordinal)
            || !string.Equals(manifestPolicy, CanonicalMaterializationPolicyId, StringComparison.Ordinal)
            || !string.Equals(provenancePolicy, CanonicalMaterializationPolicyId, StringComparison.Ordinal)
            || !string.Equals(manifestProfile, CanonicalMaterializationProfileId, StringComparison.Ordinal)
            || !string.Equals(provenanceProfile, CanonicalMaterializationProfileId, StringComparison.Ordinal))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_MATERIALIZER_CONTRACT_INVALID",
                "Canonical runtime materializer contract is invalid or inconsistent.");
        }

        var readAudit = ReadProvenanceObject(provenance, "read_audit");
        var candidateOnly = ReadProvenanceBool(readAudit, "candidate_only");
        var legacySourceReadCount = ReadProvenanceInt(readAudit, "legacy_source_read_count");
        if (!candidateOnly || legacySourceReadCount != 0)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                "Canonical runtime provenance does not prove candidate-only materialization.");
        }

        var manifestReadiness = ReadReadiness(ReadProvenanceObject(manifest, "readiness"));
        var provenanceReadiness = ReadReadiness(ReadProvenanceObject(provenance, "readiness"));
        if (manifestReadiness != provenanceReadiness || !provenanceReadiness.MaterializationValid)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                "Canonical runtime readiness differs between manifest and provenance.");
        }

        var sourceComponents = ReadAndValidateSourceComponents(manifest, provenance);
        var manifestFiles = ReadManifestFiles(manifest);
        var fileHashes = ReadHashMap(provenance, "file_hashes");
        var manifestIdentityHashes = ReadHashMap(manifest, "identity_payload_file_hashes");
        var provenanceIdentityHashes = ReadHashMap(provenance, "identity_payload_file_hashes");
        if (!string.Equals(
                ReadProvenanceString(provenance, "file_hash_scope"),
                CanonicalFileHashScope,
                StringComparison.Ordinal))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_HASH_SET_INVALID",
                "Canonical runtime provenance uses an unsupported file hash scope.");
        }

        var expectedHashedFiles = manifestFiles
            .Where(path => !string.Equals(path, "provenance.json", StringComparison.Ordinal))
            .ToHashSet(StringComparer.Ordinal);
        if (!expectedHashedFiles.SetEquals(fileHashes.Keys)
            || !HashMapsEqual(manifestIdentityHashes, provenanceIdentityHashes)
            || manifestIdentityHashes.Any(pair =>
                !fileHashes.TryGetValue(pair.Key, out var fileHash)
                || !string.Equals(pair.Value, fileHash, StringComparison.Ordinal)))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_HASH_SET_INVALID",
                "Canonical runtime hash declarations do not match the manifest contract.");
        }

        foreach (var (relativePath, expectedHash) in fileHashes)
        {
            var fullPath = ResolveSafePackagePath(packageDirectory, relativePath);
            if (!File.Exists(fullPath))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_HASHED_FILE_MISSING",
                    "A canonical runtime hashed file is missing.");
            }

            string actualHash;
            try
            {
                actualHash = "sha256:" + Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(fullPath))).ToLowerInvariant();
            }
            catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_HASHED_FILE_MISSING",
                    "A canonical runtime hashed file could not be read.",
                    exception);
            }
            if (!string.Equals(actualHash, expectedHash, StringComparison.Ordinal))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_HASH_MISMATCH",
                    "A canonical runtime file hash does not match its provenance declaration.");
            }
        }

        return new RuntimePackageProvenance(
            provenanceRuntimeId,
            provenanceCandidateId,
            provenancePackageSetId,
            materializerId,
            materializerContractVersion,
            provenanceProfile,
            provenancePolicy,
            candidateOnly,
            legacySourceReadCount,
            sourceComponents,
            provenanceReadiness,
            fileHashes,
            provenanceIdentityHashes);
    }

    private static ImmutableDictionary<string, RuntimeSourceComponentProvenance> ReadAndValidateSourceComponents(
        JsonElement manifest,
        JsonElement provenance)
    {
        var manifestComponents = ReadProvenanceArray(manifest, "source_components");
        var manifestIdentities = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var component in manifestComponents.EnumerateArray())
        {
            RequireProvenanceObject(component, "Canonical runtime source component must be an object.");
            var kind = ReadProvenanceString(component, "component_kind");
            var identity = ReadProvenanceString(component, "component_identity");
            RequireSha256Identity(identity);
            if (!manifestIdentities.TryAdd(kind, identity))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                    "Canonical runtime source component kind is duplicated.");
            }
        }

        var requiredKinds = new HashSet<string>(["CARDDATABASE", "REGISTRY"], StringComparer.Ordinal);
        if (!requiredKinds.SetEquals(manifestIdentities.Keys))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                "Canonical runtime source components must be CARDDATABASE and REGISTRY.");
        }

        var provenanceComponents = ReadProvenanceObject(provenance, "source_components");
        var result = ImmutableDictionary.CreateBuilder<string, RuntimeSourceComponentProvenance>(StringComparer.Ordinal);
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var property in provenanceComponents.EnumerateObject())
        {
            if (!seen.Add(property.Name))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                    "Canonical runtime source component kind is duplicated.");
            }

            RequireProvenanceObject(property.Value, "Canonical runtime source component provenance must be an object.");
            var identity = ReadProvenanceString(property.Value, "component_identity");
            var contentHash = ReadProvenanceString(property.Value, "content_hash");
            RequireSha256Identity(identity);
            RequireSha256Identity(contentHash);
            if (!manifestIdentities.TryGetValue(property.Name, out var manifestIdentity)
                || !string.Equals(manifestIdentity, identity, StringComparison.Ordinal))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_PROVENANCE_ID_MISMATCH",
                    "Canonical runtime source component identities do not agree.");
            }

            result.Add(property.Name, new RuntimeSourceComponentProvenance(identity, contentHash));
        }

        if (!requiredKinds.SetEquals(result.Keys))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                "Canonical runtime provenance source components must be CARDDATABASE and REGISTRY.");
        }

        return result.ToImmutable();
    }

    private static HashSet<string> ReadManifestFiles(JsonElement manifest)
    {
        var result = new HashSet<string>(StringComparer.Ordinal);
        foreach (var entry in ReadProvenanceArray(manifest, "files").EnumerateArray())
        {
            RequireProvenanceObject(entry, "Canonical runtime manifest file entry must be an object.");
            var path = ReadProvenanceString(entry, "path");
            ValidateSafeRelativePath(path);
            if (!result.Add(path))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_HASH_PATH_DUPLICATE",
                    "Canonical runtime manifest contains a duplicate file path.");
            }
        }

        if (!result.Contains("provenance.json") || RequiredFiles.Any(path => !result.Contains(path)))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_HASH_SET_INVALID",
                "Canonical runtime manifest file set is incomplete.");
        }

        return result;
    }

    private static ImmutableDictionary<string, string> ReadHashMap(JsonElement root, string propertyName)
    {
        var hashObject = ReadProvenanceObject(root, propertyName);
        var result = ImmutableDictionary.CreateBuilder<string, string>(StringComparer.Ordinal);
        foreach (var property in hashObject.EnumerateObject())
        {
            ValidateSafeRelativePath(property.Name);
            if (property.Value.ValueKind != JsonValueKind.String || property.Value.GetString() is not { } hash)
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_HASH_INVALID",
                    "Canonical runtime hash must be a SHA-256 string.");
            }

            RequireSha256Identity(hash);
            if (!result.TryAdd(property.Name, hash))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_HASH_PATH_DUPLICATE",
                    "Canonical runtime hash declaration contains a duplicate path.");
            }
        }

        return result.ToImmutable();
    }

    private static bool HashMapsEqual(
        IReadOnlyDictionary<string, string> left,
        IReadOnlyDictionary<string, string> right) =>
        left.Count == right.Count
        && left.All(pair => right.TryGetValue(pair.Key, out var value)
            && string.Equals(pair.Value, value, StringComparison.Ordinal));

    private static string ResolveSafePackagePath(string packageDirectory, string relativePath)
    {
        ValidateSafeRelativePath(relativePath);
        var root = Path.GetFullPath(packageDirectory);
        var fullPath = Path.GetFullPath(Path.Combine(root, relativePath.Replace('/', Path.DirectorySeparatorChar)));
        var rootPrefix = root.EndsWith(Path.DirectorySeparatorChar)
            ? root
            : root + Path.DirectorySeparatorChar;
        if (!fullPath.StartsWith(rootPrefix, StringComparison.OrdinalIgnoreCase))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_HASH_PATH_INVALID",
                "Canonical runtime hash path escapes the package directory.");
        }

        return fullPath;
    }

    private static void ValidateSafeRelativePath(string path)
    {
        if (string.IsNullOrWhiteSpace(path)
            || Path.IsPathRooted(path)
            || path.Contains('\\')
            || path.Contains(':')
            || path.Split('/').Any(segment => segment.Length == 0 || segment is "." or ".."))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_HASH_PATH_INVALID",
                "Canonical runtime hash path must be a safe normalized relative path.");
        }
    }

    private static void RequireSha256Identity(string value)
    {
        const string prefix = "sha256:";
        if (!value.StartsWith(prefix, StringComparison.Ordinal)
            || value.Length != prefix.Length + 64
            || value.AsSpan(prefix.Length).ToString().Any(character =>
                character is not (>= '0' and <= '9') and not (>= 'a' and <= 'f')))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_HASH_INVALID",
                "Canonical runtime identity must use lowercase sha256:<64 hex> format.");
        }
    }

    private static RuntimePackageReadiness ReadReadiness(JsonElement readiness) => new(
        ReadProvenanceBool(readiness, "materialization_valid"),
        ReadProvenanceBool(readiness, "production_ready"),
        ReadProvenanceBool(readiness, "publish_allowed"));

    private static JsonElement ReadProvenanceObject(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value) || value.ValueKind != JsonValueKind.Object)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                $"Canonical runtime object is missing: {propertyName}");
        }

        return value;
    }

    private static JsonElement ReadProvenanceArray(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value) || value.ValueKind != JsonValueKind.Array)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                $"Canonical runtime array is missing: {propertyName}");
        }

        return value;
    }

    private static string ReadProvenanceString(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                $"Canonical runtime string is missing: {propertyName}");
        }

        return value.GetString()!;
    }

    private static bool ReadProvenanceBool(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind is not (JsonValueKind.True or JsonValueKind.False))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                $"Canonical runtime boolean is missing: {propertyName}");
        }

        return value.GetBoolean();
    }

    private static int ReadProvenanceInt(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var result))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_PROVENANCE_INVALID",
                $"Canonical runtime integer is missing: {propertyName}");
        }

        return result;
    }

    private static void RequireProvenanceObject(JsonElement value, string message)
    {
        if (value.ValueKind != JsonValueKind.Object)
        {
            throw new EngineInputException("RUNTIME_PACKAGE_PROVENANCE_INVALID", message);
        }
    }

    internal static void ValidateCatalog(RuntimePackageCatalog? catalog)
    {
        if (catalog is null
            || string.IsNullOrWhiteSpace(catalog.PackageId)
            || catalog.Cards is null
            || catalog.Decks is null
            || catalog.Lookups is null)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_CATALOG_INVALID",
                "Runtime package catalog is missing required data.");
        }

        if (catalog.Cards.Count == 0)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_EMPTY_CARDS",
                "Runtime package card registry is empty.");
        }

        ValidateLookupCatalog(catalog.Lookups);
        foreach (var (cardId, definition) in catalog.Cards)
        {
            if (definition is null
                || string.IsNullOrWhiteSpace(cardId)
                || !string.Equals(cardId, definition.CardId, StringComparison.Ordinal)
                || definition.Magnitude < 0
                || definition.PrintedAuraCost < 0
                || string.IsNullOrWhiteSpace(definition.Realm)
                || !catalog.Lookups.ContainsCanonicalValue("realm", definition.Realm)
                || string.IsNullOrWhiteSpace(definition.CardType)
                || !catalog.Lookups.ContainsCanonicalValue("card_type", definition.CardType))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_CATALOG_INVALID",
                    "Runtime package card definition is invalid.");
            }
        }

        foreach (var (deckId, deck) in catalog.Decks)
        {
            if (deck is null
                || string.IsNullOrWhiteSpace(deckId)
                || !string.Equals(deckId, deck.DeckId, StringComparison.Ordinal)
                || deck.OrderedCardIds.Any(cardId => !catalog.Cards.ContainsKey(cardId)))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_CATALOG_INVALID",
                    "Runtime package deck definition is invalid.");
            }
        }
    }

    private static RuntimeLookupCatalog ReadRuntimeLookupCatalog(string path)
    {
        using var document = ParseJsonFile(path);
        if (document.RootElement.ValueKind != JsonValueKind.Object)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_LOOKUPS_ROOT_INVALID",
                "Runtime lookups root must be an object.");
        }

        if (!document.RootElement.TryGetProperty("lookups", out var records)
            || records.ValueKind != JsonValueKind.Array)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_LOOKUPS_ARRAY_INVALID",
                "Runtime lookups must contain a lookups array.");
        }

        var aliasesByGroup = new Dictionary<string, ImmutableDictionary<string, string>.Builder>(
            StringComparer.Ordinal);
        foreach (var groupName in RequiredLookupGroups)
        {
            aliasesByGroup.Add(
                groupName,
                ImmutableDictionary.CreateBuilder<string, string>(StringComparer.Ordinal));
        }

        foreach (var record in records.EnumerateArray())
        {
            if (record.ValueKind != JsonValueKind.Object)
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_LOOKUP_RECORD_INVALID",
                    "Runtime lookup record must be an object.");
            }

            var lookupGroup = ReadRequiredLookupRecordString(record, "lookup_group");
            var alias = ReadRequiredLookupRecordString(record, "value");
            var status = ReadRequiredLookupRecordString(record, "status");
            var canonicalValue = ReadRequiredLookupRecordString(record, "canonical_value");
            if (!aliasesByGroup.TryGetValue(lookupGroup, out var aliases))
            {
                continue;
            }

            if (!IsStableRuntimeToken(canonicalValue))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_LOOKUP_RECORD_INVALID",
                    "Runtime lookup canonical_value must be a stable lowercase runtime token.");
            }

            if (!string.Equals(status, "active", StringComparison.Ordinal))
            {
                continue;
            }

            if (aliases.TryGetValue(alias, out var existingCanonicalValue))
            {
                if (!string.Equals(existingCanonicalValue, canonicalValue, StringComparison.Ordinal))
                {
                    throw new EngineInputException(
                        "RUNTIME_PACKAGE_LOOKUP_ALIAS_CONFLICT",
                        "Runtime lookup alias maps to conflicting canonical values.");
                }

                continue;
            }

            aliases.Add(alias, canonicalValue);
        }

        var groups = ImmutableDictionary.CreateBuilder<string, RuntimeLookupGroup>(StringComparer.Ordinal);
        foreach (var groupName in RequiredLookupGroups)
        {
            var aliases = aliasesByGroup[groupName];
            if (aliases.Count == 0)
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_LOOKUP_GROUP_MISSING",
                    $"Required active runtime lookup group is missing or empty: {groupName}");
            }

            groups.Add(groupName, new RuntimeLookupGroup(groupName, aliases.ToImmutable()));
        }

        return new RuntimeLookupCatalog(groups.ToImmutable());
    }

    private static void ValidateLookupCatalog(RuntimeLookupCatalog lookups)
    {
        if (lookups.Groups is null
            || !Equals(lookups.Groups.KeyComparer, StringComparer.Ordinal))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_CATALOG_INVALID",
                "Runtime lookup catalog is missing required data or ordinal comparison.");
        }

        foreach (var requiredGroup in RequiredLookupGroups)
        {
            if (!lookups.Groups.TryGetValue(requiredGroup, out var group)
                || group is null
                || !string.Equals(requiredGroup, group.LookupGroup, StringComparison.Ordinal)
                || group.ActiveAliases is null
                || group.ActiveAliases.Count == 0
                || !Equals(group.ActiveAliases.KeyComparer, StringComparer.Ordinal))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_CATALOG_INVALID",
                    $"Required runtime lookup group is invalid: {requiredGroup}");
            }
        }

        foreach (var (groupName, group) in lookups.Groups)
        {
            if (group is null
                || string.IsNullOrWhiteSpace(groupName)
                || !string.Equals(groupName, group.LookupGroup, StringComparison.Ordinal)
                || group.ActiveAliases is null
                || !Equals(group.ActiveAliases.KeyComparer, StringComparer.Ordinal)
                || group.ActiveAliases.Any(pair =>
                    string.IsNullOrWhiteSpace(pair.Key)
                    || string.IsNullOrWhiteSpace(pair.Value)
                    || !IsStableRuntimeToken(pair.Value)))
            {
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_CATALOG_INVALID",
                    "Runtime lookup catalog is internally inconsistent.");
            }
        }
    }

    private static JsonDocument ParseJsonFile(string path)
    {
        try
        {
            return JsonDocument.Parse(File.ReadAllBytes(path));
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or JsonException)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_JSON_INVALID",
                "Runtime package JSON could not be read or parsed.",
                exception);
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
            throw new EngineInputException(
                "RUNTIME_PACKAGE_JSONL_INVALID",
                "Runtime package JSONL could not be read.",
                exception);
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
                throw new EngineInputException(
                    "RUNTIME_PACKAGE_JSONL_INVALID",
                    "Runtime package JSONL record is invalid.",
                    exception);
            }

            using (document)
            {
                RequireObject(document.RootElement, "Runtime package JSONL record must be an object.");
                yield return document.RootElement.Clone();
            }
        }
    }

    private static string ReadRequiredString(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_FIELD_INVALID",
                $"Required runtime package string is missing: {propertyName}");
        }

        return value.GetString()!;
    }

    private static int ReadRequiredInt(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var result))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_FIELD_INVALID",
                $"Required runtime package integer is missing: {propertyName}");
        }

        return result;
    }

    private static int ReadRequiredMagnitude(JsonElement root)
    {
        if (!root.TryGetProperty("magnitude", out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var magnitude)
            || magnitude < 0)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_CARD_MAGNITUDE_INVALID",
                "Runtime card magnitude must be a non-negative Int32 JSON number.");
        }

        return magnitude;
    }

    private static int ReadRequiredAuraCost(JsonElement root)
    {
        if (!root.TryGetProperty("aura_cost", out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var auraCost)
            || auraCost < 0)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_CARD_AURA_COST_INVALID",
                "Runtime card aura_cost must be a non-negative Int32 JSON number.");
        }

        return auraCost;
    }

    private static string ReadAndResolveCardLookup(
        JsonElement root,
        string propertyName,
        string lookupGroup,
        string errorCode,
        RuntimeLookupCatalog lookups)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw new EngineInputException(
                errorCode,
                $"Runtime card {propertyName} must be a non-empty string.");
        }

        var alias = value.GetString()!;
        if (!lookups.TryResolve(lookupGroup, alias, out var canonicalValue))
        {
            throw new EngineInputException(
                errorCode,
                $"Runtime card {propertyName} is not an active lookup alias.");
        }

        return canonicalValue;
    }

    private static string ReadRequiredLookupRecordString(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_LOOKUP_RECORD_INVALID",
                $"Runtime lookup record string is missing or empty: {propertyName}");
        }

        return value.GetString()!;
    }

    private static bool IsStableRuntimeToken(string value)
    {
        if (value.Length == 0 || value[0] is < 'a' or > 'z')
        {
            return false;
        }

        return value.Skip(1).All(character =>
            character is >= 'a' and <= 'z'
            or >= '0' and <= '9'
            or '_');
    }

    private static JsonElement ReadRequiredArray(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out var value) || value.ValueKind != JsonValueKind.Array)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_FIELD_INVALID",
                $"Required runtime package array is missing: {propertyName}");
        }

        return value;
    }

    private static void RequireObject(JsonElement value, string message)
    {
        if (value.ValueKind != JsonValueKind.Object)
        {
            throw new EngineInputException("RUNTIME_PACKAGE_SHAPE_INVALID", message);
        }
    }
}

public sealed class EngineInputException : Exception
{
    public EngineInputException(string code, string message, Exception? innerException = null)
        : base(message, innerException)
    {
        Code = code;
    }

    public string Code { get; }
}
