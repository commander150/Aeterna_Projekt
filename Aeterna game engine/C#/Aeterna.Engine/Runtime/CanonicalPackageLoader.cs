using System.Collections.Immutable;
using System.Text.Json;

namespace Aeterna.Engine.Runtime;

public enum CanonicalPackageValidationMode
{
    Production,
    Development,
}

public sealed record CanonicalRecord(ImmutableDictionary<string, JsonElement> Fields)
{
    public bool TryGetValue(string fieldName, out JsonElement value) => Fields.TryGetValue(fieldName, out value);

    public string GetRequiredString(string fieldName)
    {
        if (!Fields.TryGetValue(fieldName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw new EngineInputException(
                "CANONICAL_RECORD_FIELD_INVALID",
                $"Canonical record field must be a non-empty string: {fieldName}");
        }

        return value.GetString()!;
    }
}

public sealed record CanonicalTable(
    string TableId,
    string PrimaryKey,
    ImmutableArray<CanonicalRecord> Records,
    ImmutableDictionary<string, CanonicalRecord> RecordsById);

public sealed record CanonicalRegistryPackage(
    string PackageId,
    string SchemaVersion,
    string DataVersion,
    string ManifestFileName,
    string MetaFileName,
    ImmutableDictionary<string, CanonicalTable> Tables);

public sealed record CanonicalCardDatabasePackage(
    string PackageId,
    string SchemaVersion,
    string DataVersion,
    string ManifestFileName,
    string MetaFileName,
    ImmutableDictionary<string, CanonicalTable> Tables,
    CanonicalRegistryPackage Registry);

public static class CanonicalPackageLoader
{
    public const string CanonicalFormat = "aeterna_canonical_table_v1";
    public const string RegistryManifestFileName = "registry.export_manifest.json";
    public const string CardDatabaseManifestFileName = "carddatabase.export_manifest.json";
    private const string CanonicalNullSentinel = "#NULL";
    private const string CanonicalTbdSentinel = "#TBD";

    public static CanonicalRegistryPackage LoadRegistry(
        string packageDirectory,
        CanonicalPackageValidationMode validationMode = CanonicalPackageValidationMode.Production)
    {
        var loaded = LoadPackage(packageDirectory, RegistryManifestFileName, "aeterna_registry", validationMode);
        return new CanonicalRegistryPackage(
            loaded.PackageId,
            loaded.SchemaVersion,
            loaded.DataVersion,
            RegistryManifestFileName,
            loaded.MetaFileName,
            loaded.Tables);
    }

    public static CanonicalCardDatabasePackage LoadCardDatabase(
        string packageDirectory,
        CanonicalRegistryPackage registry,
        CanonicalPackageValidationMode validationMode = CanonicalPackageValidationMode.Production)
    {
        ArgumentNullException.ThrowIfNull(registry);
        var loaded = LoadPackage(packageDirectory, CardDatabaseManifestFileName, "aeterna_carddatabase", validationMode);
        var minimumSchemaVersion = ReadRequiredMetaString(loaded.Meta, "minimum_registry_schema_version");
        var minimumDataVersion = ReadRequiredMetaString(loaded.Meta, "minimum_registry_data_version");
        if (CompareVersions(registry.SchemaVersion, minimumSchemaVersion) < 0
            || CompareVersions(registry.DataVersion, minimumDataVersion) < 0)
        {
            throw new EngineInputException(
                "CANONICAL_REGISTRY_VERSION_INCOMPATIBLE",
                "REGISTRY schema or data version does not satisfy the CARDDATABASE dependency.");
        }

        var registryManifestReference = ReadRequiredMetaString(loaded.Meta, "registry_manifest_reference");
        var registryMetaReference = ReadRequiredMetaString(loaded.Meta, "registry_meta_reference");
        if (!string.Equals(Path.GetFileName(registryManifestReference), registry.ManifestFileName, StringComparison.Ordinal)
            || !string.Equals(Path.GetFileName(registryMetaReference), registry.MetaFileName, StringComparison.Ordinal))
        {
            throw new EngineInputException(
                "CANONICAL_REGISTRY_REFERENCE_MISMATCH",
                "CARDDATABASE registry file references contradict the loaded REGISTRY package.");
        }

        return new CanonicalCardDatabasePackage(
            loaded.PackageId,
            loaded.SchemaVersion,
            loaded.DataVersion,
            CardDatabaseManifestFileName,
            loaded.MetaFileName,
            loaded.Tables,
            registry);
    }

