using System.Collections.Immutable;
using System.Text.Json;
using System.Text.Json.Nodes;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Headless;
using Aeterna.Engine.Rules;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;
using EngineCanonicalJson = Aeterna.Engine.Serialization.CanonicalJson;

internal sealed record ProductionEngineTest(string Name, Action Body);

internal static class ProductionEngineTests
{
    public static IReadOnlyList<ProductionEngineTest> All { get; } =
    [
        new("contract_surface_and_initial_state", ContractSurfaceAndInitialState),
        new("draw_transition_and_event", DrawTransitionAndEvent),
        new("viewer_safe_event_projection", ViewerSafeEventProjection),
        new("invalid_json_contract_inputs_are_rejected", InvalidJsonContractInputsAreRejected),
        new("stale_request_is_immutable", StaleRequestIsImmutable),
        new("end_turn_and_second_draw", EndTurnAndSecondDraw),
        new("player_snapshot_hides_private_information", PlayerSnapshotHidesPrivateInformation),
        new("initial_wellspring_is_empty_and_summarized", InitialWellspringIsEmptyAndSummarized),
        new("active_wellspring_summary", ActiveWellspringSummary),
        new("exhausted_wellspring_summary", ExhaustedWellspringSummary),
        new("mixed_wellspring_summary", MixedWellspringSummary),
        new("wellspring_projection_respects_viewer_visibility", WellspringProjectionRespectsViewerVisibility),
        new("wellspring_projection_is_defensive_and_non_mutating", WellspringProjectionIsDefensiveAndNonMutating),
        new("wellspring_duplicate_instance_is_rejected", WellspringDuplicateInstanceIsRejected),
        new("wellspring_unknown_instance_is_rejected", WellspringUnknownInstanceIsRejected),
        new("wellspring_cross_zone_membership_is_rejected", WellspringCrossZoneMembershipIsRejected),
        new("wellspring_wrong_zone_is_rejected", WellspringWrongZoneIsRejected),
        new("wellspring_wrong_zone_index_is_rejected", WellspringWrongZoneIndexIsRejected),
        new("wellspring_wrong_controller_is_rejected", WellspringWrongControllerIsRejected),
        new("wellspring_wrong_visibility_is_rejected", WellspringWrongVisibilityIsRejected),
        new("wellspring_null_activity_is_rejected", WellspringNullActivityIsRejected),
        new("wellspring_unknown_activity_is_rejected", WellspringUnknownActivityIsRejected),
        new("wellspring_registry_list_mismatch_is_rejected", WellspringRegistryListMismatchIsRejected),
        new("normal_inflow_legal_action_contract", NormalInflowLegalActionContract),
        new("normal_inflow_disabled_reasons_are_stable", NormalInflowDisabledReasonsAreStable),
        new("normal_inflow_payload_rejections_are_immutable", NormalInflowPayloadRejectionsAreImmutable),
        new("normal_inflow_card_reference_rejections_are_immutable", NormalInflowCardReferenceRejectionsAreImmutable),
        new("normal_inflow_registry_list_mismatch_is_rejected", NormalInflowRegistryListMismatchIsRejected),
        new("normal_inflow_stale_request_is_immutable", NormalInflowStaleRequestIsImmutable),
        new("normal_inflow_transition_moves_selected_hand_card", NormalInflowTransitionMovesSelectedHandCard),
        new("normal_inflow_reindexes_hand_and_appends_wellspring", NormalInflowReindexesHandAndAppendsWellspring),
        new("normal_inflow_updates_resource_summary_immediately", NormalInflowUpdatesResourceSummaryImmediately),
        new("normal_inflow_event_visibility_is_safe", NormalInflowEventVisibilityIsSafe),
        new("normal_inflow_is_once_per_turn_and_restores_next_round", NormalInflowIsOncePerTurnAndRestoresNextRound),
        new("end_turn_remains_enabled_without_normal_inflow", EndTurnRemainsEnabledWithoutNormalInflow),
        new("normal_inflow_snapshots_are_defensive_and_non_mutating", NormalInflowSnapshotsAreDefensiveAndNonMutating),
        new("normal_inflow_usage_state_invariants_are_enforced", NormalInflowUsageStateInvariantsAreEnforced),
        new("runtime_card_magnitude_loader_accepts_valid_values", RuntimeCardMagnitudeLoaderAcceptsValidValues),
        new("runtime_card_magnitude_loader_rejects_invalid_values", RuntimeCardMagnitudeLoaderRejectsInvalidValues),
        new("runtime_card_catalog_rejects_invalid_card_references", RuntimeCardCatalogRejectsInvalidCardReferences),
        new("runtime_card_catalog_is_immutable", RuntimeCardCatalogIsImmutable),
        new("runtime_package_catalog_lifecycle_is_atomic", RuntimePackageCatalogLifecycleIsAtomic),
        new("magnitude_preflight_threshold_results", MagnitudePreflightThresholdResults),
        new("magnitude_preflight_counts_all_wellspring_sources", MagnitudePreflightCountsAllWellspringSources),
        new("magnitude_preflight_source_rejections_are_immutable", MagnitudePreflightSourceRejectionsAreImmutable),
        new("magnitude_preflight_hand_mismatch_is_immutable", MagnitudePreflightHandMismatchIsImmutable),
        new("magnitude_preflight_runtime_definition_missing_is_immutable", MagnitudePreflightRuntimeDefinitionMissingIsImmutable),
        new("magnitude_preflight_requires_runtime_catalog", MagnitudePreflightRequiresRuntimeCatalog),
        new("magnitude_preflight_is_pure_deterministic_and_defensive", MagnitudePreflightIsPureDeterministicAndDefensive),
        new("normal_inflow_updates_magnitude_preflight", NormalInflowUpdatesMagnitudePreflight),
        new("public_results_are_defensive", PublicResultsAreDefensive),
        new("canonical_fixture_matches_python_oracle", CanonicalFixtureMatchesPythonOracle),
        new("canonical_fixture_is_deterministic_for_100_runs", CanonicalFixtureIsDeterministicForOneHundredRuns),
        new("fixture_seed_mutation_changes_canonical_result", FixtureSeedMutationChangesCanonicalResult),
        new("invalid_fixture_is_rejected", InvalidFixtureIsRejected),
        new("headless_summary_is_machine_readable", HeadlessSummaryIsMachineReadable),
    ];

    private static void ContractSurfaceAndInitialState()
    {
        var publicSessionMethods = typeof(EngineSession)
            .GetMethods(System.Reflection.BindingFlags.Instance
                | System.Reflection.BindingFlags.Public
                | System.Reflection.BindingFlags.DeclaredOnly)
            .Select(method => method.Name)
            .OrderBy(name => name, StringComparer.Ordinal);
        SequenceEqual(
            ["CreateMatch", "GetEvents", "GetMatchResult", "GetPlayerSnapshot", "ListLegalActions", "SubmitAction"],
            publicSessionMethods,
            "EngineSession public boundary differs from the active contract.");
        var publicEventMethods = typeof(EngineSession)
            .GetMethods(System.Reflection.BindingFlags.Instance
                | System.Reflection.BindingFlags.Public
                | System.Reflection.BindingFlags.DeclaredOnly)
            .Where(method => method.Name == "GetEvents")
            .ToArray();
        Equal(1, publicEventMethods.Length, "EngineSession must expose exactly one production GetEvents route.");
        var eventParameters = publicEventMethods.Single().GetParameters();
        Equal(2, eventParameters.Length, "Production GetEvents parameter count is invalid.");
        Equal(typeof(string), eventParameters[0].ParameterType, "Production GetEvents must require a viewer ID.");
        Equal(false, eventParameters[0].HasDefaultValue, "Production GetEvents viewer ID must not be optional.");
        True(
            typeof(EngineSession).GetMethod(
                "GetDebugEvents",
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic) is not null,
            "Internal debug event history route is missing.");
        True(
            typeof(EngineSession).Assembly
                .GetCustomAttributes(
                    typeof(System.Runtime.CompilerServices.InternalsVisibleToAttribute),
                    inherit: false)
                .Cast<System.Runtime.CompilerServices.InternalsVisibleToAttribute>()
                .All(attribute => !attribute.AssemblyName.StartsWith("Aeterna.Godot", StringComparison.Ordinal)),
            "Godot must not receive internal production engine access.");

        var (session, _, createResponse) = CreateSession();
        Equal(true, createResponse.Accepted, "CreateMatch must accept the canonical fixture.");
        Equal(0, createResponse.StateVersion, "Initial state_version must be zero.");
        Equal(ContractSchemas.CreateMatchResponse, createResponse.SchemaVersion, "Create response schema is invalid.");

        var state = session.GetDebugSnapshot();
        Equal(0, state.StateVersion, "Initial debug state version is invalid.");
        Equal(1, state.TurnNumber, "Initial turn is invalid.");
        Equal("player_1", state.ActivePlayerId, "Initial active player is invalid.");
        Equal(0, state.Events.Length, "Initial event log must be empty.");
        Equal(6, state.CardInstances.Length, "Initial card registry count is invalid.");

        var legal = session.ListLegalActions("player_1", includeDisabled: true);
        SequenceEqual(["end_turn", "normal_inflow", "draw_card"], legal.Actions.Select(item => item.ActionType), "Legal action order is invalid.");
        Equal(3, legal.Actions.Count(item => item.Enabled), "Initial enabled action count is invalid.");
        JsonSerializer.Serialize(createResponse);
        JsonSerializer.Serialize(legal);

        var duplicateCreate = session.CreateMatch(RuntimeComparisonFixture.Load(FixtureLocator.LocateCanonicalFixture()).CreateMatchRequest());
        Equal(false, duplicateCreate.Accepted, "A session must not accept a second match.");
        Equal("MATCH_ALREADY_CREATED", duplicateCreate.Diagnostics.Single().Code, "Duplicate match diagnostic is invalid.");
    }

    private static void DrawTransitionAndEvent()
    {
        var (session, fixture, _) = CreateSession();
        var action = EnabledAction(session, "player_1", "draw_card");
        var response = session.SubmitAction(Request(fixture, action, "test_draw_1", 0));

        Equal(true, response.Accepted, "Draw must be accepted.");
        Equal(0, response.StateVersionBefore, "Draw response before-version is invalid.");
        Equal(1, response.StateVersionAfter, "Draw response after-version is invalid.");
        Equal(1, response.Events.Length, "Draw must emit one event.");
        Equal("zone_move", response.Events[0].EventType, "Draw event type is invalid.");
        Equal(1, response.Events[0].EventSequence, "Draw event sequence is invalid.");
        Equal(1, session.GetDebugEvents().Length, "Session event history is invalid after draw.");

        var player = session.GetDebugSnapshot().Players.Single(item => item.PlayerId == "player_1");
        Equal(2, player.HandCardInstanceIds.Length, "Draw did not add a card to hand.");
        Equal(1, player.DeckCardInstanceIds.Length, "Draw did not remove a card from deck.");
        JsonSerializer.Serialize(response);
    }

    private static void ViewerSafeEventProjection()
    {
        var (session, fixture, _) = CreateSession();
        var draw = EnabledAction(session, "player_1", "draw_card");
        session.SubmitAction(Request(fixture, draw, "viewer_safe_draw", 0));

        var ownerEvent = session.GetEvents("player_1").Single();
        var opponentEvent = session.GetEvents("player_2").Single();
        var debugEvent = session.GetDebugEvents().Single();
        True(ownerEvent.Payload.TryGetProperty("card_instance_id", out _), "Owner event lost card_instance_id.");
        True(ownerEvent.Payload.TryGetProperty("card_id", out _), "Owner event lost card_id.");
        True(debugEvent.Payload.TryGetProperty("card_instance_id", out _), "Internal debug event lost card_instance_id.");
        Equal(false, opponentEvent.Payload.TryGetProperty("card_instance_id", out _), "Opponent event leaked card_instance_id.");
        Equal(false, opponentEvent.Payload.TryGetProperty("card_id", out _), "Opponent event leaked card_id.");
        Equal(true, opponentEvent.Payload.GetProperty("identity_redacted").GetBoolean(), "Opponent event is not marked redacted.");
        Equal(1, opponentEvent.Payload.GetProperty("to_zone_count_delta").GetInt32(), "Opponent draw count delta is invalid.");
        JsonSerializer.Serialize(ownerEvent);
        JsonSerializer.Serialize(opponentEvent);
    }

