using System.Collections.Immutable;
using System.Text.Json;
using System.Text.Json.Nodes;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Serialization;
using Aeterna.GodotRuntime.EngineBridge;
using Godot;

namespace Aeterna.GodotRuntime.DebugProof;

public partial class CsharpProductionEngineBridgeSmoke : Node
{
    private const string Prefix = "AETERNA_GODOT_CSHARP_PRODUCTION_BRIDGE ";

    public override void _Ready()
    {
        var exitCode = 1;
        try
        {
            var bridge = new AeternaEngineBridge();
            AddChild(bridge);
            var runtimePackagePath = ResolveRuntimePackagePath();
            var createRequest = new CreateMatchRequest(
                ContractSchemas.CreateMatchRequest,
                "RUNTIME-COMPARISON-MINIMAL-DRAW-END-TURN-V1",
                Seed: 1,
                ImmutableArray.Create(
                    new PlayerSetup("player_1", "FIXTURE-DECK-PLAYER-1"),
                    new PlayerSetup("player_2", "FIXTURE-DECK-PLAYER-2")),
                StartingHandSize: 1,
                new RuntimePackageSource(runtimePackagePath));
            var createResponse = Deserialize<CreateMatchResponse>(
                bridge.CreateMatchJson(JsonSerializer.Serialize(createRequest)));
            Require(createResponse.Accepted, "CREATE_MATCH_REJECTED", "Godot bridge could not create the fixture match.");

            var drawPlayerOne = EnabledAction(bridge, "player_1", "draw_card");
            var drawOneResponse = Submit(
                bridge,
                createRequest.MatchId,
                drawPlayerOne,
                "godot_bridge_draw_player_1",
                expectedStateVersion: 0);
            Require(drawOneResponse.Accepted, "DRAW_REJECTED", "Player one draw was rejected.");

            var snapshotBeforeStale = bridge.GetPlayerSnapshotJson("player_1");
            var eventsBeforeStale = bridge.GetEventsJson("player_1");
            var staleEndTurn = EnabledAction(bridge, "player_1", "end_turn");
            var staleResponse = Submit(
                bridge,
                createRequest.MatchId,
                staleEndTurn,
                "godot_bridge_stale_end_turn_player_1",
                expectedStateVersion: 0);
            Require(!staleResponse.Accepted, "STALE_ACCEPTED", "Stale request was accepted.");
            Require(staleResponse.Reason == "stale_state_version", "STALE_REASON_INVALID", "Stale reason is invalid.");
            Require(snapshotBeforeStale == bridge.GetPlayerSnapshotJson("player_1"), "STALE_STATE_MUTATED", "Stale request changed a player projection.");
            Require(eventsBeforeStale == bridge.GetEventsJson("player_1"), "STALE_EVENTS_MUTATED", "Stale request changed the event log.");

            var endTurn = EnabledAction(bridge, "player_1", "end_turn");
            var endTurnResponse = Submit(
                bridge,
                createRequest.MatchId,
                endTurn,
                "godot_bridge_end_turn_player_1",
                expectedStateVersion: 1);
            Require(endTurnResponse.Accepted, "END_TURN_REJECTED", "Player one end turn was rejected.");

            var drawPlayerTwo = EnabledAction(bridge, "player_2", "draw_card");
            var drawTwoResponse = Submit(
                bridge,
                createRequest.MatchId,
                drawPlayerTwo,
                "godot_bridge_draw_player_2",
                expectedStateVersion: 2);
            Require(drawTwoResponse.Accepted, "SECOND_DRAW_REJECTED", "Player two draw was rejected.");

            var playerOneSnapshot = Deserialize<PlayerSnapshot>(bridge.GetPlayerSnapshotJson("player_1"));
            var playerTwoSnapshot = Deserialize<PlayerSnapshot>(bridge.GetPlayerSnapshotJson("player_2"));
            ValidateVisibility(playerOneSnapshot, "player_1", "player_2");
            ValidateVisibility(playerTwoSnapshot, "player_2", "player_1");
            var events = Deserialize<ImmutableArray<EngineEvent>>(bridge.GetEventsJson("player_1"));
            var opponentEvents = Deserialize<ImmutableArray<EngineEvent>>(bridge.GetEventsJson("player_2"));
            var matchResult = Deserialize<MatchResult>(bridge.GetMatchResultJson());
            Require(events.Length == 3, "EVENT_COUNT_INVALID", "Godot bridge event count is invalid.");
            Require(events.Select(item => item.EventSequence).SequenceEqual([1, 2, 3]), "EVENT_SEQUENCE_INVALID", "Godot bridge event sequence is invalid.");
            var opponentDraw = opponentEvents.Single(item =>
                item.EventType == "zone_move" && item.ActorPlayerId == "player_1");
            Require(!opponentDraw.Payload.TryGetProperty("card_instance_id", out _), "EVENT_CARD_INSTANCE_LEAK", "Godot bridge leaked opponent card_instance_id.");
            Require(!opponentDraw.Payload.TryGetProperty("card_id", out _), "EVENT_CARD_ID_LEAK", "Godot bridge leaked opponent card_id.");
            Require(!matchResult.Completed, "MATCH_RESULT_INVALID", "Minimal match unexpectedly completed.");

            var summary = new JsonObject
            {
                ["ok"] = true,
                ["schema_version"] = "aeterna-godot-csharp-production-bridge-smoke-v1",
                ["bridge_type"] = nameof(AeternaEngineBridge),
                ["engine_assembly"] = typeof(Aeterna.Engine.EngineSession).Assembly.GetName().Name,
                ["direct_in_process"] = true,
                ["separate_engine_process"] = false,
                ["python_process_started"] = false,
                ["tcp_listener_used"] = false,
                ["final_state_version"] = drawTwoResponse.StateVersionAfter,
                ["event_count"] = events.Length,
                ["event_sequences"] = new JsonArray(events.Select(item => JsonValue.Create(item.EventSequence)).ToArray()),
                ["stale_rejected"] = !staleResponse.Accepted,
                ["stale_state_unchanged"] = true,
                ["hidden_information_checks_passed"] = true,
                ["final_result"] = "PASS",
                ["error_code"] = null,
                ["error"] = null,
            };
            GD.Print(Prefix + CanonicalJson.Compact(summary));
            exitCode = 0;
        }
        catch (Exception exception)
        {
            var summary = new JsonObject
            {
                ["ok"] = false,
                ["schema_version"] = "aeterna-godot-csharp-production-bridge-smoke-v1",
                ["direct_in_process"] = true,
                ["separate_engine_process"] = false,
                ["python_process_started"] = false,
                ["tcp_listener_used"] = false,
                ["final_result"] = "FAIL",
                ["error_code"] = exception is BridgeSmokeException smokeException
                    ? smokeException.Code
                    : "GODOT_CSHARP_PRODUCTION_BRIDGE_FAILED",
                ["error"] = exception.Message,
            };
            GD.Print(Prefix + CanonicalJson.Compact(summary));
        }

        GetTree().Quit(exitCode);
    }

