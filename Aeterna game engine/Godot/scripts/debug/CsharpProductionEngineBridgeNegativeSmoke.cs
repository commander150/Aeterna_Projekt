using System.Collections.Immutable;
using System.Text.Json;
using System.Text.Json.Nodes;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Serialization;
using Aeterna.GodotRuntime.EngineBridge;
using Godot;

namespace Aeterna.GodotRuntime.DebugProof;

public partial class CsharpProductionEngineBridgeNegativeSmoke : Node
{
    private const string Prefix = "AETERNA_GODOT_CSHARP_PRODUCTION_BRIDGE_NEGATIVE ";

    public override void _Ready()
    {
        var exitCode = 1;
        try
        {
            var bridge = new AeternaEngineBridge();
            AddChild(bridge);

            var malformedCreate = Deserialize<CreateMatchResponse>(bridge.CreateMatchJson("{"));
            Require(!malformedCreate.Accepted, "MALFORMED_CREATE_ACCEPTED", "Malformed create JSON was accepted.");
            Require(
                malformedCreate.Diagnostics.Single().Code == "CREATE_MATCH_REQUEST_MISSING",
                "MALFORMED_CREATE_DIAGNOSTIC_INVALID",
                "Malformed create JSON returned an unstable diagnostic.");

            var validCreateRequest = CreateRequest(ResolveRuntimePackagePath());
            var missingRuntimePackage = Deserialize<CreateMatchResponse>(bridge.CreateMatchJson(
                JsonSerializer.Serialize(validCreateRequest with { RuntimePackage = null! })));
            Require(!missingRuntimePackage.Accepted, "NULL_RUNTIME_PACKAGE_ACCEPTED", "Null runtime_package was accepted.");
            Require(
                missingRuntimePackage.Diagnostics.Single().Code == "RUNTIME_PACKAGE_SOURCE_MISSING",
                "NULL_RUNTIME_PACKAGE_DIAGNOSTIC_INVALID",
                "Null runtime_package returned an unstable diagnostic.");

            var createResponse = Deserialize<CreateMatchResponse>(
                bridge.CreateMatchJson(JsonSerializer.Serialize(validCreateRequest)));
            Require(createResponse.Accepted, "CREATE_MATCH_REJECTED", "Valid create request was rejected.");
            var stateBeforeInvalidActions = bridge.GetPlayerSnapshotJson("player_1");

            var malformedAction = Deserialize<ActionResponse>(bridge.SubmitActionJson("[]"));
            Require(!malformedAction.Accepted, "MALFORMED_ACTION_ACCEPTED", "Malformed action JSON was accepted.");
            Require(
                malformedAction.Diagnostics.Single().Code == "ACTION_REQUEST_MISSING",
                "MALFORMED_ACTION_DIAGNOSTIC_INVALID",
                "Malformed action JSON returned an unstable diagnostic.");

            var drawAction = EnabledAction(bridge, "player_1", "draw_card");
            var whitespaceRequestId = Deserialize<ActionResponse>(bridge.SubmitActionJson(JsonSerializer.Serialize(
                Request(validCreateRequest.MatchId, drawAction, "   ", ContractJsonValue.EmptyObject()))));
            Require(!whitespaceRequestId.Accepted, "EMPTY_REQUEST_ID_ACCEPTED", "Whitespace request_id was accepted.");
            Require(
                whitespaceRequestId.Diagnostics.Single().Code == "ACTION_REQUEST_ID_INVALID",
                "EMPTY_REQUEST_ID_DIAGNOSTIC_INVALID",
                "Whitespace request_id returned an unstable diagnostic.");

            var missingPayloadNode = JsonSerializer.SerializeToNode(
                    Request(validCreateRequest.MatchId, drawAction, "missing_payload", ContractJsonValue.EmptyObject()))
                ?.AsObject()
                ?? throw new InvalidOperationException("Action request serialization returned null.");
            missingPayloadNode.Remove("payload");
            var missingPayload = Deserialize<ActionResponse>(bridge.SubmitActionJson(missingPayloadNode.ToJsonString()));
            Require(!missingPayload.Accepted, "MISSING_PAYLOAD_ACCEPTED", "Missing action payload was accepted.");
            Require(
                missingPayload.Diagnostics.Single().Code == "ACTION_PAYLOAD_INVALID",
                "MISSING_PAYLOAD_DIAGNOSTIC_INVALID",
                "Missing payload returned an unstable diagnostic.");

            var nullPayload = Deserialize<ActionResponse>(bridge.SubmitActionJson(JsonSerializer.Serialize(
                Request(
                    validCreateRequest.MatchId,
                    drawAction,
                    "null_payload",
                    JsonDocument.Parse("null").RootElement.Clone()))));
            Require(!nullPayload.Accepted, "NULL_PAYLOAD_ACCEPTED", "Null action payload was accepted.");
            Require(
                nullPayload.Diagnostics.Single().Code == "ACTION_PAYLOAD_INVALID",
                "NULL_PAYLOAD_DIAGNOSTIC_INVALID",
                "Null payload returned an unstable diagnostic.");
            Require(
                stateBeforeInvalidActions == bridge.GetPlayerSnapshotJson("player_1"),
                "INVALID_ACTION_MUTATED_STATE",
                "Rejected bridge input changed production state.");

            var drawResponse = Deserialize<ActionResponse>(bridge.SubmitActionJson(JsonSerializer.Serialize(
                Request(
                    validCreateRequest.MatchId,
                    drawAction,
                    "negative_smoke_valid_draw",
                    ContractJsonValue.EmptyObject()))));
            Require(drawResponse.Accepted, "VALID_DRAW_REJECTED", "Valid draw was rejected after negative checks.");

            var ownerEvent = Deserialize<ImmutableArray<EngineEvent>>(bridge.GetEventsJson("player_1")).Single();
            var opponentEvent = Deserialize<ImmutableArray<EngineEvent>>(bridge.GetEventsJson("player_2")).Single();
            Require(ownerEvent.Payload.TryGetProperty("card_instance_id", out _), "OWNER_EVENT_REDACTED", "Owner event lost card_instance_id.");
            Require(ownerEvent.Payload.TryGetProperty("card_id", out _), "OWNER_CARD_ID_REDACTED", "Owner event lost card_id.");
            Require(!opponentEvent.Payload.TryGetProperty("card_instance_id", out _), "OPPONENT_INSTANCE_ID_LEAK", "Opponent event leaked card_instance_id.");
            Require(!opponentEvent.Payload.TryGetProperty("card_id", out _), "OPPONENT_CARD_ID_LEAK", "Opponent event leaked card_id.");

            var summary = new JsonObject
            {
                ["ok"] = true,
                ["schema_version"] = "aeterna-godot-csharp-production-bridge-negative-smoke-v1",
                ["controlled_create_rejections"] = 2,
                ["controlled_action_rejections"] = 4,
                ["owner_event_identity_visible"] = true,
                ["opponent_event_identity_redacted"] = true,
                ["state_unchanged_after_rejections"] = true,
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
                ["schema_version"] = "aeterna-godot-csharp-production-bridge-negative-smoke-v1",
                ["final_result"] = "FAIL",
                ["error_code"] = exception is BridgeNegativeSmokeException smokeException
                    ? smokeException.Code
                    : "GODOT_CSHARP_PRODUCTION_BRIDGE_NEGATIVE_FAILED",
                ["error"] = exception.Message,
            };
            GD.Print(Prefix + CanonicalJson.Compact(summary));
        }

        GetTree().Quit(exitCode);
    }