    private static LoadedPackage LoadPackage(
        string packageDirectory,
        string manifestFileName,
        string expectedPackageId,
        CanonicalPackageValidationMode validationMode)
    {
        if (string.IsNullOrWhiteSpace(packageDirectory))
        {
            throw new EngineInputException("CANONICAL_PACKAGE_PATH_INVALID", "Canonical package directory is empty.");
        }

        var fullDirectory = Path.GetFullPath(packageDirectory);
        if (!Directory.Exists(fullDirectory))
        {
            throw new EngineInputException("CANONICAL_PACKAGE_NOT_FOUND", "Canonical package directory was not found.");
        }

        var manifestPath = Path.Combine(fullDirectory, manifestFileName);
        if (!File.Exists(manifestPath))
        {
            throw new EngineInputException("CANONICAL_MANIFEST_MISSING", "Canonical export manifest is missing.");
        }

        var manifestTable = ParseTable(manifestPath, "export_manifest", expectedPackageId, validationMode);
        var entries = ImmutableArray.CreateBuilder<ManifestEntry>();
        var tableIds = new HashSet<string>(StringComparer.Ordinal);
        var exportFiles = new HashSet<string>(StringComparer.Ordinal);
        var exportOrders = new HashSet<int>();
        foreach (var record in manifestTable.Records)
        {
            if (!ReadRequiredBoolean(record, "export_enabled"))
            {
                continue;
            }

            var tableId = record.GetRequiredString("table_id");
            var exportFile = record.GetRequiredString("export_file");
            var exportFormat = record.GetRequiredString("export_format");
            var exportOrder = ReadRequiredInteger(record, "export_order");
            if (!string.Equals(exportFormat, "json", StringComparison.Ordinal))
            {
                throw new EngineInputException(
                    "CANONICAL_EXPORT_FORMAT_UNSUPPORTED",
                    "Canonical manifest contains an unsupported export format.");
            }

            if (exportOrder < 1)
            {
                throw new EngineInputException("CANONICAL_EXPORT_ORDER_INVALID", "Canonical export order must be positive.");
            }

            if (!IsSafeFileName(exportFile))
            {
                throw new EngineInputException("CANONICAL_EXPORT_FILE_INVALID", "Canonical export filename is unsafe or invalid.");
            }

            if (!tableIds.Add(tableId))
            {
                throw new EngineInputException("CANONICAL_TABLE_ID_DUPLICATE", "Canonical manifest contains a duplicate logical table_id.");
            }

            if (!exportFiles.Add(exportFile))
            {
                throw new EngineInputException("CANONICAL_EXPORT_FILE_DUPLICATE", "Canonical manifest contains a duplicate export filename.");
            }

            if (!exportOrders.Add(exportOrder))
            {
                throw new EngineInputException("CANONICAL_EXPORT_ORDER_DUPLICATE", "Canonical manifest contains a duplicate export order.");
            }

            entries.Add(new ManifestEntry(tableId, exportFile, exportOrder));
        }

        var orderedEntries = entries.ToImmutable().OrderBy(entry => entry.ExportOrder).ToImmutableArray();
        if (orderedEntries.Length == 0
            || !string.Equals(orderedEntries[0].TableId, "export_manifest", StringComparison.Ordinal)
            || !string.Equals(orderedEntries[0].ExportFile, manifestFileName, StringComparison.Ordinal))
        {
            throw new EngineInputException(
                "CANONICAL_MANIFEST_CONTENT_INVALID",
                "Canonical manifest must declare itself as the first logical table.");
        }

        var rawTables = new Dictionary<string, RawTable>(StringComparer.Ordinal)
        {
            ["export_manifest"] = manifestTable,
        };
        foreach (var entry in orderedEntries.Skip(1))
        {
            var path = Path.Combine(fullDirectory, entry.ExportFile);
            if (!File.Exists(path))
            {
                throw new EngineInputException(
                    "CANONICAL_EXPORTED_FILE_MISSING",
                    $"Manifest-referenced canonical file is missing: {entry.ExportFile}");
            }

            rawTables.Add(entry.TableId, ParseTable(path, entry.TableId, expectedPackageId, validationMode));
        }

        if (!rawTables.TryGetValue("meta", out var rawMeta))
        {
            throw new EngineInputException("CANONICAL_META_MISSING", "Canonical manifest does not declare meta.");
        }

        var meta = BuildMeta(rawMeta.Records);
        ValidateSentinel(meta, "null_sentinel", CanonicalNullSentinel, "CANONICAL_NULL_SENTINEL_INVALID");
        ValidateSentinel(meta, "tbd_sentinel", CanonicalTbdSentinel, "CANONICAL_TBD_SENTINEL_INVALID");
        var packageId = ReadRequiredMetaString(meta, "workbook_id");
        if (!string.Equals(packageId, expectedPackageId, StringComparison.Ordinal))
        {
            throw new EngineInputException("CANONICAL_PACKAGE_ID_MISMATCH", "Canonical package identity is invalid.");
        }

        var schemaVersion = ReadRequiredMetaString(meta, "schema_version");
        var dataVersion = ReadRequiredMetaString(meta, "data_version");
        ValidateVersion(schemaVersion);
        ValidateVersion(dataVersion);
        var declaredManifest = ReadRequiredMetaString(meta, "export_manifest_file");
        if (!string.Equals(declaredManifest, manifestFileName, StringComparison.Ordinal))
        {
            throw new EngineInputException("CANONICAL_MANIFEST_FILENAME_MISMATCH", "META contradicts the loaded manifest filename.");
        }

        var metaEntry = orderedEntries.Single(entry => string.Equals(entry.TableId, "meta", StringComparison.Ordinal));
        if (!rawTables.TryGetValue("schema_tables", out var schemaTables))
        {
            throw new EngineInputException("CANONICAL_SCHEMA_TABLES_MISSING", "Canonical schema_tables export is missing.");
        }

        var primaryKeys = BuildPrimaryKeyMap(schemaTables.Records);
        var tables = ImmutableDictionary.CreateBuilder<string, CanonicalTable>(StringComparer.Ordinal);
        foreach (var entry in orderedEntries)
        {
            var rawTable = rawTables[entry.TableId];
            if (!primaryKeys.TryGetValue(entry.TableId, out var primaryKey))
            {
                throw new EngineInputException(
                    "CANONICAL_TABLE_SCHEMA_MISSING",
                    $"Canonical table has no active SCHEMA_TABLES definition: {entry.TableId}");
            }

            var byId = ImmutableDictionary.CreateBuilder<string, CanonicalRecord>(StringComparer.Ordinal);
            foreach (var record in rawTable.Records)
            {
                var recordId = record.GetRequiredString(primaryKey);
                if (!byId.TryAdd(recordId, record))
                {
                    throw new EngineInputException(
                        "CANONICAL_PRIMARY_ID_DUPLICATE",
                        $"Canonical table contains a duplicate primary record ID: {entry.TableId}");
                }
            }

            tables.Add(entry.TableId, new CanonicalTable(entry.TableId, primaryKey, rawTable.Records, byId.ToImmutable()));
        }

        return new LoadedPackage(packageId, schemaVersion, dataVersion, metaEntry.ExportFile, meta, tables.ToImmutable());
    }

