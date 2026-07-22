using System.Collections.Immutable;
using System.Text.Json;
using System.Text.Json.Nodes;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Serialization;

namespace Aeterna.Engine.Headless;

public sealed record RuntimeComparisonRunResult(
    string FixtureId,
    JsonObject Result,
    byte[] CanonicalBytes,
    string Sha256)
{
    public int CanonicalByteCount => CanonicalBytes.Length;
}

public static class RuntimeComparisonFixtureRunner
{
    public const string ExpectedCanonicalSha256 =
        "650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d";

    public const int ExpectedCanonicalByteCount = 210730;

    private const string ResultSchemaVersion = "aeterna-python-reference-fixture-run-v1";

    private static readonly IReadOnlyDictionary<string, string> RequestIds =
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["draw_player_1"] = "fixture_req_001_draw_player_1",
            ["stale_end_turn_player_1"] = "fixture_req_002_stale_end_turn_player_1",
            ["end_turn_player_1"] = "fixture_req_003_end_turn_player_1",
            ["draw_player_2"] = "fixture_req_004_draw_player_2",
        };

    private static readonly ImmutableHashSet<string> ForbiddenHiddenIdentityKeys =
        ImmutableHashSet.Create(
            StringComparer.Ordinal,
            "object_id",
            "card_instance_id",
            "card_id");

    public static RuntimeComparisonRunResult Run(string fixturePath) =>
        Run(RuntimeComparisonFixture.Load(fixturePath));

    public static RuntimeComparisonRunResult Run(RuntimeComparisonFixture fixture)
    {
        ArgumentNullException.ThrowIfNull(fixture);
        var session = new EngineSession();
        var createResponse = session.CreateMatch(fixture.CreateMatchRequest());
        Require(
            createResponse.Accepted,
            "CREATE_MATCH_REJECTED",
            createResponse.Diagnostics.FirstOrDefault()?.DeveloperMessage
                ?? "Production EngineSession rejected the canonical fixture match.");

        var initialDebug = session.GetDebugSnapshot();
        var initialState = FixtureProjection.BuildCanonicalState(initialDebug);
        var checkpoints = new JsonArray();
        var requests = new JsonArray();
        var responses = new JsonArray();
        var responseContracts = new List<ActionResponse>();

        var playerOne = fixture.Players[0].PlayerId;
        var playerTwo = fixture.Players[1].PlayerId;
        var initialActions = ObserveLegalActions(
            session,
            playerOne,
            out var initialActionsStateUnchanged);
        checkpoints.Add(FixtureProjection.BuildCheckpoint(
            initialDebug,
            "initial_v0",
            initialActions,
            initialActionsStateUnchanged));

        var drawPlayerOne = SelectAction(initialActions, "draw_card", playerOne);
        Submit(
            session,
            BuildRequest(
                fixture.MatchId,
                drawPlayerOne,
                RequestIds["draw_player_1"],
                expectedStateVersion: 0),
            requests,
            responses,
            responseContracts);

        var afterPlayerOneDraw = session.GetDebugSnapshot();
        var afterPlayerOneDrawActions = ObserveLegalActions(
            session,
            playerOne,
            out var afterPlayerOneDrawActionsStateUnchanged);
        checkpoints.Add(FixtureProjection.BuildCheckpoint(
            afterPlayerOneDraw,
            "after_player_1_draw_v1",
            afterPlayerOneDrawActions,
            afterPlayerOneDrawActionsStateUnchanged));

        var staleEndTurn = SelectAction(afterPlayerOneDrawActions, "end_turn", playerOne);
        var staleRequest = BuildRequest(
            fixture.MatchId,
            staleEndTurn,
            RequestIds["stale_end_turn_player_1"],
            expectedStateVersion: 0);
        var staleRequestBefore = FixtureProjection.BuildLegacyRequest(staleRequest);
        var staleStateBefore = FixtureProjection.BuildCanonicalState(session.GetDebugSnapshot());
        var staleBytesBefore = CanonicalJson.Serialize(staleStateBefore);
        var staleHashBefore = CanonicalJson.Sha256(staleBytesBefore);
        var eventCountBeforeStale = session.GetDebugEvents().Length;
        var staleResponse = Submit(
            session,
            staleRequest,
            requests,
            responses,
            responseContracts);
        var staleStateAfter = FixtureProjection.BuildCanonicalState(session.GetDebugSnapshot());
        var staleBytesAfter = CanonicalJson.Serialize(staleStateAfter);
        var staleHashAfter = CanonicalJson.Sha256(staleBytesAfter);
        var staleRequestAfter = FixtureProjection.BuildLegacyRequest(staleRequest);
        Require(!staleResponse.Accepted, "STALE_REQUEST_ACCEPTED", "Stale action request was accepted.");
        Require(
            staleResponse.Reason == "stale_state_version",
            "STALE_REASON_INVALID",
            "Stale action request returned an unexpected reason.");
        var staleRequestUnchanged = JsonNode.DeepEquals(staleRequestBefore, staleRequestAfter);
        var staleCanonicalStateUnchanged = staleBytesBefore.AsSpan().SequenceEqual(staleBytesAfter);
        var staleEventLogUnchanged = session.GetDebugEvents().Length == eventCountBeforeStale;
        Require(
            staleRequestUnchanged,
            "REQUEST_MUTATED",
            "Rejected action request was mutated.");
        Require(
            staleCanonicalStateUnchanged,
            "STALE_STATE_MUTATED",
            "Stale action request changed canonical state.");
        Require(
            staleEventLogUnchanged,
            "STALE_EVENT_EMITTED",
            "Stale action request changed the event log.");

        var currentEndTurn = SelectAction(
            ObserveLegalActions(session, playerOne, out _),
            "end_turn",
            playerOne);
        Submit(
            session,
            BuildRequest(
                fixture.MatchId,
                currentEndTurn,
                RequestIds["end_turn_player_1"],
                expectedStateVersion: 1),
            requests,
            responses,
            responseContracts);

        var afterEndTurn = session.GetDebugSnapshot();
        var afterEndTurnActions = ObserveLegalActions(
            session,
            playerTwo,
            out var afterEndTurnActionsStateUnchanged);
        checkpoints.Add(FixtureProjection.BuildCheckpoint(
            afterEndTurn,
            "after_player_1_end_turn_v2",
            afterEndTurnActions,
            afterEndTurnActionsStateUnchanged));

        var drawPlayerTwo = SelectAction(afterEndTurnActions, "draw_card", playerTwo);
        Submit(
            session,
            BuildRequest(
                fixture.MatchId,
                drawPlayerTwo,
                RequestIds["draw_player_2"],
                expectedStateVersion: 2),
            requests,
            responses,
            responseContracts);

        var finalDebug = session.GetDebugSnapshot();
        var finalActions = ObserveLegalActions(
            session,
            playerTwo,
            out var finalActionsStateUnchanged);
        checkpoints.Add(FixtureProjection.BuildCheckpoint(
            finalDebug,
            "after_player_2_draw_v3",
            finalActions,
            finalActionsStateUnchanged));

        var finalStateValid = ValidateFinalState(finalDebug, playerTwo);
        var finalInvariantDiagnostics = session.GetDebugInvariantDiagnostics();
        Require(
            finalInvariantDiagnostics.IsEmpty,
            "STATE_INVARIANT_FAILED",
            finalInvariantDiagnostics.FirstOrDefault()?.DeveloperMessage
                ?? "Final state invariant validation failed.");

        var playerOneStateBeforeSnapshot = CanonicalDebugBytes(session);
        var productionSnapshotPlayerOne = session.GetPlayerSnapshot(playerOne);
        var visibleEventsPlayerOne = session.GetEvents(playerOne);
        var playerOneSnapshotNonMutating = playerOneStateBeforeSnapshot.AsSpan()
            .SequenceEqual(CanonicalDebugBytes(session));
        ValidatePlayerProjection(productionSnapshotPlayerOne, playerOne, playerTwo);

        var playerTwoStateBeforeSnapshot = CanonicalDebugBytes(session);
        var productionSnapshotPlayerTwo = session.GetPlayerSnapshot(playerTwo);
        var visibleEventsPlayerTwo = session.GetEvents(playerTwo);
        var playerTwoSnapshotNonMutating = playerTwoStateBeforeSnapshot.AsSpan()
            .SequenceEqual(CanonicalDebugBytes(session));
        ValidatePlayerProjection(productionSnapshotPlayerTwo, playerTwo, playerOne);

        var playerOneActions = ObserveLegalActions(
            session,
            playerOne,
            out var playerOneActionsStateUnchanged);
        Require(
            playerOneActionsStateUnchanged,
            "LEGAL_ACTION_QUERY_MUTATED_STATE",
            "Player one final legal action query changed state.");
        ValidateSnapshotLegalActions(productionSnapshotPlayerOne, playerOneActions);
        ValidateSnapshotLegalActions(productionSnapshotPlayerTwo, finalActions);

        var snapshotPlayerOne = FixtureProjection.BuildPlayerSnapshot(
            productionSnapshotPlayerOne,
            playerOneActions,
            visibleEventsPlayerOne,
            finalInvariantDiagnostics);
        var snapshotPlayerTwo = FixtureProjection.BuildPlayerSnapshot(
            productionSnapshotPlayerTwo,
            finalActions,
            visibleEventsPlayerTwo,
            finalInvariantDiagnostics);
        var playerOneVisibility = BuildVisibilityCheck(
            productionSnapshotPlayerOne,
            snapshotPlayerOne,
            playerOneSnapshotNonMutating);
        var playerTwoVisibility = BuildVisibilityCheck(
            productionSnapshotPlayerTwo,
            snapshotPlayerTwo,
            playerTwoSnapshotNonMutating);
        var allVisibilityChecksPassed = playerOneVisibility["passed"]!.GetValue<bool>()
            && playerTwoVisibility["passed"]!.GetValue<bool>();
        Require(
            allVisibilityChecksPassed,
            "VISIBILITY_CHECK_FAILED",
            "A player-visible snapshot failed the measured visibility checks.");
        var finalState = FixtureProjection.BuildCanonicalState(finalDebug);
        var staleDiagnostic = FixtureProjection.BuildLegacyResponse(
            staleResponse,
            invariantsOk: finalInvariantDiagnostics.IsEmpty)["diagnostics"]![0]!.DeepClone();
        var eventSequences = finalDebug.Events.Select(item => item.EventSequence);
        var eventTypes = finalDebug.Events.Select(item => item.EventType);
        var acceptedResponseCount = responseContracts.Count(response => response.Accepted);
        var rejectedResponseCount = responseContracts.Count(response => !response.Accepted);
        var invariantErrorCount = finalInvariantDiagnostics.Count(item => item.Severity == "error");
        var staleStateUnchanged = staleCanonicalStateUnchanged && staleEventLogUnchanged;
        var runCompleted = finalStateValid
            && responseContracts.Count == RequestIds.Count
            && acceptedResponseCount + rejectedResponseCount == responseContracts.Count
            && invariantErrorCount == 0
            && staleStateUnchanged
            && staleRequestUnchanged
            && allVisibilityChecksPassed;
        Require(runCompleted, "RUN_CHECK_FAILED", "Canonical production run checks did not complete successfully.");

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
                ["runtime_package_id"] = createResponse.RuntimePackageId,
            },
            ["initial_canonical_state"] = initialState.DeepClone(),
            ["requests"] = requests,
            ["responses"] = responses,
            ["legal_action_checkpoints"] = checkpoints,
            ["events"] = FixtureProjection.CanonicalEvents(finalDebug.Events),
            ["snapshot_player_1"] = snapshotPlayerOne,
            ["snapshot_player_2"] = snapshotPlayerTwo,
            ["final_canonical_state"] = finalState,
            ["diagnostics"] = new JsonArray(staleDiagnostic),
            ["stale_immutability"] = BuildStaleImmutability(
                staleStateBefore,
                staleStateAfter,
                staleHashBefore,
                staleHashAfter,
                staleRequestUnchanged),
            ["visibility_checks"] = new JsonObject
            {
                ["player_1"] = playerOneVisibility,
                ["player_2"] = playerTwoVisibility,
                ["all_passed"] = allVisibilityChecksPassed,
            },
            ["run_summary"] = new JsonObject
            {
                ["completed"] = runCompleted,
                ["request_count"] = requests.Count,
                ["accepted_response_count"] = acceptedResponseCount,
                ["rejected_response_count"] = rejectedResponseCount,
                ["state_version_path"] = IntArray(
                    new[] { createResponse.StateVersion }
                        .Concat(responseContracts.Select(response => response.StateVersionAfter))),
                ["event_count"] = finalDebug.Events.Length,
                ["event_sequences"] = IntArray(eventSequences),
                ["event_types"] = StringArray(eventTypes),
                ["legal_action_checkpoint_count"] = checkpoints.Count,
                ["invariant_error_count"] = invariantErrorCount,
                ["stale_state_unchanged"] = staleStateUnchanged,
                ["hidden_information_checks_passed"] = allVisibilityChecksPassed,
            },
        };

        var canonicalBytes = CanonicalJson.Serialize(result);
        return new RuntimeComparisonRunResult(
            fixture.FixtureId,
            result,
            canonicalBytes,
            CanonicalJson.Sha256(canonicalBytes));
    }

    public static JsonObject BuildProofSummary(
        RuntimeComparisonRunResult result,
        int deterministicRuns,
        bool deterministic)
    {
        var shaMatch = result.Sha256 == ExpectedCanonicalSha256;
        var byteCountMatch = result.CanonicalByteCount == ExpectedCanonicalByteCount;
        var errorCode = !deterministic
            ? "NON_DETERMINISTIC_RESULT"
            : !shaMatch
                ? "CANONICAL_SHA_MISMATCH"
                : !byteCountMatch
                    ? "CANONICAL_BYTE_COUNT_MISMATCH"
                    : null;
        return new JsonObject
        {
            ["ok"] = errorCode is null,
            ["schema_version"] = "aeterna-csharp-production-headless-proof-v1",
            ["fixture_id"] = result.FixtureId,
            ["target_framework"] = "net8.0",
            ["direct_in_process"] = true,
            ["separate_engine_process"] = false,
            ["python_process_started"] = false,
            ["tcp_listener_used"] = false,
            ["canonical_result_bytes"] = result.CanonicalByteCount,
            ["actual_sha256"] = result.Sha256,
            ["expected_sha256"] = ExpectedCanonicalSha256,
            ["sha_match"] = shaMatch,
            ["byte_count_match"] = byteCountMatch,
            ["deterministic_runs"] = deterministicRuns,
            ["deterministic"] = deterministic,
            ["engine_assembly"] = typeof(EngineSession).Assembly.GetName().Name,
            ["error_code"] = errorCode,
        };
    }

    private static ActionRequest BuildRequest(
        string matchId,
        LegalAction action,
        string requestId,
        int expectedStateVersion) => new(
            ContractSchemas.ActionRequest,
            requestId,
            matchId,
            action.PlayerId,
            expectedStateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.EmptyObject());

    private static ActionResponse Submit(
        EngineSession session,
        ActionRequest request,
        JsonArray requests,
        JsonArray responses,
        ICollection<ActionResponse> responseContracts)
    {
        var requestProjection = FixtureProjection.BuildLegacyRequest(request);
        var response = session.SubmitAction(request);
        var invariantDiagnostics = session.GetDebugInvariantDiagnostics();
        var invariantsOk = invariantDiagnostics.IsEmpty;
        Require(
            invariantsOk,
            "STATE_INVARIANT_FAILED",
            invariantDiagnostics.FirstOrDefault()?.DeveloperMessage
                ?? "State invariant validation failed after an action response.");
        requests.Add(requestProjection);
        responses.Add(FixtureProjection.BuildLegacyResponse(response, invariantsOk));
        responseContracts.Add(response);
        return response;
    }

    private static LegalActionSpace ObserveLegalActions(
        EngineSession session,
        string playerId,
        out bool stateUnchanged)
    {
        var before = CanonicalDebugBytes(session);
        var actions = session.ListLegalActions(playerId, includeDisabled: true);
        var after = CanonicalDebugBytes(session);
        stateUnchanged = before.AsSpan().SequenceEqual(after);
        Require(
            stateUnchanged,
            "LEGAL_ACTION_QUERY_MUTATED_STATE",
            $"Legal action query changed state for viewer {playerId}.");
        return actions;
    }

    private static LegalAction SelectAction(
        LegalActionSpace actionSpace,
        string actionType,
        string playerId) => actionSpace.Actions.Single(action =>
            action.Enabled
            && string.Equals(action.ActionType, actionType, StringComparison.Ordinal)
            && string.Equals(action.PlayerId, playerId, StringComparison.Ordinal));

    private static bool ValidateFinalState(DebugSnapshot state, string expectedActivePlayerId)
    {
        var validStateVersion = state.StateVersion == 3;
        var validEventCount = state.Events.Length == 3;
        var validActivePlayer = string.Equals(
            state.ActivePlayerId,
            expectedActivePlayerId,
            StringComparison.Ordinal);
        Require(validStateVersion, "FINAL_STATE_INVALID", "Final state_version must be three.");
        Require(validEventCount, "FINAL_STATE_INVALID", "Final event count must be three.");
        Require(
            validActivePlayer,
            "FINAL_STATE_INVALID",
            "Final active player is invalid.");
        return validStateVersion && validEventCount && validActivePlayer;
    }

    private static void ValidatePlayerProjection(
        PlayerSnapshot snapshot,
        string viewerPlayerId,
        string opponentPlayerId)
    {
        var viewer = snapshot.Players.Single(item => item.PlayerId == viewerPlayerId);
        var opponent = snapshot.Players.Single(item => item.PlayerId == opponentPlayerId);
        Require(viewer.Hand.Objects.Length == viewer.Hand.Count, "VISIBILITY_INVALID", "Own hand is not visible.");
        Require(opponent.Hand.Redacted && opponent.Hand.Objects.IsEmpty, "VISIBILITY_INVALID", "Opponent hand leaked.");
        Require(snapshot.Players.All(item => item.Deck.Redacted && item.Deck.Objects.IsEmpty), "VISIBILITY_INVALID", "Deck contents leaked.");
    }

    private static void ValidateSnapshotLegalActions(
        PlayerSnapshot snapshot,
        LegalActionSpace fullActionSpace)
    {
        var enabledActions = fullActionSpace.Actions.Where(action => action.Enabled).ToArray();
        Require(
            snapshot.LegalActions.Length == enabledActions.Length,
            "SNAPSHOT_ACTIONS_INVALID",
            "Player snapshot legal action count differs from the enabled production action space.");
        Require(
            snapshot.LegalActions.Select(action => action.ActionId)
                .SequenceEqual(enabledActions.Select(action => action.ActionId)),
            "SNAPSHOT_ACTIONS_INVALID",
            "Player snapshot legal action IDs differ from the enabled production action space.");
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

    private static JsonObject BuildVisibilityCheck(
        PlayerSnapshot productionSnapshot,
        JsonObject canonicalSnapshot,
        bool snapshotNonMutating)
    {
        var viewer = productionSnapshot.Players.Single(player =>
            string.Equals(player.PlayerId, productionSnapshot.ViewerPlayerId, StringComparison.Ordinal));
        var opponents = productionSnapshot.Players.Where(player =>
            !string.Equals(player.PlayerId, productionSnapshot.ViewerPlayerId, StringComparison.Ordinal));
        var hiddenValueLeakCount = productionSnapshot.Players.Sum(player => player.Deck.Objects.Length)
            + opponents.Sum(player => player.Hand.Objects.Length);
        var forbiddenKeyCount = CountForbiddenKeysInRedactedZones(canonicalSnapshot);
        var pythonMetadataCount = CountPythonMetadata(canonicalSnapshot);
        var ownHandVisible = !viewer.Hand.Redacted && viewer.Hand.Objects.Length == viewer.Hand.Count;
        var opponentHandsRedacted = opponents.All(player =>
            player.Hand.Redacted && player.Hand.Objects.IsEmpty);
        var decksRedacted = productionSnapshot.Players.All(player =>
            player.Deck.Redacted && player.Deck.Objects.IsEmpty);
        var passed = ownHandVisible
            && opponentHandsRedacted
            && decksRedacted
            && hiddenValueLeakCount == 0
            && forbiddenKeyCount == 0
            && pythonMetadataCount == 0
            && snapshotNonMutating;
        return new JsonObject
        {
            ["passed"] = passed,
            ["hidden_value_leak_count"] = hiddenValueLeakCount,
            ["forbidden_key_count"] = forbiddenKeyCount,
            ["python_metadata_count"] = pythonMetadataCount,
            ["snapshot_non_mutating"] = snapshotNonMutating,
        };
    }

    private static int CountForbiddenKeysInRedactedZones(JsonObject canonicalSnapshot)
    {
        var count = 0;
        foreach (var playerNode in canonicalSnapshot["players"]?.AsArray() ?? [])
        {
            var player = playerNode?.AsObject()
                ?? throw new RuntimeComparisonRunException(
                    "SNAPSHOT_PROJECTION_INVALID",
                    "Canonical player projection is not an object.");
            var zones = player["zones"]?.AsObject()
                ?? throw new RuntimeComparisonRunException(
                    "SNAPSHOT_PROJECTION_INVALID",
                    "Canonical player projection has no zones object.");
            count += CountKeys(zones["deck"], ForbiddenHiddenIdentityKeys);
            if (player["relation"]?.GetValue<string>() == "opponent")
            {
                count += CountKeys(zones["hand"], ForbiddenHiddenIdentityKeys);
            }
        }

        return count;
    }

    private static int CountKeys(JsonNode? node, IReadOnlySet<string> forbiddenKeys)
    {
        if (node is JsonObject item)
        {
            return item.Sum(property =>
                (forbiddenKeys.Contains(property.Key) ? 1 : 0)
                + CountKeys(property.Value, forbiddenKeys));
        }

        return node is JsonArray array
            ? array.Sum(child => CountKeys(child, forbiddenKeys))
            : 0;
    }

    private static int CountPythonMetadata(JsonNode? node)
    {
        if (node is JsonObject item)
        {
            return item.Sum(property =>
                (property.Key.Contains("python", StringComparison.OrdinalIgnoreCase) ? 1 : 0)
                + CountPythonMetadata(property.Value));
        }

        if (node is JsonArray array)
        {
            return array.Sum(CountPythonMetadata);
        }

        return node is JsonValue value
               && value.TryGetValue<string>(out var text)
               && text.Contains("python", StringComparison.OrdinalIgnoreCase)
            ? 1
            : 0;
    }

    private static byte[] CanonicalDebugBytes(EngineSession session) =>
        CanonicalJson.Serialize(FixtureProjection.BuildCanonicalState(session.GetDebugSnapshot()));

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
            throw new RuntimeComparisonRunException(code, message);
        }
    }
}

public sealed class RuntimeComparisonRunException : Exception
{
    public RuntimeComparisonRunException(string code, string message, Exception? innerException = null)
        : base(message, innerException)
    {
        Code = code;
    }

    public string Code { get; }
}
