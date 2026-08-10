using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Headless;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

internal static class CanonicalRuntimeBindingTests
{
    internal static void LegacyV1RequestRemainsCompatible()
    {
        var request = LegacyRequest();
        var json = JsonSerializer.Serialize(request);
        False(json.Contains("canonical_data", StringComparison.Ordinal), "Legacy v1 JSON shape gained a null canonical_data field.");
        var roundTrip = JsonSerializer.Deserialize<CreateMatchRequest>(json)
            ?? throw new InvalidOperationException("Legacy v1 request did not deserialize.");
        Equal(null, roundTrip.CanonicalData, "Omitted canonical_data must deserialize as not configured.");

        var session = new EngineSession();
        var response = session.CreateMatch(roundTrip);
        True(response.Accepted, "Legacy-only v1 CreateMatch was rejected.");
        False(session.GetDebugCanonicalAbilityRuntimeStatus().Available, "Legacy-only session partially enabled canonical runtime.");
    }

    internal static void ValidCanonicalSourceBindsCatalog()
    {
        using var packages = TemporaryCanonicalRuntimePackages.Create();
        var session = new EngineSession();
        var response = session.CreateMatch(WithCanonicalSource(LegacyRequest(), packages));

        True(response.Accepted, "Valid canonical source was rejected.");
        var status = session.GetDebugCanonicalAbilityRuntimeStatus();
        True(status.Available, "Canonical runtime was not bound to the session.");
        Equal("aeterna_registry", status.RegistryPackageId, "Bound REGISTRY identity is invalid.");
        Equal("aeterna_carddatabase", status.CardDatabasePackageId, "Bound CARDDATABASE identity is invalid.");
        Equal(CanonicalPackageValidationMode.Production, status.ValidationMode, "Canonical validation mode is invalid.");
        Equal(7, status.AbilityCount, "Unexpected canonical ability count was bound.");
    }

    internal static void InvalidCanonicalPathsAreRejected()
    {
        using var packages = TemporaryCanonicalRuntimePackages.Create();
        var missingRegistry = new EngineSession().CreateMatch(LegacyRequest() with
        {
            CanonicalData = new CanonicalRuntimeSource(
                Path.Combine(packages.RootDirectory, "missing-registry"),
                packages.CardDatabaseDirectory),
        });
        AssertRejected(missingRegistry, "CANONICAL_RUNTIME_LOAD_FAILED");

        var missingCards = new EngineSession().CreateMatch(LegacyRequest() with
        {
            CanonicalData = new CanonicalRuntimeSource(
                packages.RegistryDirectory,
                Path.Combine(packages.RootDirectory, "missing-carddatabase")),
        });
        AssertRejected(missingCards, "CANONICAL_RUNTIME_LOAD_FAILED");
    }

    internal static void InvalidCanonicalSourceModeIsRejected()
    {
        using var packages = TemporaryCanonicalRuntimePackages.Create();
        var response = new EngineSession().CreateMatch(LegacyRequest() with
        {
            CanonicalData = new CanonicalRuntimeSource(
                packages.RegistryDirectory,
                packages.CardDatabaseDirectory,
                "permissive"),
        });

        AssertRejected(response, "CANONICAL_RUNTIME_SOURCE_INVALID");
    }

    internal static void CanonicalDependencyMismatchIsRejected()
    {
        using var packages = TemporaryCanonicalRuntimePackages.Create(minimumRegistrySchemaVersion: "9.0.0");
        var response = new EngineSession().CreateMatch(WithCanonicalSource(LegacyRequest(), packages));
        AssertRejected(response, "CANONICAL_RUNTIME_LOAD_FAILED");
        Contains(
            response.Diagnostics.Single().DeveloperMessage,
            "CANONICAL_REGISTRY_VERSION_INCOMPATIBLE",
            "Dependency failure did not preserve the loader diagnostic context.");
    }

    internal static void CanonicalMaterializationFailureIsRejected()
    {
        var malformed = CanonicalAbilityCatalogTests.SetField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.Effects,
            "effect_ign_ham_005_01_exhaust_target",
            "target_id",
            "missing_target");
        using var packages = TemporaryCanonicalRuntimePackages.Create(malformed);
        var response = new EngineSession().CreateMatch(WithCanonicalSource(LegacyRequest(), packages));