    private static RawTable ParseTable(
        string path,
        string expectedTableId,
        string expectedPackageId,
        CanonicalPackageValidationMode validationMode)
    {
        JsonDocument document;
        try
        {
            document = JsonDocument.Parse(File.ReadAllBytes(path));
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or JsonException)
        {
            throw new EngineInputException("CANONICAL_JSON_INVALID", "Canonical JSON could not be read or parsed.", exception);
        }

        using (document)
        {
            var root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object
                || !TryReadString(root, "canonical_format", out var format)
                || !string.Equals(format, CanonicalFormat, StringComparison.Ordinal))
            {
                throw new EngineInputException("CANONICAL_FORMAT_UNSUPPORTED", "Canonical table format is missing or unsupported.");
            }

            if (!TryReadString(root, "package_id", out var packageId)
                || !string.Equals(packageId, expectedPackageId, StringComparison.Ordinal))
            {
                throw new EngineInputException("CANONICAL_PACKAGE_ID_MISMATCH", "Canonical table package identity is invalid.");
            }

            if (!TryReadString(root, "table_id", out var tableId)
                || !string.Equals(tableId, expectedTableId, StringComparison.Ordinal))
            {
                throw new EngineInputException("CANONICAL_TABLE_ID_MISMATCH", "Manifest and canonical table identity disagree.");
            }

            if (!root.TryGetProperty("records", out var recordsElement)
                || recordsElement.ValueKind != JsonValueKind.Array)
            {
                throw new EngineInputException("CANONICAL_RECORDS_INVALID", "Canonical table records must be an array.");
            }

            var records = ImmutableArray.CreateBuilder<CanonicalRecord>();
            foreach (var element in recordsElement.EnumerateArray())
            {
                if (element.ValueKind != JsonValueKind.Object)
                {
                    throw new EngineInputException("CANONICAL_RECORD_INVALID", "Canonical record must be an object.");
                }

                var declaresTbdSentinel = string.Equals(expectedTableId, "meta", StringComparison.Ordinal)
                    && TryReadString(element, "key", out var metaKey)
                    && string.Equals(metaKey, "tbd_sentinel", StringComparison.Ordinal);
                var fields = ImmutableDictionary.CreateBuilder<string, JsonElement>(StringComparer.Ordinal);
                foreach (var property in element.EnumerateObject())
                {
                    if (validationMode == CanonicalPackageValidationMode.Production
                        && !(declaresTbdSentinel && string.Equals(property.Name, "value", StringComparison.Ordinal)))
                    {
                        RejectTbd(property.Value);
                    }

                    if (!fields.TryAdd(property.Name, property.Value.Clone()))
                    {
                        throw new EngineInputException(
                            "CANONICAL_RECORD_FIELD_DUPLICATE",
                            $"Canonical record contains a duplicate field: {property.Name}");
                    }
                }

                records.Add(new CanonicalRecord(fields.ToImmutable()));
            }

            return new RawTable(tableId, records.ToImmutable());
        }
    }

