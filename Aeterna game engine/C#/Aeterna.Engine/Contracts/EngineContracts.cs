using System.Collections.Immutable;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Aeterna.Engine.Contracts;

public static class ContractSchemas
{
    public const string CreateMatchRequest = "aeterna-create-match-request-v1";
    public const string CreateMatchResponse = "aeterna-create-match-response-v1";
    public const string ActionRequest = "aeterna-action-request-v1";
    public const string ActionResponse = "minimal-action-response-v0";
    public const string LegalActionSpace = "minimal-legal-action-space-v0";
    public const string PlayerSnapshot = "engine-player-visible-snapshot-v3";
    public const string WellspringProjection = "aeterna-player-visible-wellspring-v1";
    public const string WellspringResourceSummary = "aeterna-wellspring-resource-summary-v1";
    public const string ResourceSummary = "aeterna-resource-summary-v1";
    public const string DomainBoardProjection = "aeterna-player-visible-domain-board-v1";
    public const string DebugSnapshot = "aeterna-debug-match-snapshot-v2";
    public const string EngineEvent = "minimal-engine-event-v0";
    public const string EngineDiagnostic = "aeterna-engine-diagnostic-v1";
    public const string MatchResult = "aeterna-match-result-v1";
}

public static class ContractJsonValue
{
    public static JsonElement EmptyObject() =>
        JsonSerializer.SerializeToElement(new Dictionary<string, object?>());

    public static JsonElement From<T>(T value) => JsonSerializer.SerializeToElement(value);

    public static JsonElement Clone(JsonElement value) => value.Clone();
}

public sealed record RuntimePackageSource(
    [property: JsonPropertyName("package_directory")] string PackageDirectory,
    [property: JsonPropertyName("expected_package_id")] string? ExpectedPackageId = null);

public sealed record CanonicalRuntimeSource(
    [property: JsonPropertyName("registry_package_directory")] string RegistryPackageDirectory,
    [property: JsonPropertyName("carddatabase_package_directory")] string CardDatabasePackageDirectory,
    [property: JsonPropertyName("validation_mode")] string ValidationMode = "production");

public sealed record PlayerSetup(
    [property: JsonPropertyName("player_id")] string PlayerId,
    [property: JsonPropertyName("deck_id")] string DeckId);

public sealed record CreateMatchRequest(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("match_id")] string MatchId,
    [property: JsonPropertyName("seed")] int Seed,
    [property: JsonPropertyName("players")] ImmutableArray<PlayerSetup> Players,
    [property: JsonPropertyName("starting_hand_size")] int StartingHandSize,
    [property: JsonPropertyName("runtime_package")] RuntimePackageSource RuntimePackage,
    [property: JsonPropertyName("canonical_data")]
    [property: JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    CanonicalRuntimeSource? CanonicalData = null);

public sealed record CreateMatchResponse(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("accepted")] bool Accepted,
    [property: JsonPropertyName("match_id")] string? MatchId,
    [property: JsonPropertyName("runtime_package_id")] string? RuntimePackageId,
    [property: JsonPropertyName("state_version")] int StateVersion,
    [property: JsonPropertyName("diagnostics")] ImmutableArray<EngineDiagnostic> Diagnostics);

public sealed record LegalAction(
    [property: JsonPropertyName("action_id")] string ActionId,
    [property: JsonPropertyName("action_type")] string ActionType,
    [property: JsonPropertyName("player_id")] string PlayerId,
    [property: JsonPropertyName("enabled")] bool Enabled,
    [property: JsonPropertyName("order_rank")] int OrderRank,
    [property: JsonPropertyName("disabled_reason")] string? DisabledReason,
    [property: JsonPropertyName("payload_schema")] JsonElement PayloadSchema);

public sealed record LegalActionSpace(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("match_id")] string MatchId,
    [property: JsonPropertyName("state_version")] int StateVersion,
    [property: JsonPropertyName("turn")] int Turn,
    [property: JsonPropertyName("phase")] string Phase,
    [property: JsonPropertyName("active_player_id")] string ActivePlayerId,
    [property: JsonPropertyName("priority_player_id")] string PriorityPlayerId,
    [property: JsonPropertyName("player_id")] string PlayerId,
    [property: JsonPropertyName("actions")] ImmutableArray<LegalAction> Actions);

