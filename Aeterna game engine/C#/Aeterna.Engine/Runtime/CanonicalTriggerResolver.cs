using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record CanonicalAbilityRuntimeContext(
    string RegistryPackageId,
    string RegistrySchemaVersion,
    string RegistryDataVersion,
    string CardDatabasePackageId,
    string CardDatabaseSchemaVersion,
    string CardDatabaseDataVersion,
    CanonicalPackageValidationMode ValidationMode,
    CanonicalCardCatalog? Cards,
    CanonicalAbilityCatalog Abilities);

internal sealed record CanonicalAbilityRuntimeStatus(
    bool Available,
    string? RegistryPackageId,
    string? CardDatabasePackageId,
    CanonicalPackageValidationMode? ValidationMode,
    int AbilityCount);

internal sealed record CanonicalTriggeredAbilityDiscovery(
    string AbilityId,
    int AbilityIndex,
    string SourceCardInstanceId,
    string SourceCardId,
    string TriggerId,
    int TriggerSequence,
    string CanonicalEventTypeId,
    string ControllerPlayerId,
    string EngineEventId,
    string EngineEventType,
    string AbilityKindId,
    string ActiveZoneId,
    string? TriggerFilterConditionId,
    string? SourceFromZoneId,
    string? SourceToZoneId,
    string? SourceZoneTransitionInstanceId);

internal sealed record CanonicalTriggerEventSource(
    CardInstanceState Card,
    string ActivationZoneId,
    string? FromZoneId,
    string? ToZoneId,
    string? ZoneTransitionInstanceId);

internal static class CanonicalTriggerResolver
{
    internal const string EnteredPlayEngineEventType = "card_entered_play";
    internal const string EnteredPlayCanonicalEventTypeId = "event_card_entered_play";
    internal const string ZoneChangedEngineEventType = "card_zone_changed";
    internal const string ZoneChangedCanonicalEventTypeId = "event_card_zone_changed";

    private const string TriggeredAbilityKindId = "triggered";
    private const string AbilitySourceCardReferenceTypeId = "ref_ability_source_card";
    private const string ActiveStatus = "active";
    private const string AfterEventStageId = "after";

    internal static string? MapEngineEventType(string engineEventType) => engineEventType switch
    {
        EnteredPlayEngineEventType => EnteredPlayCanonicalEventTypeId,
        ZoneChangedEngineEventType => ZoneChangedCanonicalEventTypeId,
        _ => null,
    };

