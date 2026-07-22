using Aeterna.Engine.Contracts;

namespace Aeterna.Engine.State;

internal sealed class MatchState
{
    public required string MatchId { get; init; }

    public required int Seed { get; init; }

    public required string RuntimePackageId { get; init; }

    public int StateVersion { get; set; }

    public int TurnNumber { get; set; } = 1;

    public string Phase { get; set; } = "main";

    public required string ActivePlayerId { get; set; }

    public required string PriorityPlayerId { get; set; }

    public List<PlayerState> Players { get; } = [];

    public Dictionary<string, CardInstanceState> CardInstances { get; } =
        new(StringComparer.Ordinal);

    public List<EngineEvent> Events { get; } = [];

    public MatchResult Result { get; } = new(
        ContractSchemas.MatchResult,
        Completed: false,
        Outcome: "in_progress",
        WinnerPlayerId: null,
        Reason: null);

    public PlayerState GetPlayer(string playerId) => Players.Single(player =>
        string.Equals(player.PlayerId, playerId, StringComparison.Ordinal));

    public CardInstanceState GetCardInstance(string cardInstanceId) => CardInstances[cardInstanceId];

    public string GetNextPlayerId(string playerId)
    {
        var index = Players.FindIndex(player =>
            string.Equals(player.PlayerId, playerId, StringComparison.Ordinal));
        return Players[(index + 1) % Players.Count].PlayerId;
    }
}

internal sealed class PlayerState
{
    public required string PlayerId { get; init; }

    public required string DeckId { get; init; }

    public List<string> DeckCardInstanceIds { get; } = [];

    public List<string> HandCardInstanceIds { get; } = [];

    public List<string> DiscardCardInstanceIds { get; } = [];

    public List<string> WellspringCardInstanceIds { get; } = [];
}

internal sealed class CardInstanceState
{
    public required string CardInstanceId { get; init; }

    public required string CardId { get; init; }

    public required string OwnerPlayerId { get; init; }

    public required string ControllerPlayerId { get; init; }

    public required string Zone { get; set; }

    public required int ZoneIndex { get; set; }

    public required string Visibility { get; set; }

    public required int CreatedSequence { get; init; }

    public required int ZoneSequence { get; set; }

    public required string InitialZone { get; init; }

    public string? ActivityState { get; set; }
}