public sealed record ActionRequest(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("request_id")] string RequestId,
    [property: JsonPropertyName("match_id")] string MatchId,
    [property: JsonPropertyName("player_id")] string PlayerId,
    [property: JsonPropertyName("expected_state_version")] int ExpectedStateVersion,
    [property: JsonPropertyName("action_id")] string ActionId,
    [property: JsonPropertyName("action_type")] string ActionType,
    [property: JsonPropertyName("payload")] JsonElement Payload);

public sealed record NormalInflowActionPayload(
    [property: JsonPropertyName("card_instance_id")] string CardInstanceId);

public sealed record PlayCardActionPayload(
    [property: JsonPropertyName("card_instance_id")] string CardInstanceId,
    [property: JsonPropertyName("domain_row")] string DomainRow,
    [property: JsonPropertyName("lane_index")] int LaneIndex,
    [property: JsonPropertyName("aura_source_card_instance_ids")]
    ImmutableArray<string> AuraSourceCardInstanceIds);

public sealed record CanonicalTargetSelectionPayload(
    [property: JsonPropertyName("target_id")] string TargetId,
    [property: JsonPropertyName("card_instance_ids")]
    ImmutableArray<string> CardInstanceIds);

public sealed record ResolveTriggeredAbilityActionPayload(
    [property: JsonPropertyName("pending_trigger_id")] string PendingTriggerId,
    [property: JsonPropertyName("target_selections")]
    ImmutableArray<CanonicalTargetSelectionPayload> TargetSelections);

public sealed record EngineDiagnostic(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("code")] string Code,
    [property: JsonPropertyName("severity")] string Severity,
    [property: JsonPropertyName("category")] string Category,
    [property: JsonPropertyName("blocking")] bool Blocking,
    [property: JsonPropertyName("safe_message")] string SafeMessage,
    [property: JsonPropertyName("developer_message")] string DeveloperMessage,
    [property: JsonPropertyName("retry_policy")] string RetryPolicy,
    [property: JsonPropertyName("details")] JsonElement Details);

public sealed record ZoneMovePayload(
    [property: JsonPropertyName("source_action_id")] string SourceActionId,
    [property: JsonPropertyName("source_action_type")] string SourceActionType,
    [property: JsonPropertyName("card_instance_id")] string CardInstanceId,
    [property: JsonPropertyName("card_id")] string CardId,
    [property: JsonPropertyName("owner_player_id")] string OwnerPlayerId,
    [property: JsonPropertyName("controller_player_id")] string ControllerPlayerId,
    [property: JsonPropertyName("from_zone")] string FromZone,
    [property: JsonPropertyName("to_zone")] string ToZone,
    [property: JsonPropertyName("from_zone_index")] int FromZoneIndex,
    [property: JsonPropertyName("to_zone_index")] int ToZoneIndex,
    [property: JsonPropertyName("visibility_before")] string VisibilityBefore,
    [property: JsonPropertyName("visibility_after")] string VisibilityAfter);

public sealed record DomainZoneMovePayload(
    [property: JsonPropertyName("source_action_id")] string SourceActionId,
    [property: JsonPropertyName("source_action_type")] string SourceActionType,
    [property: JsonPropertyName("card_instance_id")] string CardInstanceId,
    [property: JsonPropertyName("card_id")] string CardId,
    [property: JsonPropertyName("owner_player_id")] string OwnerPlayerId,
    [property: JsonPropertyName("controller_player_id")] string ControllerPlayerId,
    [property: JsonPropertyName("from_zone")] string FromZone,
    [property: JsonPropertyName("to_zone")] string ToZone,
    [property: JsonPropertyName("from_zone_index")] int FromZoneIndex,
    [property: JsonPropertyName("domain_row")] string DomainRow,
    [property: JsonPropertyName("lane_index")] int LaneIndex,
    [property: JsonPropertyName("visibility_before")] string VisibilityBefore,
    [property: JsonPropertyName("visibility_after")] string VisibilityAfter);

public sealed record AuraSourceExhaustedPayload(
    [property: JsonPropertyName("source_action_id")] string SourceActionId,
    [property: JsonPropertyName("source_action_type")] string SourceActionType,
    [property: JsonPropertyName("payment_for_card_instance_id")] string PaymentForCardInstanceId,
    [property: JsonPropertyName("card_instance_id")] string CardInstanceId,
    [property: JsonPropertyName("card_id")] string CardId,
    [property: JsonPropertyName("owner_player_id")] string OwnerPlayerId,
    [property: JsonPropertyName("controller_player_id")] string ControllerPlayerId,
    [property: JsonPropertyName("wellspring_zone_index")] int WellspringZoneIndex,
    [property: JsonPropertyName("activity_state_before")] string ActivityStateBefore,
    [property: JsonPropertyName("activity_state_after")] string ActivityStateAfter,
    [property: JsonPropertyName("aura_units")] int AuraUnits);

