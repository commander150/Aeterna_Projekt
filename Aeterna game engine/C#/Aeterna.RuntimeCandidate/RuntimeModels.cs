using System.Text.Json.Nodes;

namespace Aeterna.RuntimeCandidate;

internal sealed record FixtureDefinition(
    string SchemaVersion,
    string FixtureId,
    string RuntimePackageId,
    int Seed,
    string MatchId,
    IReadOnlyList<string> PlayerIds,
    IReadOnlyList<string> DeckIds,
    int StartingHandSize,
    string StepPlanId,
    IReadOnlyDictionary<string, DeckDefinition> Decks,
    IReadOnlySet<string> CardIds);

internal sealed record DeckDefinition(string DeckId, IReadOnlyList<string> OrderedCardIds);

internal sealed class PlayerRuntimeState
{
    public required string PlayerId { get; init; }

    public required string DeckId { get; init; }

    public List<string> DeckCardInstanceIds { get; } = [];

    public List<string> HandCardInstanceIds { get; } = [];

    public List<string> DiscardCardInstanceIds { get; } = [];
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
}

internal sealed class RuntimeState
{
    public required string MatchId { get; init; }

    public int StateVersion { get; set; }

    public int TurnNumber { get; set; } = 1;

    public string Phase { get; set; } = "main";

    public required string ActivePlayerId { get; set; }

    public List<PlayerRuntimeState> Players { get; } = [];

    public Dictionary<string, CardInstanceState> CardInstances { get; } =
        new(StringComparer.Ordinal);

    public List<RuntimeEvent> Events { get; } = [];

    public PlayerRuntimeState GetPlayer(string playerId) =>
        Players.Single(player => string.Equals(player.PlayerId, playerId, StringComparison.Ordinal));

    public CardInstanceState GetCardInstance(string cardInstanceId) => CardInstances[cardInstanceId];

    public string GetInactivePlayerId() =>
        Players.Single(player => !string.Equals(player.PlayerId, ActivePlayerId, StringComparison.Ordinal)).PlayerId;
}

internal sealed record RuntimeEvent(JsonObject ResponseEvent, JsonObject CanonicalEvent);

internal sealed record LegalAction(
    string ActionId,
    string ActionType,
    string PlayerId,
    bool Enabled,
    int OrderRank,
    string? DisabledReason);
