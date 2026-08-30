using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Rules;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

internal static class ReactionPriorityTests
{
    private const string UnderlyingCardId = "IGN-HAM-044";
    private const string UnderlyingAbilityId = "ability_ign_ham_044_01";
    private const string UnderlyingTargetId = "target_ign_ham_044_01_enemy_zenit_entity";
    private const string ExhaustReactionCardId = "IGN-HAM-005";
    private const string ExhaustReactionAbilityId = "ability_ign_ham_005_01";
    private const string ExhaustReactionTargetId = "target_ign_ham_005_01_enemy_horizont_entity";
    private const string MoveReactionCardId = "AQU-MOR-007";
    private const string MoveReactionAbilityId = "ability_aqu_mor_007_01";
    private const string MoveReactionTargetId = "target_aqu_mor_007_01_enemy_horizont_entity";
    private const string DamageReactionCardId = "IGN-LAN-003";
    private const string DamageReactionAbilityId = "ability_ign_lan_003_01";
    private const string DamageReactionTargetId = "target_ign_lan_003_01_enemy_entity";
    private const string ProfileId = "test_reaction_profile_v1";

    internal static void OpeningStateLegalSurfaceAndProjection()
    {
        var fixture = CreateFixture();
        var response = OpenWindow(fixture);
        True(response.Accepted, "Explicit reactable profile did not open a window.");
        Equal(1, response.StateVersionAfter, "Reaction opening did not commit one state version.");
        Equal("active", fixture.State.GetCardInstance("underlying_target").ActivityState, "Underlying final effect resolved before closure.");
        Equal("resolution", fixture.State.GetCardInstance(fixture.UnderlyingSourceId).Zone, "Played-card prerequisite transition did not complete.");

        var window = NotNull(fixture.State.ReactionWindow, "ReactionWindow is not authoritative MatchState state.");
        Equal("player_2", fixture.State.PriorityPlayerId, "Non-initiator did not receive first priority.");
        Equal(2, window.EligibleResponderPlayerIds.Count, "Both-player profile produced the wrong responder set.");
        Equal(0, window.ConsecutivePassCount, "Opening pass count is invalid.");
        Equal(1, window.OpenedAtStateVersion, "OpenedAtStateVersion is invalid.");
        True(!window.ReactionSubjectId.StartsWith("event_", StringComparison.Ordinal), "ReactionSubjectId reused EngineEvent identity.");
        var bottom = Single(fixture.State.ResolutionStack);
        Equal("underlying_resolution", bottom.EntryKindId, "Underlying resolution is not the bottom entry.");
        Equal(window.UnderlyingResolutionId, bottom.ResolutionId, "Window and bottom resolution identities differ.");
        Equal("played_card", bottom.AbilityResolution.ResolutionOriginId, "Underlying origin is invalid.");
        Equal(ReactionPolicyIds.PlayedCardResolutionPresence,
            bottom.AbilityResolution.SourceRelevancePolicyId,
            "Underlying played-card lifecycle reused reaction-source same-zone policy.");

        var priorityActions = fixture.Session.ListLegalActions("player_2", includeDisabled: true).Actions;
        True(priorityActions.Single(action => action.ActionType == "pass_priority").Enabled, "Priority player cannot pass.");
        var react = priorityActions.Single(action => action.ActionType == "react");
        True(react.Enabled, "Legal public/in-play reaction did not enable react.");
        var option = Single(react.PayloadSchema.GetProperty("reaction_options").EnumerateArray());
        Equal(ExhaustReactionAbilityId, option.GetProperty("ability_id").GetString(), "Reaction option exposed the wrong typed ability.");
        True(priorityActions.Where(action => action.ActionType is "advance_phase" or "play_card")
            .All(action => !action.Enabled && action.DisabledReason == "reaction_window_open"), "Normal phase actions bypassed the ReactionWindow.");

        var nonPriorityActions = fixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions;
        True(nonPriorityActions.Where(action => action.ActionType is "react" or "pass_priority")
            .All(action => !action.Enabled && action.DisabledReason == "not_priority_player"), "Non-priority reaction action was enabled.");
        False(nonPriorityActions.Single(action => action.ActionType == "react").PayloadSchema.TryGetProperty("reaction_options", out _), "Non-priority viewer received reaction options.");

        var prioritySummary = fixture.Session.GetPlayerSnapshot("player_2").PendingDecisionSummary;
        Equal("reaction_window", prioritySummary.GetProperty("pending_type").GetString(), "Pending summary type is invalid.");
        True(prioritySummary.GetProperty("viewer_is_priority_player").GetBoolean(), "Priority viewer summary flag is false.");
        True(prioritySummary.GetProperty("viewer_is_eligible_responder").GetBoolean(), "Eligible viewer summary flag is false.");
        Equal(1, prioritySummary.GetProperty("stack_depth").GetInt32(), "Pending summary stack depth is invalid.");
        False(prioritySummary.TryGetProperty("reaction_options", out _), "Snapshot leaked reaction options.");
        False(prioritySummary.TryGetProperty("source_card_instance_id", out _), "Snapshot leaked stack source identity.");

        var nonPrioritySummary = fixture.Session.GetPlayerSnapshot("player_1").PendingDecisionSummary;
        False(nonPrioritySummary.GetProperty("viewer_is_priority_player").GetBoolean(), "Non-priority viewer summary flag is true.");
        Equal(window.ReactionSubjectId, nonPrioritySummary.GetProperty("reaction_subject_id").GetString(), "Viewer summaries lost subject correlation.");
        EngineSession.ValidateState(fixture.State, fixture.CanonicalCards, fixture.CanonicalAbilities);
    }