        AssertRejected(response, "CANONICAL_RUNTIME_MATERIALIZATION_FAILED");
        Contains(
            response.Diagnostics.Single().DeveloperMessage,
            "CANONICAL_ABILITY_REFERENCE_MISSING",
            "Materialization failure did not preserve the canonical diagnostic context.");
    }

    internal static void CanonicalCreationFailureIsAtomic()
    {
        using var packages = TemporaryCanonicalRuntimePackages.Create(minimumRegistrySchemaVersion: "9.0.0");
        var session = new EngineSession();
        AssertRejected(
            session.CreateMatch(WithCanonicalSource(LegacyRequest(), packages)),
            "CANONICAL_RUNTIME_LOAD_FAILED");
        False(session.GetDebugCanonicalAbilityRuntimeStatus().Available, "Failed setup retained a canonical runtime.");

        var retry = session.CreateMatch(LegacyRequest());
        True(retry.Accepted, "Failed canonical setup committed legacy match state.");
        False(session.GetDebugCanonicalAbilityRuntimeStatus().Available, "Legacy retry unexpectedly enabled canonical runtime.");
    }

    internal static void EnteredPlayBridgeAndRealAbilityAreDiscovered()
    {
        var fixture = CreatePlayFixture("IGN-HAM-005", includeCanonicalRuntime: true);
        var response = Play(fixture);
        True(response.Accepted, "IGN-HAM-005 play was rejected.");
        Equal(1, fixture.State.StateVersion, "Trigger discovery added an extra state version.");
        Equal(4, response.Events.Length, "No-target trigger did not emit its authoritative lifecycle events.");
        Equal(
            "zone_move,card_entered_play,canonical_ability_triggered,canonical_ability_resolved",
            string.Join(',', response.Events.Select(item => item.EventType)),
            "No-target trigger lifecycle event order is invalid.");
        Equal("event_card_entered_play", CanonicalTriggerResolver.MapEngineEventType("card_entered_play"), "Engine/canonical event bridge is invalid.");

        var discovery = Single(fixture.Session.GetDebugCanonicalTriggerDiscoveries());
        Equal("ability_ign_ham_005_01", discovery.AbilityId, "Wrong entered-play ability was discovered.");
        Equal("trigger_ign_ham_005_01_entered_play", discovery.TriggerId, "Wrong entered-play trigger was discovered.");
        Equal("event_card_entered_play", discovery.CanonicalEventTypeId, "Canonical event identity is invalid.");
        Equal(fixture.TargetCardInstanceId, discovery.SourceCardInstanceId, "Discovery source instance is invalid.");
        Equal("IGN-HAM-005", discovery.SourceCardId, "Discovery source Card_ID is invalid.");
        Equal("player_1", discovery.ControllerPlayerId, "Ability controller is invalid.");
        Equal(1, discovery.AbilityIndex, "Ability ordering identity is invalid.");
        Equal(1, discovery.TriggerSequence, "Trigger ordering identity is invalid.");

        var card = fixture.State.GetCardInstance(fixture.TargetCardInstanceId);
        Equal("active", card.ActivityState, "Discovery executed the exhaust effect against the source.");
        Equal(0, fixture.State.GetPlayer("player_2").Domain.HorizonCardInstanceIds.Count(value => value is not null), "Discovery selected or mutated an enemy target.");
        Equal(null, fixture.State.PendingTriggerWindow, "No-target trigger created an unresolvable pending window.");
        var resolution = Single(fixture.Session.GetDebugCanonicalAbilityResolutions());
        Equal(CanonicalEffectExecutor.NoLegalTargetOutcome, resolution.ResolutionOutcome, "No-target trigger outcome is invalid.");
        False(
            fixture.Session.GetPlayerSnapshot("player_1").PendingDecisionSummary.GetProperty("has_pending").GetBoolean(),
            "No-target trigger left the public snapshot deadlocked.");
    }

    internal static void KeywordAndResolutionAbilitiesDoNotTrigger()
    {
        var keywordOnly = CreatePlayFixture("IGN-HAM-001", includeCanonicalRuntime: true);
        True(Play(keywordOnly).Accepted, "Keyword-only fixture play was rejected.");
        Equal(0, keywordOnly.Session.GetDebugCanonicalTriggerDiscoveries().Length, "Keyword-only card produced canonical Riadó discovery.");

        var resolution = CreatePlayFixture("AQU-ART-044", includeCanonicalRuntime: true);
        True(Play(resolution).Accepted, "Resolution fixture play was rejected.");
        Equal(0, resolution.Session.GetDebugCanonicalTriggerDiscoveries().Length, "Resolution ability was discovered as a trigger.");
    }

    internal static void DiscoveryIsRestrictedToEnteringCard()
    {
        var fixture = CreatePlayFixture("AQU-MOR-007", includeCanonicalRuntime: true);
        True(Play(fixture).Accepted, "Second triggered-card fixture play was rejected.");
        var discovery = Single(fixture.Session.GetDebugCanonicalTriggerDiscoveries());
        Equal("ability_aqu_mor_007_01", discovery.AbilityId, "Another card's entered-play ability was discovered.");
        False(
            fixture.Session.GetDebugCanonicalTriggerDiscoveries().Any(item => item.AbilityId == "ability_ign_ham_005_01"),
            "IGN-HAM-005 observer trigger leaked into another card's event.");
    }

    internal static void FailedPlayAndLegacyOnlySessionDoNotDiscover()
    {
        var failed = CreatePlayFixture("IGN-HAM-005", includeCanonicalRuntime: true);
        var response = Play(failed, laneIndex: 99);
        False(response.Accepted, "Invalid play was accepted.");
        Equal(0, failed.Session.GetDebugCanonicalTriggerDiscoveries().Length, "Failed play discovered a canonical trigger.");
        Equal(0, failed.State.Events.Count, "Failed play emitted an authoritative event.");

        var legacy = CreatePlayFixture("IGN-HAM-005", includeCanonicalRuntime: false);
        True(Play(legacy).Accepted, "Legacy-only play was rejected.");
        False(legacy.Session.GetDebugCanonicalAbilityRuntimeStatus().Available, "Legacy-only play enabled canonical runtime.");
        Equal(0, legacy.Session.GetDebugCanonicalTriggerDiscoveries().Length, "Legacy-only session attempted canonical discovery.");
    }

    internal static void HandAndStructuralDomainPlacementDoNotDiscover()
    {
        var fixture = CreatePlayFixture("IGN-HAM-005", includeCanonicalRuntime: true);
        Equal(0, fixture.Session.GetDebugCanonicalTriggerDiscoveries().Length, "Card in hand triggered discovery.");

        var player = fixture.State.GetPlayer("player_1");
        var card = fixture.State.GetCardInstance(fixture.TargetCardInstanceId);
        player.HandCardInstanceIds.Remove(fixture.TargetCardInstanceId);
        True(player.Domain.TryOccupy(DomainRow.Horizon, 0, fixture.TargetCardInstanceId), "Structural Domain placement failed.");
        card.Zone = "dominion";
        card.ZoneIndex = -1;
        card.Visibility = "public";
        card.ActivityState = "active";
        card.DomainRow = DomainRow.Horizon;
        card.DomainLaneIndex = 0;
        card.EnteredDomainTurnNumber = fixture.State.TurnNumber;
        card.ZoneSequence += 1;
        EngineSession.ValidateState(fixture.State);

        Equal(0, fixture.State.Events.Count, "Structural placement invented an entered-play event.");
        Equal(0, fixture.Session.GetDebugCanonicalTriggerDiscoveries().Length, "Structural Domain placement triggered discovery.");
    }

    internal static void UnsupportedEventReturnsEmptyAndInvalidSourceIsInvariant()
    {
        Equal(null, CanonicalTriggerResolver.MapEngineEventType("turn_ended"), "Unsupported event acquired a canonical mapping.");
        var fixture = CreatePlayFixture("IGN-HAM-005", includeCanonicalRuntime: true);
        var unsupported = new EngineEvent(
            ContractSchemas.EngineEvent,
            "event_000001",
            1,
            "turn_ended",
            fixture.State.MatchId,
            fixture.State.StateVersion,
            fixture.State.TurnNumber,
            "player_1",
            "end_turn",
            "public",
            ContractJsonValue.EmptyObject());
        Equal(
            0,
            CanonicalTriggerResolver.Resolve(Materialize(), unsupported, fixture.State).Length,
            "Unsupported event returned trigger candidates.");

        fixture.State.StateVersion = 1;
        var invalid = unsupported with
        {
            EventType = "card_entered_play",
            Payload = ContractJsonValue.From(new CardEnteredPlayPayload(
                "play:1",
                "play_card",
                "ci_unknown",
                "IGN-HAM-005",
                "player_1",
                "player_1",
                "horizon",
                0,
                "active",
                1)),
        };
        fixture.State.Events.Add(invalid);
        ThrowsStateCode(
            "CANONICAL_TRIGGER_SOURCE_INVALID",
            () => CanonicalTriggerResolver.Resolve(Materialize(), invalid, fixture.State));
    }

    internal static void DiscoveryResultsAreImmutableAndDeterministic()
    {
        var first = CreatePlayFixture("IGN-HAM-005", includeCanonicalRuntime: true);
        var second = CreatePlayFixture("IGN-HAM-005", includeCanonicalRuntime: true);
        True(Play(first).Accepted && Play(second).Accepted, "Determinism fixture play failed.");

        var firstResult = first.Session.GetDebugCanonicalTriggerDiscoveries();
        var secondResult = second.Session.GetDebugCanonicalTriggerDiscoveries();
        Equal(
            JsonSerializer.Serialize(firstResult),
            JsonSerializer.Serialize(secondResult),
            "Repeated identical discovery was not deterministic.");
        var changedCopy = firstResult.SetItem(0, firstResult[0] with { AbilityId = "mutated-copy" });
        Equal("mutated-copy", changedCopy[0].AbilityId, "Immutable copy proof did not change the copy.");
        Equal(
            "ability_ign_ham_005_01",
            first.Session.GetDebugCanonicalTriggerDiscoveries()[0].AbilityId,
            "Caller mutation changed session discovery history.");
    }

    private static CanonicalAbilityCatalog Materialize() =>
        CanonicalAbilityMaterializer.Materialize(CanonicalAbilityCatalogTests.CreatePackage());

    private static CreateMatchRequest LegacyRequest() =>
        RuntimeComparisonFixture.Load(FixtureLocator.LocateCanonicalFixture()).CreateMatchRequest();

    private static CreateMatchRequest WithCanonicalSource(
        CreateMatchRequest request,
        TemporaryCanonicalRuntimePackages packages) => request with
    {
        CanonicalData = new CanonicalRuntimeSource(
            packages.RegistryDirectory,
            packages.CardDatabaseDirectory),
    };

    private static PlayFixture CreatePlayFixture(string cardId, bool includeCanonicalRuntime)
    {
        var state = new MatchState
        {
            MatchId = "canonical-trigger-test-match",
            Seed = 17,
            RuntimePackageId = "canonical-trigger-legacy-runtime",
            StateVersion = 0,
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        var playerOne = new PlayerState { PlayerId = "player_1", DeckId = "deck_1" };
        var playerTwo = new PlayerState { PlayerId = "player_2", DeckId = "deck_2" };
        state.Players.Add(playerOne);
        state.Players.Add(playerTwo);
        const string instanceId = "ci_player_1_hand_0001";
        state.CardInstances.Add(instanceId, new CardInstanceState
        {
            CardInstanceId = instanceId,
            CardId = cardId,
            OwnerPlayerId = "player_1",
            ControllerPlayerId = "player_1",
            Zone = "hand",
            ZoneIndex = 0,
            Visibility = "owner_only",
            CreatedSequence = 1,
            ZoneSequence = 1,
            InitialZone = "hand",
            ActivityState = null,
        });
        playerOne.HandCardInstanceIds.Add(instanceId);

        var realms = ImmutableDictionary.CreateRange(StringComparer.Ordinal, new Dictionary<string, string>
        {
            ["ignis"] = "ignis",
            ["aqua"] = "aqua",
            ["terra"] = "terra",
            ["lux"] = "lux",
            ["umbra"] = "umbra",
            ["ventus"] = "ventus",
            ["aether"] = "aether",
        });
        var cardTypes = ImmutableDictionary.CreateRange(StringComparer.Ordinal, new Dictionary<string, string>
        {
            ["entity"] = "entity",
            ["incantation"] = "incantation",
            ["ritual"] = "ritual",
            ["sigil"] = "sigil",
            ["plane"] = "plane",
        });
        var lookupGroups = ImmutableDictionary.CreateBuilder<string, RuntimeLookupGroup>(StringComparer.Ordinal);
        lookupGroups.Add("realm", new RuntimeLookupGroup("realm", realms));
        lookupGroups.Add("card_type", new RuntimeLookupGroup("card_type", cardTypes));
        var runtime = new RuntimePackageCatalog(
            state.RuntimePackageId,
            ImmutableDictionary.CreateRange(StringComparer.Ordinal, new[]
            {
                new KeyValuePair<string, RuntimeCardDefinition>(
                    cardId,
                    new RuntimeCardDefinition(cardId, 0, 0, "ignis", "entity")),
            }),
            ImmutableDictionary<string, RuntimeDeckDefinition>.Empty.WithComparers(StringComparer.Ordinal),
            new RuntimeLookupCatalog(lookupGroups.ToImmutable()));
        EngineSession.ValidateState(state);
        var session = includeCanonicalRuntime
            ? new EngineSession(state, runtime, Materialize())
            : new EngineSession(state, runtime);
        return new PlayFixture(session, state, instanceId);
    }

    private static ActionResponse Play(PlayFixture fixture, int laneIndex = 0)
    {
        var action = fixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions
            .Single(item => item.ActionType == "play_card");
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "canonical-trigger-play",
            fixture.State.MatchId,
            "player_1",
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new PlayCardActionPayload(
                fixture.TargetCardInstanceId,
                "horizon",
                laneIndex,
                ImmutableArray<string>.Empty))));
    }

    private static void AssertRejected(CreateMatchResponse response, string code)
    {
        False(response.Accepted, $"CreateMatch unexpectedly accepted {code} fixture.");
        Equal(code, response.Diagnostics.Single().Code, "CreateMatch returned an unexpected diagnostic code.");
        Equal(0, response.StateVersion, "Rejected CreateMatch returned a committed state version.");
    }

    private static void ThrowsStateCode(string code, Action action)
    {
        try
        {
            action();
        }
        catch (EngineStateException exception)
        {
            Equal(code, exception.Code, "Trigger invariant returned an unexpected code.");
            return;
        }

        throw new InvalidOperationException($"Expected EngineStateException with code {code}.");
    }

    private static T Single<T>(IEnumerable<T> values)
    {
        var materialized = values.ToArray();
        Equal(1, materialized.Length, "Expected exactly one item.");
        return materialized[0];
    }

    private static void Contains(string actual, string expected, string message)
    {
        if (!actual.Contains(expected, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void True(bool condition, string message)
    {
        if (!condition)
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void False(bool condition, string message) => True(!condition, message);

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected={expected}; Actual={actual}");
        }
    }

    private sealed record PlayFixture(
        EngineSession Session,
        MatchState State,
        string TargetCardInstanceId);

    private sealed class TemporaryCanonicalRuntimePackages : IDisposable
    {
        private TemporaryCanonicalRuntimePackages(
            CanonicalCardDatabasePackage package,
            string minimumRegistrySchemaVersion)
        {
            RootDirectory = Path.Combine(
                Path.GetTempPath(),
                "aeterna_canonical_runtime_binding_" + Guid.NewGuid().ToString("N"));
            RegistryDirectory = Path.Combine(RootDirectory, "REGISTRY");
            CardDatabaseDirectory = Path.Combine(RootDirectory, "CARDDATABASE");
            Directory.CreateDirectory(RegistryDirectory);
            Directory.CreateDirectory(CardDatabaseDirectory);
            WritePackage(
                RegistryDirectory,
                "registry",
                package.Registry.PackageId,
                package.Registry.SchemaVersion,
                package.Registry.DataVersion,
                CanonicalPackageLoader.RegistryManifestFileName,
                package.Registry.Tables,
                []);
            WritePackage(
                CardDatabaseDirectory,
                "carddatabase",
                package.PackageId,
                package.SchemaVersion,
                package.DataVersion,
                CanonicalPackageLoader.CardDatabaseManifestFileName,
                package.Tables,
                [
                    ("minimum_registry_schema_version", minimumRegistrySchemaVersion),
                    ("minimum_registry_data_version", package.Registry.DataVersion),
                    ("registry_manifest_reference", "../REGISTRY/registry.export_manifest.json"),
                    ("registry_meta_reference", "../REGISTRY/registry.meta.json"),
                ]);
        }

        internal string RootDirectory { get; }

        internal string RegistryDirectory { get; }

        internal string CardDatabaseDirectory { get; }

        internal static TemporaryCanonicalRuntimePackages Create(
            CanonicalCardDatabasePackage? package = null,
            string minimumRegistrySchemaVersion = "0.5.1") =>
            new(package ?? CanonicalAbilityCatalogTests.CreatePackage(), minimumRegistrySchemaVersion);

        public void Dispose() => Directory.Delete(RootDirectory, recursive: true);

        private static void WritePackage(
            string directory,
            string filePrefix,
            string packageId,
            string schemaVersion,
            string dataVersion,
            string manifestFileName,
            ImmutableDictionary<string, CanonicalTable> sourceTables,
            IReadOnlyList<(string Key, string Value)> extraMeta)
        {
            var tables = sourceTables
                .Where(pair => pair.Key is not ("export_manifest" or "meta" or "schema_tables"))
                .OrderBy(pair => pair.Key, StringComparer.Ordinal)
                .ToArray();
            var manifest = new List<Dictionary<string, object?>>
            {
                ManifestRecord("export_manifest", manifestFileName, 1),
                ManifestRecord("meta", $"{filePrefix}.meta.json", 2),
                ManifestRecord("schema_tables", $"{filePrefix}.schema_tables.json", 3),
            };
            for (var index = 0; index < tables.Length; index += 1)
            {
                manifest.Add(ManifestRecord(
                    tables[index].Key,
                    $"{filePrefix}.{tables[index].Key}.json",
                    10 + index));
            }

            WriteTable(directory, manifestFileName, packageId, "export_manifest", manifest);
            var meta = new List<Dictionary<string, object?>>
            {
                MetaRecord("workbook_id", packageId),
                MetaRecord("schema_version", schemaVersion),
                MetaRecord("data_version", dataVersion),
                MetaRecord("export_manifest_file", manifestFileName),
                MetaRecord("null_sentinel", "#NULL"),
                MetaRecord("tbd_sentinel", "#TBD"),
            };
            meta.AddRange(extraMeta.Select(item => MetaRecord(item.Key, item.Value)));
            WriteTable(directory, $"{filePrefix}.meta.json", packageId, "meta", meta);

            var schemaTables = new List<Dictionary<string, object?>>
            {
                SchemaRecord("export_manifest", "table_id"),
                SchemaRecord("meta", "key"),
                SchemaRecord("schema_tables", "table_id"),
            };
            schemaTables.AddRange(tables.Select(pair => SchemaRecord(pair.Key, pair.Value.PrimaryKey)));
            WriteTable(directory, $"{filePrefix}.schema_tables.json", packageId, "schema_tables", schemaTables);
            foreach (var (tableId, table) in tables)
            {
                WriteTable(
                    directory,
                    $"{filePrefix}.{tableId}.json",
                    packageId,
                    tableId,
                    table.Records.Select(record => record.Fields));
            }
        }

        private static Dictionary<string, object?> ManifestRecord(string tableId, string fileName, int order) => new()
        {
            ["table_id"] = tableId,
            ["export_enabled"] = true,
            ["export_file"] = fileName,
            ["export_format"] = "json",
            ["export_order"] = order,
        };

        private static Dictionary<string, object?> MetaRecord(string key, string value) => new()
        {
            ["key"] = key,
            ["value"] = value,
            ["value_type"] = "string",
            ["description"] = "canonical runtime binding fixture",
        };

        private static Dictionary<string, object?> SchemaRecord(string tableId, string primaryKey) => new()
        {
            ["table_id"] = tableId,
            ["sheet_name"] = tableId.ToUpperInvariant(),
            ["record_type"] = "fixture",
            ["schema_version"] = "1.0.0",
            ["primary_key"] = primaryKey,
            ["status"] = "active",
            ["notes"] = "canonical runtime binding fixture",
        };

        private static void WriteTable<T>(
            string directory,
            string fileName,
            string packageId,
            string tableId,
            IEnumerable<T> records)
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
