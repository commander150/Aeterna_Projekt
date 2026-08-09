using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine.Runtime;

internal static class CanonicalPackageLoaderTests
{
    public static void SuccessfulRegistryAndCardDatabaseLoadPreservesAllFields()
    {
        using var fixture = TemporaryCanonicalPackages.Create();

        var registry = CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory);
        var cards = CanonicalPackageLoader.LoadCardDatabase(fixture.CardDatabaseDirectory, registry);

        Equal("0.5.1", registry.SchemaVersion, "REGISTRY schema version was not loaded.");
        Equal("0.13.0", registry.DataVersion, "REGISTRY data version was not loaded.");
        Equal("0.4.0", cards.SchemaVersion, "CARDDATABASE schema version was not loaded.");
        Equal("value_1", registry.Tables["values"].Records[0].GetRequiredString("value_id"), "Registry record was not loaded.");
        True(registry.Tables["values"].Records[0].Fields.ContainsKey("unused_field"), "An exported field was discarded.");
        Equal("preserved", registry.Tables["values"].Records[0].GetRequiredString("unused_field"), "Unused field value changed.");
        True(ReferenceEquals(registry, cards.Registry), "CARDDATABASE did not retain its validated REGISTRY dependency.");
    }

    public static void ManifestDrivenFilenameResolutionWorks()
    {
        using var fixture = TemporaryCanonicalPackages.Create();

        var registry = CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory);

        Equal(1, registry.Tables["values"].Records.Length, "Manifest-declared non-default filename was not resolved.");
        True(File.Exists(Path.Combine(fixture.RegistryDirectory, "registry.manifest_declared_values.json")), "Fixture filename is invalid.");
        True(!File.Exists(Path.Combine(fixture.RegistryDirectory, "registry.values.json")), "Fixture accidentally allowed guessed filename resolution.");
    }

    public static void MissingFileIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        File.Delete(Path.Combine(fixture.RegistryDirectory, "registry.manifest_declared_values.json"));

        ThrowsCode("CANONICAL_EXPORTED_FILE_MISSING", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void MissingManifestAndMetaAreRejected()
    {
        using (var missingManifest = TemporaryCanonicalPackages.Create())
        {
            File.Delete(Path.Combine(missingManifest.RegistryDirectory, "registry.export_manifest.json"));
            ThrowsCode("CANONICAL_MANIFEST_MISSING", () => CanonicalPackageLoader.LoadRegistry(missingManifest.RegistryDirectory));
        }

        using (var missingMeta = TemporaryCanonicalPackages.Create())
        {
            File.Delete(Path.Combine(missingMeta.RegistryDirectory, "registry.meta.json"));
            ThrowsCode("CANONICAL_EXPORTED_FILE_MISSING", () => CanonicalPackageLoader.LoadRegistry(missingMeta.RegistryDirectory));
        }
    }

    public static void MalformedJsonIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        File.WriteAllText(Path.Combine(fixture.RegistryDirectory, "registry.manifest_declared_values.json"), "{");

        ThrowsCode("CANONICAL_JSON_INVALID", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void DuplicateLogicalTableIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.AddDuplicateRegistryManifestEntry();

        ThrowsCode("CANONICAL_TABLE_ID_DUPLICATE", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void DuplicatePrimaryRecordIdIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.WriteDuplicateRegistryValue();

        ThrowsCode("CANONICAL_PRIMARY_ID_DUPLICATE", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void UnsupportedExportFormatIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.SetRegistryManifestFormat("yaml");

        ThrowsCode("CANONICAL_EXPORT_FORMAT_UNSUPPORTED", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void ManifestAndTableIdentityMismatchIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.WriteRegistryValueWithTableId("wrong_table_id");

        ThrowsCode("CANONICAL_TABLE_ID_MISMATCH", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void ProductionTbdIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.WriteRegistryValue("#TBD");

        ThrowsCode("CANONICAL_TBD_FORBIDDEN", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void DevelopmentTbdIsPreserved()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.WriteRegistryValue("#TBD");

        var registry = CanonicalPackageLoader.LoadRegistry(
            fixture.RegistryDirectory,
            CanonicalPackageValidationMode.Development);

        Equal("#TBD", registry.Tables["values"].Records[0].GetRequiredString("unused_field"), "Development loader did not preserve #TBD.");
    }

    public static void MissingNullSentinelIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.RemoveRegistryMeta("null_sentinel");

        ThrowsCode("CANONICAL_NULL_SENTINEL_INVALID", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void MissingTbdSentinelIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.RemoveRegistryMeta("tbd_sentinel");

        ThrowsCode("CANONICAL_TBD_SENTINEL_INVALID", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void InvalidNullSentinelIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.SetRegistryMeta("null_sentinel", "NULL");

        ThrowsCode("CANONICAL_NULL_SENTINEL_INVALID", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void InvalidTbdSentinelIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.SetRegistryMeta("tbd_sentinel", "TBD");

        ThrowsCode("CANONICAL_TBD_SENTINEL_INVALID", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void ValidSentinelContractIsAccepted()
    {
        using var fixture = TemporaryCanonicalPackages.Create();

        var registry = CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory);

        Equal("aeterna_registry", registry.PackageId, "A valid canonical v1 sentinel declaration was rejected.");
    }

    public static void ExportFilenameContractIsExactAndPlatformIndependent()
    {
        var cases = new (string FileName, bool Valid)[]
        {
            ("valid.json", true),
            ("invalid.JSON", false),
            ("../escape.json", false),
            ("sub/file.json", false),
            (@"C:\escape.json", false),
            ("/escape.json", false),
        };

        foreach (var (fileName, valid) in cases)
        {
            using var fixture = TemporaryCanonicalPackages.Create();
            fixture.SetRegistryValuesExportFile(fileName, renameExport: valid);
            if (valid)
            {
                var registry = CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory);
                Equal(1, registry.Tables["values"].Records.Length, "A valid lowercase .json filename was rejected.");
            }
            else
            {
                ThrowsCode("CANONICAL_EXPORT_FILE_INVALID", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
            }
        }
    }

    public static void DuplicateRecordFieldIsRejectedWithStableCode()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        fixture.WriteRegistryValueWithDuplicateProperty();

        ThrowsCode("CANONICAL_RECORD_FIELD_DUPLICATE", () => CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory));
    }

    public static void RegistryVersionIncompatibilityIsRejected()
    {
        using var fixture = TemporaryCanonicalPackages.Create(minimumRegistrySchemaVersion: "9.0.0");
        var registry = CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory);

        ThrowsCode(
            "CANONICAL_REGISTRY_VERSION_INCOMPATIBLE",
            () => CanonicalPackageLoader.LoadCardDatabase(fixture.CardDatabaseDirectory, registry));
    }

    public static void CanonicalCatalogIsImmutableAndOrdinal()
    {
        using var fixture = TemporaryCanonicalPackages.Create();
        var registry = CanonicalPackageLoader.LoadRegistry(fixture.RegistryDirectory);

        Equal(StringComparer.Ordinal, registry.Tables.KeyComparer, "Table catalog does not use ordinal comparison.");
        Equal(StringComparer.Ordinal, registry.Tables["values"].RecordsById.KeyComparer, "Record catalog does not use ordinal comparison.");
        Equal(StringComparer.Ordinal, registry.Tables["values"].Records[0].Fields.KeyComparer, "Record fields do not use ordinal comparison.");
        var changed = registry.Tables.SetItem("other", registry.Tables["values"]);
        True(!registry.Tables.ContainsKey("other"), "Immutable table catalog was mutated.");
        True(changed.ContainsKey("other"), "Immutable catalog copy operation failed.");
    }

    private static void ThrowsCode(string expectedCode, Action action)
    {
        try
        {
            action();
        }
        catch (EngineInputException exception)
        {
            Equal(expectedCode, exception.Code, "Canonical loader returned an unexpected diagnostic code.");
            return;
        }

        throw new InvalidOperationException($"Expected EngineInputException with code {expectedCode}.");
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
            throw new InvalidOperationException($"{message} Expected: {expected}; actual: {actual}.");
        }
    }

    private sealed class TemporaryCanonicalPackages : IDisposable
    {
        private readonly string _root;
        private readonly List<Dictionary<string, object?>> _registryManifest;
        private readonly List<Dictionary<string, object?>> _registryMeta;
        private readonly List<Dictionary<string, object?>> _cardDatabaseMeta;

        private TemporaryCanonicalPackages(string root, string minimumRegistrySchemaVersion)
        {
            _root = root;
            RegistryDirectory = Path.Combine(root, "REGISTRY");
            CardDatabaseDirectory = Path.Combine(root, "CARDDATABASE");
            Directory.CreateDirectory(RegistryDirectory);
            Directory.CreateDirectory(CardDatabaseDirectory);

            _registryManifest = ManifestRecords(
                ("export_manifest", "registry.export_manifest.json", 1),
                ("meta", "registry.meta.json", 2),
                ("schema_tables", "registry.schema_tables.json", 3),
                ("values", "registry.manifest_declared_values.json", 10));
            WriteRegistryManifest();
            _registryMeta = MetaRecords(
                ("workbook_id", "aeterna_registry"),
                ("schema_version", "0.5.1"),
                ("data_version", "0.13.0"),
                ("export_manifest_file", "registry.export_manifest.json"),
                ("null_sentinel", "#NULL"),
                ("tbd_sentinel", "#TBD"));
            WriteRegistryMeta();
            WriteTable(RegistryDirectory, "registry.schema_tables.json", "aeterna_registry", "schema_tables", SchemaTableRecords("values"));
            WriteRegistryValue("preserved");

            var cardManifest = ManifestRecords(
                ("export_manifest", "carddatabase.export_manifest.json", 1),
                ("meta", "carddatabase.meta.json", 2),
                ("schema_tables", "carddatabase.schema_tables.json", 3),
                ("cards", "carddatabase.manifest_declared_cards.json", 10));
            WriteTable(CardDatabaseDirectory, "carddatabase.export_manifest.json", "aeterna_carddatabase", "export_manifest", cardManifest);
            _cardDatabaseMeta = MetaRecords(
                ("workbook_id", "aeterna_carddatabase"),
                ("schema_version", "0.4.0"),
                ("data_version", "0.12.0"),
                ("export_manifest_file", "carddatabase.export_manifest.json"),
                ("null_sentinel", "#NULL"),
                ("tbd_sentinel", "#TBD"),
                ("minimum_registry_schema_version", minimumRegistrySchemaVersion),
                ("minimum_registry_data_version", "0.13.0"),
                ("registry_manifest_reference", "../REGISTRY/registry.export_manifest.json"),
                ("registry_meta_reference", "../REGISTRY/registry.meta.json"));
            WriteCardDatabaseMeta();
            WriteTable(CardDatabaseDirectory, "carddatabase.schema_tables.json", "aeterna_carddatabase", "schema_tables", SchemaTableRecords("cards"));
            WriteTable(CardDatabaseDirectory, "carddatabase.manifest_declared_cards.json", "aeterna_carddatabase", "cards",
                [new Dictionary<string, object?> { ["card_id"] = "CARD-001", ["future_field"] = 17 }]);
        }

        public string RegistryDirectory { get; }

        public string CardDatabaseDirectory { get; }

        public static TemporaryCanonicalPackages Create(string minimumRegistrySchemaVersion = "0.5.1")
        {
            var root = Path.Combine(Path.GetTempPath(), "aeterna_canonical_loader_" + Guid.NewGuid().ToString("N"));
            return new TemporaryCanonicalPackages(root, minimumRegistrySchemaVersion);
        }

        public void AddDuplicateRegistryManifestEntry()
        {
            _registryManifest.Add(new Dictionary<string, object?>
            {
                ["table_id"] = "values",
                ["export_enabled"] = true,
                ["export_file"] = "registry.other.json",
                ["export_format"] = "json",
                ["export_order"] = 11,
            });
            WriteRegistryManifest();
        }

        public void SetRegistryManifestFormat(string format)
        {
            _registryManifest.Single(record => Equals(record["table_id"], "values"))["export_format"] = format;
            WriteRegistryManifest();
        }

        public void SetRegistryValuesExportFile(string fileName, bool renameExport)
        {
            const string oldFileName = "registry.manifest_declared_values.json";
            _registryManifest.Single(record => Equals(record["table_id"], "values"))["export_file"] = fileName;
            if (renameExport)
            {
                File.Move(
                    Path.Combine(RegistryDirectory, oldFileName),
                    Path.Combine(RegistryDirectory, fileName));
            }

            WriteRegistryManifest();
        }

        public void RemoveRegistryMeta(string key)
        {
            _registryMeta.RemoveAll(record => Equals(record["key"], key));
            WriteRegistryMeta();
        }

        public void SetRegistryMeta(string key, string value)
        {
            _registryMeta.Single(record => Equals(record["key"], key))["value"] = value;
            WriteRegistryMeta();
        }

        public void WriteDuplicateRegistryValue()
        {
            WriteTable(RegistryDirectory, "registry.manifest_declared_values.json", "aeterna_registry", "values",
            [
                new Dictionary<string, object?> { ["value_id"] = "value_1", ["unused_field"] = "first" },
                new Dictionary<string, object?> { ["value_id"] = "value_1", ["unused_field"] = "second" },
            ]);
        }

        public void WriteRegistryValue(string unusedField)
        {
            WriteTable(RegistryDirectory, "registry.manifest_declared_values.json", "aeterna_registry", "values",
                [new Dictionary<string, object?> { ["value_id"] = "value_1", ["unused_field"] = unusedField }]);
        }

        public void WriteRegistryValueWithTableId(string tableId)
        {
            WriteTable(RegistryDirectory, "registry.manifest_declared_values.json", "aeterna_registry", tableId,
                [new Dictionary<string, object?> { ["value_id"] = "value_1", ["unused_field"] = "preserved" }]);
        }

        public void WriteRegistryValueWithDuplicateProperty()
        {
            File.WriteAllText(
                Path.Combine(RegistryDirectory, "registry.manifest_declared_values.json"),
                $$"""
                {
                  "canonical_format": "{{CanonicalPackageLoader.CanonicalFormat}}",
                  "package_id": "aeterna_registry",
                  "table_id": "values",
                  "records": [
                    {
                      "value_id": "value_1",
                      "status": "active",
                      "status": "deprecated"
                    }
                  ]
                }
                """);
        }

        public void Dispose()
        {
            Directory.Delete(_root, recursive: true);
        }

        private void WriteRegistryManifest() =>
            WriteTable(RegistryDirectory, "registry.export_manifest.json", "aeterna_registry", "export_manifest", _registryManifest);

        private void WriteRegistryMeta() =>
            WriteTable(RegistryDirectory, "registry.meta.json", "aeterna_registry", "meta", _registryMeta);

        private void WriteCardDatabaseMeta() =>
            WriteTable(CardDatabaseDirectory, "carddatabase.meta.json", "aeterna_carddatabase", "meta", _cardDatabaseMeta);

        private static List<Dictionary<string, object?>> ManifestRecords(params (string TableId, string FileName, int Order)[] entries) =>
            entries.Select(entry => new Dictionary<string, object?>
            {
                ["table_id"] = entry.TableId,
                ["export_enabled"] = true,
                ["export_file"] = entry.FileName,
                ["export_format"] = "json",
                ["export_order"] = entry.Order,
            }).ToList();

        private static List<Dictionary<string, object?>> MetaRecords(params (string Key, string Value)[] entries) =>
            entries.Select(entry => new Dictionary<string, object?>
            {
                ["key"] = entry.Key,
                ["value"] = entry.Value,
                ["value_type"] = "string",
                ["description"] = "fixture",
            }).ToList();

        private static List<Dictionary<string, object?>> SchemaTableRecords(string dataTableId) =>
        [
            SchemaTableRecord("export_manifest", "table_id"),
            SchemaTableRecord("meta", "key"),
            SchemaTableRecord("schema_tables", "table_id"),
            SchemaTableRecord(dataTableId, dataTableId == "cards" ? "card_id" : "value_id"),
        ];

        private static Dictionary<string, object?> SchemaTableRecord(string tableId, string primaryKey) => new()
        {
            ["table_id"] = tableId,
            ["sheet_name"] = tableId.ToUpperInvariant(),
            ["record_type"] = "fixture",
            ["schema_version"] = "1.0.0",
            ["primary_key"] = primaryKey,
            ["status"] = "active",
            ["notes"] = "fixture",
        };

        private static void WriteTable(
            string directory,
            string fileName,
            string packageId,
            string tableId,
            IEnumerable<Dictionary<string, object?>> records)
        {
            var envelope = new Dictionary<string, object?>
            {
                ["canonical_format"] = CanonicalPackageLoader.CanonicalFormat,
                ["package_id"] = packageId,
                ["table_id"] = tableId,
                ["records"] = records,
            };
            File.WriteAllText(
                Path.Combine(directory, fileName),
                JsonSerializer.Serialize(envelope, new JsonSerializerOptions { WriteIndented = true }));
        }
    }
}