    internal static void ReactablePlayMovesHandToResolution()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        var response = OpenWindow(fixture);
        True(response.Accepted, "Reactable played card was rejected.");
        var card = fixture.State.GetCardInstance(fixture.UnderlyingSourceId);
        Equal("resolution", card.Zone, "Reactable played card did not enter Resolution.");
        Equal(0, card.ZoneIndex, "Resolution-zone index is invalid.");
        Equal(fixture.UnderlyingSourceId, Single(fixture.State.ResolutionCardInstanceIds), "Shared Resolution membership is invalid.");
        Equal("public", card.Visibility, "Resolution card is not public.");
    }

    internal static void ReactablePlayRemovesOrdinaryHandMembership()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        OpenWindow(fixture);
        False(fixture.State.GetPlayer("player_1").HandCardInstanceIds.Contains(
            fixture.UnderlyingSourceId,
            StringComparer.Ordinal), "Pending Resolution card remained in Hand.");
    }

    internal static void ReactablePlayDoesNotEnterVoidWhileWindowOpen()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        OpenWindow(fixture);
        False(fixture.State.GetPlayer("player_1").VoidCardInstanceIds.Contains(
            fixture.UnderlyingSourceId,
            StringComparer.Ordinal), "Pending Resolution card entered Void before its attempt.");
        Equal("resolution", fixture.State.GetCardInstance(fixture.UnderlyingSourceId).Zone, "Pending source left Resolution.");
    }

    internal static void ResolutionZoneProjectionIsPublic()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        var opening = OpenWindow(fixture);
        foreach (var viewer in new[] { "player_1", "player_2" })
        {
            var projection = fixture.Session.GetPlayerSnapshot(viewer)
                .PendingDecisionSummary
                .GetProperty("resolution_zone");
            Equal("resolution", projection.GetProperty("zone").GetString(), "Projected shared zone token is invalid.");
            Equal("public", projection.GetProperty("visibility_mode").GetString(), "Projected Resolution visibility is invalid.");
            var visibleCard = Single(projection.GetProperty("objects").EnumerateArray());
            Equal(fixture.UnderlyingSourceId, visibleCard.GetProperty("card_instance_id").GetString(), "Resolution projection hid object identity.");
            Equal(UnderlyingCardId, visibleCard.GetProperty("card_id").GetString(), "Resolution projection hid card identity.");
        }

        var opposingMove = fixture.Session.GetEvents("player_2")
            .Single(item => opening.Events.Any(source => source.EventId == item.EventId)
                            && item.EventType == "zone_move");
        Equal("resolution", opposingMove.Payload.GetProperty("to_zone").GetString(), "Opponent did not observe Resolution entry.");
        Equal(false, opposingMove.Payload.GetProperty("identity_redacted").GetBoolean(), "Public Resolution identity was redacted.");
    }

    internal static void PendingResolutionCardCannotBeReplayed()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        OpenWindow(fixture);
        var play = ListedAction(fixture, "player_1", "play_card");
        False(play.Enabled, "Normal play remained enabled during the Reaction window.");
        AssertRejectedImmutable(
            fixture,
            () => SubmitRaw(
                fixture,
                "player_1",
                play.ActionId,
                play.ActionType,
                ContractJsonValue.From(new PlayCardActionPayload(
                    fixture.UnderlyingSourceId,
                    DomainRow: null,
                    LaneIndex: null,
                    ImmutableArray<string>.Empty,
                    [new CanonicalTargetSelectionPayload(UnderlyingTargetId, ["underlying_target"])]))),
            "ACTION_DISABLED");
    }

    internal static void StandardClosureResolvesThenMovesToVoid()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        OpenWindow(fixture);
        Pass(fixture, "player_2");
        var closure = Pass(fixture, "player_1");
        True(closure.Accepted, "Standard closure was rejected.");
        Equal("exhausted", fixture.State.GetCardInstance("underlying_target").ActivityState, "Underlying attempt did not resolve.");
        Equal("void", fixture.State.GetCardInstance(fixture.UnderlyingSourceId).Zone, "Resolved source did not enter Void.");
        Equal(0, fixture.State.ResolutionCardInstanceIds.Count, "Resolution retained the completed source.");
    }

    internal static void ReactionsResolveAboveUnderlyingCard()
    {
        var fixture = CreateFixture();
        OpenWindow(fixture);
        var reaction = React(fixture, "player_2", "p1_reaction_target");
        var reactionResolutionId = reaction.Events.Single(item => item.EventType == "reaction_declared")
            .Payload.GetProperty("resolution_id").GetString();
        Pass(fixture, "player_1");
        var closure = Pass(fixture, "player_2");
        var resolved = closure.Events.Where(item => item.EventType == "resolution_entry_resolved")
            .Select(item => item.Payload.GetProperty("resolution_id").GetString())
            .ToArray();
        Equal(reactionResolutionId, resolved[0], "Reaction did not resolve above the underlying entry.");
        Equal("void", fixture.State.GetCardInstance(fixture.UnderlyingSourceId).Zone, "Underlying lifecycle did not complete after the reaction.");
    }

    internal static void InvalidatedUnderlyingStillMovesToVoid()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        OpenWindow(fixture);
        fixture.State.GetCardInstance("underlying_target").ZoneSequence += 1;
        Pass(fixture, "player_2");
        var closure = Pass(fixture, "player_1");
        True(closure.Events.Any(item => item.EventType == "resolution_entry_invalidated"
                                        && item.Payload.GetProperty("entry_kind_id").GetString() == "underlying_resolution"), "Underlying attempt was not invalidated.");
        Equal("active", fixture.State.GetCardInstance("underlying_target").ActivityState, "Invalidated underlying effect mutated its target.");
        Equal("void", fixture.State.GetCardInstance(fixture.UnderlyingSourceId).Zone, "Invalidated underlying source did not enter Void.");
    }

    internal static void VoidMoveFollowsResolutionAttemptEvent()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        OpenWindow(fixture);
        Pass(fixture, "player_2");
        var closure = Pass(fixture, "player_1");
        var events = closure.Events.ToArray();
        var resolvedIndex = Array.FindIndex(events, item => item.EventType == "resolution_entry_resolved");
        var voidIndex = Array.FindIndex(events, item => item.EventType == "zone_move"
            && item.Payload.GetProperty("from_zone").GetString() == "resolution"
            && item.Payload.GetProperty("to_zone").GetString() == "void");
        True(resolvedIndex >= 0 && voidIndex > resolvedIndex, "Void transition preceded the underlying resolution attempt completion.");
    }

    internal static void ResolutionIsNotDomainOrEnteredPlay()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        var opening = OpenWindow(fixture);
        var card = fixture.State.GetCardInstance(fixture.UnderlyingSourceId);
        Equal(null, card.DomainRow, "Resolution card acquired a Domain row.");
        Equal(null, card.DomainLaneIndex, "Resolution card acquired a Domain lane.");
        False(fixture.State.Players.SelectMany(player => player.Domain.HorizonCardInstanceIds
                .Concat(player.Domain.ZenithCardInstanceIds))
            .Contains(fixture.UnderlyingSourceId), "Resolution card occupied a Domain slot.");
        False(opening.Events.Any(item => item.EventType == "card_entered_play"), "Resolution entry emitted Domain entered_play.");
    }

    internal static void ResolutionHasNoSlotCapacityGate()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        var play = ListedAction(fixture, "player_1", "play_card");
        var option = play.PayloadSchema.GetProperty("play_options").EnumerateArray()
            .Single(item => item.GetProperty("card_instance_id").GetString() == fixture.UnderlyingSourceId);
        False(option.GetRawText().Contains("resolution_slot", StringComparison.Ordinal), "Resolution play invented a slot-capacity contract.");
        True(OpenWindow(fixture).Accepted, "Slot-free Resolution play was rejected.");
    }

    internal static void NonReactableResolutionPreservesSemanticOrder()
    {
        var fixture = CreateFixture(
            includeReactionSources: false,
            reactableOpening: false);
        var response = SubmitUnderlyingPlay(fixture);
        True(response.Accepted, "Non-reactable Resolution play was rejected.");
        var types = response.Events.Select(item => item.EventType).ToArray();
        var enterIndex = Array.FindIndex(types, item => item == "zone_move");
        var resolvedIndex = Array.FindIndex(types, item => item == "canonical_ability_resolved");
        var voidIndex = Array.FindLastIndex(types, item => item == "zone_move");
        True(enterIndex >= 0 && enterIndex < resolvedIndex && voidIndex > resolvedIndex,
            "Non-reactable play did not preserve hand-to-resolution, attempt, resolution-to-void order.");
        Equal("resolution", response.Events[enterIndex].Payload.GetProperty("to_zone").GetString(), "Non-reactable entry destination is invalid.");
        Equal("resolution", response.Events[voidIndex].Payload.GetProperty("from_zone").GetString(), "Non-reactable Void departure source is invalid.");
        Equal("void", fixture.State.GetCardInstance(fixture.UnderlyingSourceId).Zone, "Non-reactable source did not finish in Void.");
    }

    internal static void StandardPassLifecycleAndUnderlyingResolution()
    {
        var fixture = CreateFixture(includeReactionSources: false);
        OpenWindow(fixture);
        var first = Pass(fixture, "player_2");
        True(first.Accepted, "First standard pass was rejected.");
        Equal("player_1", fixture.State.PriorityPlayerId, "First pass did not transfer priority.");
        Equal(1, fixture.State.ReactionWindow!.ConsecutivePassCount, "First pass count is invalid.");
        Equal(false, Single(first.Events).Payload.GetProperty("window_closed").GetBoolean(), "First pass falsely closed the window.");
        Equal("active", fixture.State.GetCardInstance("underlying_target").ActivityState, "First pass resolved the underlying effect.");

        var second = Pass(fixture, "player_1");
        True(second.Accepted, "Second standard pass was rejected.");
        Equal(null, fixture.State.ReactionWindow, "Two passes did not close the window.");
        Equal(0, fixture.State.ResolutionStack.Count, "Stack remained after closure.");
        Equal("exhausted", fixture.State.GetCardInstance("underlying_target").ActivityState, "Underlying resolution did not resolve last.");
        Equal(
            "priority_passed,reaction_window_closed,resolution_entry_started,card_activity_changed,canonical_ability_resolved,resolution_entry_resolved,zone_move",
            string.Join(',', second.Events.Select(item => item.EventType)),
            "Pass closure lifecycle order is invalid.");
        Equal(1, fixture.Session.GetDebugCanonicalAbilityResolutions().Length, "Underlying canonical resolution was not recorded once.");
        True(fixture.State.ClosedReactionSubjectIds.Count == 1, "Closed subject identity was not retained.");
        EngineSession.ValidateState(fixture.State, fixture.CanonicalCards, fixture.CanonicalAbilities);
    }

    internal static void ReactionDeclarationResetsPassesAndResolvesLifo()
    {
        var fixture = CreateFixture();
        OpenWindow(fixture);
        Pass(fixture, "player_2");
        var firstReaction = React(fixture, "player_1", "p2_reaction_target");
        True(firstReaction.Accepted, "First reaction was rejected.");
        Equal(0, fixture.State.ReactionWindow!.ConsecutivePassCount, "Accepted reaction did not reset passes.");
        Equal("player_2", fixture.State.PriorityPlayerId, "Standard further response did not hand priority to the other player.");
        Equal(2, fixture.State.ResolutionStack.Count, "Reaction was not pushed above the underlying entry.");
        var publicDeclaration = Single(firstReaction.Events);
        Equal("reaction_declared", publicDeclaration.EventType, "Accepted reaction emitted the wrong declaration lifecycle event.");
        False(publicDeclaration.Payload.TryGetProperty("target_selections", out _), "Public reaction declaration leaked selected target payloads.");
        Equal(
            publicDeclaration.Payload.GetRawText(),
            fixture.Session.GetEvents("player_2").Single(item => item.EventId == publicDeclaration.EventId).Payload.GetRawText(),
            "Public reaction declaration projection changed for the opposing viewer.");

        var secondReaction = React(fixture, "player_2", "p1_reaction_target");
        True(secondReaction.Accepted, "Second reaction was rejected.");
        Equal("player_1", fixture.State.PriorityPlayerId, "Second reaction priority handoff is invalid.");
        Equal(3, fixture.State.ResolutionStack.Count, "Second reaction was not pushed.");
        var expectedOrder = fixture.State.ResolutionStack.AsEnumerable().Reverse()
            .Select(entry => entry.ResolutionId)
            .ToArray();

        Pass(fixture, "player_1");
        var closure = Pass(fixture, "player_2");
        var actualOrder = closure.Events
            .Where(item => item.EventType == "resolution_entry_resolved")
            .Select(item => item.Payload.GetProperty("resolution_id").GetString())
            .ToArray();
        Equal(string.Join(',', expectedOrder), string.Join(',', actualOrder), "Resolution stack did not unwind LIFO.");
        Equal("exhausted", fixture.State.GetCardInstance("p2_reaction_target").ActivityState, "Top reaction did not resolve.");
        Equal("exhausted", fixture.State.GetCardInstance("p1_reaction_target").ActivityState, "Lower reaction did not resolve.");
        Equal("exhausted", fixture.State.GetCardInstance("underlying_target").ActivityState, "Underlying resolution did not resolve after reactions.");
        Equal(3, fixture.Session.GetDebugCanonicalAbilityResolutions().Length, "Canonical resolution records do not match stack depth.");

        var declared = fixture.State.Events.Where(item => item.EventType == "reaction_declared").ToArray();
        Equal(2, declared.Length, "Reaction declaration lifecycle events are missing.");
        True(declared.All(item => item.Payload.GetProperty("reaction_subject_id").GetString()
            == fixture.State.ClosedReactionSubjectIds.Single()), "Lifecycle event subject correlation differs.");
        True(closure.Events.All(item => !item.Payload.TryGetProperty("developer_message", out _)), "Public response leaked developer diagnostics.");
    }

    internal static void SingleResponderAndTerminalPolicies()
    {
        var passFixture = CreateFixture(
            openingPolicy: ReactionPolicyIds.SingleResponderOnce,
            responderScope: ReactionResponderScope.NonInitiatorOnly,
            includeReactionSources: false);
        OpenWindow(passFixture);
        Equal(1, passFixture.State.ReactionWindow!.EligibleResponderPlayerIds.Count, "RC1 did not create exactly one responder.");
        var pass = Pass(passFixture, "player_2");
        True(pass.Accepted, "RC1 sole responder pass was rejected.");
        Equal(null, passFixture.State.ReactionWindow, "RC1 pass did not close immediately.");
        False(passFixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions.Any(action => action.ActionType == "pass_priority"), "RC1 invented a fake second pass.");

        var standardFixture = CreateFixture(
            openingPolicy: ReactionPolicyIds.SingleResponderOnce,
            responderScope: ReactionResponderScope.NonInitiatorOnly);
        OpenWindow(standardFixture);
        var reaction = React(standardFixture, "player_2", "p1_reaction_target");
        True(reaction.Accepted, "RC1 reaction with standard next policy was rejected.");
        Equal(ReactionPolicyIds.StandardAlternatingResponse, standardFixture.State.ReactionWindow!.CurrentResponsePolicyId, "RC1 did not transition through the typed next policy.");
        Equal(2, standardFixture.State.ReactionWindow.EligibleResponderPlayerIds.Count, "RC1 standard transition did not establish both responders.");
        Equal("player_1", standardFixture.State.PriorityPlayerId, "RC1 standard transition priority is invalid.");

        var terminalFixture = CreateFixture(
            openingPolicy: ReactionPolicyIds.SingleResponderOnce,
            responderScope: ReactionResponderScope.NonInitiatorOnly,
            nextPolicy: ReactionPolicyIds.NoFurtherResponse);
        OpenWindow(terminalFixture);
        var terminal = React(terminalFixture, "player_2", "p1_reaction_target");
        True(terminal.Accepted, "no_further_response reaction was rejected.");
        Equal(null, terminalFixture.State.ReactionWindow, "no_further_response left external input open.");
        Equal(0, terminalFixture.State.ResolutionStack.Count, "Terminal response did not fully unwind.");
        True(terminal.Events.Any(item => item.EventType == "reaction_window_closed"
                                        && item.Payload.GetProperty("closure_reason").GetString() == "no_further_response"), "Terminal closure reason is missing.");
    }

    internal static void ResolutionRevalidationInvalidatesWithoutRetarget()
    {
        var sourceFixture = CreateFixture();
        OpenWindow(sourceFixture);
        React(sourceFixture, "player_2", "p1_reaction_target");
        sourceFixture.State.GetCardInstance("p2_reaction_source").ZoneSequence += 1;
        Pass(sourceFixture, "player_1");
        var sourceClosure = Pass(sourceFixture, "player_2");
        True(sourceClosure.Events.Any(item => item.EventType == "resolution_entry_invalidated"
                                              && item.Payload.GetProperty("safe_reason_code").GetString() == "source_relevance_invalid"), "Source presence was not revalidated.");
        Equal("active", sourceFixture.State.GetCardInstance("p1_reaction_target").ActivityState, "Invalid source still mutated its declared target.");
        Equal("exhausted", sourceFixture.State.GetCardInstance("underlying_target").ActivityState, "Invalid reaction blocked valid underlying resolution.");

        var targetFixture = CreateFixture();
        OpenWindow(targetFixture);
        React(targetFixture, "player_2", "p1_reaction_target");
        targetFixture.State.GetCardInstance("p1_reaction_target").ZoneSequence += 1;
        Pass(targetFixture, "player_1");
        var targetClosure = Pass(targetFixture, "player_2");
        True(targetClosure.Events.Any(item => item.EventType == "resolution_entry_invalidated"
                                              && item.Payload.GetProperty("safe_reason_code").GetString() == "target_object_context_invalid"), "Target object context was not revalidated.");
        Equal("active", targetFixture.State.GetCardInstance("p1_reaction_target").ActivityState, "Invalid target was mutated or auto-retargeted.");
        Equal("active", targetFixture.State.GetCardInstance("p1_reaction_source").ActivityState, "Invalid reaction auto-retargeted another legal card.");
    }

    internal static void RejectedRequestsAreAtomic()
    {
        var outside = CreateFixture();
        AssertRejectedImmutable(
            outside,
            () => SubmitRaw(outside, "player_1", "pass_priority:missing", "pass_priority", ContractJsonValue.EmptyObject()),
            "ACTION_NOT_FOUND");
        AssertRejectedImmutable(
            outside,
            () => SubmitRaw(outside, "player_1", "react:missing", "react", ReactPayload("missing", ExhaustReactionTargetId, "p2_reaction_target")),
            "ACTION_NOT_FOUND");

        var fixture = CreateFixture();
        OpenWindow(fixture);
        AssertRejectedImmutable(
            fixture,
            () => SubmitListed(fixture, "player_1", "pass_priority", ContractJsonValue.EmptyObject()),
            "ACTION_DISABLED");
        AssertRejectedImmutable(
            fixture,
            () => SubmitListed(fixture, "player_1", "react", ReactPayload("not-current", ExhaustReactionTargetId, "p2_reaction_target")),
            "ACTION_DISABLED");

        var reactAction = ListedAction(fixture, "player_2", "react");
        var optionId = CurrentOptionId(reactAction);
        AssertRejectedImmutable(
            fixture,
            () => SubmitRaw(
                fixture,
                "player_2",
                reactAction.ActionId,
                "react",
                ReactPayload(optionId, ExhaustReactionTargetId, "p1_reaction_target"),
                expectedStateVersion: fixture.State.StateVersion - 1),
            "STALE_STATE_VERSION");
        AssertRejectedImmutable(
            fixture,
            () => SubmitRaw(fixture, "player_2", "react:wrong-action", "react", ReactPayload(optionId, ExhaustReactionTargetId, "p1_reaction_target")),
            "ACTION_NOT_FOUND");
        AssertRejectedImmutable(
            fixture,
            () => SubmitListed(fixture, "player_2", "react", ReactPayload("reaction-option:invalid", ExhaustReactionTargetId, "p1_reaction_target")),
            "REACTION_OPTION_INVALID");
        AssertRejectedImmutable(
            fixture,
            () => SubmitListed(fixture, "player_2", "react", ReactPayload(optionId, ExhaustReactionTargetId)),
            "REACTION_TARGET_INVALID");
        AssertRejectedImmutable(
            fixture,
            () => SubmitListed(fixture, "player_2", "react", ReactPayload(optionId, ExhaustReactionTargetId, "unknown_target")),
            "REACTION_TARGET_INVALID");
        AssertRejectedImmutable(
            fixture,
            () => SubmitListed(fixture, "player_2", "advance_phase", ContractJsonValue.EmptyObject()),
            "ACTION_DISABLED");
        AssertRejectedImmutable(
            fixture,
            () => SubmitListed(
                fixture,
                "player_2",
                "play_card",
                ContractJsonValue.From(new PlayCardActionPayload(
                    fixture.UnderlyingSourceId,
                    DomainRow: null,
                    LaneIndex: null,
                    ImmutableArray<string>.Empty,
                    [new CanonicalTargetSelectionPayload(UnderlyingTargetId, ["underlying_target"])]))),
            "ACTION_DISABLED");

        var sourceChanged = CreateFixture();
        OpenWindow(sourceChanged);
        var sourceAction = ListedAction(sourceChanged, "player_2", "react");
        var sourceOption = CurrentOptionId(sourceAction);
        sourceChanged.State.GetCardInstance("p2_reaction_source").ZoneSequence += 1;
        AssertRejectedImmutable(
            sourceChanged,
            () => SubmitRaw(sourceChanged, "player_2", sourceAction.ActionId, "react", ReactPayload(sourceOption, ExhaustReactionTargetId, "p1_reaction_target")),
            "REACTION_OPTION_INVALID");

        var targetChanged = CreateFixture();
        OpenWindow(targetChanged);
        var targetAction = ListedAction(targetChanged, "player_2", "react");
        var targetOption = CurrentOptionId(targetAction);
        targetChanged.State.GetCardInstance("p1_reaction_target").ZoneSequence += 1;
        AssertRejectedImmutable(
            targetChanged,
            () => SubmitRaw(targetChanged, "player_2", targetAction.ActionId, "react", ReactPayload(targetOption, ExhaustReactionTargetId, "p1_reaction_target")),
            "REACTION_OPTION_INVALID");

        var closed = CreateFixture(includeReactionSources: false);
        OpenWindow(closed);
        var oldPassAction = ListedAction(closed, "player_2", "pass_priority");
        Pass(closed, "player_2");
        Pass(closed, "player_1");
        AssertRejectedImmutable(
            closed,
            () => SubmitRaw(closed, "player_2", oldPassAction.ActionId, "pass_priority", ContractJsonValue.EmptyObject()),
            "ACTION_NOT_FOUND");

        var previousOption = CreateFixture();
        OpenWindow(previousOption);
        var oldReactAction = ListedAction(previousOption, "player_2", "react");
        var oldOptionId = CurrentOptionId(oldReactAction);
        Pass(previousOption, "player_2");
        Pass(previousOption, "player_1");
        AssertRejectedImmutable(
            previousOption,
            () => SubmitRaw(
                previousOption,
                "player_2",
                oldReactAction.ActionId,
                "react",
                ReactPayload(oldOptionId, ExhaustReactionTargetId, "p1_reaction_target")),
            "ACTION_NOT_FOUND");

        var pending = CreateFixture(
            package: CreateMoveReactionPackage(),
            reactionCardId: MoveReactionCardId,
            reactionAbilityId: MoveReactionAbilityId);
        OpenWindow(pending);
        React(pending, "player_2", "p1_reaction_target", MoveReactionTargetId);
        Pass(pending, "player_1");
        Pass(pending, "player_2");
        True(pending.State.PendingTriggerWindow is not null, "Pending-family bypass proof did not create its blocking window.");
        AssertRejectedImmutable(
            pending,
            () => SubmitListed(
                pending,
                "player_1",
                "play_card",
                ContractJsonValue.From(new PlayCardActionPayload(
                    pending.UnderlyingSourceId,
                    DomainRow: null,
                    LaneIndex: null,
                    ImmutableArray<string>.Empty,
                    [new CanonicalTargetSelectionPayload(UnderlyingTargetId, ["underlying_target"])]))),
            "ACTION_DISABLED");
    }

    internal static void UnsupportedPoliciesChoicesAndNestingAreControlled()
    {
        var duplicateBindingRejected = false;
        try
        {
            _ = new ReactionPolicyResolver(
                [],
                [
                    new ReactionOptionProfileBinding(ProfileId, ExhaustReactionAbilityId, ReactionPolicyIds.NoFurtherResponse),
                    new ReactionOptionProfileBinding(ProfileId, ExhaustReactionAbilityId, ReactionPolicyIds.StandardAlternatingResponse),
                ]);
        }
        catch (ArgumentException)
        {
            duplicateBindingRejected = true;
        }
        True(duplicateBindingRejected, "Duplicate Reaction option profile/ability binding was accepted.");

        var opening = CreateFixture(openingPolicy: "unknown_response_policy");
        AssertRejectedImmutable(opening, () => OpenWindow(opening), "REACTION_RESPONSE_POLICY_UNSUPPORTED");

        var next = CreateFixture(nextPolicy: "unknown_response_policy");
        OpenWindow(next);
        AssertRejectedImmutable(
            next,
            () => React(next, "player_2", "p1_reaction_target"),
            "REACTION_RESPONSE_POLICY_UNSUPPORTED");

        var choice = CreateFixture(requiresPostDeclarationChoice: true);
        OpenWindow(choice);
        AssertRejectedImmutable(
            choice,
            () => React(choice, "player_2", "p1_reaction_target"),
            "REACTION_RESOLUTION_UNSUPPORTED");

        var payment = CreateFixture(requiresPaymentSelection: true);
        OpenWindow(payment);
        AssertRejectedImmutable(
            payment,
            () => React(payment, "player_2", "p1_reaction_target"),
            "REACTION_RESOLUTION_UNSUPPORTED");

        var nested = CreateFixture(requiresNestedWindow: true);
        OpenWindow(nested);
        AssertRejectedImmutable(
            nested,
            () => React(nested, "player_2", "p1_reaction_target"),
            "REACTION_NESTED_WINDOW_DURING_RESOLUTION_UNSUPPORTED");

        var multiTrigger = CreateFixture(
            package: CreateMultiTriggerMoveReactionPackage(),
            reactionCardId: MoveReactionCardId,
            reactionAbilityId: MoveReactionAbilityId);
        OpenWindow(multiTrigger);
        React(multiTrigger, "player_2", "p1_reaction_target", MoveReactionTargetId);
        Pass(multiTrigger, "player_1");
        AssertRejectedImmutable(
            multiTrigger,
            () => Pass(multiTrigger, "player_2"),
            "REACTION_TRIGGER_BATCH_ORDERING_UNSUPPORTED");
    }

    internal static void DynamicLowerLethalTriggerBatchRejectsWholeClosureAtomically()
    {
        var fixture = CreateFixture(
            package: CreateDynamicLethalTriggerPackage(),
            reactionCardId: DamageReactionCardId,
            reactionAbilityId: DamageReactionAbilityId,
            underlyingTargetCardId: ExhaustReactionCardId);
        OpenWindow(fixture);
        Equal(0, fixture.State.GetCardInstance("underlying_target").DamageMarked,
            "Dynamic atomicity target did not start undamaged.");
        Pass(fixture, "player_2");
        var reaction = React(
            fixture,
            "player_1",
            "underlying_target",
            DamageReactionTargetId);
        True(reaction.Accepted, "Upper damage reaction was rejected.");
        Pass(fixture, "player_2");
        AssertRejectedImmutable(
            fixture,
            () => Pass(fixture, "player_1"),
            "REACTION_TRIGGER_BATCH_ORDERING_UNSUPPORTED");
        Equal(0, fixture.State.GetCardInstance("underlying_target").DamageMarked,
            "Rejected dynamic closure retained simulated upper damage.");
        Equal("dominion", fixture.State.GetCardInstance("underlying_target").Zone,
            "Rejected dynamic closure retained simulated lethal movement.");
    }

    internal static void TechnicalEventsAreNotTriggerSources()
    {
        foreach (var eventType in new[]
                 {
                     "reaction_window_opened",
                     "priority_passed",
                     "reaction_declared",
                     "reaction_window_closed",
                     "resolution_entry_started",
                     "resolution_entry_resolved",
                     "resolution_entry_invalidated",
                     "zone_move",
                 })
        {
            Equal(null, CanonicalTriggerResolver.MapEngineEventType(eventType), $"Technical event became a gameplay trigger source: {eventType}");
        }
    }

    internal static void QueuedTriggersActivateAtPostResolutionCheckpoint()
    {
        var package = CreateMoveReactionPackage();
        var fixture = CreateFixture(
            package: package,
            reactionCardId: MoveReactionCardId,
            reactionAbilityId: MoveReactionAbilityId);
        OpenWindow(fixture);
        React(fixture, "player_2", "p1_reaction_target", MoveReactionTargetId);
        React(fixture, "player_1", "p2_reaction_target", MoveReactionTargetId);
        var stackDepth = fixture.State.ResolutionStack.Count;
        Pass(fixture, "player_2");
        var closure = Pass(fixture, "player_1");

        Equal(3, stackDepth, "RC2 proof did not enter closure with two reactions and underlying entry.");
        Equal(0, fixture.State.ResolutionStack.Count, "RC2 checkpoint ran before full stack unwind completed.");
        var triggeredEvents = closure.Events.Where(item => item.EventType == "canonical_ability_triggered").ToArray();
        Equal(2, triggeredEvents.Length, "Resolution-time trigger discovery count is invalid.");
        var firstResolvedIndex = Array.FindIndex(closure.Events.ToArray(), item => item.EventType == "resolution_entry_resolved");
        var firstTriggeredIndex = Array.FindIndex(closure.Events.ToArray(), item => item.EventType == "canonical_ability_triggered");
        True(firstTriggeredIndex >= 0 && firstTriggeredIndex < firstResolvedIndex, "Trigger discovery was deferred past its resolution entry lifecycle.");
        var pending = NotNull(fixture.State.PendingTriggerWindow, "Post-resolution checkpoint did not activate the earliest batch.");
        Equal(1, pending.PendingTriggers.Count, "Earliest queued batch did not materialize as one pending trigger.");
        Equal(1, fixture.State.QueuedTriggerBatches.Count, "Later FIFO batch did not survive blocking pending input.");
        var firstSequence = pending.PendingTriggers[0].SourceEngineEventSequence;
        var laterSequence = fixture.State.QueuedTriggerBatches[0].OriginatingEventSequence;
        True(firstSequence < laterSequence, "Different-timing trigger batches were not activated by event-sequence FIFO.");

        var firstController = pending.ControllerPlayerId;
        var firstResolution = ResolvePending(fixture, firstController);
        True(firstResolution.Accepted, "Earliest queued trigger could not resolve.");
        var secondPending = NotNull(fixture.State.PendingTriggerWindow, "Queue did not resume after the first pending trigger cleared.");
        Equal(laterSequence, secondPending.PendingTriggers[0].SourceEngineEventSequence, "Queue resumed with the wrong FIFO batch.");
        Equal(0, fixture.State.QueuedTriggerBatches.Count, "Activated second batch remained duplicated in the queue.");
        True(ResolvePending(fixture, secondPending.ControllerPlayerId).Accepted, "Second queued trigger could not resolve.");
        Equal(null, fixture.State.PendingTriggerWindow, "RC2 queue did not reach stable state.");
        Equal(0, fixture.State.QueuedTriggerBatches.Count, "RC2 queue remained non-empty after all pending triggers.");
        EngineSession.ValidateState(fixture.State, fixture.CanonicalCards, fixture.CanonicalAbilities);
    }

    internal static void StateInvariantsRejectMalformedReactionFamilies()
    {
        var fixture = CreateFixture();
        OpenWindow(fixture);
        fixture.State.ReactionWindow!.CurrentResponsePolicyId = "unknown_policy";
        ThrowsState(
            () => EngineSession.ValidateState(fixture.State, fixture.CanonicalCards, fixture.CanonicalAbilities),
            "policy",
            "Unknown open response policy passed state validation.");

        var stack = CreateFixture();
        OpenWindow(stack);
        stack.State.ResolutionStack.Clear();
        ThrowsState(
            () => EngineSession.ValidateState(stack.State, stack.CanonicalCards, stack.CanonicalAbilities),
            "bottom",
            "Non-underlying bottom stack entry passed state validation.");
    }

    internal static void RepeatedProtocolIsDeterministic()
    {
        static string Run()
        {
            var fixture = CreateFixture();
            OpenWindow(fixture);
            React(fixture, "player_2", "p1_reaction_target");
            React(fixture, "player_1", "p2_reaction_target");
            Pass(fixture, "player_2");
            Pass(fixture, "player_1");
            return Fingerprint(fixture);
        }

        Equal(Run(), Run(), "Reaction/Priority protocol is not deterministic.");
    }

    private static Fixture CreateFixture(
        string openingPolicy = ReactionPolicyIds.StandardAlternatingResponse,
        ReactionResponderScope responderScope = ReactionResponderScope.BothPlayers,
        string nextPolicy = ReactionPolicyIds.StandardAlternatingResponse,
        bool includeReactionSources = true,
        bool requiresPostDeclarationChoice = false,
        bool requiresPaymentSelection = false,
        bool requiresNestedWindow = false,
        CanonicalCardDatabasePackage? package = null,
        string reactionCardId = ExhaustReactionCardId,
        string reactionAbilityId = ExhaustReactionAbilityId,
        string underlyingTargetCardId = "IGN-HAM-001",
        bool reactableOpening = true)
    {
        package ??= CanonicalAbilityCatalogTests.CreatePackage();
        var canonicalAbilities = CanonicalAbilityMaterializer.Materialize(package);
        var canonicalCards = CanonicalCardMaterializer.Materialize(package);
        var state = new MatchState
        {
            MatchId = "reaction-priority-test",
            Seed = 907,
            RuntimePackageId = "reaction-priority-runtime",
            StateVersion = 0,
            Phase = CanonicalPhaseIds.Manifestation,
            StartingPlayerId = "player_1",
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        var playerOne = new PlayerState { PlayerId = "player_1", DeckId = "deck_1" };
        var playerTwo = new PlayerState { PlayerId = "player_2", DeckId = "deck_2" };
        state.Players.Add(playerOne);
        state.Players.Add(playerTwo);
        var sourceId = AddHandCard(state, playerOne, UnderlyingCardId);
        AddHandCard(state, playerOne, "TEST-HIDDEN-HAND", "p1_hidden_hand_target");
        AddWellspringCard(state, playerOne, "TEST-WELL-1");
        AddWellspringCard(state, playerOne, "TEST-WELL-2");

        AddBoardCard(state, playerTwo, "underlying_target", underlyingTargetCardId, DomainRow.Zenith, 2);
        var reactionTargetCardId = string.Equals(
            reactionCardId,
            MoveReactionCardId,
            StringComparison.Ordinal)
            ? ExhaustReactionCardId
            : "IGN-HAM-001";
        AddBoardCard(state, playerOne, "p1_reaction_target", reactionTargetCardId, DomainRow.Horizon, 0);
        AddBoardCard(state, playerTwo, "p2_reaction_target", reactionTargetCardId, DomainRow.Horizon, 0);
        AddBoardCard(state, playerOne, "p1_pending_anchor", "IGN-HAM-001", DomainRow.Horizon, 1);
        AddBoardCard(state, playerTwo, "p2_pending_anchor", "IGN-HAM-001", DomainRow.Horizon, 1);
        if (includeReactionSources)
        {
            AddBoardCard(state, playerOne, "p1_reaction_source", reactionCardId, DomainRow.Zenith, 0);
            AddBoardCard(state, playerTwo, "p2_reaction_source", reactionCardId, DomainRow.Zenith, 0);
        }

        var runtimeCards = canonicalCards.Definitions.ToImmutableDictionary(
            definition => definition.CardId,
            definition => new RuntimeCardDefinition(
                definition.CardId,
                definition.Magnitude,
                definition.PrintedAuraCost,
                definition.Realm,
                definition.CardType switch
                {
                    "spell" => "incantation",
                    "sign" => "sigil",
                    _ => definition.CardType,
                }),
            StringComparer.Ordinal).ToBuilder();
        runtimeCards[UnderlyingCardId] = new RuntimeCardDefinition(
            UnderlyingCardId,
            Magnitude: 2,
            PrintedAuraCost: 2,
            Realm: "ignis",
            CardType: "incantation");
        runtimeCards["TEST-HIDDEN-HAND"] = new RuntimeCardDefinition("TEST-HIDDEN-HAND", 0, 0, "ignis", "entity");
        runtimeCards["TEST-WELL-1"] = new RuntimeCardDefinition("TEST-WELL-1", 0, 0, "ignis", "entity");
        runtimeCards["TEST-WELL-2"] = new RuntimeCardDefinition("TEST-WELL-2", 0, 0, "ignis", "entity");
        var runtime = new RuntimePackageCatalog(
            state.RuntimePackageId,
            runtimeCards.ToImmutable(),
            ImmutableDictionary<string, RuntimeDeckDefinition>.Empty.WithComparers(StringComparer.Ordinal),
            CreateLookups());
        var resolver = new ReactionPolicyResolver(
            reactableOpening
                ? [new ReactionOpeningProfileBinding(ProfileId, UnderlyingAbilityId, openingPolicy, responderScope)]
                : [],
            [new ReactionOptionProfileBinding(
                ProfileId,
                reactionAbilityId,
                nextPolicy,
                ReactionPolicyIds.SameZonePresence,
                requiresPostDeclarationChoice,
                requiresPaymentSelection,
                requiresNestedWindow)]);
        EngineSession.ValidateState(state, canonicalCards, canonicalAbilities);
        var session = new EngineSession(state, runtime, canonicalAbilities, canonicalCards, resolver);
        return new Fixture(session, state, canonicalCards, canonicalAbilities, sourceId);
    }

    private static CanonicalCardDatabasePackage CreateDynamicLethalTriggerPackage()
    {
        var package = CanonicalAbilityCatalogTests.CreatePackage();
        package = CanonicalAbilityCatalogTests.SetField(
            package,
            CanonicalAbilityTableIds.Cards,
            ExhaustReactionCardId,
            "hp",
            2);
        package = CanonicalAbilityCatalogTests.SetField(
            package,
            CanonicalAbilityTableIds.Effects,
            "effect_ign_ham_044_01_exhaust_target",
            "effect_action_type_id",
            "effect_deal_damage");
        package = CanonicalAbilityCatalogTests.AddRecord(
            package,
            CanonicalAbilityTableIds.EffectParameters,
            CanonicalAbilityCatalogTests.Record(
                ("effect_parameter_id", "reaction_underlying_damage_kind"),
                ("effect_id", "effect_ign_ham_044_01_exhaust_target"),
                ("contract_field_id", "parameter_field_deal_damage_damage_kind"),
                ("item_index", 1),
                ("value_registry_value_id", "damage_kind_direct")));
        package = CanonicalAbilityCatalogTests.AddRecord(
            package,
            CanonicalAbilityTableIds.EffectParameters,
            CanonicalAbilityCatalogTests.Record(
                ("effect_parameter_id", "reaction_underlying_damage_amount"),
                ("effect_id", "effect_ign_ham_044_01_exhaust_target"),
                ("contract_field_id", "parameter_field_deal_damage_amount"),
                ("item_index", 1),
                ("value_integer", 1)));
        package = CanonicalAbilityCatalogTests.SetField(
            package,
            CanonicalAbilityTableIds.Triggers,
            "trigger_ign_ham_005_01_entered_play",
            "event_type_id",
            "event_card_zone_changed");
        package = CanonicalAbilityCatalogTests.SetField(
            package,
            CanonicalAbilityTableIds.Triggers,
            "trigger_ign_ham_005_01_entered_play",
            "from_zone_id",
            "dominion");
        package = CanonicalAbilityCatalogTests.SetField(
            package,
            CanonicalAbilityTableIds.Triggers,
            "trigger_ign_ham_005_01_entered_play",
            "to_zone_id",
            "void");
        return CanonicalAbilityCatalogTests.AddRecord(
            package,
            CanonicalAbilityTableIds.Triggers,
            CanonicalAbilityCatalogTests.Record(
                ("trigger_id", "trigger_ign_ham_005_01_lethal_second"),
                ("ability_id", ExhaustReactionAbilityId),
                ("sequence", 2),
                ("event_type_id", "event_card_zone_changed"),
                ("event_stage_id", "after"),
                ("subject_reference_type_id", "ref_ability_source_card"),
                ("from_zone_id", "dominion"),
                ("to_zone_id", "void")));
    }

    private static CanonicalCardDatabasePackage CreateMoveReactionPackage()
    {
        var package = CanonicalAbilityCatalogTests.CreatePackage();
        var table = package.Registry.Tables["effect_action_types"];
        var record = CanonicalAbilityCatalogTests.Record(("effect_action_type_id", "effect_move_card_between_zones"));
        var id = record.GetRequiredString(table.PrimaryKey);
        var changedTable = table with
        {
            Records = table.Records.Add(record),
            RecordsById = table.RecordsById.Add(id, record),
        };
        package = package with
        {
            Registry = package.Registry with
            {
                Tables = package.Registry.Tables.SetItem("effect_action_types", changedTable),
            },
        };
        package = CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Targets, MoveReactionTargetId, "game_object_id", "card_instance");
        package = CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Targets, MoveReactionTargetId, "card_type_id", "entity");
        package = CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Targets, MoveReactionTargetId, "zone_id", "dominion");
        package = CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "effect_action_type_id", "effect_move_card_between_zones");
        package = CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "from_zone_id", "dominion");
        package = CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "to_zone_id", "hand");
        package = CanonicalAbilityCatalogTests.AddRecord(
            package,
            CanonicalAbilityTableIds.EffectParameters,
            CanonicalAbilityCatalogTests.Record(
                ("effect_parameter_id", "reaction_move_destination"),
                ("effect_id", "effect_aqu_mor_007_01_exhaust_target"),
                ("contract_field_id", "parameter_field_move_between_zones_destination_player"),
                ("item_index", 1),
                ("value_registry_value_id", "player_reference_subject_card_owner")));
        package = CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Triggers, "trigger_ign_ham_005_01_entered_play", "event_type_id", "event_card_zone_changed");
        package = CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Triggers, "trigger_ign_ham_005_01_entered_play", "from_zone_id", "dominion");
        package = CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Triggers, "trigger_ign_ham_005_01_entered_play", "to_zone_id", "hand");
        return package;
    }

    private static CanonicalCardDatabasePackage CreateMultiTriggerMoveReactionPackage() =>
        CanonicalAbilityCatalogTests.AddRecord(
            CreateMoveReactionPackage(),
            CanonicalAbilityTableIds.Triggers,
            CanonicalAbilityCatalogTests.Record(
                ("trigger_id", "trigger_ign_ham_005_01_zone_changed_second"),
                ("ability_id", ExhaustReactionAbilityId),
                ("sequence", 2),
                ("event_type_id", "event_card_zone_changed"),
                ("event_stage_id", "after"),
                ("subject_reference_type_id", "ref_ability_source_card"),
                ("from_zone_id", "dominion"),
                ("to_zone_id", "hand")));

    private static RuntimeLookupCatalog CreateLookups()
    {
        var realms = ImmutableDictionary.CreateRange(StringComparer.Ordinal, new Dictionary<string, string>
        {
            ["ignis"] = "ignis",
            ["aqua"] = "aqua",
            ["terra"] = "terra",
            ["lux"] = "lux",
            ["umbra"] = "umbra",
            ["ventus"] = "ventus",
            ["aether"] = "aether",
        });
        var cardTypes = ImmutableDictionary.CreateRange(StringComparer.Ordinal, new Dictionary<string, string>
        {
            ["entity"] = "entity",
            ["incantation"] = "incantation",
            ["ritual"] = "ritual",
            ["sigil"] = "sigil",
            ["plane"] = "plane",
        });
        return new RuntimeLookupCatalog(ImmutableDictionary.CreateRange(
            StringComparer.Ordinal,
            new Dictionary<string, RuntimeLookupGroup>
            {
                ["realm"] = new RuntimeLookupGroup("realm", realms),
                ["card_type"] = new RuntimeLookupGroup("card_type", cardTypes),
            }));
    }

    private static ActionResponse OpenWindow(Fixture fixture) => SubmitUnderlyingPlay(fixture);

    private static ActionResponse SubmitUnderlyingPlay(Fixture fixture)
    {
        var action = ListedAction(fixture, "player_1", "play_card");
        var option = action.PayloadSchema.GetProperty("play_options").EnumerateArray()
            .Single(item => string.Equals(
                item.GetProperty("card_instance_id").GetString(),
                fixture.UnderlyingSourceId,
                StringComparison.Ordinal));
        var payableAuraCost = option.GetProperty("payable_aura_cost").GetInt32();
        var auraSourceIds = option.GetProperty("eligible_aura_source_card_instance_ids")
            .EnumerateArray()
            .Select(item => item.GetString()!)
            .Take(payableAuraCost)
            .ToImmutableArray();
        return SubmitRaw(
            fixture,
            "player_1",
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new PlayCardActionPayload(
                fixture.UnderlyingSourceId,
                DomainRow: null,
                LaneIndex: null,
                auraSourceIds,
                [new CanonicalTargetSelectionPayload(UnderlyingTargetId, ["underlying_target"])])));
    }

    private static ActionResponse Pass(Fixture fixture, string playerId) =>
        SubmitListed(fixture, playerId, "pass_priority", ContractJsonValue.EmptyObject());

    private static ActionResponse React(
        Fixture fixture,
        string playerId,
        string targetCardInstanceId,
        string targetId = ExhaustReactionTargetId)
    {
        var action = ListedAction(fixture, playerId, "react");
        return SubmitRaw(
            fixture,
            playerId,
            action.ActionId,
            action.ActionType,
            ReactPayload(CurrentOptionId(action), targetId, targetCardInstanceId));
    }

    private static ActionResponse ResolvePending(Fixture fixture, string playerId)
    {
        var action = ListedAction(fixture, playerId, "resolve_triggered_ability");
        var option = Single(action.PayloadSchema.GetProperty("pending_trigger_options").EnumerateArray());
        var targetContract = Single(option.GetProperty("target_contracts").EnumerateArray());
        var candidate = targetContract.GetProperty("candidate_card_instance_ids").EnumerateArray().First().GetString()!;
        return SubmitRaw(
            fixture,
            playerId,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new ResolveTriggeredAbilityActionPayload(
                option.GetProperty("pending_trigger_id").GetString()!,
                [new CanonicalTargetSelectionPayload(targetContract.GetProperty("target_id").GetString()!, [candidate])])));
    }

    private static JsonElement ReactPayload(string optionId, string targetId, params string[] cardInstanceIds) =>
        ContractJsonValue.From(new ReactActionPayload(
            optionId,
            [new CanonicalTargetSelectionPayload(targetId, cardInstanceIds.ToImmutableArray())]));

    private static string CurrentOptionId(LegalAction action) =>
        Single(action.PayloadSchema.GetProperty("reaction_options").EnumerateArray())
            .GetProperty("reaction_option_id").GetString()!;

    private static LegalAction ListedAction(Fixture fixture, string playerId, string actionType) =>
        fixture.Session.ListLegalActions(playerId, includeDisabled: true).Actions
            .Single(action => action.ActionType == actionType);

    private static ActionResponse SubmitListed(
        Fixture fixture,
        string playerId,
        string actionType,
        JsonElement payload)
    {
        var action = ListedAction(fixture, playerId, actionType);
        return SubmitRaw(fixture, playerId, action.ActionId, action.ActionType, payload);
    }

    private static ActionResponse SubmitRaw(
        Fixture fixture,
        string playerId,
        string actionId,
        string actionType,
        JsonElement payload,
        int? expectedStateVersion = null) => fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            $"reaction_request_{fixture.NextRequestSequence++:000}",
            fixture.State.MatchId,
            playerId,
            expectedStateVersion ?? fixture.State.StateVersion,
            actionId,
            actionType,
            payload));

    private static void AssertRejectedImmutable(
        Fixture fixture,
        Func<ActionResponse> submit,
        string diagnosticCode)
    {
        var before = Fingerprint(fixture);
        var response = submit();
        False(response.Accepted, $"Negative Reaction fixture {diagnosticCode} was accepted.");
        Equal(diagnosticCode, Single(response.Diagnostics).Code, "Unexpected Reaction rejection diagnostic.");
        Equal(0, response.Events.Length, "Rejected Reaction action emitted events.");
        Equal(response.StateVersionBefore, response.StateVersionAfter, "Rejected Reaction action changed state version.");
        Equal(before, Fingerprint(fixture), $"{diagnosticCode} rejection mutated authoritative state.");
    }

    private static string Fingerprint(Fixture fixture) => JsonSerializer.Serialize(new
    {
        Snapshot = fixture.Session.GetDebugSnapshot(),
        Reaction = fixture.State.ReactionWindow,
        Stack = fixture.State.ResolutionStack,
        Queue = fixture.State.QueuedTriggerBatches,
        Closed = fixture.State.ClosedReactionSubjectIds.OrderBy(item => item, StringComparer.Ordinal),
        fixture.State.NextReactionWindowSequence,
        fixture.State.NextReactionSubjectSequence,
        fixture.State.NextResolutionSequence,
        Discoveries = fixture.Session.GetDebugCanonicalTriggerDiscoveries(),
        Resolutions = fixture.Session.GetDebugCanonicalAbilityResolutions(),
    });

    private static string AddHandCard(
        MatchState state,
        PlayerState player,
        string cardId,
        string instanceId = "underlying_source")
    {
        var id = instanceId;
        state.CardInstances.Add(id, new CardInstanceState
        {
            CardInstanceId = id,
            CardId = cardId,
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "hand",
            ZoneIndex = player.HandCardInstanceIds.Count,
            Visibility = "owner_only",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "hand",
        });
        player.HandCardInstanceIds.Add(id);
        return id;
    }

    private static void AddWellspringCard(MatchState state, PlayerState player, string cardId)
    {
        var id = $"ci_{cardId.ToLowerInvariant()}";
        state.CardInstances.Add(id, new CardInstanceState
        {
            CardInstanceId = id,
            CardId = cardId,
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "wellspring",
            ZoneIndex = player.WellspringCardInstanceIds.Count,
            Visibility = "owner_only",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "wellspring",
            ActivityState = "active",
        });
        player.WellspringCardInstanceIds.Add(id);
    }

    private static void AddBoardCard(
        MatchState state,
        PlayerState player,
        string instanceId,
        string cardId,
        DomainRow row,
        int laneIndex)
    {
        True(player.Domain.TryOccupy(row, laneIndex, instanceId), "Reaction fixture Domain placement failed.");
        state.CardInstances.Add(instanceId, new CardInstanceState
        {
            CardInstanceId = instanceId,
            CardId = cardId,
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "dominion",
            ZoneIndex = -1,
            Visibility = "public",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "dominion",
            ActivityState = "active",
            DomainRow = row,
            DomainLaneIndex = laneIndex,
            EnteredDomainTurnNumber = 1,
        });
    }

    private static void ThrowsState(Action action, string expectedMessagePart, string message)
    {
        try
        {
            action();
        }
        catch (EngineStateException exception)
        {
            True(exception.Message.Contains(expectedMessagePart, StringComparison.OrdinalIgnoreCase), message);
            return;
        }

        throw new InvalidOperationException(message);
    }

    private static T NotNull<T>(T? value, string message) where T : class =>
        value ?? throw new InvalidOperationException(message);

    private static T Single<T>(IEnumerable<T> values)
    {
        var materialized = values.ToArray();
        Equal(1, materialized.Length, "Expected exactly one item.");
        return materialized[0];
    }

    private static void True(bool condition, string message)
    {
        if (!condition)
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void False(bool condition, string message) => True(!condition, message);

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected={expected}; Actual={actual}");
        }
    }

    private sealed class Fixture(
        EngineSession session,
        MatchState state,
        CanonicalCardCatalog canonicalCards,
        CanonicalAbilityCatalog canonicalAbilities,
        string underlyingSourceId)
    {
        internal EngineSession Session { get; } = session;
        internal MatchState State { get; } = state;
        internal CanonicalCardCatalog CanonicalCards { get; } = canonicalCards;
        internal CanonicalAbilityCatalog CanonicalAbilities { get; } = canonicalAbilities;
        internal string UnderlyingSourceId { get; } = underlyingSourceId;
        internal int NextRequestSequence { get; set; } = 1;
    }
}