public sealed record CardEnteredPlayPayload(
    [property: JsonPropertyName("source_action_id")] string SourceActionId,
    [property: JsonPropertyName("source_action_type")] string SourceActionType,
    [property: JsonPropertyName("card_instance_id")] string CardInstanceId,
    [property: JsonPropertyName("card_id")] string CardId,
    [property: JsonPropertyName("owner_player_id")] string OwnerPlayerId,
    [property: JsonPropertyName("controller_player_id")] string ControllerPlayerId,
    [property: JsonPropertyName("domain_row")] string DomainRow,
    [property: JsonPropertyName("lane_index")] int LaneIndex,
    [property: JsonPropertyName("activity_state")] string ActivityState,
    [property: JsonPropertyName("entered_domain_turn_number")] int EnteredDomainTurnNumber);

public sealed record CanonicalAbilityTriggeredPayload(
    [property: JsonPropertyName("pending_trigger_id")] string PendingTriggerId,
    [property: JsonPropertyName("ability_id")] string AbilityId,
    [property: JsonPropertyName("trigger_id")] string TriggerId,
    [property: JsonPropertyName("source_card_instance_id")] string SourceCardInstanceId,
    [property: JsonPropertyName("source_card_id")] string SourceCardId,
    [property: JsonPropertyName("controller_player_id")] string ControllerPlayerId,
    [property: JsonPropertyName("source_engine_event_id")] string SourceEngineEventId,
    [property: JsonPropertyName("source_engine_event_sequence")] int SourceEngineEventSequence,
    [property: JsonPropertyName("canonical_event_type_id")] string CanonicalEventTypeId);

public sealed record CardActivityChangedPayload(
    [property: JsonPropertyName("card_instance_id")] string CardInstanceId,
    [property: JsonPropertyName("card_id")] string CardId,
    [property: JsonPropertyName("from_activity_state")] string FromActivityState,
    [property: JsonPropertyName("to_activity_state")] string ToActivityState,
    [property: JsonPropertyName("source_ability_id")] string SourceAbilityId,
    [property: JsonPropertyName("source_effect_id")] string SourceEffectId,
    [property: JsonPropertyName("pending_trigger_id")] string PendingTriggerId);

public sealed record CanonicalAbilityResolvedPayload(
    [property: JsonPropertyName("pending_trigger_id")] string PendingTriggerId,
    [property: JsonPropertyName("ability_id")] string AbilityId,
    [property: JsonPropertyName("trigger_id")] string TriggerId,
    [property: JsonPropertyName("source_card_instance_id")] string SourceCardInstanceId,
    [property: JsonPropertyName("source_card_id")] string SourceCardId,
    [property: JsonPropertyName("controller_player_id")] string ControllerPlayerId,
    [property: JsonPropertyName("resolution_outcome")] string ResolutionOutcome,
    [property: JsonPropertyName("applied_effect_count")] int AppliedEffectCount);

public sealed record TurnTransitionPayload(
    [property: JsonPropertyName("source_action_id")] string SourceActionId,
    [property: JsonPropertyName("source_action_type")] string SourceActionType,
    [property: JsonPropertyName("previous_active_player_id")] string PreviousActivePlayerId,
    [property: JsonPropertyName("next_active_player_id")] string NextActivePlayerId,
    [property: JsonPropertyName("previous_priority_player_id")] string PreviousPriorityPlayerId,
    [property: JsonPropertyName("next_priority_player_id")] string NextPriorityPlayerId,
    [property: JsonPropertyName("turn_number_before")] int TurnNumberBefore,
    [property: JsonPropertyName("turn_number_after")] int TurnNumberAfter,
    [property: JsonPropertyName("phase_before")] string PhaseBefore,
    [property: JsonPropertyName("phase_after")] string PhaseAfter);

