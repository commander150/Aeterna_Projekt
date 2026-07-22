using System.Text.Json;
using System.Text.Json.Nodes;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Headless;
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
        SequenceEqual(["end_turn", "draw_card"], legal.Actions.Select(item => item.ActionType), "Legal action order is invalid.");
        Equal(2, legal.Actions.Count(item => item.Enabled), "Initial enabled action count is invalid.");
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

    private static LegalAction EnabledAction(EngineSession session, string playerId, string actionType) =>
        session.ListLegalActions(playerId).Actions.Single(item =>
            item.Enabled && string.Equals(item.ActionType, actionType, StringComparison.Ordinal));

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

    private static string CanonicalDebugState(EngineSession session)
    {
        var node = JsonSerializer.SerializeToNode(session.GetDebugSnapshot())
            ?? throw new InvalidOperationException("Debug snapshot serialization returned null.");
        return Convert.ToHexString(EngineCanonicalJson.Serialize(node));
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
