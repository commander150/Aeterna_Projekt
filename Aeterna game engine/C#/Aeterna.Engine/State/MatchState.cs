using System.Collections.Immutable;
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

    public MatchSetupState? Setup { get; set; }

    public int NextShuffleSequence { get; set; } = 1;

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

    public List<string> ResolutionCardInstanceIds { get; } = [];

    public PendingTriggerWindowState? PendingTriggerWindow { get; set; }

    public ReactionWindowState? ReactionWindow { get; set; }

    public List<ResolutionStackEntryState> ResolutionStack { get; } = [];

    public List<QueuedTriggerBatchState> QueuedTriggerBatches { get; } = [];

    public HashSet<string> ClosedReactionSubjectIds { get; } = new(StringComparer.Ordinal);

    public int NextReactionWindowSequence { get; set; } = 1;

    public int NextReactionSubjectSequence { get; set; } = 1;

    public int NextResolutionSequence { get; set; } = 1;

    public PendingCombatState? PendingCombat { get; set; }

    public int NextCombatSequence { get; set; } = 1;

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

internal sealed class ReactionWindowState
{
    public required string ReactionWindowId { get; init; }

    public required string ReactionSubjectId { get; init; }

    public string? OriginatingEventId { get; init; }

    public int? OriginatingEventSequence { get; init; }

    public required string UnderlyingResolutionId { get; init; }

    public required string InitiatorPlayerId { get; init; }

    public List<string> EligibleResponderPlayerIds { get; } = [];

    public required string CurrentResponsePolicyId { get; set; }

    public int ConsecutivePassCount { get; set; }

    public required int OpenedAtStateVersion { get; init; }

    public required string ReactionProfileId { get; init; }
}

internal sealed class ResolutionStackEntryState
{
    public required string ResolutionId { get; init; }

    public required int Sequence { get; init; }

    public required string EntryKindId { get; init; }

    public required string ReactionWindowId { get; init; }

    public required string ReactionSubjectId { get; init; }

    public string? ParentResolutionId { get; init; }

    public CanonicalAbilityResolutionState? AbilityResolution { get; init; }

    public CombatContinuationState? CombatContinuation { get; init; }

    public string? ReactionOptionId { get; init; }

    public string? NextResponsePolicyId { get; init; }
}

internal sealed record CombatContinuationState(
    string CombatId,
    string CombatStageId,
    int StageSequence,
    string ResumePointId);

internal sealed record GameObjectRefState(
    string ObjectKindId,
    string ObjectId,
    int IncarnationSequence);

internal sealed record CombatTargetState(
    string TargetKindId,
    string PublicTargetId,
    GameObjectRefState? EntityRef);

internal sealed class PendingCombatState
{
    public required string CombatId { get; init; }

    public required int CombatSequence { get; init; }

    public required string StageId { get; set; }

    public required int StageSequence { get; set; }

    public required string AttackingPlayerId { get; init; }

    public required string DefendingPlayerId { get; init; }

    public required GameObjectRefState AttackerRef { get; init; }

    public required CombatTargetState OriginalTarget { get; init; }

    public required int OriginalAttackLaneIndex { get; init; }

    public required bool AttackCommitted { get; init; }

    public required int AttackCommitStateVersion { get; init; }

    public required string AttackTimingAnchorId { get; init; }

    public GameObjectRefState? DefenderRef { get; set; }

    public bool DefenseCommitted { get; set; }

    public string? OutcomeId { get; set; }
}

internal sealed record CanonicalAbilityResolutionState(
    string ResolutionOriginId,
    string? SourceActionId,
    string SourceActionType,
    string AbilityId,
    string SourceCardInstanceId,
    string SourceCardId,
    string SourceZoneIdAtDeclaration,
    int SourceZoneSequenceAtDeclaration,
    string SourceRelevancePolicyId,
    string ControllerPlayerId,
    ImmutableArray<CanonicalTargetSelectionPayload> DeclaredTargetSelections,
    ImmutableArray<DeclaredTargetSelectionState> DeclaredTargetStates,
    string? PendingTriggerId,
    string? TriggerId,
    int DeclarationStateVersion);

internal sealed record DeclaredTargetSelectionState(
    string TargetId,
    ImmutableArray<DeclaredTargetObjectState> SelectedObjects);

internal sealed record DeclaredTargetObjectState(
    string CardInstanceId,
    int ZoneSequenceAtDeclaration);

internal sealed class QueuedTriggerBatchState
{
    public required string TriggerBatchId { get; init; }

    public required string OriginatingEventId { get; init; }

    public required int OriginatingEventSequence { get; init; }

    public required string BatchOrderPolicyId { get; init; }

    public List<PendingTriggeredAbilityState> Triggers { get; } = [];
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

internal sealed class MatchSetupState
{
    public required string SetupModeId { get; init; }

    public string? CurrentProphecyPlayerId { get; set; }

    public List<string> CompletedProphecyPlayerIds { get; } = [];

    public bool Completed { get; set; }
}

internal sealed class PlayerState
{
    public required string PlayerId { get; init; }

    public required string DeckId { get; init; }

    public List<string> DeckCardInstanceIds { get; } = [];

    public List<string> HandCardInstanceIds { get; } = [];

    public List<string> VoidCardInstanceIds { get; } = [];

    public List<string> WellspringCardInstanceIds { get; } = [];

    public DomainState Domain { get; } = new();

    public List<SealSlotState> SealSlots { get; } = [];

    public int? NormalInflowUsedTurnNumber { get; set; }
}

internal sealed class SealSlotState
{
    public required string SealSlotId { get; init; }

    public required string OwnerPlayerId { get; init; }

    public required int LaneIndex { get; init; }

    public required string Status { get; set; }

    public string? CardInstanceId { get; set; }
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