    internal static ImmutableArray<CanonicalTriggeredAbilityDiscovery> Resolve(
        CanonicalAbilityCatalog catalog,
        EngineEvent engineEvent,
        MatchState state)
    {
        ArgumentNullException.ThrowIfNull(catalog);
        ArgumentNullException.ThrowIfNull(engineEvent);
        ArgumentNullException.ThrowIfNull(state);

        var canonicalEventTypeId = MapEngineEventType(engineEvent.EventType);
        if (canonicalEventTypeId is null)
        {
            return ImmutableArray<CanonicalTriggeredAbilityDiscovery>.Empty;
        }

        ValidateAuthoritativeEvent(engineEvent, state);
        var source = canonicalEventTypeId switch
        {
            EnteredPlayCanonicalEventTypeId => new CanonicalTriggerEventSource(
                ReadEnteredPlaySource(engineEvent.Payload, state),
                "dominion",
                null,
                "dominion",
                null),
            ZoneChangedCanonicalEventTypeId => ReadZoneChangedSource(engineEvent.Payload, state),
            _ => throw SourceInvalid("Mapped canonical trigger event is unsupported."),
        };
        if (!catalog.AbilitiesByCardId.TryGetValue(source.Card.CardId, out var abilities))
        {
            return ImmutableArray<CanonicalTriggeredAbilityDiscovery>.Empty;
        }

        var result = ImmutableArray.CreateBuilder<CanonicalTriggeredAbilityDiscovery>();
        foreach (var ability in abilities)
        {
            if (!string.Equals(ability.Status, ActiveStatus, StringComparison.Ordinal)
                || !string.Equals(ability.AbilityKindId, TriggeredAbilityKindId, StringComparison.Ordinal)
                || !string.Equals(ability.ActiveZoneId, source.ActivationZoneId, StringComparison.Ordinal))
            {
                continue;
            }

            foreach (var trigger in ability.Triggers)
            {
                if (!MatchesTrigger(trigger, canonicalEventTypeId, source, state))
                {
                    continue;
                }

                result.Add(new CanonicalTriggeredAbilityDiscovery(
                    ability.AbilityId,
                    ability.AbilityIndex,
                    source.Card.CardInstanceId,
                    source.Card.CardId,
                    trigger.TriggerId,
                    trigger.Sequence,
                    canonicalEventTypeId,
                    source.Card.ControllerPlayerId,
                    engineEvent.EventId,
                    engineEvent.EventType,
                    ability.AbilityKindId!,
                    ability.ActiveZoneId!,
                    trigger.FilterConditionId,
                    string.Equals(canonicalEventTypeId, ZoneChangedCanonicalEventTypeId, StringComparison.Ordinal)
                        ? source.FromZoneId
                        : null,
                    string.Equals(canonicalEventTypeId, ZoneChangedCanonicalEventTypeId, StringComparison.Ordinal)
                        ? source.ToZoneId
                        : null,
                    string.Equals(canonicalEventTypeId, ZoneChangedCanonicalEventTypeId, StringComparison.Ordinal)
                        ? source.ZoneTransitionInstanceId
                        : null));
            }
        }

        // CanonicalAbilityMaterializer validates unique (card_id, ability_index)
        // and (ability_id, trigger sequence) scopes and stores both arrays in that
        // order. No game-semantic tie-breaker is introduced here.
        return result.ToImmutable();
    }

    private static bool MatchesTrigger(
        CanonicalAbilityTriggerDefinition trigger,
        string canonicalEventTypeId,
        CanonicalTriggerEventSource source,
        MatchState state) =>
        string.Equals(trigger.Status, ActiveStatus, StringComparison.Ordinal)
        && string.Equals(trigger.EventTypeId, canonicalEventTypeId, StringComparison.Ordinal)
        && string.Equals(trigger.SubjectReferenceTypeId, AbilitySourceCardReferenceTypeId, StringComparison.Ordinal)
        && (trigger.EventStageId is null
            || string.Equals(trigger.EventStageId, AfterEventStageId, StringComparison.Ordinal))
        && (trigger.FromZoneId is null
            || string.Equals(trigger.FromZoneId, source.FromZoneId, StringComparison.Ordinal))
        && (trigger.ToZoneId is null
            || string.Equals(trigger.ToZoneId, source.ToZoneId, StringComparison.Ordinal))
        && (trigger.PhaseId is null
            || string.Equals(trigger.PhaseId, state.Phase, StringComparison.Ordinal))
        && (trigger.PlayerReferenceId is null
            || string.Equals(trigger.PlayerReferenceId, "ability_controller", StringComparison.Ordinal));