    private static void InvalidJsonContractInputsAreRejected()
    {
        var fixture = RuntimeComparisonFixture.Load(FixtureLocator.LocateCanonicalFixture());
        var session = new EngineSession();

        var missingCreateRequest = session.CreateMatch(null);
        Equal(false, missingCreateRequest.Accepted, "Missing create request must be rejected.");
        Equal("CREATE_MATCH_REQUEST_MISSING", missingCreateRequest.Diagnostics.Single().Code, "Missing create request diagnostic is invalid.");

        var missingPackage = session.CreateMatch(fixture.CreateMatchRequest() with { RuntimePackage = null! });
        Equal(false, missingPackage.Accepted, "Missing runtime package source must be rejected.");
        Equal("RUNTIME_PACKAGE_SOURCE_MISSING", missingPackage.Diagnostics.Single().Code, "Missing runtime package diagnostic is invalid.");

        var createResponse = session.CreateMatch(fixture.CreateMatchRequest());
        Equal(true, createResponse.Accepted, "Valid create request failed after structured rejections.");
        var draw = EnabledAction(session, "player_1", "draw_card");
        var stateBefore = CanonicalDebugState(session);

        var missingActionRequest = session.SubmitAction(null);
        Equal(false, missingActionRequest.Accepted, "Missing action request must be rejected.");
        Equal("ACTION_REQUEST_MISSING", missingActionRequest.Diagnostics.Single().Code, "Missing action request diagnostic is invalid.");

        var emptyRequestId = session.SubmitAction(Request(fixture, draw, "   ", 0));
        Equal(false, emptyRequestId.Accepted, "Whitespace request_id must be rejected.");
        Equal("ACTION_REQUEST_ID_INVALID", emptyRequestId.Diagnostics.Single().Code, "Whitespace request_id diagnostic is invalid.");

        var missingPayload = session.SubmitAction(Request(fixture, draw, "missing_payload", 0) with
        {
            Payload = default,
        });
        Equal(false, missingPayload.Accepted, "Missing payload must be rejected.");
        Equal("ACTION_PAYLOAD_INVALID", missingPayload.Diagnostics.Single().Code, "Missing payload diagnostic is invalid.");

        using var nullPayloadDocument = JsonDocument.Parse("null");
        var nullPayload = session.SubmitAction(Request(fixture, draw, "null_payload", 0) with
        {
            Payload = nullPayloadDocument.RootElement.Clone(),
        });
        Equal(false, nullPayload.Accepted, "Null payload must be rejected.");
        Equal("ACTION_PAYLOAD_INVALID", nullPayload.Diagnostics.Single().Code, "Null payload diagnostic is invalid.");

        var invalidPayloadShape = session.SubmitAction(Request(fixture, draw, "invalid_payload_shape", 0) with
        {
            Payload = ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["unexpected"] = true,
            }),
        });
        Equal(false, invalidPayloadShape.Accepted, "Unexpected draw payload fields must be rejected.");
        Equal("ACTION_PAYLOAD_INVALID", invalidPayloadShape.Diagnostics.Single().Code, "Payload shape diagnostic is invalid.");
        Equal(stateBefore, CanonicalDebugState(session), "Invalid contract input mutated state.");
        Equal(0, session.GetDebugEvents().Length, "Invalid contract input emitted events.");
    }

    private static void StaleRequestIsImmutable()
    {
        var (session, fixture, _) = CreateSession();
        var draw = EnabledAction(session, "player_1", "draw_card");
        session.SubmitAction(Request(fixture, draw, "test_draw_before_stale", 0));
        var endTurn = EnabledAction(session, "player_1", "end_turn");
        var staleRequest = Request(fixture, endTurn, "test_stale", 0);
        var requestBefore = JsonSerializer.Serialize(staleRequest);
        var stateBefore = CanonicalDebugState(session);
        var eventCountBefore = session.GetDebugEvents().Length;

        var response = session.SubmitAction(staleRequest);

        Equal(false, response.Accepted, "Stale request must be rejected.");
        Equal("stale_state_version", response.Reason, "Stale reason is invalid.");
        Equal(1, response.StateVersionBefore, "Rejected response before-version is invalid.");
        Equal(1, response.StateVersionAfter, "Rejected response after-version is invalid.");
        Equal(0, response.Events.Length, "Rejected request must not emit an event.");
        Equal("STALE_STATE_VERSION", response.Diagnostics.Single().Code, "Stale diagnostic is invalid.");
        Equal(stateBefore, CanonicalDebugState(session), "Stale request mutated state.");
        Equal(eventCountBefore, session.GetDebugEvents().Length, "Stale request mutated event history.");
        Equal(requestBefore, JsonSerializer.Serialize(staleRequest), "Stale request object was mutated.");
    }

    private static void EndTurnAndSecondDraw()
    {
        var (session, fixture, _) = CreateSession();
        session.SubmitAction(Request(fixture, EnabledAction(session, "player_1", "draw_card"), "draw_p1", 0));
        var endResponse = session.SubmitAction(Request(
            fixture,
            EnabledAction(session, "player_1", "end_turn"),
            "end_p1",
            1));
        Equal(true, endResponse.Accepted, "End turn must be accepted.");
        Equal("turn_transition", endResponse.Events.Single().EventType, "End turn event is invalid.");
        Equal("player_2", session.GetDebugSnapshot().ActivePlayerId, "Active player did not change.");

        var secondDrawResponse = session.SubmitAction(Request(
            fixture,
            EnabledAction(session, "player_2", "draw_card"),
            "draw_p2",
            2));
        Equal(true, secondDrawResponse.Accepted, "Player two draw must be accepted.");
        Equal(3, secondDrawResponse.StateVersionAfter, "Final state version is invalid.");
        SequenceEqual([1, 2, 3], session.GetDebugEvents().Select(item => item.EventSequence), "Event sequence is invalid.");
        SequenceEqual(["zone_move", "turn_transition", "zone_move"], session.GetDebugEvents().Select(item => item.EventType), "Event type order is invalid.");
        Equal(false, session.GetMatchResult().Completed, "Minimal match must remain in progress.");
    }

    private static void PlayerSnapshotHidesPrivateInformation()
    {
        var (session, _, _) = CreateSession();
        var snapshot = session.GetPlayerSnapshot("player_1");
        var self = snapshot.Players.Single(item => item.PlayerId == "player_1");
        var opponent = snapshot.Players.Single(item => item.PlayerId == "player_2");

        Equal(self.Hand.Count, self.Hand.Objects.Length, "Own hand must be visible.");
        Equal(false, self.Hand.Redacted, "Own hand must not be redacted.");
        Equal(true, opponent.Hand.Redacted, "Opponent hand must be redacted.");
        Equal(0, opponent.Hand.Objects.Length, "Opponent hand objects leaked.");
        Equal(true, self.Deck.Redacted, "Own deck contents must be redacted.");
        Equal(true, opponent.Deck.Redacted, "Opponent deck contents must be redacted.");
        Equal(0, self.Deck.Objects.Length, "Own deck objects leaked.");
        Equal(0, opponent.Deck.Objects.Length, "Opponent deck objects leaked.");
        JsonSerializer.Serialize(snapshot);
    }

    private static void InitialWellspringIsEmptyAndSummarized()
    {
        var (session, _, _) = CreateSession();
        var debug = session.GetDebugSnapshot();
        True(
            debug.Players.All(player => player.WellspringCardInstanceIds.IsEmpty),
            "Every player must start with an empty Wellspring.");

        var snapshot = session.GetPlayerSnapshot("player_1");
        foreach (var player in snapshot.Players)
        {
            AssertWellspringCounts(player.Wellspring, 0, 0, 0, 0, 0);
        }

        foreach (var summary in snapshot.ResourceSummary.Players)
        {
            AssertWellspringCounts(summary, 0, 0, 0, 0, 0);
        }

        Equal(
            ContractSchemas.ResourceSummary,
            snapshot.ResourceSummary.SchemaVersion,
            "Resource summary schema is invalid.");
        var resourceJson = JsonSerializer.Serialize(snapshot.ResourceSummary);
        True(
            resourceJson.Contains("\"wellspring_card_count\"", StringComparison.Ordinal),
            "Resource summary does not expose the typed Wellspring count.");
        Equal(
            false,
            resourceJson.Contains("not_in_c5b_scope", StringComparison.Ordinal),
            "Resource summary still contains the C.5B placeholder.");
    }

    private static void ActiveWellspringSummary()
    {
        var (session, _) = CreateWellspringSession("active");
        var snapshot = session.GetPlayerSnapshot("player_1");
        AssertWellspringCounts(
            snapshot.Players.Single(player => player.PlayerId == "player_1").Wellspring,
            1,
            1,
            1,
            0,
            1);
        AssertWellspringCounts(
            snapshot.ResourceSummary.Players.Single(summary => summary.PlayerId == "player_1"),
            1,
            1,
            1,
            0,
            1);
    }

    private static void ExhaustedWellspringSummary()
    {
        var (session, _) = CreateWellspringSession("exhausted");
        var snapshot = session.GetPlayerSnapshot("player_1");
        AssertWellspringCounts(
            snapshot.Players.Single(player => player.PlayerId == "player_1").Wellspring,
            1,
            1,
            0,
            1,
            0);
        AssertWellspringCounts(
            snapshot.ResourceSummary.Players.Single(summary => summary.PlayerId == "player_1"),
            1,
            1,
            0,
            1,
            0);
    }

    private static void MixedWellspringSummary()
    {
        var (session, _) = CreateWellspringSession("active", "exhausted", "active");
        var snapshot = session.GetPlayerSnapshot("player_1");
        AssertWellspringCounts(
            snapshot.Players.Single(player => player.PlayerId == "player_1").Wellspring,
            3,
            3,
            2,
            1,
            2);
        AssertWellspringCounts(
            snapshot.ResourceSummary.Players.Single(summary => summary.PlayerId == "player_1"),
            3,
            3,
            2,
            1,
            2);
    }

    private static void WellspringProjectionRespectsViewerVisibility()
    {
        var (session, _) = CreateWellspringSession("active", "exhausted");
        var ownerSnapshot = session.GetPlayerSnapshot("player_1");
        var ownerWellspring = ownerSnapshot.Players
            .Single(player => player.PlayerId == "player_1")
            .Wellspring;
        Equal(false, ownerWellspring.Redacted, "Own Wellspring must not be redacted.");
        Equal("owner_visible", ownerWellspring.VisibilityMode, "Own Wellspring visibility mode is invalid.");
        SequenceEqual(
            ["WELLSPRING-CARD-0001", "WELLSPRING-CARD-0002"],
            ownerWellspring.Objects.Select(card => card.CardId),
            "Own Wellspring card identities are invalid.");
        SequenceEqual(
            ["active", "exhausted"],
            ownerWellspring.Objects.Select(card => card.ActivityState),
            "Own Wellspring activity states are invalid.");
        SequenceEqual(
            ["ci_player_1_wellspring_0001", "ci_player_1_wellspring_0002"],
            session.GetDebugSnapshot().Players
                .Single(player => player.PlayerId == "player_1")
                .WellspringCardInstanceIds,
            "Debug snapshot lost the authoritative Wellspring instance list.");
        var ownerJson = JsonSerializer.Serialize(ownerWellspring);
        True(ownerJson.Contains("\"card_id\"", StringComparison.Ordinal), "Own Wellspring lost card identity.");
        True(ownerJson.Contains("\"activity_state\"", StringComparison.Ordinal), "Own Wellspring lost activity state.");
        Equal(
            false,
            ownerJson.Contains("card_instance_id", StringComparison.Ordinal),
            "Own Wellspring leaked a technical card instance ID.");

        var opponentSnapshot = session.GetPlayerSnapshot("player_2");
        var opponentWellspring = opponentSnapshot.Players
            .Single(player => player.PlayerId == "player_1")
            .Wellspring;
        Equal(true, opponentWellspring.Redacted, "Opponent Wellspring identity must be redacted.");
        Equal("summary_only", opponentWellspring.VisibilityMode, "Opponent Wellspring visibility mode is invalid.");
        Equal(0, opponentWellspring.Objects.Length, "Opponent Wellspring objects leaked.");
        AssertWellspringCounts(opponentWellspring, 2, 2, 1, 1, 1);
        var opponentJson = JsonSerializer.Serialize(opponentWellspring);
        Equal(
            false,
            opponentJson.Contains("\"card_id\"", StringComparison.Ordinal),
            "Opponent Wellspring leaked card_id.");
        Equal(
            false,
            opponentJson.Contains("card_instance_id", StringComparison.Ordinal),
            "Opponent Wellspring leaked card_instance_id.");
    }

    private static void WellspringProjectionIsDefensiveAndNonMutating()
    {
        var (session, state) = CreateWellspringSession("active");
        var stateBeforeProjection = CanonicalDebugState(session);
        var stateVersionBefore = state.StateVersion;
        var eventCountBefore = state.Events.Count;
        var firstSnapshot = session.GetPlayerSnapshot("player_1");
        Equal(
            stateBeforeProjection,
            CanonicalDebugState(session),
            "Wellspring projection mutated authoritative state.");
        Equal(stateVersionBefore, state.StateVersion, "Wellspring projection changed state_version.");
        Equal(eventCountBefore, state.Events.Count, "Wellspring projection emitted an event.");

        AddWellspringCard(state, state.GetPlayer("player_1"), "exhausted");
        EngineSession.ValidateState(state);
        var secondSnapshot = session.GetPlayerSnapshot("player_1");
        var firstWellspring = firstSnapshot.Players
            .Single(player => player.PlayerId == "player_1")
            .Wellspring;
        var secondWellspring = secondSnapshot.Players
            .Single(player => player.PlayerId == "player_1")
            .Wellspring;
        AssertWellspringCounts(firstWellspring, 1, 1, 1, 0, 1);
        AssertWellspringCounts(secondWellspring, 2, 2, 1, 1, 1);
        Equal(1, firstWellspring.Objects.Length, "Earlier Wellspring projection changed after internal state update.");
        Equal(2, secondWellspring.Objects.Length, "Fresh Wellspring projection did not reflect internal state update.");
        Equal(stateVersionBefore, state.StateVersion, "Internal test setup unexpectedly changed state_version.");
        Equal(eventCountBefore, state.Events.Count, "Internal test setup unexpectedly emitted an event.");
    }

    private static void WellspringDuplicateInstanceIsRejected()
    {
        var state = CreateWellspringState("active");
        state.GetPlayer("player_1").WellspringCardInstanceIds.Add("ci_player_1_wellspring_0001");
        AssertStateInvariantRejected(state, "multiple zones", "Duplicate Wellspring membership was accepted.");
    }

    private static void WellspringUnknownInstanceIsRejected()
    {
        var state = CreateWellspringState();
        state.GetPlayer("player_1").WellspringCardInstanceIds.Add("ci_missing");
        AssertStateInvariantRejected(state, "unknown card instance", "Unknown Wellspring instance was accepted.");
    }

    private static void WellspringCrossZoneMembershipIsRejected()
    {
        var state = CreateWellspringState("active");
        state.GetPlayer("player_1").HandCardInstanceIds.Add("ci_player_1_wellspring_0001");
        AssertStateInvariantRejected(state, "multiple zones", "Cross-zone Wellspring membership was accepted.");
    }

    private static void WellspringWrongZoneIsRejected()
    {
        var state = CreateWellspringState("active");
        state.GetCardInstance("ci_player_1_wellspring_0001").Zone = "hand";
        AssertStateInvariantRejected(state, "zone must be wellspring", "Wrong Wellspring registry zone was accepted.");
    }

    private static void WellspringWrongZoneIndexIsRejected()
    {
        var state = CreateWellspringState("active");
        state.GetCardInstance("ci_player_1_wellspring_0001").ZoneIndex = 4;
        AssertStateInvariantRejected(state, "zone index", "Wrong Wellspring zone_index was accepted.");
    }

    private static void WellspringWrongControllerIsRejected()
    {
        var state = CreateWellspringState();
        AddWellspringCard(
            state,
            state.GetPlayer("player_1"),
            "active",
            controllerPlayerId: "player_2");
        AssertStateInvariantRejected(state, "controller", "Wrong Wellspring controller was accepted.");
    }

    private static void WellspringWrongVisibilityIsRejected()
    {
        var state = CreateWellspringState("active");
        state.GetCardInstance("ci_player_1_wellspring_0001").Visibility = "public";
        AssertStateInvariantRejected(state, "visibility", "Wrong Wellspring visibility was accepted.");
    }

    private static void WellspringNullActivityIsRejected()
    {
        var state = CreateWellspringState("active");
        state.GetCardInstance("ci_player_1_wellspring_0001").ActivityState = null;
        AssertStateInvariantRejected(state, "activity state", "Null Wellspring activity was accepted.");
    }

    private static void WellspringUnknownActivityIsRejected()
    {
        var state = CreateWellspringState("active");
        state.GetCardInstance("ci_player_1_wellspring_0001").ActivityState = "ready";
        AssertStateInvariantRejected(state, "activity state", "Unknown Wellspring activity was accepted.");
    }

    private static void WellspringRegistryListMismatchIsRejected()
    {
        var state = CreateWellspringState("active");
        state.GetPlayer("player_1").WellspringCardInstanceIds.Clear();
        AssertStateInvariantRejected(state, "registry and zones disagree", "Wellspring registry/list mismatch was accepted.");
    }

    private static void NormalInflowLegalActionContract()
    {
        var (session, state) = CreateNormalInflowSession(handCount: 1);
        var first = Action(session, "player_1", "normal_inflow", includeDisabled: true);
        var second = Action(session, "player_1", "normal_inflow", includeDisabled: true);

        Equal(true, first.Enabled, "Normal Inflow must be enabled for the active player with a hand card.");
        Equal(null, first.DisabledReason, "Enabled Normal Inflow has a disabled reason.");
        Equal("normal_inflow:1:0:player_1", first.ActionId, "Normal Inflow action_id is not deterministic.");
        Equal(first.ActionId, second.ActionId, "Repeated legal action queries changed the action_id.");
        Equal(150, first.OrderRank, "Normal Inflow action ordering is invalid.");
        Equal(0, state.StateVersion, "Legal action projection changed state_version.");
        Equal(0, state.Events.Count, "Legal action projection emitted an event.");

        var schema = first.PayloadSchema;
        Equal(JsonValueKind.Object, schema.ValueKind, "Normal Inflow payload schema must be an object.");
        SequenceEqual(
            ["additional_properties", "properties", "required", "type"],
            schema.EnumerateObject().Select(property => property.Name).OrderBy(name => name, StringComparer.Ordinal),
            "Normal Inflow payload schema fields are invalid.");
        Equal(false, schema.GetProperty("additional_properties").GetBoolean(), "Extra payload fields must be forbidden.");
        SequenceEqual(
            ["card_instance_id"],
            schema.GetProperty("required").EnumerateArray().Select(item => item.GetString()!),
            "Normal Inflow required payload fields are invalid.");
        var properties = schema.GetProperty("properties");
        Equal(1, properties.EnumerateObject().Count(), "Normal Inflow must expose exactly one payload property.");
        Equal("string", properties.GetProperty("card_instance_id").GetProperty("type").GetString(), "Card selector type is invalid.");
        Equal("hand", properties.GetProperty("card_instance_id").GetProperty("source_zone").GetString(), "Card selector source zone is invalid.");

        var typedPayload = new NormalInflowActionPayload("ci_test");
        var typedPayloadJson = JsonSerializer.Serialize(typedPayload);
        True(typedPayloadJson.Contains("\"card_instance_id\"", StringComparison.Ordinal), "Typed payload is not snake_case.");
        Equal(false, typedPayloadJson.Contains("CardInstanceId", StringComparison.Ordinal), "Typed payload leaked a C# property name.");
    }

    private static void NormalInflowDisabledReasonsAreStable()
    {
        var (session, state) = CreateNormalInflowSession(handCount: 1, playerTwoHandCount: 0);
        var inactive = Action(session, "player_2", "normal_inflow", includeDisabled: true);
        Equal(false, inactive.Enabled, "Inactive player Normal Inflow must be disabled.");
        Equal("not_active_player", inactive.DisabledReason, "Inactive player disabled reason is invalid.");

        var (emptyHandSession, _) = CreateNormalInflowSession(handCount: 0);
        var emptyHand = Action(emptyHandSession, "player_1", "normal_inflow", includeDisabled: true);
        Equal(false, emptyHand.Enabled, "Normal Inflow must be disabled for an empty hand.");
        Equal("hand_empty", emptyHand.DisabledReason, "Empty hand disabled reason is invalid.");

        state.GetPlayer("player_1").NormalInflowUsedTurnNumber = state.TurnNumber;
        EngineSession.ValidateState(state);
        var alreadyUsed = Action(session, "player_1", "normal_inflow", includeDisabled: true);
        Equal(false, alreadyUsed.Enabled, "Normal Inflow must be disabled after use in the current turn.");
        Equal("normal_inflow_already_used", alreadyUsed.DisabledReason, "Already-used disabled reason is invalid.");

        state.GetPlayer("player_2").NormalInflowUsedTurnNumber = state.TurnNumber;
        EngineSession.ValidateState(state);
        var inactivePrecedence = Action(session, "player_2", "normal_inflow", includeDisabled: true);
        Equal("not_active_player", inactivePrecedence.DisabledReason, "Inactive-player reason precedence is unstable.");
    }

    private static void NormalInflowPayloadRejectionsAreImmutable()
    {
        var (session, state) = CreateNormalInflowSession(handCount: 1);
        var action = EnabledAction(session, "player_1", "normal_inflow");
        var cardInstanceId = state.GetPlayer("player_1").HandCardInstanceIds.Single();
        var invalidPayloads = new JsonElement[]
        {
            default,
            JsonSerializer.SerializeToElement<object?>(null),
            ContractJsonValue.From(new[] { cardInstanceId }),
            ContractJsonValue.EmptyObject(),
            ContractJsonValue.From(new Dictionary<string, object?> { ["card_instance_id"] = 42 }),
            ContractJsonValue.From(new Dictionary<string, object?> { ["card_instance_id"] = "   " }),
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["card_instance_id"] = cardInstanceId,
                ["unexpected"] = true,
            }),
        };

        for (var index = 0; index < invalidPayloads.Length; index++)
        {
            var request = Request(
                session,
                action,
                $"normal_inflow_invalid_payload_{index + 1}",
                invalidPayloads[index],
                expectedStateVersion: 0);
            var requestBefore = ActionRequestFingerprint(request);
            var stateBefore = CanonicalDebugState(session);
            var response = session.SubmitAction(request);

            Equal(false, response.Accepted, "Malformed Normal Inflow payload was accepted.");
            Equal("action_payload_invalid", response.Reason, "Malformed payload rejection reason is invalid.");
            Equal("ACTION_PAYLOAD_INVALID", response.Diagnostics.Single().Code, "Malformed payload diagnostic is invalid.");
            Equal(0, response.Events.Length, "Malformed payload emitted an event.");
            Equal(stateBefore, CanonicalDebugState(session), "Malformed payload mutated state.");
            Equal(requestBefore, ActionRequestFingerprint(request), "Malformed payload request was mutated.");
        }

        Equal(0, state.StateVersion, "Malformed payload changed state_version.");
        Equal(0, state.Events.Count, "Malformed payload changed event history.");
    }

    private static void NormalInflowCardReferenceRejectionsAreImmutable()
    {
        var (session, state) = CreateNormalInflowSession(
            handCount: 1,
            deckCount: 1,
            playerTwoHandCount: 1);
        var action = EnabledAction(session, "player_1", "normal_inflow");
        var playerOne = state.GetPlayer("player_1");
        var playerTwo = state.GetPlayer("player_2");
        var cases = new[]
        {
            (CardInstanceId: "ci_missing", Reason: "card_instance_unknown", Code: "NORMAL_INFLOW_CARD_UNKNOWN"),
            (CardInstanceId: playerTwo.HandCardInstanceIds.Single(), Reason: "card_not_owned_or_controlled", Code: "NORMAL_INFLOW_CARD_AUTHORITY_INVALID"),
            (CardInstanceId: playerOne.DeckCardInstanceIds.Single(), Reason: "card_not_in_hand", Code: "NORMAL_INFLOW_CARD_ZONE_INVALID"),
        };

        for (var index = 0; index < cases.Length; index++)
        {
            var stateBefore = CanonicalDebugState(session);
            var response = session.SubmitAction(Request(
                session,
                action,
                $"normal_inflow_invalid_reference_{index + 1}",
                NormalInflowPayload(cases[index].CardInstanceId),
                expectedStateVersion: 0));
            Equal(false, response.Accepted, "Invalid Normal Inflow card reference was accepted.");
            Equal(cases[index].Reason, response.Reason, "Card reference rejection reason is invalid.");
            Equal(cases[index].Code, response.Diagnostics.Single().Code, "Card reference diagnostic is invalid.");
            Equal(stateBefore, CanonicalDebugState(session), "Invalid card reference mutated state.");
            Equal(0, response.Events.Length, "Invalid card reference emitted an event.");
        }

        Equal(0, state.StateVersion, "Invalid card reference changed state_version.");
        Equal(0, state.Events.Count, "Invalid card reference changed event history.");
    }

    private static void NormalInflowRegistryListMismatchIsRejected()
    {
        var (session, state) = CreateNormalInflowSession(handCount: 1);
        var action = EnabledAction(session, "player_1", "normal_inflow");
        var card = state.GetCardInstance(state.GetPlayer("player_1").HandCardInstanceIds.Single());
        card.Zone = "deck";
        var stateBefore = CanonicalDebugState(session);

        try
        {
            session.SubmitAction(Request(
                session,
                action,
                "normal_inflow_registry_list_mismatch",
                NormalInflowPayload(card.CardInstanceId),
                expectedStateVersion: 0));
            throw new InvalidOperationException("Normal Inflow registry/list mismatch was accepted.");
        }
        catch (EngineStateException exception)
        {
            True(exception.Message.Contains("Hand card zone", StringComparison.Ordinal), "Unexpected hand invariant failure.");
        }

        Equal(stateBefore, CanonicalDebugState(session), "Registry/list mismatch path mutated state.");
        Equal(0, state.Events.Count, "Registry/list mismatch path emitted an event.");
    }

    private static void NormalInflowStaleRequestIsImmutable()
    {
        var (session, state) = CreateNormalInflowSession(handCount: 2, deckCount: 1);
        var staleAction = EnabledAction(session, "player_1", "normal_inflow");
        var selectedCardId = state.GetPlayer("player_1").HandCardInstanceIds[0];
        var staleRequest = Request(
            session,
            staleAction,
            "normal_inflow_stale",
            NormalInflowPayload(selectedCardId),
            expectedStateVersion: 0);
        var draw = EnabledAction(session, "player_1", "draw_card");
        var drawResponse = session.SubmitAction(Request(
            session,
            draw,
            "normal_inflow_stale_setup_draw",
            ContractJsonValue.EmptyObject(),
            expectedStateVersion: 0));
        Equal(true, drawResponse.Accepted, "Stale request setup draw failed.");

        var stateBefore = CanonicalDebugState(session);
        var requestBefore = JsonSerializer.Serialize(staleRequest);
        var response = session.SubmitAction(staleRequest);
        Equal(false, response.Accepted, "Stale Normal Inflow request was accepted.");
        Equal("stale_state_version", response.Reason, "Stale Normal Inflow reason is invalid.");
        Equal("STALE_STATE_VERSION", response.Diagnostics.Single().Code, "Stale Normal Inflow diagnostic is invalid.");
        Equal(stateBefore, CanonicalDebugState(session), "Stale Normal Inflow request mutated state.");
        Equal(requestBefore, JsonSerializer.Serialize(staleRequest), "Stale Normal Inflow request object was mutated.");
        Equal(1, state.Events.Count, "Stale Normal Inflow changed event history.");
    }

    private static void NormalInflowTransitionMovesSelectedHandCard()
    {
        var (session, state) = CreateNormalInflowSession(handCount: 1);
        var player = state.GetPlayer("player_1");
        var cardInstanceId = player.HandCardInstanceIds.Single();
        var cardBefore = session.GetDebugSnapshot().CardInstances.Single(card => card.CardInstanceId == cardInstanceId);
        var action = EnabledAction(session, "player_1", "normal_inflow");
        var response = session.SubmitAction(Request(
            session,
            action,
            "normal_inflow_success",
            NormalInflowPayload(cardInstanceId),
            expectedStateVersion: 0));

        Equal(true, response.Accepted, "Normal Inflow must be accepted.");
        Equal(0, response.StateVersionBefore, "Normal Inflow before-version is invalid.");
        Equal(1, response.StateVersionAfter, "Normal Inflow must increment state_version exactly once.");
        Equal(1, response.Events.Length, "Normal Inflow must emit exactly one gameplay event.");
        Equal("zone_move", response.Events.Single().EventType, "Normal Inflow event type is invalid.");
        Equal("normal_inflow", response.Events.Single().CauseActionType, "Normal Inflow event cause is invalid.");
        Equal(0, player.HandCardInstanceIds.Count, "Normal Inflow did not remove the selected hand card.");
        SequenceEqual([cardInstanceId], player.WellspringCardInstanceIds, "Normal Inflow did not append to Wellspring.");
        Equal(1, player.NormalInflowUsedTurnNumber, "Normal Inflow turn usage state is invalid.");

        var cardAfter = session.GetDebugSnapshot().CardInstances.Single(card => card.CardInstanceId == cardInstanceId);
        Equal("wellspring", cardAfter.Zone, "Infused card zone is invalid.");
        Equal(0, cardAfter.ZoneIndex, "Infused card zone index is invalid.");
        Equal("owner_only", cardAfter.Visibility, "Infused card visibility is invalid.");
        Equal("active", cardAfter.ActivityState, "Infused card must enter active.");
        Equal(cardBefore.ZoneSequence + 1, cardAfter.ZoneSequence, "Infused card zone_sequence must increment exactly once.");
        Equal(cardBefore.InitialZone, cardAfter.InitialZone, "Normal Inflow changed initial_zone.");
        Equal(cardBefore.OwnerPlayerId, cardAfter.OwnerPlayerId, "Normal Inflow changed owner.");
        Equal(cardBefore.ControllerPlayerId, cardAfter.ControllerPlayerId, "Normal Inflow changed controller.");
        Equal(0, session.GetDebugInvariantDiagnostics().Length, "Normal Inflow produced an invalid state.");
    }

    private static void NormalInflowReindexesHandAndAppendsWellspring()
    {
        var (session, state) = CreateNormalInflowSession(
            handCount: 3,
            activeWellspringCount: 1,
            exhaustedWellspringCount: 1);
        var player = state.GetPlayer("player_1");
        var initialHand = player.HandCardInstanceIds.ToArray();
        var initialWellspring = player.WellspringCardInstanceIds.ToArray();
        var selected = initialHand[1];
        var response = session.SubmitAction(Request(
            session,
            EnabledAction(session, "player_1", "normal_inflow"),
            "normal_inflow_middle_hand_card",
            NormalInflowPayload(selected),
            expectedStateVersion: 0));
        Equal(true, response.Accepted, "Middle hand card Normal Inflow failed.");

        SequenceEqual([initialHand[0], initialHand[2]], player.HandCardInstanceIds, "Remaining hand order is unstable.");
        SequenceEqual(initialWellspring.Append(selected), player.WellspringCardInstanceIds, "Wellspring append order is unstable.");
        var debug = session.GetDebugSnapshot();
        SequenceEqual(
            [0, 1],
            player.HandCardInstanceIds.Select(id => debug.CardInstances.Single(card => card.CardInstanceId == id).ZoneIndex),
            "Remaining hand indexes are not continuous.");
        var infused = debug.CardInstances.Single(card => card.CardInstanceId == selected);
        Equal(initialWellspring.Length, infused.ZoneIndex, "Infused card was not appended at Wellspring end.");
        Equal("active", infused.ActivityState, "Appended Wellspring card is not active.");
    }

    private static void NormalInflowUpdatesResourceSummaryImmediately()
    {
        var (session, state) = CreateNormalInflowSession(
            handCount: 1,
            activeWellspringCount: 1,
            exhaustedWellspringCount: 1);
        var before = session.GetPlayerSnapshot("player_1");
        AssertWellspringCounts(
            before.Players.Single(player => player.PlayerId == "player_1").Wellspring,
            2,
            2,
            1,
            1,
            1);
        var selected = state.GetPlayer("player_1").HandCardInstanceIds.Single();
        var selectedCardId = state.GetCardInstance(selected).CardId;
        var response = session.SubmitAction(Request(
            session,
            EnabledAction(session, "player_1", "normal_inflow"),
            "normal_inflow_resource_update",
            NormalInflowPayload(selected),
            expectedStateVersion: 0));
        Equal(true, response.Accepted, "Normal Inflow resource update failed.");

        var ownerSnapshot = session.GetPlayerSnapshot("player_1");
        var ownWellspring = ownerSnapshot.Players.Single(player => player.PlayerId == "player_1").Wellspring;
        AssertWellspringCounts(ownWellspring, 3, 3, 2, 1, 2);
        Equal(selectedCardId, ownWellspring.Objects.Last().CardId, "Owner projection lost infused card identity.");
        Equal("active", ownWellspring.Objects.Last().ActivityState, "Freshly infused source is not immediately active.");
        Equal(false, ownWellspring.Objects.Last().ActivityState == "exhausted", "Freshly infused source entered exhausted.");
        AssertWellspringCounts(
            ownerSnapshot.ResourceSummary.Players.Single(player => player.PlayerId == "player_1"),
            3,
            3,
            2,
            1,
            2);

        var opponentView = session.GetPlayerSnapshot("player_2").Players
            .Single(player => player.PlayerId == "player_1")
            .Wellspring;
        Equal(true, opponentView.Redacted, "Opponent Wellspring identity is not redacted after Normal Inflow.");
        Equal(0, opponentView.Objects.Length, "Opponent saw an infused card identity.");
        AssertWellspringCounts(opponentView, 3, 3, 2, 1, 2);
    }

    private static void NormalInflowEventVisibilityIsSafe()
    {
        var (session, state) = CreateNormalInflowSession(handCount: 1);
        var selected = state.GetPlayer("player_1").HandCardInstanceIds.Single();
        var selectedCardId = state.GetCardInstance(selected).CardId;
        var response = session.SubmitAction(Request(
            session,
            EnabledAction(session, "player_1", "normal_inflow"),
            "normal_inflow_visibility",
            NormalInflowPayload(selected),
            expectedStateVersion: 0));
        Equal(true, response.Accepted, "Normal Inflow event setup failed.");

        var ownerEvent = session.GetEvents("player_1").Single();
        var opponentEvent = session.GetEvents("player_2").Single();
        Equal(selected, ownerEvent.Payload.GetProperty("card_instance_id").GetString(), "Owner event lost card_instance_id.");
        Equal(selectedCardId, ownerEvent.Payload.GetProperty("card_id").GetString(), "Owner event lost card_id.");
        Equal("hand", ownerEvent.Payload.GetProperty("from_zone").GetString(), "Owner event source zone is invalid.");
        Equal("wellspring", ownerEvent.Payload.GetProperty("to_zone").GetString(), "Owner event target zone is invalid.");
        Equal(false, opponentEvent.Payload.TryGetProperty("card_instance_id", out _), "Opponent event leaked card_instance_id.");
        Equal(false, opponentEvent.Payload.TryGetProperty("card_id", out _), "Opponent event leaked card_id.");
        Equal("hand", opponentEvent.Payload.GetProperty("from_zone").GetString(), "Opponent event source zone is invalid.");
        Equal("wellspring", opponentEvent.Payload.GetProperty("to_zone").GetString(), "Opponent event target zone is invalid.");
        Equal(-1, opponentEvent.Payload.GetProperty("from_zone_count_delta").GetInt32(), "Opponent source delta is invalid.");
        Equal(1, opponentEvent.Payload.GetProperty("to_zone_count_delta").GetInt32(), "Opponent target delta is invalid.");
        Equal(true, opponentEvent.Payload.GetProperty("identity_redacted").GetBoolean(), "Opponent event lacks redaction marker.");
    }

    private static void NormalInflowIsOncePerTurnAndRestoresNextRound()
    {
        var (session, state) = CreateNormalInflowSession(handCount: 2, playerTwoHandCount: 1);
        var player = state.GetPlayer("player_1");
        var firstSelected = player.HandCardInstanceIds[0];
        var firstResponse = session.SubmitAction(Request(
            session,
            EnabledAction(session, "player_1", "normal_inflow"),
            "normal_inflow_once",
            NormalInflowPayload(firstSelected),
            expectedStateVersion: 0));
        Equal(true, firstResponse.Accepted, "First Normal Inflow failed.");

        var disabled = Action(session, "player_1", "normal_inflow", includeDisabled: true);
        Equal(false, disabled.Enabled, "Second Normal Inflow remained enabled in the same turn.");
        Equal("normal_inflow_already_used", disabled.DisabledReason, "Second Normal Inflow disabled reason is invalid.");
        var stateBeforeSecond = CanonicalDebugState(session);
        var secondResponse = session.SubmitAction(Request(
            session,
            disabled,
            "normal_inflow_twice",
            NormalInflowPayload(player.HandCardInstanceIds.Single()),
            expectedStateVersion: 1));
        Equal(false, secondResponse.Accepted, "Second Normal Inflow was accepted in the same turn.");
        Equal("normal_inflow_already_used", secondResponse.Reason, "Second Normal Inflow rejection reason is invalid.");
        Equal(stateBeforeSecond, CanonicalDebugState(session), "Second Normal Inflow mutated state.");

        var endPlayerOne = session.SubmitAction(Request(
            session,
            EnabledAction(session, "player_1", "end_turn"),
            "normal_inflow_end_player_1",
            ContractJsonValue.EmptyObject(),
            expectedStateVersion: 1));
        Equal(true, endPlayerOne.Accepted, "Player one end_turn failed.");
        var endPlayerTwo = session.SubmitAction(Request(
            session,
            EnabledAction(session, "player_2", "end_turn"),
            "normal_inflow_end_player_2",
            ContractJsonValue.EmptyObject(),
            expectedStateVersion: 2));
        Equal(true, endPlayerTwo.Accepted, "Player two end_turn failed.");
        Equal(2, state.TurnNumber, "Full round did not advance turn_number.");
        Equal(1, player.NormalInflowUsedTurnNumber, "Turn usage history was reset instead of remaining turn-scoped.");

        var nextOwnTurn = EnabledAction(session, "player_1", "normal_inflow");
        Equal("normal_inflow:2:3:player_1", nextOwnTurn.ActionId, "Next own turn action_id is invalid.");
    }

    private static void EndTurnRemainsEnabledWithoutNormalInflow()
    {
        var (session, state) = CreateNormalInflowSession(handCount: 1);
        Equal(true, EnabledAction(session, "player_1", "normal_inflow").Enabled, "Normal Inflow setup is invalid.");
        var handBefore = state.GetPlayer("player_1").HandCardInstanceIds.ToArray();
        var response = session.SubmitAction(Request(
            session,
            EnabledAction(session, "player_1", "end_turn"),
            "end_turn_without_normal_inflow",
            ContractJsonValue.EmptyObject(),
            expectedStateVersion: 0));

        Equal(true, response.Accepted, "end_turn must remain available when Normal Inflow is unused.");
        Equal("turn_transition", response.Events.Single().EventType, "Optional Normal Inflow changed end_turn event semantics.");
        Equal(null, state.GetPlayer("player_1").NormalInflowUsedTurnNumber, "Skipping Normal Inflow created a usage marker.");
        SequenceEqual(handBefore, state.GetPlayer("player_1").HandCardInstanceIds, "end_turn moved a hand card implicitly.");
    }

    private static void NormalInflowSnapshotsAreDefensiveAndNonMutating()
    {
        var (session, state) = CreateNormalInflowSession(handCount: 1);
        var stateBeforeProjection = CanonicalDebugState(session);
        var eventCountBeforeProjection = state.Events.Count;
        var oldDebug = session.GetDebugSnapshot();
        var oldPlayerSnapshot = session.GetPlayerSnapshot("player_1");
        session.GetPlayerSnapshot("player_2");
        session.ListLegalActions("player_1", includeDisabled: true);
        Equal(stateBeforeProjection, CanonicalDebugState(session), "Projection mutated authoritative state.");
        Equal(eventCountBeforeProjection, state.Events.Count, "Projection emitted a gameplay event.");

        var selected = state.GetPlayer("player_1").HandCardInstanceIds.Single();
        var response = session.SubmitAction(Request(
            session,
            EnabledAction(session, "player_1", "normal_inflow"),
            "normal_inflow_snapshot_defensive",
            NormalInflowPayload(selected),
            expectedStateVersion: 0));
        Equal(true, response.Accepted, "Normal Inflow snapshot transition failed.");
        var newDebug = session.GetDebugSnapshot();
        var newPlayerSnapshot = session.GetPlayerSnapshot("player_1");

        Equal(0, oldDebug.Players.Single(player => player.PlayerId == "player_1").WellspringCardInstanceIds.Length, "Old debug snapshot changed.");
        Equal(null, oldDebug.Players.Single(player => player.PlayerId == "player_1").NormalInflowUsedTurnNumber, "Old debug usage state changed.");
        Equal(0, oldPlayerSnapshot.Players.Single(player => player.PlayerId == "player_1").Wellspring.WellspringCardCount, "Old player snapshot changed.");
        Equal(1, newDebug.Players.Single(player => player.PlayerId == "player_1").WellspringCardInstanceIds.Length, "Fresh debug snapshot missed Normal Inflow.");
        Equal(1, newPlayerSnapshot.Players.Single(player => player.PlayerId == "player_1").Wellspring.WellspringCardCount, "Fresh player snapshot missed Normal Inflow.");
    }

    private static void NormalInflowUsageStateInvariantsAreEnforced()
    {
        var state = CreateNormalInflowState(handCount: 1);
        var player = state.GetPlayer("player_1");
        player.NormalInflowUsedTurnNumber = 0;
        AssertStateInvariantRejected(state, "positive", "Zero Normal Inflow usage turn was accepted.");

        player.NormalInflowUsedTurnNumber = 2;
        AssertStateInvariantRejected(state, "future", "Future Normal Inflow usage turn was accepted.");

        player.NormalInflowUsedTurnNumber = 1;
        EngineSession.ValidateState(state);
        player.NormalInflowUsedTurnNumber = null;
        EngineSession.ValidateState(state);
    }

    private static void RuntimeCardMagnitudeLoaderAcceptsValidValues()
    {
        using var package = TemporaryRuntimePackage.Create(
            [
                RuntimeCardJson("CARD-ZERO", 0),
                RuntimeCardJson("CARD-THREE", 3),
            ],
            ["CARD-ZERO", "CARD-THREE"]);

        var catalog = RuntimePackageLoader.Load(package.Source);

        Equal(2, catalog.Cards.Count, "Runtime card definition count is invalid.");
        Equal(0, catalog.Cards["CARD-ZERO"].Magnitude, "Magnitude zero was not preserved.");
        Equal(3, catalog.Cards["CARD-THREE"].Magnitude, "Runtime card magnitude was not preserved.");
        Equal("CARD-THREE", catalog.Cards["CARD-THREE"].CardId, "Runtime card ID was not preserved.");
        SequenceEqual(
            ["CARD-ZERO", "CARD-THREE"],
            catalog.Decks["test-deck"].OrderedCardIds,
            "Deck validation did not use typed runtime card definitions.");
        Equal(
            null,
            typeof(RuntimePackageCatalog).GetProperty("CardIds"),
            "Runtime package catalog retained a second card-ID authority.");
    }

    private static void RuntimeCardMagnitudeLoaderRejectsInvalidValues()
    {
        var invalidRecords = new[]
        {
            RuntimeCardJson("CARD-INVALID", magnitude: null, includeMagnitude: false),
            RuntimeCardJson("CARD-INVALID", magnitude: null),
            RuntimeCardJson("CARD-INVALID", "1"),
            """{"card_id":"CARD-INVALID","magnitude":1.0}""",
            RuntimeCardJson("CARD-INVALID", 1.5),
            RuntimeCardJson("CARD-INVALID", -1),
            RuntimeCardJson("CARD-INVALID", (long)int.MaxValue + 1),
        };

        foreach (var invalidRecord in invalidRecords)
        {
            using var package = TemporaryRuntimePackage.Create([invalidRecord], ["CARD-INVALID"]);
            AssertEngineInputRejected(
                "RUNTIME_PACKAGE_CARD_MAGNITUDE_INVALID",
                () => RuntimePackageLoader.Load(package.Source),
                "Invalid runtime card magnitude was accepted.");
        }
    }

    private static void RuntimeCardCatalogRejectsInvalidCardReferences()
    {
        using (var missingCardId = TemporaryRuntimePackage.Create(
                   [RuntimeCardJson(cardId: null, magnitude: 1, includeCardId: false)],
                   ["CARD-MISSING"]))
        {
            AssertEngineInputRejected(
                "RUNTIME_PACKAGE_FIELD_INVALID",
                () => RuntimePackageLoader.Load(missingCardId.Source),
                "Missing card_id was accepted.");
        }

        using (var emptyCardId = TemporaryRuntimePackage.Create(
                   [RuntimeCardJson("   ", 1)],
                   ["CARD-EMPTY"]))
        {
            AssertEngineInputRejected(
                "RUNTIME_PACKAGE_FIELD_INVALID",
                () => RuntimePackageLoader.Load(emptyCardId.Source),
                "Empty card_id was accepted.");
        }

        using (var duplicate = TemporaryRuntimePackage.Create(
                   [
                       RuntimeCardJson("CARD-DUPLICATE", 1),
                       RuntimeCardJson("CARD-DUPLICATE", 2),
                   ],
                   ["CARD-DUPLICATE"]))
        {
            AssertEngineInputRejected(
                "RUNTIME_PACKAGE_DUPLICATE_CARD",
                () => RuntimePackageLoader.Load(duplicate.Source),
                "Duplicate card_id was accepted.");
        }

        using var unknownDeckCard = TemporaryRuntimePackage.Create(
            [RuntimeCardJson("CARD-KNOWN", 1)],
            ["CARD-UNKNOWN"]);
        AssertEngineInputRejected(
            "RUNTIME_PACKAGE_UNKNOWN_CARD",
            () => RuntimePackageLoader.Load(unknownDeckCard.Source),
            "Unknown deck card reference was accepted.");
    }

    private static void RuntimeCardCatalogIsImmutable()
    {
        using var package = TemporaryRuntimePackage.Create(
            [RuntimeCardJson("CARD-IMMUTABLE", 2)],
            ["CARD-IMMUTABLE"]);
        var catalog = RuntimePackageLoader.Load(package.Source);
        var originalDefinition = catalog.Cards["CARD-IMMUTABLE"];
        var changedDefinition = originalDefinition with { Magnitude = 9 };
        var changedCards = catalog.Cards.SetItem(changedDefinition.CardId, changedDefinition);

        NotSame(catalog.Cards, changedCards, "Immutable card registry returned the same mutated reference.");
        Equal(2, catalog.Cards["CARD-IMMUTABLE"].Magnitude, "Runtime catalog card definition was mutated.");
        Equal(9, changedCards["CARD-IMMUTABLE"].Magnitude, "Detached immutable card registry update failed.");
        Equal(1, catalog.Cards.Count, "Runtime catalog card registry changed externally.");
    }

    private static void RuntimePackageCatalogLifecycleIsAtomic()
    {
        using var invalidPackage = TemporaryRuntimePackage.Create(
            [RuntimeCardJson("CARD-LIFECYCLE", -1)],
            ["CARD-LIFECYCLE"]);
        using var validPackage = TemporaryRuntimePackage.Create(
            [RuntimeCardJson("CARD-LIFECYCLE", 2)],
            ["CARD-LIFECYCLE"]);
        var session = new EngineSession();

        var rejected = session.CreateMatch(CreatePackageMatchRequest(invalidPackage.Source));
        Equal(false, rejected.Accepted, "CreateMatch accepted an invalid magnitude package.");
        Equal(
            "RUNTIME_PACKAGE_CARD_MAGNITUDE_INVALID",
            rejected.Diagnostics.Single().Code,
            "CreateMatch magnitude diagnostic is invalid.");

        var accepted = session.CreateMatch(CreatePackageMatchRequest(validPackage.Source));
        Equal(true, accepted.Accepted, "CreateMatch retained partial state or catalog after rejection.");
        var targetId = session.GetDebugSnapshot().Players
            .Single(player => player.PlayerId == "player_1")
            .HandCardInstanceIds
            .Single();
        var result = session.EvaluateMagnitudePreflight("player_1", targetId);
        Equal(2, result.RequiredMagnitude, "Session did not retain the validated runtime catalog.");
    }

    private static void MagnitudePreflightThresholdResults()
    {
        var evaluator = typeof(EngineSession).GetMethod(
            "EvaluateMagnitudePreflight",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)
            ?? throw new InvalidOperationException("Internal Magnitude preflight evaluator is missing.");
        SequenceEqual(
            [typeof(string), typeof(string)],
            evaluator.GetParameters().Select(parameter => parameter.ParameterType),
            "Magnitude preflight caller can provide unsupported threshold inputs.");
        Equal(false, typeof(MagnitudePreflightResult).IsPublic, "Magnitude preflight result became public.");

        var (zeroSession, _, zeroCardId, _) = CreateMagnitudePreflightSession(
            requiredMagnitude: 0,
            activeWellspringCount: 0,
            exhaustedWellspringCount: 0);
        var zero = zeroSession.EvaluateMagnitudePreflight("player_1", zeroCardId);
        Equal(0, zero.RequiredMagnitude, "Required magnitude zero is invalid.");
        Equal(0, zero.CurrentMagnitude, "Current magnitude zero is invalid.");
        Equal(true, zero.RequirementMet, "Required zero/current zero must pass.");
        Equal(null, zero.FailureReason, "Successful zero threshold has a failure reason.");

        var (belowSession, _, belowCardId, _) = CreateMagnitudePreflightSession(
            requiredMagnitude: 2,
            activeWellspringCount: 1,
            exhaustedWellspringCount: 0);
        var below = belowSession.EvaluateMagnitudePreflight("player_1", belowCardId);
        Equal(2, below.RequiredMagnitude, "Runtime card definition magnitude was not used.");
        Equal(1, below.CurrentMagnitude, "Below-threshold current magnitude is invalid.");
        Equal(false, below.RequirementMet, "Below-threshold magnitude passed.");
        Equal(
            "magnitude_requirement_not_met",
            below.FailureReason,
            "Magnitude threshold failure reason is invalid.");

        var (equalSession, _, equalCardId, _) = CreateMagnitudePreflightSession(
            requiredMagnitude: 2,
            activeWellspringCount: 1,
            exhaustedWellspringCount: 1);
        var equal = equalSession.EvaluateMagnitudePreflight("player_1", equalCardId);
        Equal(true, equal.RequirementMet, "Equal magnitude threshold failed.");
        Equal(null, equal.FailureReason, "Equal threshold has a failure reason.");

        var (aboveSession, _, aboveCardId, _) = CreateMagnitudePreflightSession(
            requiredMagnitude: 1,
            activeWellspringCount: 2,
            exhaustedWellspringCount: 0);
        var above = aboveSession.EvaluateMagnitudePreflight("player_1", aboveCardId);
        Equal(true, above.RequirementMet, "Above-threshold magnitude failed.");
        Equal(null, above.FailureReason, "Above threshold has a failure reason.");
    }

    private static void MagnitudePreflightCountsAllWellspringSources()
    {
        var (mixedSession, _, mixedCardId, _) = CreateMagnitudePreflightSession(
            requiredMagnitude: 2,
            activeWellspringCount: 1,
            exhaustedWellspringCount: 1);
        var mixed = mixedSession.EvaluateMagnitudePreflight("player_1", mixedCardId);
        Equal(2, mixed.CurrentMagnitude, "Active and exhausted Wellspring cards were not both counted.");
        Equal(true, mixed.RequirementMet, "Mixed Wellspring magnitude threshold failed.");

        var (exhaustedSession, _, exhaustedCardId, _) = CreateMagnitudePreflightSession(
            requiredMagnitude: 1,
            activeWellspringCount: 0,
            exhaustedWellspringCount: 1);
        var exhausted = exhaustedSession.EvaluateMagnitudePreflight("player_1", exhaustedCardId);
        var resource = exhaustedSession.GetPlayerSnapshot("player_1").ResourceSummary.Players
            .Single(summary => summary.PlayerId == "player_1");
        Equal(1, exhausted.CurrentMagnitude, "Exhausted Wellspring card did not count toward Magnitude.");
        Equal(0, resource.AvailableAura, "Exhausted-only Wellspring unexpectedly provides Aura.");
        Equal(true, exhausted.RequirementMet, "Available Aura incorrectly affected Magnitude preflight.");
    }

    private static void MagnitudePreflightSourceRejectionsAreImmutable()
    {
        var (unknownSession, _, _, _) = CreateMagnitudePreflightSession(requiredMagnitude: 1);
        AssertMagnitudePreflightRejected(
            unknownSession,
            "player_1",
            "ci_unknown",
            "MAGNITUDE_PREFLIGHT_CARD_UNKNOWN",
            "Unknown card instance was accepted.");

        var authorityState = CreateNormalInflowState(handCount: 1, playerTwoHandCount: 1);
        var authorityCatalog = CreateRuntimeCatalog(authorityState);
        var authoritySession = new EngineSession(authorityState, authorityCatalog);
        var otherPlayerCard = authorityState.GetPlayer("player_2").HandCardInstanceIds.Single();
        AssertMagnitudePreflightRejected(
            authoritySession,
            "player_1",
            otherPlayerCard,
            "MAGNITUDE_PREFLIGHT_CARD_AUTHORITY_INVALID",
            "Another player's card was accepted.");

        var zoneState = CreateNormalInflowState(handCount: 1, deckCount: 1);
        var zoneCatalog = CreateRuntimeCatalog(zoneState);
        var zoneSession = new EngineSession(zoneState, zoneCatalog);
        var deckCard = zoneState.GetPlayer("player_1").DeckCardInstanceIds.Single();
        AssertMagnitudePreflightRejected(
            zoneSession,
            "player_1",
            deckCard,
            "MAGNITUDE_PREFLIGHT_CARD_ZONE_INVALID",
            "Non-hand card was accepted.");
    }

    private static void MagnitudePreflightHandMismatchIsImmutable()
    {
        var (session, state, cardInstanceId, _) = CreateMagnitudePreflightSession(requiredMagnitude: 1);
        state.GetCardInstance(cardInstanceId).ZoneIndex = 9;

        AssertMagnitudePreflightRejected(
            session,
            "player_1",
            cardInstanceId,
            "MAGNITUDE_PREFLIGHT_HAND_MEMBERSHIP_INVALID",
            "Hand registry/list mismatch was accepted.");
    }

    private static void MagnitudePreflightRuntimeDefinitionMissingIsImmutable()
    {
        var state = CreateNormalInflowState(handCount: 2);
        var targetId = state.GetPlayer("player_1").HandCardInstanceIds[0];
        var targetCardId = state.GetCardInstance(targetId).CardId;
        var catalog = CreateRuntimeCatalog(state, excludedCardIds: [targetCardId]);
        var session = new EngineSession(state, catalog);

        AssertMagnitudePreflightRejected(
            session,
            "player_1",
            targetId,
            "MAGNITUDE_PREFLIGHT_RUNTIME_CARD_MISSING",
            "Missing runtime card definition was treated as a threshold result.");
    }

    private static void MagnitudePreflightRequiresRuntimeCatalog()
    {
        var state = CreateNormalInflowState(handCount: 1);
        var session = new EngineSession(state);
        var targetId = state.GetPlayer("player_1").HandCardInstanceIds.Single();

        AssertMagnitudePreflightRejected(
            session,
            "player_1",
            targetId,
            "MAGNITUDE_PREFLIGHT_RUNTIME_PACKAGE_MISSING",
            "Magnitude preflight ran without a runtime package catalog.");
    }

    private static void MagnitudePreflightIsPureDeterministicAndDefensive()
    {
        var (session, state, targetId, _) = CreateMagnitudePreflightSession(
            requiredMagnitude: 2,
            handCount: 2,
            activeWellspringCount: 1);
        var stateBefore = CanonicalDebugState(session);
        var actionSpaceBefore = JsonSerializer.Serialize(session.ListLegalActions("player_1", includeDisabled: true));
        var eventsBefore = session.GetDebugEvents().Length;
        var first = session.EvaluateMagnitudePreflight("player_1", targetId);
        var second = session.EvaluateMagnitudePreflight("player_1", targetId);

        Equal(first, second, "Repeated Magnitude preflight query is not deterministic.");
        Equal(stateBefore, CanonicalDebugState(session), "Magnitude preflight mutated MatchState.");
        Equal(0, state.StateVersion, "Magnitude preflight changed state_version.");
        Equal(eventsBefore, session.GetDebugEvents().Length, "Magnitude preflight emitted an event.");
        Equal(
            actionSpaceBefore,
            JsonSerializer.Serialize(session.ListLegalActions("player_1", includeDisabled: true)),
            "Magnitude preflight changed legal action space.");
        Equal(null, state.GetPlayer("player_1").NormalInflowUsedTurnNumber, "Magnitude preflight changed Inflow state.");

        var otherCardId = state.GetPlayer("player_1").HandCardInstanceIds
            .Single(cardInstanceId => !string.Equals(cardInstanceId, targetId, StringComparison.Ordinal));
        var inflow = session.SubmitAction(Request(
            session,
            EnabledAction(session, "player_1", "normal_inflow"),
            "magnitude_preflight_defensive_transition",
            NormalInflowPayload(otherCardId),
            expectedStateVersion: 0));
        Equal(true, inflow.Accepted, "Defensive-result transition setup failed.");
        var after = session.EvaluateMagnitudePreflight("player_1", targetId);
        Equal(1, first.CurrentMagnitude, "Previously returned result changed after transition.");
        Equal(false, first.RequirementMet, "Previously returned threshold result changed after transition.");
        Equal(2, after.CurrentMagnitude, "Fresh preflight did not observe the later transition.");
        Equal(true, after.RequirementMet, "Fresh preflight did not pass after Magnitude increased.");
    }

    private static void NormalInflowUpdatesMagnitudePreflight()
    {
        var (session, state, targetId, _) = CreateMagnitudePreflightSession(
            requiredMagnitude: 1,
            handCount: 2);
        var before = session.EvaluateMagnitudePreflight("player_1", targetId);
        Equal(0, before.CurrentMagnitude, "Pre-Inflow Magnitude is invalid.");
        Equal(false, before.RequirementMet, "Required one/current zero unexpectedly passed.");
        Equal(0, session.GetDebugEvents().Length, "Preflight emitted an event before Inflow.");

        var inflowCardId = state.GetPlayer("player_1").HandCardInstanceIds
            .Single(cardInstanceId => !string.Equals(cardInstanceId, targetId, StringComparison.Ordinal));
        var response = session.SubmitAction(Request(
            session,
            EnabledAction(session, "player_1", "normal_inflow"),
            "magnitude_preflight_inflow",
            NormalInflowPayload(inflowCardId),
            expectedStateVersion: 0));
        Equal(true, response.Accepted, "Normal Inflow integration setup failed.");
        Equal(1, response.Events.Length, "Normal Inflow integration emitted an unexpected event count.");

        var after = session.EvaluateMagnitudePreflight("player_1", targetId);
        var infusedCard = state.GetCardInstance(inflowCardId);
        var resource = session.GetPlayerSnapshot("player_1").ResourceSummary.Players
            .Single(summary => summary.PlayerId == "player_1");
        Equal(1, after.CurrentMagnitude, "Normal Inflow did not increase Magnitude.");
        Equal(true, after.RequirementMet, "Normal Inflow did not satisfy the Magnitude threshold.");
        Equal("active", infusedCard.ActivityState, "Normal Inflow integration source is not active.");
        Equal(1, resource.AvailableAura, "Active Inflow source did not update available Aura.");
        Equal(1, session.GetDebugEvents().Length, "Post-Inflow preflight emitted an extra event.");
    }

    private static void PublicResultsAreDefensive()
    {
        var (session, fixture, _) = CreateSession();
        var firstActions = session.ListLegalActions("player_1", includeDisabled: true);
        var secondActions = session.ListLegalActions("player_1", includeDisabled: true);
        NotSame(firstActions, secondActions, "Legal action spaces must be independent projections.");
        NotSame(firstActions.Actions[0], secondActions.Actions[0], "Legal action records must be cloned.");

        var firstSnapshot = session.GetPlayerSnapshot("player_1");
        var secondSnapshot = session.GetPlayerSnapshot("player_1");
        NotSame(firstSnapshot, secondSnapshot, "Player snapshots must be independent projections.");
        NotSame(firstSnapshot.Players[0], secondSnapshot.Players[0], "Player projection records must be independent.");
        var originalHandCount = firstSnapshot.Players.Single(item => item.PlayerId == "player_1").Hand.Count;
        session.SubmitAction(Request(
            fixture,
            EnabledAction(session, "player_1", "draw_card"),
            "defensive_snapshot_draw",
            expectedStateVersion: 0));
        Equal(originalHandCount, firstSnapshot.Players.Single(item => item.PlayerId == "player_1").Hand.Count, "Earlier snapshot changed after a transition.");
        Equal(originalHandCount + 1, session.GetPlayerSnapshot("player_1").Players.Single(item => item.PlayerId == "player_1").Hand.Count, "Fresh snapshot did not reflect the transition.");

        var firstResult = session.GetMatchResult();
        var secondResult = session.GetMatchResult();
        NotSame(firstResult, secondResult, "Match result must be returned defensively.");
    }

    private static void CanonicalFixtureMatchesPythonOracle()
    {
        var fixturePath = FixtureLocator.LocateCanonicalFixture();
        var production = RuntimeComparisonFixtureRunner.Run(fixturePath);

        Equal(RuntimeComparisonFixtureRunner.ExpectedCanonicalByteCount, production.CanonicalByteCount, "Production canonical byte count is invalid.");
        Equal(RuntimeComparisonFixtureRunner.ExpectedCanonicalSha256, production.Sha256, "Production canonical SHA differs from the Python oracle.");
    }

    private static void CanonicalFixtureIsDeterministicForOneHundredRuns()
    {
        var fixturePath = FixtureLocator.LocateCanonicalFixture();
        var first = RuntimeComparisonFixtureRunner.Run(fixturePath);
        for (var index = 1; index < 100; index++)
        {
            var current = RuntimeComparisonFixtureRunner.Run(fixturePath);
            Equal(first.Sha256, current.Sha256, $"Determinism SHA mismatch at run {index + 1}.");
            True(first.CanonicalBytes.AsSpan().SequenceEqual(current.CanonicalBytes), $"Determinism byte mismatch at run {index + 1}.");
        }
    }

    private static void FixtureSeedMutationChangesCanonicalResult()
    {
        var fixture = RuntimeComparisonFixture.Load(FixtureLocator.LocateCanonicalFixture());
        var baseline = RuntimeComparisonFixtureRunner.Run(fixture);
        var mutated = RuntimeComparisonFixtureRunner.Run(fixture with { Seed = 2 });

        NotEqual(baseline.Sha256, mutated.Sha256, "Seed mutation must change the canonical SHA.");
        NotEqual(RuntimeComparisonFixtureRunner.ExpectedCanonicalSha256, mutated.Sha256, "Mutated fixture must fail the canonical SHA gate.");
        True(!baseline.CanonicalBytes.AsSpan().SequenceEqual(mutated.CanonicalBytes), "Seed mutation must change canonical bytes.");
        var summary = RuntimeComparisonFixtureRunner.BuildProofSummary(mutated, 1, deterministic: true);
        Equal(false, summary["ok"]!.GetValue<bool>(), "Mutated fixture must fail the proof summary.");
        Equal("CANONICAL_SHA_MISMATCH", summary["error_code"]!.GetValue<string>(), "Mutation failure code is invalid.");
    }

    private static void InvalidFixtureIsRejected()
    {
        try
        {
            RuntimeComparisonFixture.Load(Path.Combine(Path.GetTempPath(), "aeterna-c5b-missing-fixture.json"));
            throw new InvalidOperationException("Missing fixture was unexpectedly accepted.");
        }
        catch (RuntimeComparisonFixtureException exception)
        {
            Equal("FIXTURE_NOT_FOUND", exception.Code, "Missing fixture diagnostic code is invalid.");
        }
    }

    private static void HeadlessSummaryIsMachineReadable()
    {
        var result = RuntimeComparisonFixtureRunner.Run(FixtureLocator.LocateCanonicalFixture());
        var summary = RuntimeComparisonFixtureRunner.BuildProofSummary(result, 1, deterministic: true);
        var compact = EngineCanonicalJson.Compact(summary);
        var parsed = JsonNode.Parse(compact)?.AsObject()
            ?? throw new InvalidOperationException("Headless summary is not JSON.");

        Equal(true, parsed["ok"]!.GetValue<bool>(), "Headless summary did not pass.");
        Equal(true, parsed["direct_in_process"]!.GetValue<bool>(), "Headless summary did not prove in-process execution.");
        Equal(false, parsed["python_process_started"]!.GetValue<bool>(), "Headless summary reported a Python process.");
        Equal(false, parsed["tcp_listener_used"]!.GetValue<bool>(), "Headless summary reported a TCP listener.");
    }

    private static (EngineSession Session, RuntimeComparisonFixture Fixture, CreateMatchResponse Response) CreateSession()
    {
        var fixture = RuntimeComparisonFixture.Load(FixtureLocator.LocateCanonicalFixture());
        var session = new EngineSession();
        var response = session.CreateMatch(fixture.CreateMatchRequest());
        return (session, fixture, response);
    }

    private static CreateMatchRequest CreatePackageMatchRequest(RuntimePackageSource source) => new(
        ContractSchemas.CreateMatchRequest,
        "runtime-package-lifecycle-test-match",
        Seed: 1,
        ImmutableArray.Create(
            new PlayerSetup("player_1", "test-deck"),
            new PlayerSetup("player_2", "test-deck")),
        StartingHandSize: 1,
        source);

    private static (
        EngineSession Session,
        MatchState State,
        string TargetCardInstanceId,
        RuntimePackageCatalog Catalog) CreateMagnitudePreflightSession(
            int requiredMagnitude,
            int handCount = 1,
            int deckCount = 0,
            int playerTwoHandCount = 0,
            int activeWellspringCount = 0,
            int exhaustedWellspringCount = 0)
    {
        var state = CreateNormalInflowState(
            handCount,
            deckCount,
            playerTwoHandCount,
            activeWellspringCount,
            exhaustedWellspringCount);
        var targetCardInstanceId = state.GetPlayer("player_1").HandCardInstanceIds.First();
        var targetCardId = state.GetCardInstance(targetCardInstanceId).CardId;
        var catalog = CreateRuntimeCatalog(
            state,
            new Dictionary<string, int>(StringComparer.Ordinal)
            {
                [targetCardId] = requiredMagnitude,
            });
        return (new EngineSession(state, catalog), state, targetCardInstanceId, catalog);
    }

    private static RuntimePackageCatalog CreateRuntimeCatalog(
        MatchState state,
        IReadOnlyDictionary<string, int>? magnitudes = null,
        IReadOnlyCollection<string>? excludedCardIds = null)
    {
        var cards = ImmutableDictionary.CreateBuilder<string, RuntimeCardDefinition>(StringComparer.Ordinal);
        foreach (var card in state.CardInstances.Values
                     .OrderBy(item => item.CardId, StringComparer.Ordinal))
        {
            if (excludedCardIds?.Contains(card.CardId) == true || cards.ContainsKey(card.CardId))
            {
                continue;
            }

            var magnitude = magnitudes is not null && magnitudes.TryGetValue(card.CardId, out var required)
                ? required
                : 0;
            cards.Add(card.CardId, new RuntimeCardDefinition(card.CardId, magnitude));
        }

        return new RuntimePackageCatalog(
            state.RuntimePackageId,
            cards.ToImmutable(),
            ImmutableDictionary.Create<string, RuntimeDeckDefinition>(StringComparer.Ordinal));
    }

    private static (EngineSession Session, MatchState State) CreateNormalInflowSession(
        int handCount,
        int deckCount = 0,
        int playerTwoHandCount = 0,
        int activeWellspringCount = 0,
        int exhaustedWellspringCount = 0)
    {
        var state = CreateNormalInflowState(
            handCount,
            deckCount,
            playerTwoHandCount,
            activeWellspringCount,
            exhaustedWellspringCount);
        return (new EngineSession(state), state);
    }

    private static MatchState CreateNormalInflowState(
        int handCount,
        int deckCount = 0,
        int playerTwoHandCount = 0,
        int activeWellspringCount = 0,
        int exhaustedWellspringCount = 0)
    {
        var state = new MatchState
        {
            MatchId = "production-normal-inflow-test-match",
            Seed = 1,
            RuntimePackageId = "production-normal-inflow-test-package",
            StateVersion = 0,
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        var playerOne = new PlayerState
        {
            PlayerId = "player_1",
            DeckId = "test-deck-player-1",
        };
        var playerTwo = new PlayerState
        {
            PlayerId = "player_2",
            DeckId = "test-deck-player-2",
        };
        state.Players.Add(playerOne);
        state.Players.Add(playerTwo);
        for (var index = 0; index < handCount; index++)
        {
            AddPrivateZoneCard(state, playerOne, "hand");
        }

        for (var index = 0; index < deckCount; index++)
        {
            AddPrivateZoneCard(state, playerOne, "deck");
        }

        for (var index = 0; index < playerTwoHandCount; index++)
        {
            AddPrivateZoneCard(state, playerTwo, "hand");
        }

        for (var index = 0; index < activeWellspringCount; index++)
        {
            AddWellspringCard(state, playerOne, "active");
        }

        for (var index = 0; index < exhaustedWellspringCount; index++)
        {
            AddWellspringCard(state, playerOne, "exhausted");
        }

        EngineSession.ValidateState(state);
        return state;
    }

    private static string AddPrivateZoneCard(MatchState state, PlayerState player, string zone)
    {
        var zoneList = zone switch
        {
            "hand" => player.HandCardInstanceIds,
            "deck" => player.DeckCardInstanceIds,
            _ => throw new ArgumentOutOfRangeException(nameof(zone)),
        };
        var zoneIndex = zoneList.Count;
        var cardInstanceId = $"ci_{player.PlayerId}_{zone}_{zoneIndex + 1:0000}";
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = $"{zone.ToUpperInvariant()}-CARD-{zoneIndex + 1:0000}",
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = zone,
            ZoneIndex = zoneIndex,
            Visibility = "owner_only",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = zone,
            ActivityState = null,
        });
        zoneList.Add(cardInstanceId);
        return cardInstanceId;
    }

    private static (EngineSession Session, MatchState State) CreateWellspringSession(
        params string[] activityStates)
    {
        var state = CreateWellspringState(activityStates);
        return (new EngineSession(state), state);
    }

    private static MatchState CreateWellspringState(params string[] activityStates)
    {
        var state = new MatchState
        {
            MatchId = "production-wellspring-test-match",
            Seed = 1,
            RuntimePackageId = "production-wellspring-test-package",
            StateVersion = 0,
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        var playerOne = new PlayerState
        {
            PlayerId = "player_1",
            DeckId = "test-deck-player-1",
        };
        var playerTwo = new PlayerState
        {
            PlayerId = "player_2",
            DeckId = "test-deck-player-2",
        };
        state.Players.Add(playerOne);
        state.Players.Add(playerTwo);
        foreach (var activityState in activityStates)
        {
            AddWellspringCard(state, playerOne, activityState);
        }

        EngineSession.ValidateState(state);
        return state;
    }

    private static string AddWellspringCard(
        MatchState state,
        PlayerState player,
        string activityState,
        string? controllerPlayerId = null)
    {
        var zoneIndex = player.WellspringCardInstanceIds.Count;
        var cardInstanceId = $"ci_{player.PlayerId}_wellspring_{zoneIndex + 1:0000}";
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = $"WELLSPRING-CARD-{zoneIndex + 1:0000}",
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = controllerPlayerId ?? player.PlayerId,
            Zone = "wellspring",
            ZoneIndex = zoneIndex,
            Visibility = "owner_only",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "wellspring",
            ActivityState = activityState,
        });
        player.WellspringCardInstanceIds.Add(cardInstanceId);
        return cardInstanceId;
    }

    private static void AssertWellspringCounts(
        WellspringProjection projection,
        int cardCount,
        int magnitude,
        int activeSourceCount,
        int exhaustedSourceCount,
        int availableAura)
    {
        Equal(cardCount, projection.WellspringCardCount, "Wellspring projection card count is invalid.");
        Equal(magnitude, projection.Magnitude, "Wellspring projection magnitude is invalid.");
        Equal(activeSourceCount, projection.ActiveSourceCount, "Wellspring projection active count is invalid.");
        Equal(exhaustedSourceCount, projection.ExhaustedSourceCount, "Wellspring projection exhausted count is invalid.");
        Equal(availableAura, projection.AvailableAura, "Wellspring projection available Aura is invalid.");
        Equal(
            projection.WellspringCardCount,
            projection.ActiveSourceCount + projection.ExhaustedSourceCount,
            "Wellspring projection activity counts do not match its card count.");
    }

    private static void AssertWellspringCounts(
        WellspringResourceSummary summary,
        int cardCount,
        int magnitude,
        int activeSourceCount,
        int exhaustedSourceCount,
        int availableAura)
    {
        Equal(cardCount, summary.WellspringCardCount, "Wellspring resource card count is invalid.");
        Equal(magnitude, summary.Magnitude, "Wellspring resource magnitude is invalid.");
        Equal(activeSourceCount, summary.ActiveSourceCount, "Wellspring resource active count is invalid.");
        Equal(exhaustedSourceCount, summary.ExhaustedSourceCount, "Wellspring resource exhausted count is invalid.");
        Equal(availableAura, summary.AvailableAura, "Wellspring resource available Aura is invalid.");
        Equal(
            summary.WellspringCardCount,
            summary.ActiveSourceCount + summary.ExhaustedSourceCount,
            "Wellspring resource activity counts do not match its card count.");
    }

    private static void AssertStateInvariantRejected(
        MatchState state,
        string expectedMessageFragment,
        string message)
    {
        try
        {
            EngineSession.ValidateState(state);
        }
        catch (EngineStateException exception)
        {
            True(
                exception.Message.Contains(expectedMessageFragment, StringComparison.OrdinalIgnoreCase),
                $"{message} Unexpected invariant: {exception.Message}");
            return;
        }

        throw new InvalidOperationException(message);
    }

    private static void AssertEngineInputRejected(
        string expectedCode,
        Action action,
        string message)
    {
        try
        {
            action();
        }
        catch (EngineInputException exception)
        {
            Equal(expectedCode, exception.Code, $"{message} Unexpected diagnostic code.");
            return;
        }

        throw new InvalidOperationException(message);
    }

    private static void AssertMagnitudePreflightRejected(
        EngineSession session,
        string playerId,
        string cardInstanceId,
        string expectedCode,
        string message)
    {
        var stateBefore = CanonicalDebugState(session);
        var eventCountBefore = session.GetDebugEvents().Length;
        try
        {
            session.EvaluateMagnitudePreflight(playerId, cardInstanceId);
        }
        catch (MagnitudePreflightException exception)
        {
            Equal(expectedCode, exception.Code, $"{message} Unexpected preflight error code.");
            Equal(stateBefore, CanonicalDebugState(session), $"{message} Rejection mutated state.");
            Equal(eventCountBefore, session.GetDebugEvents().Length, $"{message} Rejection emitted an event.");
            return;
        }

        throw new InvalidOperationException(message);
    }

    private static string RuntimeCardJson(
        string? cardId,
        object? magnitude,
        bool includeCardId = true,
        bool includeMagnitude = true)
    {
        var record = new Dictionary<string, object?>();
        if (includeCardId)
        {
            record["card_id"] = cardId;
        }

        if (includeMagnitude)
        {
            record["magnitude"] = magnitude;
        }

        return JsonSerializer.Serialize(record);
    }

    private static string LocateRepositoryRoot()
    {
        var directory = new DirectoryInfo(
            Path.GetDirectoryName(FixtureLocator.LocateCanonicalFixture())
            ?? throw new InvalidOperationException("Canonical fixture directory is missing."));
        while (directory is not null)
        {
            if (Directory.Exists(Path.Combine(directory.FullName, ".git")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        throw new DirectoryNotFoundException("AETERNA repository root could not be located.");
    }

    private sealed class TemporaryRuntimePackage : IDisposable
    {
        private const string PackageId = "production-magnitude-loader-test-package";

        private TemporaryRuntimePackage(string packageDirectory)
        {
            PackageDirectory = packageDirectory;
        }

        internal string PackageDirectory { get; }

        internal RuntimePackageSource Source => new(PackageDirectory, PackageId);

        internal static TemporaryRuntimePackage Create(
            IReadOnlyList<string> cardRecords,
            IReadOnlyList<string> deckCardIds)
        {
            var parentDirectory = Path.Combine(
                LocateRepositoryRoot(),
                "TEMP",
                "production_engine_tests");
            var packageDirectory = Path.Combine(parentDirectory, Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(packageDirectory);
            File.WriteAllText(
                Path.Combine(packageDirectory, "manifest.json"),
                JsonSerializer.Serialize(new Dictionary<string, object?>
                {
                    ["package_id"] = PackageId,
                }));
            File.WriteAllLines(
                Path.Combine(packageDirectory, "cards.jsonl"),
                cardRecords);
            File.WriteAllText(
                Path.Combine(packageDirectory, "decks.jsonl"),
                JsonSerializer.Serialize(new Dictionary<string, object?>
                {
                    ["deck_id"] = "test-deck",
                    ["card_entries"] = deckCardIds.Select(cardId =>
                        new Dictionary<string, object?>
                        {
                            ["card_id"] = cardId,
                            ["count"] = 1,
                        }).ToArray(),
                }));
            File.WriteAllText(Path.Combine(packageDirectory, "lookups.json"), "{}");
            return new TemporaryRuntimePackage(packageDirectory);
        }

        public void Dispose()
        {
            if (Directory.Exists(PackageDirectory))
            {
                Directory.Delete(PackageDirectory, recursive: true);
            }

            var parentDirectory = Directory.GetParent(PackageDirectory);
            if (parentDirectory is not null
                && Directory.Exists(parentDirectory.FullName)
                && !Directory.EnumerateFileSystemEntries(parentDirectory.FullName).Any())
            {
                Directory.Delete(parentDirectory.FullName);
            }
        }
    }

    private static LegalAction EnabledAction(EngineSession session, string playerId, string actionType) =>
        session.ListLegalActions(playerId).Actions.Single(item =>
            item.Enabled && string.Equals(item.ActionType, actionType, StringComparison.Ordinal));

    private static LegalAction Action(
        EngineSession session,
        string playerId,
        string actionType,
        bool includeDisabled) => session.ListLegalActions(playerId, includeDisabled).Actions.Single(item =>
            string.Equals(item.ActionType, actionType, StringComparison.Ordinal));

    private static ActionRequest Request(
        RuntimeComparisonFixture fixture,
        LegalAction action,
        string requestId,
        int expectedStateVersion) => new(
            ContractSchemas.ActionRequest,
            requestId,
            fixture.MatchId,
            action.PlayerId,
            expectedStateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.EmptyObject());

    private static ActionRequest Request(
        EngineSession session,
        LegalAction action,
        string requestId,
        JsonElement payload,
        int expectedStateVersion)
    {
        var state = session.GetDebugSnapshot();
        return new ActionRequest(
            ContractSchemas.ActionRequest,
            requestId,
            state.MatchId,
            action.PlayerId,
            expectedStateVersion,
            action.ActionId,
            action.ActionType,
            payload);
    }

    private static JsonElement NormalInflowPayload(string cardInstanceId) =>
        ContractJsonValue.From(new NormalInflowActionPayload(cardInstanceId));

    private static string CanonicalDebugState(EngineSession session)
    {
        var node = JsonSerializer.SerializeToNode(session.GetDebugSnapshot())
            ?? throw new InvalidOperationException("Debug snapshot serialization returned null.");
        return Convert.ToHexString(EngineCanonicalJson.Serialize(node));
    }

    private static string ActionRequestFingerprint(ActionRequest request)
    {
        var payload = request.Payload.ValueKind == JsonValueKind.Undefined
            ? "<undefined>"
            : request.Payload.GetRawText();
        return string.Join(
            '\u001f',
            request.SchemaVersion,
            request.RequestId,
            request.MatchId,
            request.PlayerId,
            request.ExpectedStateVersion,
            request.ActionId,
            request.ActionType,
            payload);
    }

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected: {expected}; actual: {actual}.");
        }
    }

    private static void NotEqual<T>(T left, T right, string message)
    {
        if (EqualityComparer<T>.Default.Equals(left, right))
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void SequenceEqual<T>(IEnumerable<T> expected, IEnumerable<T> actual, string message)
    {
        if (!expected.SequenceEqual(actual))
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void NotSame(object left, object right, string message)
    {
        if (ReferenceEquals(left, right))
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void True(bool value, string message)
    {
        if (!value)
        {
            throw new InvalidOperationException(message);
        }
    }
}
