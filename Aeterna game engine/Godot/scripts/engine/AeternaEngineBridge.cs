using System.Text.Json;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Serialization;
using Godot;
using ProductionEngineSession = Aeterna.Engine.EngineSession;

namespace Aeterna.GodotRuntime.EngineBridge;

public partial class AeternaEngineBridge : Node
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true,
    };

    private readonly ProductionEngineSession _session = new();

    public string CreateMatchJson(string? requestJson) =>
        Serialize(_session.CreateMatch(DeserializeOrNull<CreateMatchRequest>(requestJson)));

    public string GetPlayerSnapshotJson(string playerId) =>
        Serialize(_session.GetPlayerSnapshot(playerId));

    public string ListLegalActionsJson(string playerId, bool includeDisabled = false) =>
        Serialize(_session.ListLegalActions(playerId, includeDisabled));

    public string SubmitActionJson(string? requestJson) =>
        Serialize(_session.SubmitAction(DeserializeOrNull<ActionRequest>(requestJson)));

    public string GetEventsJson(string viewerPlayerId, int afterSequence = 0) =>
        Serialize(_session.GetEvents(viewerPlayerId, afterSequence));

    public string GetMatchResultJson() =>
        Serialize(_session.GetMatchResult());

    private static T? DeserializeOrNull<T>(string? json)
        where T : class
    {
        if (string.IsNullOrWhiteSpace(json))
        {
            return null;
        }

        try
        {
            return JsonSerializer.Deserialize<T>(json, JsonOptions);
        }
        catch (Exception exception) when (exception is JsonException or NotSupportedException)
        {
            return null;
        }
    }

    private static string Serialize<T>(T value)
    {
        var node = JsonSerializer.SerializeToNode(value, JsonOptions)
            ?? throw new InvalidOperationException("Bridge response serialization produced null JSON.");
        return CanonicalJson.Compact(node);
    }
}