    private static CreateMatchRequest CreateRequest(string runtimePackagePath) => new(
        ContractSchemas.CreateMatchRequest,
        "RUNTIME-COMPARISON-MINIMAL-DRAW-END-TURN-V1",
        Seed: 1,
        ImmutableArray.Create(
            new PlayerSetup("player_1", "FIXTURE-DECK-PLAYER-1"),
            new PlayerSetup("player_2", "FIXTURE-DECK-PLAYER-2")),
        StartingHandSize: 1,
        new RuntimePackageSource(runtimePackagePath));

    private static ActionRequest Request(
        string matchId,
        LegalAction action,
        string requestId,
        JsonElement payload) => new(
        ContractSchemas.ActionRequest,
        requestId,
        matchId,
        action.PlayerId,
        ExpectedStateVersion: 0,
        action.ActionId,
        action.ActionType,
        payload);

    private static LegalAction EnabledAction(
        AeternaEngineBridge bridge,
        string playerId,
        string actionType) =>
        Deserialize<LegalActionSpace>(bridge.ListLegalActionsJson(playerId)).Actions.Single(item =>
            item.Enabled && string.Equals(item.ActionType, actionType, StringComparison.Ordinal));

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
        return Directory.Exists(path)
            ? path
            : throw new DirectoryNotFoundException("Canonical runtime package was not found relative to res://.");
    }

    private static void Require(bool condition, string code, string message)
    {
        if (!condition)
        {
            throw new BridgeNegativeSmokeException(code, message);
        }
    }
}

internal sealed class BridgeNegativeSmokeException : Exception
{
    public BridgeNegativeSmokeException(string code, string message)
        : base(message)
    {
        Code = code;
    }

    public string Code { get; }
}
