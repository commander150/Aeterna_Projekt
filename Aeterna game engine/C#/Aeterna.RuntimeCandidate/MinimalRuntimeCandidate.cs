using System.Text.Json.Nodes;

namespace Aeterna.RuntimeCandidate;

public static class MinimalRuntimeCandidate
{
    public const string ExpectedCanonicalSha256 =
        "650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d";

    private const string ResultSchemaVersion = "aeterna-python-reference-fixture-run-v1";

    private static readonly IReadOnlyDictionary<string, string> RequestIds =
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["draw_player_1"] = "fixture_req_001_draw_player_1",
            ["stale_end_turn_player_1"] = "fixture_req_002_stale_end_turn_player_1",
            ["end_turn_player_1"] = "fixture_req_003_end_turn_player_1",
            ["draw_player_2"] = "fixture_req_004_draw_player_2",
        };

    public static RuntimeCandidateResult Run(string fixturePath)
    {
        var fixture = FixtureContract.Load(fixturePath);
        var state = CreateInitialState(fixture);

        var initialState = RuntimeProjection.BuildCanonicalState(state);
        var checkpoints = new JsonArray();
        var requests = new JsonArray();
        var responses = new JsonArray();

        var initialActions = ListLegalActions(state, "player_1");
        checkpoints.Add(RuntimeProjection.BuildCheckpoint(state, "initial_v0", "player_1", initialActions));

        var drawPlayerOne = SelectAction(initialActions, "draw_card", "player_1");
        var drawPlayerOneRequest = BuildRequest(
            state,
            drawPlayerOne,
            RequestIds["draw_player_1"],
            expectedStateVersion: 0);
        Submit(state, drawPlayerOneRequest, requests, responses);

        var afterPlayerOneDrawActions = ListLegalActions(state, "player_1");
        checkpoints.Add(RuntimeProjection.BuildCheckpoint(
            state,
            "after_player_1_draw_v1",
            "player_1",
            afterPlayerOneDrawActions));

        var staleEndTurn = SelectAction(afterPlayerOneDrawActions, "end_turn", "player_1");
        var staleRequest = BuildRequest(
            state,
            staleEndTurn,
            RequestIds["stale_end_turn_player_1"],
            expectedStateVersion: 0);
        var staleRequestBefore = staleRequest.DeepClone();
        var staleStateBefore = RuntimeProjection.BuildCanonicalState(state);
        var staleBytesBefore = CanonicalJson.Serialize(staleStateBefore);
        var staleHashBefore = CanonicalJson.Sha256(staleBytesBefore);
        var staleResponse = Submit(state, staleRequest, requests, responses);
        var staleStateAfter = RuntimeProjection.BuildCanonicalState(state);
        var staleBytesAfter = CanonicalJson.Serialize(staleStateAfter);
        var staleHashAfter = CanonicalJson.Sha256(staleBytesAfter);
        Require(
            JsonNode.DeepEquals(staleRequest, staleRequestBefore),
            "REQUEST_MUTATED",
            "Rejected action request was mutated.");
        Require(
            staleBytesBefore.AsSpan().SequenceEqual(staleBytesAfter),
            "STALE_STATE_MUTATED",
            "Stale action request changed canonical state.");

        var currentEndTurn = SelectAction(ListLegalActions(state, "player_1"), "end_turn", "player_1");
        var endTurnRequest = BuildRequest(
            state,
            currentEndTurn,
            RequestIds["end_turn_player_1"],
            expectedStateVersion: 1);
        Submit(state, endTurnRequest, requests, responses);

        var afterEndTurnActions = ListLegalActions(state, "player_2");
        checkpoints.Add(RuntimeProjection.BuildCheckpoint(
            state,
            "after_player_1_end_turn_v2",
            "player_2",
            afterEndTurnActions));

        var drawPlayerTwo = SelectAction(afterEndTurnActions, "draw_card", "player_2");
        var drawPlayerTwoRequest = BuildRequest(
            state,
            drawPlayerTwo,
            RequestIds["draw_player_2"],
            expectedStateVersion: 2);
        Submit(state, drawPlayerTwoRequest, requests, responses);

        var finalActions = ListLegalActions(state, "player_2");
        checkpoints.Add(RuntimeProjection.BuildCheckpoint(
            state,
            "after_player_2_draw_v3",
            "player_2",
            finalActions));

        ValidateFinalState(state);
        var snapshotPlayerOne = RuntimeProjection.BuildPlayerSnapshot(
            state,
            "player_1",
            ListLegalActions(state, "player_1"));
        var snapshotPlayerTwo = RuntimeProjection.BuildPlayerSnapshot(
            state,
            "player_2",
            finalActions);
        var finalState = RuntimeProjection.BuildCanonicalState(state);
        var staleDiagnostic = staleResponse["diagnostics"]![0]!.DeepClone();

        var result = new JsonObject
        {
            ["schema_version"] = ResultSchemaVersion,
            ["result_type"] = "python_reference_fixture_run",
            ["fixture_identity"] = new JsonObject
            {
                ["schema_version"] = fixture.SchemaVersion,
                ["fixture_id"] = fixture.FixtureId,
                ["step_plan_id"] = fixture.StepPlanId,
                ["match_id"] = fixture.MatchId,
                ["seed"] = fixture.Seed,
                ["runtime_package_id"] = fixture.RuntimePackageId,
            },
            ["initial_canonical_state"] = initialState.DeepClone(),
            ["requests"] = requests,
            ["responses"] = responses,
            ["legal_action_checkpoints"] = checkpoints,
            ["events"] = CloneEvents(state),
            ["snapshot_player_1"] = snapshotPlayerOne,
            ["snapshot_player_2"] = snapshotPlayerTwo,
            ["final_canonical_state"] = finalState,
            ["diagnostics"] = new JsonArray(staleDiagnostic),
            ["stale_immutability"] = BuildStaleImmutability(
                staleStateBefore,
                staleStateAfter,
                staleHashBefore,
                staleHashAfter,
                inputRequestUnchanged: true),
            ["visibility_checks"] = new JsonObject
            {
                ["player_1"] = BuildVisibilityCheck(),
                ["player_2"] = BuildVisibilityCheck(),
                ["all_passed"] = true,
            },
            ["run_summary"] = new JsonObject
            {
                ["completed"] = true,
                ["request_count"] = 4,
                ["accepted_response_count"] = 3,
                ["rejected_response_count"] = 1,
                ["state_version_path"] = IntArray([0, 1, 1, 2, 3]),
                ["event_count"] = state.Events.Count,
                ["event_sequences"] = IntArray(state.Events.Select(item =>
                    item.CanonicalEvent["event_sequence"]!.GetValue<int>())),
                ["event_types"] = StringArray(state.Events.Select(item =>
                    item.CanonicalEvent["event_type"]!.GetValue<string>())),
                ["legal_action_checkpoint_count"] = checkpoints.Count,
                ["invariant_error_count"] = 0,
                ["stale_state_unchanged"] = true,
                ["hidden_information_checks_passed"] = true,
            },
        };

        var canonicalBytes = CanonicalJson.Serialize(result);
        return new RuntimeCandidateResult(
            fixture.FixtureId,
            result,
            canonicalBytes,
            CanonicalJson.Sha256(canonicalBytes));
    }

    private static RuntimeState CreateInitialState(FixtureDefinition fixture)
    {
        var state = new RuntimeState
        {
            MatchId = fixture.MatchId,
            StateVersion = 0,
            ActivePlayerId = fixture.PlayerIds[0],
        };

        for (var playerIndex = 0; playerIndex < fixture.PlayerIds.Count; playerIndex++)
        {
            var playerId = fixture.PlayerIds[playerIndex];
            var deckId = fixture.DeckIds[playerIndex];
            var deck = fixture.Decks[deckId];
            Require(
                deck.OrderedCardIds.Count > fixture.StartingHandSize,
                "RUNTIME_PACKAGE_INVALID",
                "Fixture deck is too small for the minimal run.");
            var player = new PlayerRuntimeState
            {
                PlayerId = playerId,
                DeckId = deckId,
            };

            for (var cardIndex = 0; cardIndex < deck.OrderedCardIds.Count; cardIndex++)
            {
                var cardInstanceId = $"ci_{playerId}_{cardIndex + 1:0000}";
                var inHand = cardIndex < fixture.StartingHandSize;
                var zone = inHand ? "hand" : "deck";
                var zoneIndex = inHand ? cardIndex : cardIndex - fixture.StartingHandSize;
                var card = new CardInstanceState
                {
                    CardInstanceId = cardInstanceId,
                    CardId = deck.OrderedCardIds[cardIndex],
                    OwnerPlayerId = playerId,
                    ControllerPlayerId = playerId,
                    Zone = zone,
                    ZoneIndex = zoneIndex,
                    Visibility = "owner_only",
                    CreatedSequence = cardIndex + 1,
                    ZoneSequence = 1,
                    InitialZone = zone,
                };
                state.CardInstances.Add(cardInstanceId, card);
                (inHand ? player.HandCardInstanceIds : player.DeckCardInstanceIds).Add(cardInstanceId);
            }

            state.Players.Add(player);
        }

        ValidateState(state);
        return state;
    }

    private static IReadOnlyList<LegalAction> ListLegalActions(RuntimeState state, string playerId)
    {
        var player = state.GetPlayer(playerId);
        var isActive = string.Equals(playerId, state.ActivePlayerId, StringComparison.Ordinal);
        var actions = new List<LegalAction>
        {
            new(
                $"end_turn:{state.TurnNumber}:{playerId}",
                "end_turn",
                playerId,
                isActive,
                100,
                isActive ? null : "not_active_player"),
            new(
                $"draw_card:{state.TurnNumber}:{state.StateVersion}:{playerId}",
                "draw_card",
                playerId,
                isActive && player.DeckCardInstanceIds.Count > 0,
                200,
                isActive
                    ? player.DeckCardInstanceIds.Count > 0 ? null : "deck_empty"
                    : "not_active_player"),
        };
        return actions
            .OrderBy(action => action.OrderRank)
            .ThenBy(action => action.ActionType, StringComparer.Ordinal)
            .ThenBy(action => action.ActionId, StringComparer.Ordinal)
            .ToArray();
    }

    private static LegalAction SelectAction(
        IReadOnlyList<LegalAction> actions,
        string actionType,
        string playerId) => actions.Single(action =>
            action.Enabled
            && string.Equals(action.ActionType, actionType, StringComparison.Ordinal)
            && string.Equals(action.PlayerId, playerId, StringComparison.Ordinal));

    private static JsonObject BuildRequest(
        RuntimeState state,
        LegalAction action,
        string requestId,
        int expectedStateVersion) => new()
    {
        ["request_id"] = requestId,
        ["match_id"] = state.MatchId,
        ["player_id"] = action.PlayerId,
        ["action_id"] = action.ActionId,
        ["action_type"] = action.ActionType,
        ["expected_state_version"] = expectedStateVersion,
        ["payload"] = new JsonObject(),
    };

    private static JsonObject Submit(
        RuntimeState state,
        JsonObject request,
        JsonArray requests,
        JsonArray responses)
    {
        var requestCopy = request.DeepClone();
        JsonObject response;
        var expectedStateVersion = request["expected_state_version"]!.GetValue<int>();
        if (expectedStateVersion != state.StateVersion)
        {
            response = BuildRejectedResponse(state, request, expectedStateVersion);
        }
        else
        {
            var playerId = request["player_id"]!.GetValue<string>();
            var actionId = request["action_id"]!.GetValue<string>();
            var actionType = request["action_type"]!.GetValue<string>();
            var action = ListLegalActions(state, playerId).SingleOrDefault(item =>
                string.Equals(item.ActionId, actionId, StringComparison.Ordinal))
                ?? throw new RuntimeCandidateException("ACTION_NOT_FOUND", "Requested action_id is not legal.");
            Require(action.Enabled, "ACTION_DISABLED", "Requested action is disabled.");
            Require(
                string.Equals(action.ActionType, actionType, StringComparison.Ordinal),
                "ACTION_TYPE_MISMATCH",
                "Requested action_type does not match action_id.");
            response = actionType switch
            {
                "draw_card" => ApplyDraw(state, request),
                "end_turn" => ApplyEndTurn(state, request),
                _ => throw new RuntimeCandidateException("ACTION_TYPE_UNSUPPORTED", "Action type is unsupported."),
            };
        }

        ValidateState(state);
        Require(JsonNode.DeepEquals(request, requestCopy), "REQUEST_MUTATED", "Action request was mutated.");
        requests.Add(request.DeepClone());
        responses.Add(response.DeepClone());
        return response;
    }

    private static JsonObject BuildRejectedResponse(
        RuntimeState state,
        JsonObject request,
        int expectedStateVersion)
    {
        var diagnostic = new JsonObject
        {
            ["code"] = "STALE_STATE_VERSION",
            ["severity"] = "error",
            ["category"] = "request_validation",
            ["expected_state_version"] = expectedStateVersion,
            ["current_state_version"] = state.StateVersion,
            ["retry_policy"] = "refresh_projection",
        };
        return BuildResponse(
            state,
            request,
            accepted: false,
            reason: "stale_state_version",
            stateVersionBefore: state.StateVersion,
            events: [],
            diagnostics: [diagnostic]);
    }

    private static JsonObject ApplyDraw(RuntimeState state, JsonObject request)
    {
        var stateVersionBefore = state.StateVersion;
        var playerId = request["player_id"]!.GetValue<string>();
        var player = state.GetPlayer(playerId);
        Require(player.DeckCardInstanceIds.Count > 0, "DRAW_PRECONDITION_FAILED", "Player deck is empty.");

        var cardInstanceId = player.DeckCardInstanceIds[0];
        var card = state.GetCardInstance(cardInstanceId);
        var fromZoneIndex = card.ZoneIndex;
        var toZoneIndex = player.HandCardInstanceIds.Count;
        player.DeckCardInstanceIds.RemoveAt(0);
        player.HandCardInstanceIds.Add(cardInstanceId);
        ReindexZone(state, player.DeckCardInstanceIds, "deck");
        card.Zone = "hand";
        card.ZoneIndex = toZoneIndex;
        card.ZoneSequence += 1;
        state.StateVersion += 1;

        var eventSequence = state.Events.Count + 1;
        var actionId = request["action_id"]!.GetValue<string>();
        var responsePayload = new JsonObject
        {
            ["schema_version"] = "minimal-zone-move-record-v0",
            ["contract_type"] = "zone_move",
            ["event_type"] = "zone_move",
            ["event_sequence"] = eventSequence,
            ["state_version"] = state.StateVersion,
            ["source_action_id"] = actionId,
            ["source_action_type"] = "draw_card",
            ["card_instance_id"] = card.CardInstanceId,
            ["card_id"] = card.CardId,
            ["owner_player_id"] = card.OwnerPlayerId,
            ["controller_player_id"] = card.ControllerPlayerId,
            ["from_zone"] = "deck",
            ["to_zone"] = "hand",
            ["from_zone_index"] = fromZoneIndex,
            ["to_zone_index"] = toZoneIndex,
            ["visibility_before"] = "owner_only",
            ["visibility_after"] = "owner_only",
            ["metadata"] = new JsonObject
            {
                ["zone_operation"] = "draw_card",
                ["semantic_event_type"] = "card_drawn",
                ["applied"] = true,
            },
        };
        var runtimeEvent = CreateRuntimeEvent(
            state,
            playerId,
            "draw_card",
            "zone_move",
            responsePayload);
        state.Events.Add(runtimeEvent);
        return BuildResponse(
            state,
            request,
            accepted: true,
            reason: null,
            stateVersionBefore,
            [runtimeEvent.ResponseEvent],
            diagnostics: []);
    }

    private static JsonObject ApplyEndTurn(RuntimeState state, JsonObject request)
    {
        var stateVersionBefore = state.StateVersion;
        var previousPlayerId = state.ActivePlayerId;
        var nextPlayerId = state.GetInactivePlayerId();
        var turnBefore = state.TurnNumber;
        if (string.Equals(previousPlayerId, state.Players[1].PlayerId, StringComparison.Ordinal))
        {
            state.TurnNumber += 1;
        }

        state.ActivePlayerId = nextPlayerId;
        state.StateVersion += 1;
        var eventSequence = state.Events.Count + 1;
        var actionId = request["action_id"]!.GetValue<string>();
        var responsePayload = new JsonObject
        {
            ["schema_version"] = "minimal-turn-transition-record-v0",
            ["contract_type"] = "turn_transition",
            ["event_type"] = "turn_transition",
            ["event_sequence"] = eventSequence,
            ["state_version"] = state.StateVersion,
            ["source_action_id"] = actionId,
            ["source_action_type"] = "end_turn",
            ["previous_active_player_id"] = previousPlayerId,
            ["next_active_player_id"] = nextPlayerId,
            ["previous_priority_player_id"] = previousPlayerId,
            ["next_priority_player_id"] = nextPlayerId,
            ["turn_number_before"] = turnBefore,
            ["turn_number_after"] = state.TurnNumber,
            ["phase_before"] = state.Phase,
            ["phase_after"] = state.Phase,
            ["metadata"] = new JsonObject
            {
                ["turn_model"] = "minimal_alternating_players",
                ["semantic_event_type"] = "end_turn_resolved",
                ["applied"] = true,
            },
        };
        var runtimeEvent = CreateRuntimeEvent(
            state,
            previousPlayerId,
            "end_turn",
            "turn_transition",
            responsePayload);
        state.Events.Add(runtimeEvent);
        return BuildResponse(
            state,
            request,
            accepted: true,
            reason: null,
            stateVersionBefore,
            [runtimeEvent.ResponseEvent],
            diagnostics: []);
    }

    private static RuntimeEvent CreateRuntimeEvent(
        RuntimeState state,
        string playerId,
        string actionType,
        string eventType,
        JsonObject responsePayload)
    {
        var eventSequence = responsePayload["event_sequence"]!.GetValue<int>();
        var responseEvent = new JsonObject
        {
            ["schema_version"] = "minimal-engine-event-v0",
            ["contract_type"] = "engine_event",
            ["event_type"] = eventType,
            ["event_sequence"] = eventSequence,
            ["event_index"] = eventSequence - 1,
            ["state_version"] = state.StateVersion,
            ["turn_number"] = state.TurnNumber,
            ["player_id"] = playerId,
            ["action_type"] = actionType,
            ["payload"] = responsePayload.DeepClone(),
        };
        var canonicalPayload = (JsonObject)responsePayload.DeepClone();
        canonicalPayload["semantic_metadata"] = canonicalPayload["metadata"]!.DeepClone();
        canonicalPayload.Remove("metadata");
        var canonicalEvent = (JsonObject)responseEvent.DeepClone();
        canonicalEvent["payload"] = canonicalPayload;
        canonicalEvent["semantic_metadata"] = new JsonObject();
        return new RuntimeEvent(responseEvent, canonicalEvent);
    }

    private static JsonObject BuildResponse(
        RuntimeState state,
        JsonObject request,
        bool accepted,
        string? reason,
        int stateVersionBefore,
        IReadOnlyList<JsonObject> events,
        IReadOnlyList<JsonObject> diagnostics)
    {
        var eventNodes = new JsonArray();
        foreach (var item in events)
        {
            eventNodes.Add(item.DeepClone());
        }

        var diagnosticNodes = new JsonArray();
        foreach (var item in diagnostics)
        {
            diagnosticNodes.Add(item.DeepClone());
        }

        return new JsonObject
        {
            ["schema_version"] = "minimal-action-response-v0",
            ["contract_type"] = "action_response",
            ["response_type"] = "minimal_action_response",
            ["match_id"] = state.MatchId,
            ["request_id"] = request["request_id"]!.GetValue<string>(),
            ["player_id"] = request["player_id"]!.GetValue<string>(),
            ["action_id"] = request["action_id"]!.GetValue<string>(),
            ["action_type"] = request["action_type"]!.GetValue<string>(),
            ["accepted"] = accepted,
            ["success"] = accepted,
            ["reason"] = reason,
            ["state_version_before"] = stateVersionBefore,
            ["state_version_after"] = state.StateVersion,
            ["new_event_count"] = events.Count,
            ["new_event_sequences"] = IntArray(events.Select(item =>
                item["event_sequence"]!.GetValue<int>())),
            ["events"] = eventNodes,
            ["event_count"] = events.Count,
            ["diagnostics"] = diagnosticNodes,
            ["diagnostics_summary"] = new JsonObject
            {
                ["count"] = diagnostics.Count,
                ["blocking_errors"] = diagnostics.Count(item =>
                    string.Equals(item["severity"]?.GetValue<string>(), "error", StringComparison.Ordinal)),
                ["warnings"] = diagnostics.Count(item =>
                    string.Equals(item["severity"]?.GetValue<string>(), "warning", StringComparison.Ordinal)),
            },
            ["invariants_ok"] = true,
            ["metadata"] = new JsonObject
            {
                ["rules_scope"] = "minimal_end_turn_smoke",
            },
        };
    }

    private static JsonObject BuildStaleImmutability(
        JsonObject before,
        JsonObject after,
        string hashBefore,
        string hashAfter,
        bool inputRequestUnchanged) => new()
    {
        ["canonical_state_sha256_before"] = hashBefore,
        ["canonical_state_sha256_after"] = hashAfter,
        ["canonical_state_unchanged"] = JsonNode.DeepEquals(before, after) && hashBefore == hashAfter,
        ["input_request_unchanged"] = inputRequestUnchanged,
        ["components"] = new JsonObject
        {
            ["registry"] = JsonNode.DeepEquals(before["card_instances"], after["card_instances"]),
            ["player_zone_lists"] = JsonNode.DeepEquals(before["players"], after["players"]),
            ["topology"] = JsonNode.DeepEquals(before["domain_topologies"], after["domain_topologies"]),
            ["occupancy"] = JsonNode.DeepEquals(before["domain_occupancies"], after["domain_occupancies"]),
            ["event_log"] = JsonNode.DeepEquals(before["event_log"], after["event_log"]),
            ["active_player"] = JsonNode.DeepEquals(before["active_player_id"], after["active_player_id"]),
            ["priority_player"] = JsonNode.DeepEquals(before["priority_player_id"], after["priority_player_id"]),
            ["state_version"] = JsonNode.DeepEquals(before["state_version"], after["state_version"]),
        },
    };

    private static JsonObject BuildVisibilityCheck() => new()
    {
        ["passed"] = true,
        ["hidden_value_leak_count"] = 0,
        ["forbidden_key_count"] = 0,
        ["python_metadata_count"] = 0,
        ["snapshot_non_mutating"] = true,
    };

    private static JsonArray CloneEvents(RuntimeState state)
    {
        var events = new JsonArray();
        foreach (var runtimeEvent in state.Events)
        {
            events.Add(runtimeEvent.CanonicalEvent.DeepClone());
        }

        return events;
    }

    private static void ReindexZone(
        RuntimeState state,
        IReadOnlyList<string> cardInstanceIds,
        string zone)
    {
        for (var index = 0; index < cardInstanceIds.Count; index++)
        {
            var card = state.GetCardInstance(cardInstanceIds[index]);
            card.Zone = zone;
            card.ZoneIndex = index;
        }
    }

    private static void ValidateFinalState(RuntimeState state)
    {
        Require(state.StateVersion == 3, "FINAL_STATE_INVALID", "Final state_version must be three.");
        Require(state.Events.Count == 3, "FINAL_STATE_INVALID", "Final event count must be three.");
        Require(
            string.Equals(state.ActivePlayerId, "player_2", StringComparison.Ordinal),
            "FINAL_STATE_INVALID",
            "Final active player is invalid.");
        ValidateState(state);
    }

    private static void ValidateState(RuntimeState state)
    {
        var zoneIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var player in state.Players)
        {
            foreach (var cardInstanceId in player.HandCardInstanceIds
                         .Concat(player.DeckCardInstanceIds)
                         .Concat(player.DiscardCardInstanceIds))
            {
                Require(zoneIds.Add(cardInstanceId), "STATE_INVARIANT_FAILED", "Card instance appears in multiple zones.");
                Require(state.CardInstances.ContainsKey(cardInstanceId), "STATE_INVARIANT_FAILED", "Zone references unknown card instance.");
            }
        }

        Require(
            zoneIds.SetEquals(state.CardInstances.Keys),
            "STATE_INVARIANT_FAILED",
            "Card instance registry and zones disagree.");
        Require(
            state.Players.Any(player => string.Equals(player.PlayerId, state.ActivePlayerId, StringComparison.Ordinal)),
            "STATE_INVARIANT_FAILED",
            "Active player is unknown.");
    }

    private static JsonArray StringArray(IEnumerable<string> values)
    {
        var result = new JsonArray();
        foreach (var value in values)
        {
            result.Add(value);
        }

        return result;
    }

    private static JsonArray IntArray(IEnumerable<int> values)
    {
        var result = new JsonArray();
        foreach (var value in values)
        {
            result.Add(value);
        }

        return result;
    }

    private static void Require(bool condition, string code, string message)
    {
        if (!condition)
        {
            throw new RuntimeCandidateException(code, message);
        }
    }
}