    private static ActionResponse Submit(
        AeternaEngineBridge bridge,
        string matchId,
        LegalAction action,
        string requestId,
        int expectedStateVersion)
    {
        var request = new ActionRequest(
            ContractSchemas.ActionRequest,
            requestId,
            matchId,
            action.PlayerId,
            expectedStateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.EmptyObject());
        return Deserialize<ActionResponse>(bridge.SubmitActionJson(JsonSerializer.Serialize(request)));
    }

    private static LegalAction EnabledAction(
        AeternaEngineBridge bridge,
        string playerId,
        string actionType)
    {
        var actionSpace = Deserialize<LegalActionSpace>(bridge.ListLegalActionsJson(playerId));
        return actionSpace.Actions.Single(item =>
            item.Enabled && string.Equals(item.ActionType, actionType, StringComparison.Ordinal));
    }

    private static void ValidateVisibility(PlayerSnapshot snapshot, string viewerId, string opponentId)
    {
        var viewer = snapshot.Players.Single(item => item.PlayerId == viewerId);
        var opponent = snapshot.Players.Single(item => item.PlayerId == opponentId);
        Require(viewer.Hand.Objects.Length == viewer.Hand.Count, "OWN_HAND_REDACTED", "Viewer hand is not visible.");
        Require(opponent.Hand.Redacted && opponent.Hand.Objects.IsEmpty, "OPPONENT_HAND_LEAK", "Opponent hand leaked.");
        Require(snapshot.Players.All(item => item.Deck.Redacted && item.Deck.Objects.IsEmpty), "DECK_LEAK", "Deck contents leaked.");
    }

    private static T Deserialize<T>(string json) =>
        JsonSerializer.Deserialize<T>(json)
        ?? throw new InvalidOperationException("Godot bridge returned null JSON.");

    private static string ResolveRuntimePackagePath()
    {
        var projectRoot = ProjectSettings.GlobalizePath("res://");
        var path = Path.GetFullPath(Path.Combine(
            projectRoot,
            "..",
            "runtime_comparison",
            "fixtures",
            "minimal_draw_end_turn_v1",
            "runtime_package"));
        if (!Directory.Exists(path))
        {
            throw new DirectoryNotFoundException("Canonical runtime package was not found relative to res://.");
        }

        return path;
    }

    private static void Require(bool condition, string code, string message)
    {
        if (!condition)
        {
            throw new BridgeSmokeException(code, message);
        }
    }
}

internal sealed class BridgeSmokeException : Exception
{
    public BridgeSmokeException(string code, string message)
        : base(message)
    {
        Code = code;
    }

    public string Code { get; }
}
