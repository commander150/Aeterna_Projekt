using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

internal static class CanonicalAbilityExecutionTests
{
    private const string AbilityId = "ability_ign_ham_005_01";
    private const string TriggerId = "trigger_ign_ham_005_01_entered_play";
    private const string TargetId = "target_ign_ham_005_01_enemy_horizont_entity";
    private const string SourceCardId = "IGN-HAM-005";

    internal static void PendingCreationProjectionAndCandidateOrdering()
    {
        var fixture = CreateFixture(
            Board("ci_target_lane_4_a", "IGN-HAM-001", "player_2", DomainRow.Horizon, 4),
            Board("ci_target_lane_1_z", "IGN-HAM-001", "player_2", DomainRow.Horizon, 1));

        var play = PlaySource(fixture);

        True(play.Accepted, "Canonical source play was rejected.");
        Equal(1, fixture.State.StateVersion, "Play plus trigger creation must increment state version exactly once.");
        Equal(
            "zone_move,card_entered_play,canonical_ability_triggered",
            string.Join(',', play.Events.Select(item => item.EventType)),
            "Pending-trigger creation event order is invalid.");
        var window = NotNull(fixture.State.PendingTriggerWindow, "Supported trigger did not create a pending window.");
        Equal(1, window.PendingTriggers.Count, "Unexpected pending trigger count.");
        var pending = window.PendingTriggers[0];
        Equal(AbilityId, pending.AbilityId, "Pending ability identity is invalid.");
        Equal(TriggerId, pending.TriggerId, "Pending trigger identity is invalid.");
        Equal(fixture.SourceCardInstanceId, pending.SourceCardInstanceId, "Pending source identity is invalid.");
        Equal(2, pending.SourceEngineEventSequence, "Pending source event sequence is invalid.");

        var snapshot = fixture.Session.GetPlayerSnapshot("player_1");
        var summary = snapshot.PendingDecisionSummary;
        True(summary.GetProperty("has_pending").GetBoolean(), "Pending state is absent from player projection.");
        Equal("triggered_ability", summary.GetProperty("pending_type").GetString(), "Pending projection type is invalid.");
        Equal("player_1", summary.GetProperty("controller_player_id").GetString(), "Pending projection controller is invalid.");
        Equal(SourceCardId, summary.GetProperty("pending_triggers")[0].GetProperty("source_card_id").GetString(), "Pending public source identity is invalid.");

        var actions = fixture.Session.ListLegalActions("player_1", includeDisabled: false).Actions;
        var resolve = Single(actions);
        Equal("resolve_triggered_ability", resolve.ActionType, "Controller did not receive the resolution action.");
        var option = Single(resolve.PayloadSchema.GetProperty("pending_trigger_options").EnumerateArray());
        var contract = Single(option.GetProperty("target_contracts").EnumerateArray());
        Equal(TargetId, contract.GetProperty("target_id").GetString(), "Legal target contract identity is invalid.");
        Equal(1, contract.GetProperty("minimum_targets").GetInt32(), "Legal target minimum is invalid.");
        Equal(1, contract.GetProperty("maximum_targets").GetInt32(), "Legal target maximum is invalid.");
        Equal(
            "ci_target_lane_1_z,ci_target_lane_4_a",
            string.Join(',', contract.GetProperty("candidate_card_instance_ids").EnumerateArray().Select(item => item.GetString())),
            "Candidate ordering is not lane-first and deterministic.");
    }