    private static void ValidateAuthoritativeEvent(EngineEvent engineEvent, MatchState state)
    {
        if (!string.Equals(engineEvent.SchemaVersion, ContractSchemas.EngineEvent, StringComparison.Ordinal)
            || !string.Equals(engineEvent.MatchId, state.MatchId, StringComparison.Ordinal)
            || engineEvent.StateVersion != state.StateVersion
            || engineEvent.EventSequence < 1
            || engineEvent.EventSequence > state.Events.Count)
        {
            throw SourceInvalid("Canonical trigger discovery received an event outside the current authoritative state boundary.");
        }

        var committedEvent = state.Events[engineEvent.EventSequence - 1];
        if (!string.Equals(committedEvent.SchemaVersion, engineEvent.SchemaVersion, StringComparison.Ordinal)
            || !string.Equals(committedEvent.EventId, engineEvent.EventId, StringComparison.Ordinal)
            || committedEvent.EventSequence != engineEvent.EventSequence
            || !string.Equals(committedEvent.EventType, engineEvent.EventType, StringComparison.Ordinal)
            || !string.Equals(committedEvent.MatchId, engineEvent.MatchId, StringComparison.Ordinal)
            || committedEvent.StateVersion != engineEvent.StateVersion
            || committedEvent.TurnNumber != engineEvent.TurnNumber
            || !string.Equals(committedEvent.ActorPlayerId, engineEvent.ActorPlayerId, StringComparison.Ordinal)
            || !string.Equals(committedEvent.CauseActionType, engineEvent.CauseActionType, StringComparison.Ordinal)
            || !string.Equals(committedEvent.Visibility, engineEvent.Visibility, StringComparison.Ordinal)
            || !string.Equals(committedEvent.Payload.GetRawText(), engineEvent.Payload.GetRawText(), StringComparison.Ordinal))
        {
            throw SourceInvalid("Canonical trigger discovery requires the committed authoritative engine event.");
        }
    }

    private static CardInstanceState ReadEnteredPlaySource(JsonElement payload, MatchState state)
    {
        var cardInstanceId = ReadRequiredString(payload, "card_instance_id");
        var cardId = ReadRequiredString(payload, "card_id");
        var ownerPlayerId = ReadRequiredString(payload, "owner_player_id");
        var controllerPlayerId = ReadRequiredString(payload, "controller_player_id");
        var domainRow = ReadRequiredString(payload, "domain_row");
        var laneIndex = ReadRequiredInteger(payload, "lane_index");
        var activityState = ReadRequiredString(payload, "activity_state");
        var enteredTurn = ReadRequiredInteger(payload, "entered_domain_turn_number");

        if (!state.CardInstances.TryGetValue(cardInstanceId, out var source))
        {
            throw SourceInvalid("Entered-play event references an unknown card instance.");
        }

        var expectedRow = source.DomainRow switch
        {
            DomainRow.Horizon => "horizon",
            DomainRow.Zenith => "zenith",
            _ => null,
        };
        if (!string.Equals(source.CardId, cardId, StringComparison.Ordinal)
            || !string.Equals(source.OwnerPlayerId, ownerPlayerId, StringComparison.Ordinal)
            || !string.Equals(source.ControllerPlayerId, controllerPlayerId, StringComparison.Ordinal)
            || !string.Equals(source.Zone, "dominion", StringComparison.Ordinal)
            || !string.Equals(source.Visibility, "public", StringComparison.Ordinal)
            || !string.Equals(source.ActivityState, activityState, StringComparison.Ordinal)
            || !string.Equals(expectedRow, domainRow, StringComparison.Ordinal)
            || source.DomainLaneIndex != laneIndex
            || source.EnteredDomainTurnNumber != enteredTurn
            || state.Players.All(player => !string.Equals(player.PlayerId, controllerPlayerId, StringComparison.Ordinal)))
        {
            throw SourceInvalid("Entered-play event and source card instance are inconsistent.");
        }

        if (laneIndex is < 0 or >= DomainState.LaneCount
            || source.DomainLaneIndex is < 0 or >= DomainState.LaneCount)
        {
            throw SourceInvalid("Entered-play source Domain lane is outside the canonical engine topology.");
        }

        var controller = state.GetPlayer(controllerPlayerId);
        if (!string.Equals(controller.Domain.GetSlots(source.DomainRow!.Value)[laneIndex], cardInstanceId, StringComparison.Ordinal))
        {
            throw SourceInvalid("Entered-play source does not occupy its authoritative Domain slot.");
        }

        return source;
    }