public sealed record EngineEvent(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("event_id")] string EventId,
    [property: JsonPropertyName("event_sequence")] int EventSequence,
    [property: JsonPropertyName("event_type")] string EventType,
    [property: JsonPropertyName("match_id")] string MatchId,
    [property: JsonPropertyName("state_version")] int StateVersion,
    [property: JsonPropertyName("turn_number")] int TurnNumber,
    [property: JsonPropertyName("actor_player_id")] string ActorPlayerId,
    [property: JsonPropertyName("cause_action_type")] string CauseActionType,
    [property: JsonPropertyName("visibility")] string Visibility,
    [property: JsonPropertyName("payload")] JsonElement Payload);

public sealed record ActionResponse(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("request_id")] string RequestId,
    [property: JsonPropertyName("match_id")] string MatchId,
    [property: JsonPropertyName("player_id")] string PlayerId,
    [property: JsonPropertyName("action_id")] string ActionId,
    [property: JsonPropertyName("action_type")] string ActionType,
    [property: JsonPropertyName("accepted")] bool Accepted,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("state_version_before")] int StateVersionBefore,
    [property: JsonPropertyName("state_version_after")] int StateVersionAfter,
    [property: JsonPropertyName("events")] ImmutableArray<EngineEvent> Events,
    [property: JsonPropertyName("diagnostics")] ImmutableArray<EngineDiagnostic> Diagnostics);

public sealed record CardReference(
    [property: JsonPropertyName("card_instance_id")] string CardInstanceId,
    [property: JsonPropertyName("card_id")] string CardId,
    [property: JsonPropertyName("zone")] string Zone,
    [property: JsonPropertyName("zone_sequence")] int ZoneSequence,
    [property: JsonPropertyName("controller_player_id")] string ControllerPlayerId,
    [property: JsonPropertyName("visibility")] string Visibility);

public sealed record DomainCardProjection(
    [property: JsonPropertyName("card_instance_id")] string CardInstanceId,
    [property: JsonPropertyName("card_id")] string CardId,
    [property: JsonPropertyName("owner_player_id")] string OwnerPlayerId,
    [property: JsonPropertyName("controller_player_id")] string ControllerPlayerId,
    [property: JsonPropertyName("zone")] string Zone,
    [property: JsonPropertyName("zone_sequence")] int ZoneSequence,
    [property: JsonPropertyName("visibility")] string Visibility,
    [property: JsonPropertyName("activity_state")] string ActivityState,
    [property: JsonPropertyName("entered_domain_turn_number")] int EnteredDomainTurnNumber);

public sealed record DomainSlotProjection(
    [property: JsonPropertyName("row")] string Row,
    [property: JsonPropertyName("lane_index")] int LaneIndex,
    [property: JsonPropertyName("occupied")] bool Occupied,
    [property: JsonPropertyName("occupant")] DomainCardProjection? Occupant);

public sealed record PlayerDomainProjection(
    [property: JsonPropertyName("player_id")] string PlayerId,
    [property: JsonPropertyName("occupied_slot_count")] int OccupiedSlotCount,
    [property: JsonPropertyName("empty_slot_count")] int EmptySlotCount,
    [property: JsonPropertyName("horizon")] ImmutableArray<DomainSlotProjection> Horizon,
    [property: JsonPropertyName("zenith")] ImmutableArray<DomainSlotProjection> Zenith);

public sealed record DomainBoardProjection(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("zone")] string Zone,
    [property: JsonPropertyName("visibility_mode")] string VisibilityMode,
    [property: JsonPropertyName("lane_count")] int LaneCount,
    [property: JsonPropertyName("players")] ImmutableArray<PlayerDomainProjection> Players);

public sealed record ZoneSnapshot(
    [property: JsonPropertyName("zone")] string Zone,
    [property: JsonPropertyName("count")] int Count,
    [property: JsonPropertyName("visibility_mode")] string VisibilityMode,
    [property: JsonPropertyName("redacted")] bool Redacted,
    [property: JsonPropertyName("objects")] ImmutableArray<CardReference> Objects);

public sealed record WellspringCardProjection(
    [property: JsonPropertyName("card_id")] string CardId,
    [property: JsonPropertyName("activity_state")] string ActivityState);

public sealed record WellspringResourceSummary(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("player_id")] string PlayerId,
    [property: JsonPropertyName("wellspring_card_count")] int WellspringCardCount,
    [property: JsonPropertyName("magnitude")] int Magnitude,
    [property: JsonPropertyName("active_source_count")] int ActiveSourceCount,
    [property: JsonPropertyName("exhausted_source_count")] int ExhaustedSourceCount,
    [property: JsonPropertyName("available_aura")] int AvailableAura);