    internal static void SuccessfulResolutionIsAtomicAndOrdered()
    {
        var fixture = CreateFixture(
            Board("ci_target_selected", "IGN-HAM-001", "player_2", DomainRow.Horizon, 2),
            Board("ci_target_other", "IGN-HAM-001", "player_2", DomainRow.Horizon, 5));
        True(PlaySource(fixture).Accepted, "Canonical source play was rejected.");
        var selected = fixture.State.GetCardInstance("ci_target_selected");
        var before = CardIdentity(selected);
        var pendingId = Single(fixture.State.PendingTriggerWindow!.PendingTriggers).PendingTriggerId;

        var response = Resolve(fixture, "player_1", pendingId, TargetId, ["ci_target_selected"]);

        True(response.Accepted, "Valid canonical trigger resolution was rejected.");
        Equal(2, fixture.State.StateVersion, "Resolution must increment state version exactly once.");
        Equal(
            "card_activity_changed,canonical_ability_resolved",
            string.Join(',', response.Events.Select(item => item.EventType)),
            "Canonical resolution event order is invalid.");
        Equal("exhausted", selected.ActivityState, "effect_exhaust_card did not exhaust the selected target.");
        Equal(before, CardIdentity(selected), "effect_exhaust_card changed target identity or placement.");
        Equal("active", fixture.State.GetCardInstance("ci_target_other").ActivityState, "Unselected legal target was mutated.");
        Equal("active", fixture.State.GetCardInstance(fixture.SourceCardInstanceId).ActivityState, "Source card was mutated.");
        Equal(null, fixture.State.PendingTriggerWindow, "Completed trigger window remained pending.");
        Equal(2, response.Events[0].StateVersion, "Activity event has the wrong state version.");
        Equal(2, response.Events[1].StateVersion, "Resolution event has the wrong state version.");
        Equal("ci_target_selected", response.Events[0].Payload.GetProperty("card_instance_id").GetString(), "Activity event target is invalid.");
        Equal(CanonicalEffectExecutor.AppliedOutcome, response.Events[1].Payload.GetProperty("resolution_outcome").GetString(), "Resolution outcome is invalid.");
        True(
            fixture.Session.ListLegalActions("player_1", includeDisabled: false).Actions.Any(item => item.ActionType == "end_turn"),
            "Normal action space did not return after the pending window closed.");
    }

    internal static void CanonicalWardDoesNotRestrictNonAttackTargeting()
    {
        var wardPackage = CanonicalAbilityCatalogTests.SetField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.CardKeywords,
            "cardkw_ign_ham_001_speed",
            "keyword_id",
            "ward");
        var wardCatalog = CanonicalAbilityMaterializer.Materialize(wardPackage);
        Equal("ward", Single(wardCatalog.KeywordsByCardId["IGN-HAM-001"]).KeywordId, "Ward fixture is not canonical keyword data.");
        var fixture = CreateFixture(
            wardCatalog,
            Board("ci_ward_target", "IGN-HAM-001", "player_2", DomainRow.Horizon, 3));
        True(PlaySource(fixture).Accepted, "Canonical source play was rejected.");
        var pendingId = Single(fixture.State.PendingTriggerWindow!.PendingTriggers).PendingTriggerId;

        var response = Resolve(fixture, "player_1", pendingId, TargetId, ["ci_ward_target"]);