    private static ImmutableDictionary<string, JsonElement> BuildMeta(ImmutableArray<CanonicalRecord> records)
    {
        var meta = ImmutableDictionary.CreateBuilder<string, JsonElement>(StringComparer.Ordinal);
        foreach (var record in records)
        {
            var key = record.GetRequiredString("key");
            if (!record.TryGetValue("value", out var value) || !meta.TryAdd(key, value.Clone()))
            {
                throw new EngineInputException("CANONICAL_META_INVALID", "Canonical META contains a missing value or duplicate key.");
            }
        }

        return meta.ToImmutable();
    }

    private static ImmutableDictionary<string, string> BuildPrimaryKeyMap(ImmutableArray<CanonicalRecord> records)
    {
        var primaryKeys = ImmutableDictionary.CreateBuilder<string, string>(StringComparer.Ordinal);
        foreach (var record in records)
        {
            if (!record.TryGetValue("status", out var status)
                || status.ValueKind != JsonValueKind.String
                || !string.Equals(status.GetString(), "active", StringComparison.Ordinal))
            {
                continue;
            }

            var tableId = record.GetRequiredString("table_id");
            var primaryKey = record.GetRequiredString("primary_key");
            if (!primaryKeys.TryAdd(tableId, primaryKey))
            {
                throw new EngineInputException("CANONICAL_TABLE_ID_DUPLICATE", "SCHEMA_TABLES contains a duplicate active table_id.");
            }
        }

        return primaryKeys.ToImmutable();
    }