public sealed record WellspringProjection(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("zone")] string Zone,
    [property: JsonPropertyName("visibility_mode")] string VisibilityMode,
    [property: JsonPropertyName("redacted")] bool Redacted,
    [property: JsonPropertyName("wellspring_card_count")] int WellspringCardCount,
    [property: JsonPropertyName("magnitude")] int Magnitude,
    [property: JsonPropertyName("active_source_count")] int ActiveSourceCount,
    [property: JsonPropertyName("exhausted_source_count")] int ExhaustedSourceCount,
    [property: JsonPropertyName("available_aura")] int AvailableAura,
    [property: JsonPropertyName("objects")] ImmutableArray<WellspringCardProjection> Objects);

public sealed record ResourceSummary(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("players")] ImmutableArray<WellspringResourceSummary> Players);

public sealed record PlayerSnapshotEntry(
    [property: JsonPropertyName("player_id")] string PlayerId,
    [property: JsonPropertyName("relation")] string Relation,
    [property: JsonPropertyName("deck")] ZoneSnapshot Deck,
    [property: JsonPropertyName("hand")] ZoneSnapshot Hand,
    [property: JsonPropertyName("void")] ZoneSnapshot Void,
    [property: JsonPropertyName("wellspring")] WellspringProjection Wellspring);

public sealed record PlayerSnapshot(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("snapshot_id")] string SnapshotId,
    [property: JsonPropertyName("match_id")] string MatchId,
    [property: JsonPropertyName("viewer_player_id")] string ViewerPlayerId,
    [property: JsonPropertyName("state_version")] int StateVersion,
    [property: JsonPropertyName("turn_number")] int TurnNumber,
    [property: JsonPropertyName("phase")] string Phase,
    [property: JsonPropertyName("active_player_id")] string ActivePlayerId,
    [property: JsonPropertyName("priority_player_id")] string PriorityPlayerId,
    [property: JsonPropertyName("players")] ImmutableArray<PlayerSnapshotEntry> Players,
    [property: JsonPropertyName("legal_actions")] ImmutableArray<LegalAction> LegalActions,
    [property: JsonPropertyName("visible_event_sequence")] int VisibleEventSequence,
    [property: JsonPropertyName("board_summary")] JsonElement BoardSummary,
    [property: JsonPropertyName("resource_summary")] ResourceSummary ResourceSummary,
    [property: JsonPropertyName("pending_decision_summary")] JsonElement PendingDecisionSummary,
    [property: JsonPropertyName("match_result")] MatchResult MatchResult);

public sealed record DebugPlayerSnapshot(
    string PlayerId,
    string DeckId,
    ImmutableArray<string> DeckCardInstanceIds,
    ImmutableArray<string> HandCardInstanceIds,
    ImmutableArray<string> VoidCardInstanceIds,
    ImmutableArray<string> WellspringCardInstanceIds,
    ImmutableArray<string?> HorizonCardInstanceIds,
    ImmutableArray<string?> ZenithCardInstanceIds,
    int? NormalInflowUsedTurnNumber);

public sealed record DebugCardInstanceSnapshot(
    string CardInstanceId,
    string CardId,
    string OwnerPlayerId,
    string ControllerPlayerId,
    string Zone,
    int ZoneIndex,
    string Visibility,
    int CreatedSequence,
    int ZoneSequence,
    string InitialZone,
    string? ActivityState,
    string? DomainRow,
    int? DomainLaneIndex,
    int? EnteredDomainTurnNumber);

public sealed record DebugSnapshot(
    string SchemaVersion,
    string MatchId,
    int Seed,
    int StateVersion,
    int TurnNumber,
    string Phase,
    string ActivePlayerId,
    string PriorityPlayerId,
    ImmutableArray<DebugPlayerSnapshot> Players,
    ImmutableArray<DebugCardInstanceSnapshot> CardInstances,
    ImmutableArray<EngineEvent> Events,
    JsonElement PendingTriggerSummary,
    MatchResult MatchResult);

public sealed record MatchResult(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("completed")] bool Completed,
    [property: JsonPropertyName("outcome")] string Outcome,
    [property: JsonPropertyName("winner_player_id")] string? WinnerPlayerId,
    [property: JsonPropertyName("reason")] string? Reason);