        True(response.Accepted, "Ward incorrectly blocked a non-attack canonical ability target.");
        Equal("exhausted", fixture.State.GetCardInstance("ci_ward_target").ActivityState, "Ward target was not exhausted.");
    }

    internal static void NoLegalTargetAutoResolvesWithoutDeadlock()
    {
        var fixture = CreateFixture();

        var response = PlaySource(fixture);

        True(response.Accepted, "No-target source play was rejected.");
        Equal(1, fixture.State.StateVersion, "No-target lifecycle added an extra transition.");
        Equal(null, fixture.State.PendingTriggerWindow, "No-target lifecycle created a deadlocked pending window.");
        Equal(
            "zone_move,card_entered_play,canonical_ability_triggered,canonical_ability_resolved",
            string.Join(',', response.Events.Select(item => item.EventType)),
            "No-target lifecycle event order is invalid.");
        False(response.Events.Any(item => item.EventType == "card_activity_changed"), "No-target lifecycle emitted an activity mutation.");
        Equal(
            CanonicalEffectExecutor.NoLegalTargetOutcome,
            response.Events[^1].Payload.GetProperty("resolution_outcome").GetString(),
            "No-target lifecycle outcome is invalid.");
        True(
            fixture.Session.ListLegalActions("player_1", includeDisabled: false).Actions.Any(item => item.ActionType == "end_turn"),
            "No-target lifecycle did not restore normal gameplay.");
    }

    internal static void PendingGateBlocksNormalActionsForBothPlayers()
    {
        var fixture = CreateFixture(Board("ci_gate_target", "IGN-HAM-001", "player_2", DomainRow.Horizon, 0));
        True(PlaySource(fixture).Accepted, "Canonical source play was rejected.");
        Equal("resolve_triggered_ability", Single(fixture.Session.ListLegalActions("player_1", false).Actions).ActionType, "Controller action gate is invalid.");
        Equal(0, fixture.Session.ListLegalActions("player_2", false).Actions.Length, "Opponent received an action during the temporary pending gate.");

        foreach (var playerId in new[] { "player_1", "player_2" })
        {
            var actionSpace = fixture.Session.ListLegalActions(playerId, includeDisabled: true);
            foreach (var actionType in new[] { "end_turn", "normal_inflow", "play_card", "draw_card" })
            {
                var action = actionSpace.Actions.Single(item => item.ActionType == actionType);
                Equal("pending_trigger_resolution_required", action.DisabledReason, $"{actionType} has the wrong pending gate reason.");
                var payload = actionType switch
                {
                    "normal_inflow" => ContractJsonValue.From(new NormalInflowActionPayload("ci_missing")),
                    "play_card" => ContractJsonValue.From(new PlayCardActionPayload(
                        fixture.SourceCardInstanceId,
                        "horizon",
                        0,
                        ImmutableArray<string>.Empty)),
                    _ => ContractJsonValue.EmptyObject(),
                };
                var before = Fingerprint(fixture);
                var response = Submit(fixture, playerId, action, payload);
                AssertRejected(response, "ACTION_DISABLED");
                Equal(before, Fingerprint(fixture), $"Pending gate rejection for {playerId}/{actionType} mutated state.");
            }
        }
    }

    internal static void WrongPlayerUnknownPendingAndStaleRequestsAreImmutable()
    {
        foreach (var testCase in new[] { "wrong_player", "unknown_pending", "stale" })
        {
            var fixture = CreateFixture(Board("ci_identity_target", "IGN-HAM-001", "player_2", DomainRow.Horizon, 0));
            True(PlaySource(fixture).Accepted, "Canonical source play was rejected.");
            var pendingId = Single(fixture.State.PendingTriggerWindow!.PendingTriggers).PendingTriggerId;
            var before = Fingerprint(fixture);
            var response = testCase switch
            {
                "wrong_player" => Resolve(fixture, "player_2", pendingId, TargetId, ["ci_identity_target"]),
                "unknown_pending" => Resolve(fixture, "player_1", "pending_trigger_unknown", TargetId, ["ci_identity_target"]),
                _ => Resolve(fixture, "player_1", pendingId, TargetId, ["ci_identity_target"], expectedStateVersion: 0),
            };
            var expectedCode = testCase switch
            {
                "wrong_player" => "RESOLVE_TRIGGER_PLAYER_INVALID",
                "unknown_pending" => "RESOLVE_TRIGGER_PENDING_UNKNOWN",
                _ => "STALE_STATE_VERSION",
            };
            AssertRejected(response, expectedCode);
            Equal(before, Fingerprint(fixture), $"{testCase} rejection mutated authoritative state.");
        }
    }

    internal static void TargetShapeAndCardinalityRejectionsAreImmutable()
    {
        var cases = new (string Name, string Target, ImmutableArray<string> Cards, string Code)[]
        {
            ("wrong_target", "target_unknown", ["ci_shape_target"], "RESOLVE_TRIGGER_TARGET_ID_INVALID"),
            ("other_ability_target", "target_aqu_art_044_01_enemy_horizont_entities", ["ci_shape_target"], "RESOLVE_TRIGGER_TARGET_ID_INVALID"),
            ("zero_targets", TargetId, [], "RESOLVE_TRIGGER_TARGET_COUNT_INVALID"),
            ("two_targets", TargetId, ["ci_shape_target", "ci_shape_other"], "RESOLVE_TRIGGER_TARGET_COUNT_INVALID"),
            ("duplicate_target", TargetId, ["ci_shape_target", "ci_shape_target"], "RESOLVE_TRIGGER_TARGET_DUPLICATE"),
        };
        foreach (var testCase in cases)
        {
            var fixture = CreateFixture(
                Board("ci_shape_target", "IGN-HAM-001", "player_2", DomainRow.Horizon, 0),
                Board("ci_shape_other", "IGN-HAM-001", "player_2", DomainRow.Horizon, 1));
            True(PlaySource(fixture).Accepted, "Canonical source play was rejected.");
            var pendingId = Single(fixture.State.PendingTriggerWindow!.PendingTriggers).PendingTriggerId;
            var before = Fingerprint(fixture);

            var response = Resolve(fixture, "player_1", pendingId, testCase.Target, testCase.Cards);

            AssertRejected(response, testCase.Code);
            Equal(before, Fingerprint(fixture), $"{testCase.Name} rejection mutated authoritative state.");
        }
    }

    internal static void IllegalBoardTargetsAndUnknownInstanceAreImmutable()
    {
        var fixture = CreateFixture(
            Board("ci_legal_anchor", "IGN-HAM-001", "player_2", DomainRow.Horizon, 0),
            Board("ci_own_entity", "IGN-HAM-001", "player_1", DomainRow.Horizon, 1),
            Board("ci_enemy_zenith", "IGN-HAM-001", "player_2", DomainRow.Zenith, 1),
            Board("ci_enemy_exhausted", "IGN-HAM-001", "player_2", DomainRow.Horizon, 2, "exhausted"),
            Board("ci_enemy_non_entity", "AQU-ART-044", "player_2", DomainRow.Horizon, 3, "active", "incantation"));
        True(PlaySource(fixture, laneIndex: 2).Accepted, "Canonical source play was rejected.");
        var pendingId = Single(fixture.State.PendingTriggerWindow!.PendingTriggers).PendingTriggerId;
        foreach (var cardInstanceId in new[]
                 {
                     "ci_own_entity",
                     "ci_enemy_zenith",
                     "ci_enemy_exhausted",
                     "ci_enemy_non_entity",
                     "ci_unknown",
                 })
        {
            var before = Fingerprint(fixture);
            var response = Resolve(fixture, "player_1", pendingId, TargetId, [cardInstanceId]);
            AssertRejected(
                response,
                cardInstanceId == "ci_unknown"
                    ? "RESOLVE_TRIGGER_TARGET_UNKNOWN"
                    : "RESOLVE_TRIGGER_TARGET_ILLEGAL");
            Equal(before, Fingerprint(fixture), $"Illegal target {cardInstanceId} mutated authoritative state.");
        }
    }

    internal static void TargetInvalidatedBeforeResolutionIsRejectedAtomically()
    {
        var fixture = CreateFixture(Board("ci_late_invalid", "IGN-HAM-001", "player_2", DomainRow.Horizon, 0));
        True(PlaySource(fixture).Accepted, "Canonical source play was rejected.");
        var pendingId = Single(fixture.State.PendingTriggerWindow!.PendingTriggers).PendingTriggerId;
        fixture.State.GetCardInstance("ci_late_invalid").ActivityState = "exhausted";
        EngineSession.ValidateState(fixture.State);
        var before = Fingerprint(fixture);

        var response = Resolve(fixture, "player_1", pendingId, TargetId, ["ci_late_invalid"]);

        AssertRejected(response, "RESOLVE_TRIGGER_TARGET_ILLEGAL");
        Equal(before, Fingerprint(fixture), "Late target invalidation rejection mutated authoritative state.");
    }

    internal static void UnsupportedEffectActionIsControlledAndAtomic()
    {
        var unsupportedPackage = CanonicalAbilityCatalogTests.SetField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.Effects,
            "effect_ign_ham_005_01_exhaust_target",
            "effect_action_type_id",
            "effect_apply_modifier");
        var fixture = CreateFixture(
            CanonicalAbilityMaterializer.Materialize(unsupportedPackage),
            Board("ci_unsupported_target", "IGN-HAM-001", "player_2", DomainRow.Horizon, 0));
        var play = PlaySource(fixture);
        True(play.Accepted, "Unsupported graph source play was rejected.");
        Equal(null, fixture.State.PendingTriggerWindow, "Unsupported effect was promoted as executable pending state.");
        var sourceEvent = fixture.State.Events.Single(item => item.EventType == "card_entered_play");
        fixture.State.PendingTriggerWindow = new PendingTriggerWindowState
        {
            PendingWindowId = "pending_window_unsupported_fixture",
            ControllerPlayerId = "player_1",
        };
        fixture.State.PendingTriggerWindow.PendingTriggers.Add(new PendingTriggeredAbilityState(
            "pending_trigger_unsupported_fixture",
            AbilityId,
            TriggerId,
            fixture.SourceCardInstanceId,
            SourceCardId,
            "player_1",
            sourceEvent.EventId,
            sourceEvent.EventSequence,
            "event_card_entered_play"));
        EngineSession.ValidateState(fixture.State);
        var before = Fingerprint(fixture);

        var response = Resolve(
            fixture,
            "player_1",
            "pending_trigger_unsupported_fixture",
            TargetId,
            ["ci_unsupported_target"]);

        AssertRejected(response, "CANONICAL_EFFECT_ACTION_UNSUPPORTED");
        Equal(before, Fingerprint(fixture), "Unsupported effect action mutated authoritative state.");
    }

    internal static void MultiplePendingTriggersAllowControllerChoice()
    {
        var fixture = CreateFixture(
            Board("ci_multi_first_target", "IGN-HAM-001", "player_2", DomainRow.Horizon, 0),
            Board("ci_multi_second_target", "IGN-HAM-001", "player_2", DomainRow.Horizon, 1));
        True(PlaySource(fixture).Accepted, "Canonical source play was rejected.");
        var window = fixture.State.PendingTriggerWindow!;
        var first = Single(window.PendingTriggers);
        var second = first with { PendingTriggerId = "pending_trigger_controller_selected_second" };
        window.PendingTriggers.Add(second);
        EngineSession.ValidateState(fixture.State);
        var resolveAction = Single(fixture.Session.ListLegalActions("player_1", false).Actions);
        Equal(2, resolveAction.PayloadSchema.GetProperty("pending_trigger_options").GetArrayLength(), "Multiple pending choices were not projected.");

        var response = Resolve(
            fixture,
            "player_1",
            second.PendingTriggerId,
            TargetId,
            ["ci_multi_second_target"]);

        True(response.Accepted, "Controller could not choose the next own pending trigger.");
        Equal(1, fixture.State.PendingTriggerWindow!.PendingTriggers.Count, "Resolving one trigger removed the entire window.");
        Equal(first.PendingTriggerId, fixture.State.PendingTriggerWindow.PendingTriggers[0].PendingTriggerId, "Player-selected ordering was replaced by an ID sort.");
        Equal("exhausted", fixture.State.GetCardInstance("ci_multi_second_target").ActivityState, "Selected pending trigger effect was not applied.");
        Equal("active", fixture.State.GetCardInstance("ci_multi_first_target").ActivityState, "Unselected pending trigger target was mutated.");
    }

    internal static void MalformedResolutionPayloadIsImmutable()
    {
        var fixture = CreateFixture(Board("ci_malformed_target", "IGN-HAM-001", "player_2", DomainRow.Horizon, 0));
        True(PlaySource(fixture).Accepted, "Canonical source play was rejected.");
        var action = Single(fixture.Session.ListLegalActions("player_1", false).Actions);
        var before = Fingerprint(fixture);
        var malformed = ContractJsonValue.From(new Dictionary<string, object?>
        {
            ["pending_trigger_id"] = fixture.State.PendingTriggerWindow!.PendingTriggers[0].PendingTriggerId,
            ["target_selections"] = new[]
            {
                new Dictionary<string, object?>
                {
                    ["target_id"] = TargetId,
                    ["card_instance_ids"] = new[] { "ci_malformed_target" },
                    ["unexpected"] = true,
                },
            },
        });

        var response = Submit(fixture, "player_1", action, malformed);

        AssertRejected(response, "ACTION_PAYLOAD_INVALID");
        Equal(before, Fingerprint(fixture), "Malformed resolution payload mutated authoritative state.");
    }

    internal static void RepeatedExecutionIsDeterministic()
    {
        string Run()
        {
            var fixture = CreateFixture(
                Board("ci_deterministic_a", "IGN-HAM-001", "player_2", DomainRow.Horizon, 4),
                Board("ci_deterministic_b", "IGN-HAM-001", "player_2", DomainRow.Horizon, 1));
            var play = PlaySource(fixture);
            True(play.Accepted, "Determinism play was rejected.");
            var pendingId = Single(fixture.State.PendingTriggerWindow!.PendingTriggers).PendingTriggerId;
            var resolve = Resolve(fixture, "player_1", pendingId, TargetId, ["ci_deterministic_b"]);
            True(resolve.Accepted, "Determinism resolution was rejected.");
            return JsonSerializer.Serialize(new
            {
                Play = play,
                Resolve = resolve,
                Snapshot = fixture.Session.GetDebugSnapshot(),
                Discoveries = fixture.Session.GetDebugCanonicalTriggerDiscoveries(),
                Resolutions = fixture.Session.GetDebugCanonicalAbilityResolutions(),
            });
        }

        Equal(Run(), Run(), "Repeated canonical ability execution is not deterministic.");
    }

    private static ExecutionFixture CreateFixture(params BoardCard[] boardCards) =>
        CreateFixture(Materialize(), boardCards);

    private static ExecutionFixture CreateFixture(
        CanonicalAbilityCatalog canonicalCatalog,
        params BoardCard[] boardCards)
    {
        var state = new MatchState
        {
            MatchId = "canonical-ability-execution-test",
            Seed = 53,
            RuntimePackageId = "canonical-ability-execution-runtime",
            StateVersion = 0,
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        var playerOne = new PlayerState { PlayerId = "player_1", DeckId = "deck_1" };
        var playerTwo = new PlayerState { PlayerId = "player_2", DeckId = "deck_2" };
        state.Players.Add(playerOne);
        state.Players.Add(playerTwo);
        const string sourceInstanceId = "ci_ign_ham_005_source";
        state.CardInstances.Add(sourceInstanceId, new CardInstanceState
        {
            CardInstanceId = sourceInstanceId,
            CardId = SourceCardId,
            OwnerPlayerId = "player_1",
            ControllerPlayerId = "player_1",
            Zone = "hand",
            ZoneIndex = 0,
            Visibility = "owner_only",
            CreatedSequence = 1,
            ZoneSequence = 1,
            InitialZone = "hand",
        });
        playerOne.HandCardInstanceIds.Add(sourceInstanceId);

        var runtimeCards = ImmutableDictionary.CreateBuilder<string, RuntimeCardDefinition>(StringComparer.Ordinal);
        runtimeCards.Add(SourceCardId, new RuntimeCardDefinition(SourceCardId, 0, 0, "ignis", "entity"));
        var createdSequence = 2;
        foreach (var spec in boardCards)
        {
            var player = state.GetPlayer(spec.PlayerId);
            True(player.Domain.TryOccupy(spec.Row, spec.LaneIndex, spec.CardInstanceId), "Board fixture placement failed.");
            state.CardInstances.Add(spec.CardInstanceId, new CardInstanceState
            {
                CardInstanceId = spec.CardInstanceId,
                CardId = spec.CardId,
                OwnerPlayerId = spec.PlayerId,
                ControllerPlayerId = spec.PlayerId,
                Zone = "dominion",
                ZoneIndex = -1,
                Visibility = "public",
                CreatedSequence = createdSequence,
                ZoneSequence = 2,
                InitialZone = "deck",
                ActivityState = spec.ActivityState,
                DomainRow = spec.Row,
                DomainLaneIndex = spec.LaneIndex,
                EnteredDomainTurnNumber = 1,
            });
            createdSequence += 1;
            runtimeCards[spec.CardId] = new RuntimeCardDefinition(
                spec.CardId,
                0,
                0,
                "ignis",
                spec.CardType);
        }

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
        var groups = ImmutableDictionary.CreateBuilder<string, RuntimeLookupGroup>(StringComparer.Ordinal);
        groups.Add("realm", new RuntimeLookupGroup("realm", realms));
        groups.Add("card_type", new RuntimeLookupGroup("card_type", cardTypes));
        var runtime = new RuntimePackageCatalog(
            state.RuntimePackageId,
            runtimeCards.ToImmutable(),
            ImmutableDictionary<string, RuntimeDeckDefinition>.Empty.WithComparers(StringComparer.Ordinal),
            new RuntimeLookupCatalog(groups.ToImmutable()));
        EngineSession.ValidateState(state);
        return new ExecutionFixture(
            new EngineSession(state, runtime, canonicalCatalog),
            state,
            sourceInstanceId);
    }

    private static CanonicalAbilityCatalog Materialize() =>
        CanonicalAbilityMaterializer.Materialize(CanonicalAbilityCatalogTests.CreatePackage());

    private static BoardCard Board(
        string cardInstanceId,
        string cardId,
        string playerId,
        DomainRow row,
        int laneIndex,
        string activityState = "active",
        string cardType = "entity") =>
        new(cardInstanceId, cardId, playerId, row, laneIndex, activityState, cardType);

    private static ActionResponse PlaySource(ExecutionFixture fixture, int laneIndex = 0)
    {
        var action = fixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions
            .Single(item => item.ActionType == "play_card");
        return Submit(
            fixture,
            "player_1",
            action,
            ContractJsonValue.From(new PlayCardActionPayload(
                fixture.SourceCardInstanceId,
                "horizon",
                laneIndex,
                ImmutableArray<string>.Empty)));
    }

    private static ActionResponse Resolve(
        ExecutionFixture fixture,
        string playerId,
        string pendingTriggerId,
        string targetId,
        ImmutableArray<string> cardInstanceIds,
        int? expectedStateVersion = null)
    {
        var action = fixture.Session.ListLegalActions(playerId, includeDisabled: true).Actions
            .Single(item => item.ActionType == "resolve_triggered_ability");
        return Submit(
            fixture,
            playerId,
            action,
            ContractJsonValue.From(new ResolveTriggeredAbilityActionPayload(
                pendingTriggerId,
                [new CanonicalTargetSelectionPayload(targetId, cardInstanceIds)])),
            expectedStateVersion);
    }

    private static ActionResponse Submit(
        ExecutionFixture fixture,
        string playerId,
        LegalAction action,
        JsonElement payload,
        int? expectedStateVersion = null) =>
        fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            $"request_{playerId}_{action.ActionType}",
            fixture.State.MatchId,
            playerId,
            expectedStateVersion ?? fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            payload));

    private static object CardIdentity(CardInstanceState card) => new
    {
        card.CardInstanceId,
        card.CardId,
        card.OwnerPlayerId,
        card.ControllerPlayerId,
        card.Zone,
        card.ZoneIndex,
        card.Visibility,
        card.DomainRow,
        card.DomainLaneIndex,
        card.EnteredDomainTurnNumber,
    };

    private static string Fingerprint(ExecutionFixture fixture) => JsonSerializer.Serialize(new
    {
        Snapshot = fixture.Session.GetDebugSnapshot(),
        Discoveries = fixture.Session.GetDebugCanonicalTriggerDiscoveries(),
        Resolutions = fixture.Session.GetDebugCanonicalAbilityResolutions(),
    });

    private static void AssertRejected(ActionResponse response, string code)
    {
        False(response.Accepted, $"Action unexpectedly accepted negative fixture {code}.");
        Equal(code, Single(response.Diagnostics).Code, "Rejected action returned an unexpected diagnostic code.");
        Equal(0, response.Events.Length, "Rejected action emitted an event.");
        Equal(response.StateVersionBefore, response.StateVersionAfter, "Rejected action changed state version.");
    }

    private static T NotNull<T>(T? value, string message)
        where T : class => value ?? throw new InvalidOperationException(message);

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

    private sealed record ExecutionFixture(
        EngineSession Session,
        MatchState State,
        string SourceCardInstanceId);

    private sealed record BoardCard(
        string CardInstanceId,
        string CardId,
        string PlayerId,
        DomainRow Row,
        int LaneIndex,
        string ActivityState,
        string CardType);
}