    private static string ReadRequiredMetaString(ImmutableDictionary<string, JsonElement> meta, string key)
    {
        if (!meta.TryGetValue(key, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw new EngineInputException("CANONICAL_META_FIELD_INVALID", $"Required canonical META value is missing: {key}");
        }

        return value.GetString()!;
    }

    private static void ValidateSentinel(
        ImmutableDictionary<string, JsonElement> meta,
        string key,
        string expectedValue,
        string errorCode)
    {
        if (!meta.TryGetValue(key, out var value)
            || value.ValueKind != JsonValueKind.String
            || !string.Equals(value.GetString(), expectedValue, StringComparison.Ordinal))
        {
            throw new EngineInputException(
                errorCode,
                $"Canonical META.{key} must be the canonical v1 literal {expectedValue}.");
        }
    }

    private static bool ReadRequiredBoolean(CanonicalRecord record, string fieldName)
    {
        if (!record.TryGetValue(fieldName, out var value)
            || value.ValueKind is not (JsonValueKind.True or JsonValueKind.False))
        {
            throw new EngineInputException("CANONICAL_MANIFEST_FIELD_INVALID", $"Manifest boolean is invalid: {fieldName}");
        }

        return value.GetBoolean();
    }

    private static int ReadRequiredInteger(CanonicalRecord record, string fieldName)
    {
        if (!record.TryGetValue(fieldName, out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var result))
        {
            throw new EngineInputException("CANONICAL_MANIFEST_FIELD_INVALID", $"Manifest integer is invalid: {fieldName}");
        }

        return result;
    }

    private static bool TryReadString(JsonElement root, string propertyName, out string value)
    {
        if (root.TryGetProperty(propertyName, out var property)
            && property.ValueKind == JsonValueKind.String
            && !string.IsNullOrWhiteSpace(property.GetString()))
        {
            value = property.GetString()!;
            return true;
        }

        value = string.Empty;
        return false;
    }

    private static bool IsSafeFileName(string value) =>
        !string.IsNullOrWhiteSpace(value)
        && string.Equals(value, value.Trim(), StringComparison.Ordinal)
        && !string.Equals(value, ".", StringComparison.Ordinal)
        && !string.Equals(value, "..", StringComparison.Ordinal)
        && !value.Contains('/')
        && !value.Contains('\\')
        && !(value.Length >= 2 && char.IsAsciiLetter(value[0]) && value[1] == ':')
        && !Path.IsPathRooted(value)
        && string.Equals(value, Path.GetFileName(value), StringComparison.Ordinal)
        && string.Equals(Path.GetExtension(value), ".json", StringComparison.Ordinal);

    private static void RejectTbd(JsonElement value)
    {
        if (value.ValueKind == JsonValueKind.String
            && string.Equals(value.GetString(), CanonicalTbdSentinel, StringComparison.Ordinal))
        {
            throw new EngineInputException("CANONICAL_TBD_FORBIDDEN", "Production canonical input contains #TBD.");
        }

        if (value.ValueKind == JsonValueKind.Object)
        {
            foreach (var property in value.EnumerateObject())
            {
                RejectTbd(property.Value);
            }
        }
        else if (value.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in value.EnumerateArray())
            {
                RejectTbd(item);
            }
        }
    }

    private static void ValidateVersion(string value)
    {
        if (!Version.TryParse(value, out _))
        {
            throw new EngineInputException("CANONICAL_VERSION_INVALID", "Canonical schema or data version is invalid.");
        }
    }

    private static int CompareVersions(string actual, string minimum)
    {
        if (!Version.TryParse(actual, out var actualVersion)
            || !Version.TryParse(minimum, out var minimumVersion))
        {
            throw new EngineInputException("CANONICAL_VERSION_INVALID", "Canonical dependency version is invalid.");
        }

        return actualVersion.CompareTo(minimumVersion);
    }

    private sealed record ManifestEntry(string TableId, string ExportFile, int ExportOrder);

    private sealed record RawTable(string TableId, ImmutableArray<CanonicalRecord> Records);

    private sealed record LoadedPackage(
        string PackageId,
        string SchemaVersion,
        string DataVersion,
        string MetaFileName,
        ImmutableDictionary<string, JsonElement> Meta,
        ImmutableDictionary<string, CanonicalTable> Tables);
}
