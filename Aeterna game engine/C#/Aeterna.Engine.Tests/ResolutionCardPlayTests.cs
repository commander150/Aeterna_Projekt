using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

internal static class ResolutionCardPlayTests
{
    private const string SourceCardId = "IGN-HAM-044";
    private const string AbilityId = "ability_ign_ham_044_01";
    private const string TargetId = "target_ign_ham_044_01_enemy_zenit_entity";

    internal static void AvailabilityProjectionAndDomainIndependence()
    {
        var fixture = CreateFixture(boardCards:
        [
            Board("ci_candidate_lane_4", "player_2", DomainRow.Zenith, 4),
            Board("ci_candidate_lane_1", "player_2", DomainRow.Zenith, 1),
        ]);
        var action = PlayAction(fixture);
        True(action.Enabled, "Supported IGN-HAM-044 did not enable play_card.");
        var option = Single(action.PayloadSchema.GetProperty("play_options").EnumerateArray());
        Equal(SourceCardId, option.GetProperty("card_id").GetString(), "Projected source card is invalid.");
        Equal("incantation", option.GetProperty("card_type").GetString(), "Projected resolution card type is invalid.");
        Equal(2, option.GetProperty("printed_aura_cost").GetInt32(), "Projected Aura cost is invalid.");
        Equal(AbilityId, option.GetProperty("ability_id").GetString(), "Projected ability is invalid.");
        var contract = Single(option.GetProperty("resolution_target_contracts").EnumerateArray());
        Equal(TargetId, contract.GetProperty("target_id").GetString(), "Projected target ID is invalid.");
        Equal(
            "ci_candidate_lane_1,ci_candidate_lane_4",
            string.Join(',', contract.GetProperty("candidate_card_instance_ids").EnumerateArray().Select(item => item.GetString())),
            "Zenith candidates are not deterministic lane-first values.");

        FillOwnDomain(fixture.State);
        EngineSession.ValidateState(fixture.State);
        True(PlayAction(fixture).Enabled, "Full own Domain incorrectly blocked a resolution card.");

        Equal("not_active_player", PlayAction(fixture, "player_2").DisabledReason, "Inactive-player reason is invalid.");
        var wrongPhase = CreateFixture();
        wrongPhase.State.Phase = "combat";
        EngineSession.ValidateState(wrongPhase.State);
        Equal("phase_not_main", PlayAction(wrongPhase).DisabledReason, "Wrong-phase reason is invalid.");

        AssertUnavailable(CreateFixture(boardCards: []), "Resolution card with no legal target was enabled.");
        AssertUnavailable(CreateFixture(includeCanonicalRuntime: false), "Resolution card without canonical runtime was enabled.");
        AssertUnavailable(
            CreateFixture(sources: [Source("ignis", "active")], printedAuraCost: 0),
            "Resolution card with insufficient Magnitude was enabled.");
        AssertUnavailable(
            CreateFixture(printedAuraCost: 3),
            "Resolution card with insufficient Aura was enabled.");

        var unsupported = CanonicalAbilityCatalogTests.SetField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.Effects,
            "effect_ign_ham_044_01_exhaust_target",
            "effect_action_type_id",
            "effect_deal_damage");
        AssertUnavailable(
            CreateFixture(canonicalPackage: unsupported),
            "Unsupported canonical effect graph enabled play_card.");
    }

    internal static void SuccessfulPlayIsAtomicOrderedAndViewerSafe()
    {
        var fixture = CreateFixture(boardCards:
        [
            Board("ci_selected_zenith", "player_2", DomainRow.Zenith, 2),
            Board("ci_other_zenith", "player_2", DomainRow.Zenith, 5),
        ]);
        var response = Submit(
            fixture,
            ResolutionPayload(fixture, ["ci_selected_zenith"]));

        True(response.Accepted, "Legal IGN-HAM-044 play was rejected.");
        Equal(0, response.StateVersionBefore, "Resolution play before-version is invalid.");
        Equal(1, response.StateVersionAfter, "Resolution play must increment state exactly once.");
        Equal(
            "aura_source_exhausted,aura_source_exhausted,card_activity_changed,canonical_ability_resolved,zone_move",
            string.Join(',', response.Events.Select(item => item.EventType)),
            "Resolution play event order is invalid.");
        True(response.Events.All(item => item.StateVersion == 1), "Resolution play event versions differ.");
        False(response.Events.Any(item => item.EventType == "card_entered_play"), "Resolution card emitted card_entered_play.");
        Equal("exhausted", fixture.State.GetCardInstance("ci_selected_zenith").ActivityState, "Selected target was not exhausted.");
        Equal("active", fixture.State.GetCardInstance("ci_other_zenith").ActivityState, "Unselected target was mutated.");
        True(fixture.SourceIds.All(id => fixture.State.GetCardInstance(id).ActivityState == "exhausted"), "Aura payment was not committed.");
        Equal(null, fixture.State.PendingTriggerWindow, "Played resolution created pending trigger state.");

        var source = fixture.State.GetCardInstance(fixture.SourceCardInstanceId);
        Equal("void", source.Zone, "Resolved source did not enter Void.");
        Equal(0, source.ZoneIndex, "Resolved source Void index is invalid.");
        Equal("public", source.Visibility, "Resolved source is not public in Void.");
        Equal(null, source.ActivityState, "Void source retained activity state.");
        Equal(null, source.DomainRow, "Void source retained Domain row.");
        Equal(null, source.DomainLaneIndex, "Void source retained Domain lane.");
        Equal(null, source.EnteredDomainTurnNumber, "Void source retained Domain entry turn.");
        Equal(fixture.SourceCardInstanceId, fixture.State.GetPlayer("player_1").VoidCardInstanceIds.Single(), "Void list is invalid.");
        Equal(0, fixture.State.GetCardInstance(fixture.ExtraHandCardInstanceId).ZoneIndex, "Remaining hand was not reindexed.");
        Equal("hand", response.Events[^1].Payload.GetProperty("from_zone").GetString(), "Void move origin is invalid.");
        Equal("void", response.Events[^1].Payload.GetProperty("to_zone").GetString(), "Void move destination is invalid.");
        Equal("played_card", response.Events[^2].Payload.GetProperty("resolution_origin").GetString(), "Resolution origin is invalid.");
        False(response.Events[^2].Payload.TryGetProperty("pending_trigger_id", out _), "Played resolution pretended to be a pending trigger.");

        var record = Single(fixture.Session.GetDebugCanonicalAbilityResolutions());
        Equal("played_card", record.ResolutionOrigin, "Debug resolution origin is invalid.");
        Equal(AbilityId, record.AbilityId, "Debug resolution ability is invalid.");
        Equal(1, record.AppliedEffectCount, "Debug applied-effect count is invalid.");
        Equal(null, record.PendingTriggerId, "Played resolution acquired pending-trigger identity.");

        var opponentSnapshot = fixture.Session.GetPlayerSnapshot("player_2");
        var publicVoid = opponentSnapshot.Players.Single(player => player.PlayerId == "player_1").Void;
        Equal(fixture.SourceCardInstanceId, publicVoid.Objects.Single().CardInstanceId, "Opponent cannot see public Void source identity.");
        var opponentMove = fixture.Session.GetEvents("player_2").Single(item => item.EventType == "zone_move");
        Equal(fixture.SourceCardInstanceId, opponentMove.Payload.GetProperty("card_instance_id").GetString(), "Opponent Void event lost public identity.");
        Equal(false, opponentMove.Payload.GetProperty("identity_redacted").GetBoolean(), "Opponent Void event remained redacted.");
        False(opponentMove.Payload.TryGetProperty("from_zone_index", out _), "Opponent Void event leaked private hand order.");
        EngineSession.ValidateState(fixture.State);
    }

    internal static void PayloadAndTargetRejectionsAreAtomic()
    {
        AssertRejectedImmutable(
            CreateFixture(),
            fixture => ContractJsonValue.From(new PlayCardActionPayload(
                fixture.SourceCardInstanceId,
                "horizon",
                0,
                fixture.SourceIds)),
            "PLAY_CARD_PAYLOAD_CARD_TYPE_MISMATCH");
        AssertRejectedImmutable(
            CreateFixture(),
            fixture => ResolutionPayload(fixture, [], targetSelections: []),
            "PLAY_CARD_TARGET_SELECTION_INVALID");
        AssertRejectedImmutable(
            CreateFixture(),
            fixture => ResolutionPayload(fixture, ["ci_default_target"], targetId: "target_unknown"),
            "PLAY_CARD_TARGET_ID_INVALID");
        AssertRejectedImmutable(
            CreateFixture(),
            fixture => ResolutionPayload(fixture, ["ci_default_target", "ci_default_target"]),
            "PLAY_CARD_TARGET_DUPLICATE");

        foreach (var spec in new[]
                 {
                     Board("ci_wrong_row", "player_2", DomainRow.Horizon, 0),
                     Board("ci_own_target", "player_1", DomainRow.Zenith, 0),
                     Board("ci_exhausted_target", "player_2", DomainRow.Zenith, 0, "exhausted"),
                     Board("ci_non_entity_target", "player_2", DomainRow.Zenith, 0, cardType: "incantation"),
                 })
        {
            var fixture = CreateFixture(boardCards:
            [
                Board("ci_legal_anchor", "player_2", DomainRow.Zenith, 5),
                spec,
            ]);
            AssertRejectedImmutable(
                fixture,
                current => ResolutionPayload(current, [spec.CardInstanceId]),
                "PLAY_CARD_TARGET_ILLEGAL");
        }

        AssertRejectedImmutable(
            CreateFixture(),
            fixture => ResolutionPayload(fixture, ["ci_unknown"]),
            "PLAY_CARD_TARGET_UNKNOWN");

        var malformed = CreateFixture();
        AssertRejectedImmutable(
            malformed,
            fixture => ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["card_instance_id"] = fixture.SourceCardInstanceId,
                ["aura_source_card_instance_ids"] = fixture.SourceIds,
                ["target_selections"] = new[]
                {
                    new Dictionary<string, object?>
                    {
                        ["target_id"] = TargetId,
                        ["card_instance_ids"] = new[] { "ci_default_target" },
                        ["unexpected"] = true,
                    },
                },
            }),
            "ACTION_PAYLOAD_INVALID");
    }

    internal static void AuraPolicyAndSelectionRejectionsAreAtomic()
    {
        var aether = CreateFixture(sources:
        [
            Source("ignis", "active"),
            Source("ignis", "active"),
            Source("aether", "active"),
        ]);
        AssertRejectedImmutable(
            aether,
            fixture => ResolutionPayload(
                fixture,
                ["ci_default_target"],
                auraSourceIds: [fixture.SourceIds[0], fixture.SourceIds[2]]),
            "PLAY_CARD_AURA_SOURCE_INVALID");

        AssertRejectedImmutable(
            CreateFixture(),
            fixture => ResolutionPayload(
                fixture,
                ["ci_default_target"],
                auraSourceIds: [fixture.SourceIds[0], fixture.SourceIds[0]]),
            "PLAY_CARD_AURA_SELECTION_INVALID");

        var exhausted = CreateFixture(sources:
        [
            Source("ignis", "active"),
            Source("ignis", "active"),
            Source("ignis", "exhausted"),
        ]);
        AssertRejectedImmutable(
            exhausted,
            fixture => ResolutionPayload(
                fixture,
                ["ci_default_target"],
                auraSourceIds: [fixture.SourceIds[0], fixture.SourceIds[2]]),
            "PLAY_CARD_AURA_SOURCE_INVALID");

        var wrongOwner = CreateFixture(sources:
        [
            Source("ignis", "active"),
            Source("ignis", "active"),
            Source("ignis", "active", "player_2"),
        ]);
        AssertRejectedImmutable(
            wrongOwner,
            fixture => ResolutionPayload(
                fixture,
                ["ci_default_target"],
                auraSourceIds: [fixture.SourceIds[0], fixture.OpponentSourceIds.Single()]),
            "PLAY_CARD_AURA_SOURCE_INVALID");
    }

    internal static void UnsupportedCanonicalGraphsAreControlledAndAtomic()
    {
        var cases = new (CanonicalCardDatabasePackage Package, string Code)[]
        {
            (
                CanonicalAbilityCatalogTests.SetField(
                    CanonicalAbilityCatalogTests.CreatePackage(),
                    CanonicalAbilityTableIds.Effects,
                    "effect_ign_ham_044_01_exhaust_target",
                    "effect_action_type_id",
                    "effect_apply_modifier"),
                "CANONICAL_EFFECT_ACTION_UNSUPPORTED"),
            (
                CanonicalAbilityCatalogTests.SetField(
                    CanonicalAbilityCatalogTests.CreatePackage(),
                    CanonicalAbilityTableIds.Targets,
                    TargetId,
                    "target_primitive_id",
                    "target_all_matching_cards"),
                "CANONICAL_TARGET_CONTRACT_UNSUPPORTED"),
            (
                CanonicalAbilityCatalogTests.SetField(
                    CanonicalAbilityCatalogTests.CreatePackage(),
                    CanonicalAbilityTableIds.Abilities,
                    AbilityId,
                    "implementation_mode_id",
                    "engine_module"),
                "CANONICAL_PLAYED_CARD_GRAPH_UNSUPPORTED"),
        };

        foreach (var testCase in cases)
        {
            AssertRejectedImmutable(
                CreateFixture(canonicalPackage: testCase.Package),
                fixture => ResolutionPayload(fixture, ["ci_default_target"]),
                testCase.Code);
        }

        var templatePackage = CanonicalAbilityCatalogTests.SetField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.Abilities,
            AbilityId,
            "implementation_mode_id",
            "template_instance");
        templatePackage = CanonicalAbilityCatalogTests.SetField(
            templatePackage,
            CanonicalAbilityTableIds.Abilities,
            AbilityId,
            "ability_template_id",
            "template_resolution_damage_all_enemy_horizont_entities_v1");
        try
        {
            _ = CanonicalAbilityMaterializer.Materialize(templatePackage);
            throw new InvalidOperationException("Template/manual graph coexistence was accepted.");
        }
        catch (EngineInputException exception)
        {
            Equal(
                "CANONICAL_TEMPLATE_MANUAL_GRAPH_CONFLICT",
                exception.Code,
                "Template/manual graph conflict returned an unexpected code.");
        }

        var wrongKindPackage = CanonicalAbilityCatalogTests.SetField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.Abilities,
            AbilityId,
            "ability_kind_id",
            "triggered");
        AssertRejectedImmutable(
            CreateFixture(canonicalPackage: wrongKindPackage),
            fixture => ResolutionPayload(fixture, ["ci_default_target"]),
            "PLAY_CARD_CANONICAL_RESOLUTION_AMBIGUOUS");

        var unsupportedType = CreateFixture(sourceCardType: "sigil");
        AssertRejectedImmutable(
            unsupportedType,
            fixture => ResolutionPayload(fixture, ["ci_default_target"]),
            "PLAY_CARD_CARD_TYPE_UNSUPPORTED");
    }

    internal static void LateRevalidationWardAndRitualDispatch()
    {
        var late = CreateFixture();
        var action = PlayAction(late);
        late.State.GetCardInstance("ci_default_target").ActivityState = "exhausted";
        EngineSession.ValidateState(late.State);
        var before = Fingerprint(late);
        var response = Submit(late, ResolutionPayload(late, ["ci_default_target"]), action);
        AssertRejected(response, "PLAY_CARD_TARGET_ILLEGAL");
        Equal(before, Fingerprint(late), "Late target revalidation mutated state.");

        var wardPackage = CanonicalAbilityCatalogTests.SetField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.CardKeywords,
            "cardkw_ign_ham_001_speed",
            "keyword_id",
            "ward");
        var ward = CreateFixture(canonicalPackage: wardPackage);
        True(Submit(ward, ResolutionPayload(ward, ["ci_default_target"])).Accepted, "Ward blocked non-attack resolution targeting.");
        Equal("exhausted", ward.State.GetCardInstance("ci_default_target").ActivityState, "Ward target was not exhausted.");

        var ritual = CreateFixture(sourceCardType: "ritual");
        True(PlayAction(ritual).Enabled, "Ritual dispatch did not use the canonical resolution kernel.");
        True(Submit(ritual, ResolutionPayload(ritual, ["ci_default_target"])).Accepted, "Ritual dispatch was rejected.");

        var unrestrictedPackage = CanonicalAbilityCatalogTests.SetField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.Targets,
            TargetId,
            "activity_state_id",
            null);
        var unrestricted = CreateFixture(
            boardCards: [Board("ci_unrestricted_exhausted", "player_2", DomainRow.Zenith, 0, "exhausted")],
            canonicalPackage: unrestrictedPackage);
        var unrestrictedResponse = Submit(
            unrestricted,
            ResolutionPayload(unrestricted, ["ci_unrestricted_exhausted"]));
        True(unrestrictedResponse.Accepted, "Canonical no-activity-restriction target was rejected.");
        False(
            unrestrictedResponse.Events.Any(item => item.EventType == "card_activity_changed"),
            "Idempotent exhaust emitted an activity mutation for an exhausted target.");
    }

    internal static void RepeatedResolutionPlayIsDeterministic()
    {
        string Run()
        {
            var fixture = CreateFixture();
            var response = Submit(fixture, ResolutionPayload(fixture, ["ci_default_target"]));
            True(response.Accepted, "Determinism resolution play was rejected.");
            return JsonSerializer.Serialize(new
            {
                Response = response,
                Snapshot = fixture.Session.GetDebugSnapshot(),
                Resolutions = fixture.Session.GetDebugCanonicalAbilityResolutions(),
            });
        }

        Equal(Run(), Run(), "Repeated resolution-card execution is not deterministic.");
    }

    private static ResolutionFixture CreateFixture(
        ImmutableArray<SourceSpec>? sources = null,
        ImmutableArray<BoardSpec>? boardCards = null,
        CanonicalCardDatabasePackage? canonicalPackage = null,
        bool includeCanonicalRuntime = true,
        int requiredMagnitude = 2,
        int printedAuraCost = 2,
        string sourceCardType = "incantation")
    {
        var state = new MatchState
        {
            MatchId = "resolution-card-play-test",
            Seed = 71,
            RuntimePackageId = "resolution-card-play-runtime",
            StateVersion = 0,
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        var playerOne = new PlayerState { PlayerId = "player_1", DeckId = "deck_1" };
        var playerTwo = new PlayerState { PlayerId = "player_2", DeckId = "deck_2" };
        state.Players.Add(playerOne);
        state.Players.Add(playerTwo);

        var sourceCardInstanceId = AddHandCard(state, playerOne, SourceCardId);
        var extraHandCardInstanceId = AddHandCard(state, playerOne, "TEST-EXTRA-HAND");
        var sourceSpecs = sources ??
        [
            Source("ignis", "active"),
            Source("ignis", "active"),
        ];
        var sourceIds = ImmutableArray.CreateBuilder<string>();
        var opponentSourceIds = ImmutableArray.CreateBuilder<string>();
        var sourceRealms = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var source in sourceSpecs)
        {
            var player = state.GetPlayer(source.PlayerId);
            var sourceId = AddWellspringCard(state, player, source.ActivityState);
            sourceRealms[state.GetCardInstance(sourceId).CardId] = source.Realm;
            (source.PlayerId == "player_1" ? sourceIds : opponentSourceIds).Add(sourceId);
        }

        var boards = boardCards ?? [Board("ci_default_target", "player_2", DomainRow.Zenith, 0)];
        foreach (var board in boards)
        {
            var player = state.GetPlayer(board.PlayerId);
            True(player.Domain.TryOccupy(board.Row, board.LaneIndex, board.CardInstanceId), "Board fixture placement failed.");
            state.CardInstances.Add(board.CardInstanceId, new CardInstanceState
            {
                CardInstanceId = board.CardInstanceId,
                CardId = board.CardId,
                OwnerPlayerId = board.PlayerId,
                ControllerPlayerId = board.PlayerId,
                Zone = "dominion",
                ZoneIndex = -1,
                Visibility = "public",
                CreatedSequence = state.CardInstances.Count + 1,
                ZoneSequence = 2,
                InitialZone = "deck",
                ActivityState = board.ActivityState,
                DomainRow = board.Row,
                DomainLaneIndex = board.LaneIndex,
                EnteredDomainTurnNumber = 1,
            });
        }

        var runtimeCards = ImmutableDictionary.CreateBuilder<string, RuntimeCardDefinition>(StringComparer.Ordinal);
        runtimeCards[SourceCardId] = new RuntimeCardDefinition(SourceCardId, requiredMagnitude, printedAuraCost, "ignis", sourceCardType);
        runtimeCards["TEST-EXTRA-HAND"] = new RuntimeCardDefinition("TEST-EXTRA-HAND", 0, 0, "ignis", "sigil");
        foreach (var card in state.CardInstances.Values.Where(card => string.Equals(card.Zone, "wellspring", StringComparison.Ordinal)))
        {
            runtimeCards[card.CardId] = new RuntimeCardDefinition(card.CardId, 0, 0, sourceRealms[card.CardId], "entity");
        }

        foreach (var board in boards)
        {
            runtimeCards[board.CardId] = new RuntimeCardDefinition(board.CardId, 0, 0, "ignis", board.CardType);
        }

        var runtime = new RuntimePackageCatalog(
            state.RuntimePackageId,
            runtimeCards.ToImmutable(),
            ImmutableDictionary<string, RuntimeDeckDefinition>.Empty.WithComparers(StringComparer.Ordinal),
            CreateLookups());
        EngineSession.ValidateState(state);
        var catalog = CanonicalAbilityMaterializer.Materialize(
            canonicalPackage ?? CanonicalAbilityCatalogTests.CreatePackage());
        var session = includeCanonicalRuntime
            ? new EngineSession(state, runtime, catalog)
            : new EngineSession(state, runtime);
        return new ResolutionFixture(
            session,
            state,
            sourceCardInstanceId,
            extraHandCardInstanceId,
            sourceIds.ToImmutable(),
            opponentSourceIds.ToImmutable());
    }

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
        var groups = ImmutableDictionary.CreateBuilder<string, RuntimeLookupGroup>(StringComparer.Ordinal);
        groups["realm"] = new RuntimeLookupGroup("realm", realms);
        groups["card_type"] = new RuntimeLookupGroup("card_type", cardTypes);
        return new RuntimeLookupCatalog(groups.ToImmutable());
    }

    private static JsonElement ResolutionPayload(
        ResolutionFixture fixture,
        ImmutableArray<string> selectedIds,
        string targetId = TargetId,
        ImmutableArray<string>? auraSourceIds = null,
        ImmutableArray<CanonicalTargetSelectionPayload>? targetSelections = null) =>
        ContractJsonValue.From(new PlayCardActionPayload(
            fixture.SourceCardInstanceId,
            DomainRow: null,
            LaneIndex: null,
            auraSourceIds ?? fixture.SourceIds,
            targetSelections ?? [new CanonicalTargetSelectionPayload(targetId, selectedIds)]));

    private static ActionResponse Submit(
        ResolutionFixture fixture,
        JsonElement payload,
        LegalAction? action = null,
        int? expectedStateVersion = null)
    {
        action ??= PlayAction(fixture);
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "request_play_resolution_card",
            fixture.State.MatchId,
            "player_1",
            expectedStateVersion ?? fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            payload));
    }

    private static LegalAction PlayAction(ResolutionFixture fixture, string playerId = "player_1") =>
        fixture.Session.ListLegalActions(playerId, includeDisabled: true).Actions
            .Single(action => action.ActionType == "play_card");

    private static void AssertUnavailable(ResolutionFixture fixture, string message)
    {
        var action = PlayAction(fixture);
        False(action.Enabled, message);
        Equal("no_playable_card", action.DisabledReason, "Generic unavailable reason is invalid.");
    }

    private static void AssertRejectedImmutable(
        ResolutionFixture fixture,
        Func<ResolutionFixture, JsonElement> payload,
        string diagnosticCode)
    {
        var before = Fingerprint(fixture);
        var response = Submit(fixture, payload(fixture));
        AssertRejected(response, diagnosticCode);
        Equal(before, Fingerprint(fixture), $"{diagnosticCode} rejection mutated authoritative state.");
    }

    private static void AssertRejected(ActionResponse response, string diagnosticCode)
    {
        False(response.Accepted, $"Negative fixture {diagnosticCode} was accepted.");
        Equal(diagnosticCode, Single(response.Diagnostics).Code, "Unexpected rejection diagnostic.");
        Equal(0, response.Events.Length, "Rejected action emitted events.");
        Equal(response.StateVersionBefore, response.StateVersionAfter, "Rejected action changed state version.");
    }

    private static string Fingerprint(ResolutionFixture fixture) => JsonSerializer.Serialize(new
    {
        Snapshot = fixture.Session.GetDebugSnapshot(),
        Discoveries = fixture.Session.GetDebugCanonicalTriggerDiscoveries(),
        Resolutions = fixture.Session.GetDebugCanonicalAbilityResolutions(),
    });

    private static string AddHandCard(MatchState state, PlayerState player, string cardId)
    {
        var index = player.HandCardInstanceIds.Count;
        var cardInstanceId = $"ci_{player.PlayerId}_hand_{index + 1:0000}";
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = cardId,
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "hand",
            ZoneIndex = index,
            Visibility = "owner_only",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "hand",
        });
        player.HandCardInstanceIds.Add(cardInstanceId);
        return cardInstanceId;
    }

    private static string AddWellspringCard(MatchState state, PlayerState player, string activityState)
    {
        var index = player.WellspringCardInstanceIds.Count;
        var cardInstanceId = $"ci_{player.PlayerId}_wellspring_{index + 1:0000}";
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = $"{player.PlayerId.ToUpperInvariant()}-SOURCE-{index + 1:0000}",
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "wellspring",
            ZoneIndex = index,
            Visibility = "owner_only",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "wellspring",
            ActivityState = activityState,
        });
        player.WellspringCardInstanceIds.Add(cardInstanceId);
        return cardInstanceId;
    }

    private static void FillOwnDomain(MatchState state)
    {
        var player = state.GetPlayer("player_1");
        foreach (var row in new[] { DomainRow.Horizon, DomainRow.Zenith })
        {
            for (var laneIndex = 0; laneIndex < DomainState.LaneCount; laneIndex += 1)
            {
                var cardInstanceId = $"ci_full_domain_{row}_{laneIndex}";
                state.CardInstances.Add(cardInstanceId, new CardInstanceState
                {
                    CardInstanceId = cardInstanceId,
                    CardId = $"FULL-DOMAIN-{row}-{laneIndex}",
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
                True(player.Domain.TryOccupy(row, laneIndex, cardInstanceId), "Full-Domain fixture placement failed.");
            }
        }
    }

    private static SourceSpec Source(string realm, string activityState, string playerId = "player_1") =>
        new(realm, activityState, playerId);

    private static BoardSpec Board(
        string cardInstanceId,
        string playerId,
        DomainRow row,
        int laneIndex,
        string activityState = "active",
        string cardType = "entity") =>
        new(cardInstanceId, "IGN-HAM-001", playerId, row, laneIndex, activityState, cardType);

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

    private sealed record ResolutionFixture(
        EngineSession Session,
        MatchState State,
        string SourceCardInstanceId,
        string ExtraHandCardInstanceId,
        ImmutableArray<string> SourceIds,
        ImmutableArray<string> OpponentSourceIds);

    private sealed record SourceSpec(string Realm, string ActivityState, string PlayerId);

    private sealed record BoardSpec(
        string CardInstanceId,
        string CardId,
        string PlayerId,
        DomainRow Row,
        int LaneIndex,
        string ActivityState,
        string CardType);
}
