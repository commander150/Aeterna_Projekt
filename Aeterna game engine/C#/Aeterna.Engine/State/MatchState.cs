using Aeterna.Engine.Contracts;
using Aeterna.Engine.Rules;

namespace Aeterna.Engine.State;

internal sealed class MatchState
{
    public required string MatchId { get; init; }

    public required int Seed { get; init; }

    public required string RuntimePackageId { get; init; }

    public int StateVersion { get; set; }

    public int TurnNumber { get; set; } = 1;

    public string Phase { get; set; } = CanonicalPhaseIds.Awakening;

    internal bool LegacyPhaseCompatibility { get; init; }

    public required string StartingPlayerId { get; init; }

    public required string ActivePlayerId { get; set; }

    public required string PriorityPlayerId { get; set; }

    public List<PlayerState> Players { get; } = [];

    public Dictionary<string, CardInstanceState> CardInstances { get; } =
        new(StringComparer.Ordinal);

    public Dictionary<string, ModifierInstanceState> ModifierInstances { get; } =
        new(StringComparer.Ordinal);

    public Dictionary<string, KeywordGrantInstanceState> KeywordGrantInstances { get; } =
        new(StringComparer.Ordinal);

    public int NextContinuousEffectSequence { get; set; } = 1;

    public List<EngineEvent> Events { get; } = [];

    public PendingTriggerWindowState? PendingTriggerWindow { get; set; }

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

internal sealed class PendingTriggerWindowState
{
    public required string PendingWindowId { get; init; }

    public required string ControllerPlayerId { get; init; }

    public List<PendingTriggeredAbilityState> PendingTriggers { get; } = [];
}

internal sealed record PendingTriggeredAbilityState(
    string PendingTriggerId,
    string AbilityId,
    string TriggerId,
    string SourceCardInstanceId,
    string SourceCardId,
    string ControllerPlayerId,
    string SourceEngineEventId,
    int SourceEngineEventSequence,
    string CanonicalEventTypeId,
    string? SourceFromZoneId = null,
    string? SourceToZoneId = null,
    string? SourceZoneTransitionInstanceId = null);

internal sealed class PlayerState
{
    public required string PlayerId { get; init; }

    public required string DeckId { get; init; }

    public List<string> DeckCardInstanceIds { get; } = [];

    public List<string> HandCardInstanceIds { get; } = [];

    public List<string> VoidCardInstanceIds { get; } = [];

    public List<string> WellspringCardInstanceIds { get; } = [];

    public DomainState Domain { get; } = new();

    public int? NormalInflowUsedTurnNumber { get; set; }
}

internal enum DomainRow
{
    Horizon,
    Zenith,
}

internal sealed class DomainState
{
    public const int LaneCount = 6;

    public List<string?> HorizonCardInstanceIds { get; } =
        Enumerable.Repeat<string?>(null, LaneCount).ToList();

    public List<string?> ZenithCardInstanceIds { get; } =
        Enumerable.Repeat<string?>(null, LaneCount).ToList();

    public List<string?> GetSlots(DomainRow row) => row switch
    {
        DomainRow.Horizon => HorizonCardInstanceIds,
        DomainRow.Zenith => ZenithCardInstanceIds,
        _ => throw new ArgumentOutOfRangeException(nameof(row)),
    };

    public bool TryOccupy(DomainRow row, int laneIndex, string cardInstanceId)
    {
        if (laneIndex is < 0 or >= LaneCount)
        {
            throw new ArgumentOutOfRangeException(nameof(laneIndex));
        }

        if (string.IsNullOrWhiteSpace(cardInstanceId))
        {
            throw new ArgumentException("Card instance ID is required.", nameof(cardInstanceId));
        }

        if (HorizonCardInstanceIds.Concat(ZenithCardInstanceIds).Any(item =>
                string.Equals(item, cardInstanceId, StringComparison.Ordinal)))
        {
            return false;
        }

        var slots = GetSlots(row);
        if (slots[laneIndex] is not null)
        {
            return false;
        }

        slots[laneIndex] = cardInstanceId;
        return true;
    }
}

internal sealed class CardInstanceState
{
    public required string CardInstanceId { get; init; }

    public required string CardId { get; init; }

    public required string OwnerPlayerId { get; init; }

    public required string ControllerPlayerId { get; set; }

    public required string Zone { get; set; }

    public required int ZoneIndex { get; set; }

    public required string Visibility { get; set; }

    public required int CreatedSequence { get; init; }

    public required int ZoneSequence { get; set; }

    public required string InitialZone { get; init; }

    public string? ActivityState { get; set; }

    public DomainRow? DomainRow { get; set; }

    public int? DomainLaneIndex { get; set; }

    public int? EnteredDomainTurnNumber { get; set; }

    public int DamageMarked { get; set; }
}