    private static CanonicalTriggerEventSource ReadZoneChangedSource(JsonElement payload, MatchState state)
    {
        var transitionId = ReadRequiredString(payload, "zone_transition_instance_id");
        var cardInstanceId = ReadRequiredString(payload, "card_instance_id");
        var cardId = ReadRequiredString(payload, "card_id");
        var ownerPlayerId = ReadRequiredString(payload, "owner_player_id");
        var controllerPlayerIdBefore = ReadRequiredString(payload, "controller_player_id");
        var fromZoneId = ReadRequiredString(payload, "from_zone_id");
        var toZoneId = ReadRequiredString(payload, "to_zone_id");
        var fromPresenceId = ReadRequiredString(payload, "from_zone_presence_instance_id");
        var toPresenceId = ReadRequiredString(payload, "to_zone_presence_instance_id");
        var toZoneIndex = ReadRequiredInteger(payload, "to_zone_index");
        var visibilityAfter = ReadRequiredString(payload, "visibility_after");
        _ = ReadRequiredString(payload, "cause_event_id");
        _ = ReadRequiredString(payload, "from_domain_row_id");
        _ = ReadRequiredInteger(payload, "from_domain_lane_index");

        if (!state.CardInstances.TryGetValue(cardInstanceId, out var source)
            || !string.Equals(source.CardId, cardId, StringComparison.Ordinal)
            || !string.Equals(source.OwnerPlayerId, ownerPlayerId, StringComparison.Ordinal)
            || state.Players.All(player => !string.Equals(
                player.PlayerId,
                controllerPlayerIdBefore,
                StringComparison.Ordinal))
            || !string.Equals(fromZoneId, "dominion", StringComparison.Ordinal)
            || toZoneId is not ("void" or "hand")
            || !string.Equals(source.Zone, toZoneId, StringComparison.Ordinal)
            || source.ZoneIndex != toZoneIndex
            || source.DomainRow is not null
            || source.DomainLaneIndex is not null
            || source.ActivityState is not null
            || source.DamageMarked != 0
            || !string.Equals(source.Visibility, visibilityAfter, StringComparison.Ordinal)
            || !string.Equals(
                fromPresenceId,
                PresenceId(cardInstanceId, source.ZoneSequence - 1),
                StringComparison.Ordinal)
            || !string.Equals(
                toPresenceId,
                PresenceId(cardInstanceId, source.ZoneSequence),
                StringComparison.Ordinal))
        {
            throw SourceInvalid("Zone-change event and moved card instance are inconsistent.");
        }

        var owner = state.GetPlayer(ownerPlayerId);
        var destination = string.Equals(toZoneId, "void", StringComparison.Ordinal)
            ? owner.VoidCardInstanceIds
            : owner.HandCardInstanceIds;
        if (toZoneIndex < 0
            || toZoneIndex >= destination.Count
            || !string.Equals(destination[toZoneIndex], cardInstanceId, StringComparison.Ordinal))
        {
            throw SourceInvalid("Zone-change source does not occupy its authoritative destination index.");
        }

        return new CanonicalTriggerEventSource(
            source,
            fromZoneId,
            fromZoneId,
            toZoneId,
            transitionId);
    }

    private static string ReadRequiredString(JsonElement payload, string propertyName)
    {
        if (payload.ValueKind != JsonValueKind.Object
            || !payload.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw SourceInvalid($"Entered-play event payload string is missing: {propertyName}");
        }

        return value.GetString()!;
    }

    private static int ReadRequiredInteger(JsonElement payload, string propertyName)
    {
        if (payload.ValueKind != JsonValueKind.Object
            || !payload.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var result))
        {
            throw SourceInvalid($"Entered-play event payload integer is missing: {propertyName}");
        }

        return result;
    }

    private static EngineStateException SourceInvalid(string message) =>
        new("CANONICAL_TRIGGER_SOURCE_INVALID", message);

    private static string PresenceId(string cardInstanceId, int zoneSequence) =>
        $"zone_presence_{cardInstanceId}_{zoneSequence:000000}";
}
