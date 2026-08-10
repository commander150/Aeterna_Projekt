using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

internal sealed record PlayAuraSourceSetup(
    string Realm,
    string ActivityState,
    string PlayerId = "player_1");

internal static class PlayCardTests
{
    internal static void LegalActionContractAndAvailability()
    {
        var playable = CreateFixture(
            printedAuraCost: 1,
            requiredMagnitude: 1,
            sources: [new("ignis", "active")],
            extraHandCount: 0);
        var action = PlayAction(playable.Session, "player_1");
        Equal(true, action.Enabled, "Playable Entity did not enable play_card.");
        Equal(175, action.OrderRank, "play_card order rank is invalid.");
        var schema = action.PayloadSchema;
        SequenceEqual(
            ["card_instance_id", "aura_source_card_instance_ids"],
            schema.GetProperty("required").EnumerateArray().Select(item => item.GetString()!),
            "play_card common required payload fields are invalid.");
        Equal(2, schema.GetProperty("one_of").GetArrayLength(), "play_card lifecycle union is missing.");
        var option = schema.GetProperty("play_options")[0];
        Equal("entity", option.GetProperty("card_type").GetString(), "Entity play option type is invalid.");
        Equal(12, option.GetProperty("entity_placements").GetArrayLength(), "Entity placement projection is incomplete.");
        SequenceEqual(
            ["horizon", "zenith"],
            schema.GetProperty("properties").GetProperty("domain_row")
                .GetProperty("enum").EnumerateArray().Select(item => item.GetString()!),
            "play_card Domain row enum is invalid.");
        Equal(
            true,
            schema.GetProperty("properties").GetProperty("aura_source_card_instance_ids")
                .GetProperty("unique_items").GetBoolean(),
            "Aura source payload schema must require unique items.");

        var inactive = PlayAction(playable.Session, "player_2");
        Equal(false, inactive.Enabled, "Inactive player play_card must be disabled.");
        Equal("not_active_player", inactive.DisabledReason, "Inactive disabled reason is invalid.");

        var wrongPhase = CreateFixture(extraHandCount: 0);
        wrongPhase.State.Phase = "combat";
        EngineSession.ValidateState(wrongPhase.State);
        Equal(
            "phase_not_main",
            PlayAction(wrongPhase.Session, "player_1").DisabledReason,
            "Wrong-phase disabled reason is invalid.");

        var nonEntity = CreateFixture(targetCardType: "incantation", extraHandCount: 0);
        AssertDisabled(nonEntity, "no_playable_card", "Unsupported non-Entity enabled play_card.");
        var magnitude = CreateFixture(
            requiredMagnitude: 2,
            sources: [new("ignis", "active")],
            extraHandCount: 0);
        AssertDisabled(magnitude, "no_playable_card", "Insufficient Magnitude enabled play_card.");
        var aura = CreateFixture(
            printedAuraCost: 2,
            sources: [new("ignis", "active")],
            extraHandCount: 0);
        AssertDisabled(aura, "no_playable_card", "Insufficient Aura enabled play_card.");

        var fullDomain = CreateFixture(extraHandCount: 0);
        FillDomain(fullDomain.State.GetPlayer("player_1"), fullDomain.State);
        EngineSession.ValidateState(fullDomain.State);
        AssertDisabled(fullDomain, "no_playable_card", "Full Domain enabled entity-only play_card.");
    }

    internal static void EntityPlaysToHorizonAtomically()
    {
        var fixture = CreateFixture(
            printedAuraCost: 1,
            requiredMagnitude: 1,
            sources: [new("ignis", "active")],
            extraHandCount: 1);
        var sourceId = fixture.PlayerOneSourceIds.Single();
        var response = Submit(
            fixture,
            PlayPayload(fixture.TargetCardInstanceId, "horizon", 2, [sourceId]));

        Equal(true, response.Accepted, "Legal Horizon play was rejected.");
        Equal(0, response.StateVersionBefore, "Horizon play before-version is invalid.");
        Equal(1, response.StateVersionAfter, "Horizon play must increment state exactly once.");
        Equal(1, fixture.State.StateVersion, "Authoritative state version is invalid.");
        SequenceEqual(
            ["aura_source_exhausted", "zone_move", "card_entered_play"],
            response.Events.Select(item => item.EventType),
            "Horizon play event order is invalid.");
        SequenceEqual([1, 2, 3], response.Events.Select(item => item.EventSequence), "Event sequence is invalid.");
        True(response.Events.All(item => item.StateVersion == 1), "Play events use inconsistent state versions.");
        Equal("hand", response.Events[1].Payload.GetProperty("from_zone").GetString(), "Zone move source is invalid.");
        Equal("dominion", response.Events[1].Payload.GetProperty("to_zone").GetString(), "Zone move destination is invalid.");
        Equal("horizon", response.Events[1].Payload.GetProperty("domain_row").GetString(), "Zone move row is invalid.");
        Equal(2, response.Events[1].Payload.GetProperty("lane_index").GetInt32(), "Zone move lane is invalid.");
        Equal("active", response.Events[2].Payload.GetProperty("activity_state").GetString(), "Entered-play activity is invalid.");
        Equal(
            fixture.State.TurnNumber,
            response.Events[2].Payload.GetProperty("entered_domain_turn_number").GetInt32(),
            "Entered-play turn is invalid.");

        var player = fixture.State.GetPlayer("player_1");
        Equal(1, player.HandCardInstanceIds.Count, "Played card was not removed from hand.");
        var remaining = fixture.State.GetCardInstance(player.HandCardInstanceIds.Single());
        Equal(0, remaining.ZoneIndex, "Remaining hand was not reindexed.");
        Equal(sourceId, player.WellspringCardInstanceIds.Single(), "Wellspring order changed.");
        Equal("exhausted", fixture.State.GetCardInstance(sourceId).ActivityState, "Aura source was not exhausted.");
        Equal(fixture.TargetCardInstanceId, player.Domain.HorizonCardInstanceIds[2], "Horizon occupancy is invalid.");

        var card = fixture.State.GetCardInstance(fixture.TargetCardInstanceId);
        AssertEnteredDomainCard(card, DomainRow.Horizon, 2, fixture.State.TurnNumber);
        EngineSession.ValidateState(fixture.State);

        var ownerSnapshot = fixture.Session.GetPlayerSnapshot("player_1");
        var opponentSnapshot = fixture.Session.GetPlayerSnapshot("player_2");
        AssertProjectedCard(ownerSnapshot.BoardSummary, "player_1", "horizon", 2, fixture.TargetCardInstanceId);
        AssertProjectedCard(opponentSnapshot.BoardSummary, "player_1", "horizon", 2, fixture.TargetCardInstanceId);
        Equal(
            0,
            opponentSnapshot.Players.Single(item => item.PlayerId == "player_1").Hand.Objects.Length,
            "Opponent hand projection leaked remaining private identities.");

        var debug = fixture.Session.GetDebugSnapshot();
        Equal(
            fixture.TargetCardInstanceId,
            debug.Players.Single(item => item.PlayerId == "player_1").HorizonCardInstanceIds[2],
            "Debug Horizon occupancy is invalid.");
        Equal("exhausted", debug.CardInstances.Single(item => item.CardInstanceId == sourceId).ActivityState, "Debug Aura state is invalid.");

        var opponentEvents = fixture.Session.GetEvents("player_2");
        Equal(
            false,
            opponentEvents[0].Payload.TryGetProperty("card_instance_id", out _),
            "Opponent Aura event leaked source identity.");
        Equal(
            true,
            opponentEvents[0].Payload.GetProperty("identity_redacted").GetBoolean(),
            "Opponent Aura event is not redacted.");
        Equal(
            fixture.TargetCardInstanceId,
            opponentEvents[1].Payload.GetProperty("card_instance_id").GetString(),
            "Public Domain entry event lost card identity.");
        Equal(
            false,
            opponentEvents[1].Payload.TryGetProperty("from_zone_index", out _),
            "Opponent Domain move leaked private hand order.");
    }

    internal static void EntityPlaysToZenithActive()
    {
        var fixture = CreateFixture(extraHandCount: 0);
        var response = Submit(
            fixture,
            PlayPayload(fixture.TargetCardInstanceId, "zenith", 5, []));

        Equal(true, response.Accepted, "Legal Zenith play was rejected.");
        SequenceEqual(
            ["zone_move", "card_entered_play"],
            response.Events.Select(item => item.EventType),
            "Zero-cost Zenith event order is invalid.");
        var card = fixture.State.GetCardInstance(fixture.TargetCardInstanceId);
        AssertEnteredDomainCard(card, DomainRow.Zenith, 5, fixture.State.TurnNumber);
        Equal(
            fixture.TargetCardInstanceId,
            fixture.State.GetPlayer("player_1").Domain.ZenithCardInstanceIds[5],
            "Zenith occupancy is invalid.");
        AssertProjectedCard(
            fixture.Session.GetPlayerSnapshot("player_2").BoardSummary,
            "player_1",
            "zenith",
            5,
            fixture.TargetCardInstanceId);
    }

    internal static void MixedRealmAndAetherPaymentIsExactAndOrdered()
    {
        var fixture = CreateFixture(
            printedAuraCost: 2,
            sources:
            [
                new("ignis", "active"),
                new("aether", "active"),
                new("aqua", "active"),
            ],
            extraHandCount: 0);
        var selected = new[]
        {
            fixture.PlayerOneSourceIds[1],
            fixture.PlayerOneSourceIds[0],
        };
        var response = Submit(
            fixture,
            PlayPayload(fixture.TargetCardInstanceId, "horizon", 0, selected));

        Equal(true, response.Accepted, "Mixed own-Realm/Aether payment was rejected.");
        SequenceEqual(
            [fixture.PlayerOneSourceIds[0], fixture.PlayerOneSourceIds[1]],
            response.Events.Take(2).Select(item => item.Payload.GetProperty("card_instance_id").GetString()!),
            "Aura exhaustion events are not ordered by Wellspring index.");
        Equal("exhausted", fixture.State.GetCardInstance(fixture.PlayerOneSourceIds[0]).ActivityState, "Own-Realm source stayed active.");
        Equal("exhausted", fixture.State.GetCardInstance(fixture.PlayerOneSourceIds[1]).ActivityState, "Aether source stayed active.");
        Equal("active", fixture.State.GetCardInstance(fixture.PlayerOneSourceIds[2]).ActivityState, "Unselected source was exhausted.");
        Equal(3, fixture.State.GetPlayer("player_1").WellspringCardInstanceIds.Count, "Magnitude source count changed.");
        Equal(
            3,
            fixture.Session.GetPlayerSnapshot("player_1").ResourceSummary.Players
                .Single(item => item.PlayerId == "player_1").Magnitude,
            "Aura payment reduced Magnitude.");
    }

    internal static void ZeroCostRequiresEmptyPaymentAndEmitsNoPaymentEvent()
    {
        var fixture = CreateFixture(
            printedAuraCost: 0,
            sources: [new("ignis", "active")],
            extraHandCount: 0);
        var sourceId = fixture.PlayerOneSourceIds.Single();
        var response = Submit(
            fixture,
            PlayPayload(fixture.TargetCardInstanceId, "horizon", 1, []));

        Equal(true, response.Accepted, "Zero-cost Entity was rejected with an empty Aura list.");
        SequenceEqual(
            ["zone_move", "card_entered_play"],
            response.Events.Select(item => item.EventType),
            "Zero-cost play emitted a payment event.");
        Equal("active", fixture.State.GetCardInstance(sourceId).ActivityState, "Zero-cost play exhausted a source.");
    }

    internal static void RepeatedExecutionIsDeterministic()
    {
        var first = CreateFixture(
            printedAuraCost: 2,
            sources: [new("ignis", "active"), new("aether", "active")],
            extraHandCount: 1);
        var second = CreateFixture(
            printedAuraCost: 2,
            sources: [new("ignis", "active"), new("aether", "active")],
            extraHandCount: 1);
        var firstResponse = Submit(
            first,
            PlayPayload(first.TargetCardInstanceId, "zenith", 3, first.PlayerOneSourceIds));
        var secondResponse = Submit(
            second,
            PlayPayload(second.TargetCardInstanceId, "zenith", 3, second.PlayerOneSourceIds));

        Equal(
            JsonSerializer.Serialize(firstResponse),
            JsonSerializer.Serialize(secondResponse),
            "Identical play_card transitions produced different responses.");
        Equal(
            Fingerprint(first.Session),
            Fingerprint(second.Session),
            "Identical play_card transitions produced different authoritative states.");
    }

    internal static void PlayerPhaseAndStaleRequestsAreImmutable()
    {
        var inactive = CreateFixture(extraHandCount: 0);
        AssertRejectedImmutable(
            inactive,
            "player_2",
            PlayAction(inactive.Session, "player_2"),
            PlayPayload(inactive.PlayerTwoCardInstanceId, "horizon", 0, []),
            "PLAY_CARD_PLAYER_INVALID");

        var phase = CreateFixture(extraHandCount: 0);
        phase.State.Phase = "combat";
        EngineSession.ValidateState(phase.State);
        AssertRejectedImmutable(
            phase,
            "player_1",
            PlayAction(phase.Session, "player_1"),
            PlayPayload(phase.TargetCardInstanceId, "horizon", 0, []),
            "PLAY_CARD_PHASE_INVALID");

        var stale = CreateFixture(extraHandCount: 0);
        AssertRejectedImmutable(
            stale,
            "player_1",
            PlayAction(stale.Session, "player_1"),
            PlayPayload(stale.TargetCardInstanceId, "horizon", 0, []),
            "STALE_STATE_VERSION",
            expectedStateVersion: 1);
    }

    internal static void CardReferenceAndTypeFailuresAreImmutable()
    {
        var fixture = CreateFixture(
            sources: [new("ignis", "active")],
            extraHandCount: 0);
        var action = PlayAction(fixture.Session, "player_1");
        AssertRejectedImmutable(
            fixture,
            "player_1",
            action,
            PlayPayload("ci_unknown", "horizon", 0, []),
            "PLAY_CARD_CARD_UNKNOWN");
        AssertRejectedImmutable(
            fixture,
            "player_1",
            action,
            PlayPayload(fixture.PlayerOneSourceIds.Single(), "horizon", 0, []),
            "PLAY_CARD_CARD_ZONE_INVALID");
        AssertRejectedImmutable(
            fixture,
            "player_1",
            action,
            PlayPayload(fixture.PlayerTwoCardInstanceId, "horizon", 0, []),
            "PLAY_CARD_CARD_AUTHORITY_INVALID");

        var nonEntity = CreateFixture(targetCardType: "incantation", extraHandCount: 0);
        AssertRejectedImmutable(
            nonEntity,
            "player_1",
            PlayAction(nonEntity.Session, "player_1"),
            PlayPayload(nonEntity.TargetCardInstanceId, "horizon", 0, []),
            "PLAY_CARD_PAYLOAD_CARD_TYPE_MISMATCH");
    }

    internal static void MagnitudeAndAuraInsufficiencyAreImmutable()
    {
        var magnitude = CreateFixture(
            requiredMagnitude: 2,
            sources: [new("ignis", "active")],
            extraHandCount: 0);
        AssertRejectedImmutable(
            magnitude,
            "player_1",
            PlayAction(magnitude.Session, "player_1"),
            PlayPayload(magnitude.TargetCardInstanceId, "horizon", 0, []),
            "PLAY_CARD_MAGNITUDE_REQUIREMENT_NOT_MET");

        var aura = CreateFixture(
            printedAuraCost: 2,
            sources: [new("ignis", "active")],
            extraHandCount: 0);
        AssertRejectedImmutable(
            aura,
            "player_1",
            PlayAction(aura.Session, "player_1"),
            PlayPayload(aura.TargetCardInstanceId, "horizon", 0, aura.PlayerOneSourceIds),
            "PLAY_CARD_AURA_INSUFFICIENT");
    }

    internal static void InvalidAuraSourcesAreImmutable()
    {
        var fixture = CreateFixture(
            printedAuraCost: 1,
            sources:
            [
                new("ignis", "active"),
                new("ignis", "exhausted"),
                new("aqua", "active"),
                new("ignis", "active", "player_2"),
            ],
            extraHandCount: 0);
        var action = PlayAction(fixture.Session, "player_1");
        foreach (var sourceId in new[]
                 {
                     fixture.PlayerOneSourceIds[1],
                     fixture.PlayerOneSourceIds[2],
                     fixture.PlayerTwoSourceIds.Single(),
                     "ci_unknown_source",
                 })
        {
            AssertRejectedImmutable(
                fixture,
                "player_1",
                action,
                PlayPayload(fixture.TargetCardInstanceId, "horizon", 0, [sourceId]),
                "PLAY_CARD_AURA_SOURCE_INVALID");
        }
    }

    internal static void InvalidAuraCountsAndDuplicatesAreImmutable()
    {
        var fixture = CreateFixture(
            printedAuraCost: 2,
            sources:
            [
                new("ignis", "active"),
                new("aether", "active"),
                new("ignis", "active"),
            ],
            extraHandCount: 0);
        var action = PlayAction(fixture.Session, "player_1");
        foreach (var selection in new IReadOnlyCollection<string>[]
                 {
                     [fixture.PlayerOneSourceIds[0]],
                     fixture.PlayerOneSourceIds,
                     [fixture.PlayerOneSourceIds[0], fixture.PlayerOneSourceIds[0]],
                 })
        {
            AssertRejectedImmutable(
                fixture,
                "player_1",
                action,
                PlayPayload(fixture.TargetCardInstanceId, "horizon", 0, selection),
                "PLAY_CARD_AURA_SELECTION_INVALID");
        }

        var zero = CreateFixture(
            sources: [new("ignis", "active")],
            extraHandCount: 0);
        AssertRejectedImmutable(
            zero,
            "player_1",
            PlayAction(zero.Session, "player_1"),
            PlayPayload(
                zero.TargetCardInstanceId,
                "horizon",
                0,
                [zero.PlayerOneSourceIds.Single()]),
            "PLAY_CARD_AURA_SELECTION_INVALID");
    }

    internal static void InvalidAndOccupiedDestinationsAreImmutable()
    {
        var invalid = CreateFixture(extraHandCount: 0);
        var action = PlayAction(invalid.Session, "player_1");
        foreach (var item in new[]
                 {
                     (Row: "middle", Lane: 0, Code: "PLAY_CARD_DESTINATION_ROW_INVALID"),
                     (Row: "horizon", Lane: -1, Code: "PLAY_CARD_DESTINATION_LANE_INVALID"),
                     (Row: "zenith", Lane: 6, Code: "PLAY_CARD_DESTINATION_LANE_INVALID"),
                 })
        {
            AssertRejectedImmutable(
                invalid,
                "player_1",
                action,
                PlayPayload(invalid.TargetCardInstanceId, item.Row, item.Lane, []),
                item.Code);
        }

        var occupied = CreateFixture(extraHandCount: 0);
        AddDomainOccupant(occupied.State, occupied.State.GetPlayer("player_1"), DomainRow.Horizon, 1);
        AddDomainOccupant(occupied.State, occupied.State.GetPlayer("player_1"), DomainRow.Zenith, 4);
        EngineSession.ValidateState(occupied.State);
        var occupiedAction = PlayAction(occupied.Session, "player_1");
        foreach (var item in new[] { (Row: "horizon", Lane: 1), (Row: "zenith", Lane: 4) })
        {
            AssertRejectedImmutable(
                occupied,
                "player_1",
                occupiedAction,
                PlayPayload(occupied.TargetCardInstanceId, item.Row, item.Lane, []),
                "PLAY_CARD_DESTINATION_OCCUPIED");
        }
    }

    internal static void MalformedPayloadIsImmutable()
    {
        var fixture = CreateFixture(extraHandCount: 0);
        var action = PlayAction(fixture.Session, "player_1");
        var invalidPayloads = new[]
        {
            ContractJsonValue.EmptyObject(),
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["card_instance_id"] = fixture.TargetCardInstanceId,
                ["domain_row"] = "horizon",
                ["lane_index"] = 0,
                ["aura_source_card_instance_ids"] = (object?)null,
            }),
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["card_instance_id"] = fixture.TargetCardInstanceId,
                ["domain_row"] = "horizon",
                ["lane_index"] = 0.5,
                ["aura_source_card_instance_ids"] = Array.Empty<string>(),
            }),
        };
        foreach (var payload in invalidPayloads)
        {
            AssertRejectedImmutable(
                fixture,
                "player_1",
                action,
                payload,
                "ACTION_PAYLOAD_INVALID");
        }
    }

    internal static void CommitRevalidatesChangedAuraState()
    {
        var fixture = CreateFixture(
            printedAuraCost: 1,
            sources: [new("ignis", "active")],
            extraHandCount: 0);
        var actionFromPreflight = PlayAction(fixture.Session, "player_1");
        Equal(true, actionFromPreflight.Enabled, "Race fixture did not start playable.");
        var sourceId = fixture.PlayerOneSourceIds.Single();
        fixture.State.GetCardInstance(sourceId).ActivityState = "exhausted";
        EngineSession.ValidateState(fixture.State);

        AssertRejectedImmutable(
            fixture,
            "player_1",
            actionFromPreflight,
            PlayPayload(fixture.TargetCardInstanceId, "horizon", 0, [sourceId]),
            "PLAY_CARD_AURA_INSUFFICIENT");
    }

    private static PlayFixture CreateFixture(
        int printedAuraCost = 0,
        int requiredMagnitude = 0,
        string targetRealm = "ignis",
        string targetCardType = "entity",
        IReadOnlyList<PlayAuraSourceSetup>? sources = null,
        int extraHandCount = 1)
    {
        var state = new MatchState
        {
            MatchId = "play-card-test-match",
            Seed = 1,
            RuntimePackageId = "play-card-test-package",
            StateVersion = 0,
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        var playerOne = new PlayerState { PlayerId = "player_1", DeckId = "deck_1" };
        var playerTwo = new PlayerState { PlayerId = "player_2", DeckId = "deck_2" };
        state.Players.Add(playerOne);
        state.Players.Add(playerTwo);

        var targetId = AddHandCard(state, playerOne, "TARGET-CARD");
        for (var index = 0; index < extraHandCount; index++)
        {
            AddHandCard(state, playerOne, $"EXTRA-HAND-CARD-{index + 1:0000}");
        }

        var playerTwoCardId = AddHandCard(state, playerTwo, "PLAYER-TWO-CARD");
        var sourceRealms = new Dictionary<string, string>(StringComparer.Ordinal);
        var playerOneSourceIds = ImmutableArray.CreateBuilder<string>();
        var playerTwoSourceIds = ImmutableArray.CreateBuilder<string>();
        foreach (var source in sources ?? [])
        {
            var player = state.GetPlayer(source.PlayerId);
            var sourceId = AddWellspringCard(state, player, source.ActivityState);
            sourceRealms[state.GetCardInstance(sourceId).CardId] = source.Realm;
            (source.PlayerId == "player_1" ? playerOneSourceIds : playerTwoSourceIds).Add(sourceId);
        }

        EngineSession.ValidateState(state);
        var cards = ImmutableDictionary.CreateBuilder<string, RuntimeCardDefinition>(StringComparer.Ordinal);
        foreach (var card in state.CardInstances.Values.OrderBy(item => item.CardId, StringComparer.Ordinal))
        {
            var isTarget = string.Equals(card.CardInstanceId, targetId, StringComparison.Ordinal);
            cards[card.CardId] = new RuntimeCardDefinition(
                card.CardId,
                isTarget ? requiredMagnitude : 0,
                isTarget ? printedAuraCost : 0,
                isTarget
                    ? targetRealm
                    : sourceRealms.TryGetValue(card.CardId, out var sourceRealm)
                        ? sourceRealm
                        : "ignis",
                isTarget ? targetCardType : "entity");
        }

        var catalog = new RuntimePackageCatalog(
            state.RuntimePackageId,
            cards.ToImmutable(),
            ImmutableDictionary.Create<string, RuntimeDeckDefinition>(StringComparer.Ordinal),
            CreateLookups());
        return new PlayFixture(
            new EngineSession(state, catalog),
            state,
            targetId,
            playerTwoCardId,
            playerOneSourceIds.ToImmutable(),
            playerTwoSourceIds.ToImmutable());
    }

    private static RuntimeLookupCatalog CreateLookups()
    {
        var realms = ImmutableDictionary.CreateBuilder<string, string>(StringComparer.Ordinal);
        foreach (var realm in new[] { "ignis", "aqua", "terra", "lux", "umbra", "ventus", "aether" })
        {
            realms[realm] = realm;
        }

        var cardTypes = ImmutableDictionary.CreateBuilder<string, string>(StringComparer.Ordinal);
        foreach (var cardType in new[] { "entity", "incantation", "ritual", "sigil", "plane" })
        {
            cardTypes[cardType] = cardType;
        }

        var groups = ImmutableDictionary.CreateBuilder<string, RuntimeLookupGroup>(StringComparer.Ordinal);
        groups["realm"] = new RuntimeLookupGroup("realm", realms.ToImmutable());
        groups["card_type"] = new RuntimeLookupGroup("card_type", cardTypes.ToImmutable());
        return new RuntimeLookupCatalog(groups.ToImmutable());
    }

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
            ActivityState = null,
        });
        player.HandCardInstanceIds.Add(cardInstanceId);
        return cardInstanceId;
    }

    private static string AddWellspringCard(
        MatchState state,
        PlayerState player,
        string activityState)
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

    private static void FillDomain(PlayerState player, MatchState state)
    {
        for (var lane = 0; lane < DomainState.LaneCount; lane++)
        {
            AddDomainOccupant(state, player, DomainRow.Horizon, lane);
            AddDomainOccupant(state, player, DomainRow.Zenith, lane);
        }
    }

    private static void AddDomainOccupant(
        MatchState state,
        PlayerState player,
        DomainRow row,
        int laneIndex)
    {
        var cardInstanceId = $"ci_domain_{state.CardInstances.Count + 1:0000}";
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = $"DOMAIN-CARD-{state.CardInstances.Count + 1:0000}",
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
            EnteredDomainTurnNumber = state.TurnNumber,
        });
        True(player.Domain.TryOccupy(row, laneIndex, cardInstanceId), "Domain fixture slot was occupied.");
    }

    private static LegalAction PlayAction(EngineSession session, string playerId) => session
        .ListLegalActions(playerId, includeDisabled: true)
        .Actions.Single(item => item.ActionType == "play_card");

    private static JsonElement PlayPayload(
        string cardInstanceId,
        string domainRow,
        int laneIndex,
        IReadOnlyCollection<string> auraSourceIds) => ContractJsonValue.From(
            new PlayCardActionPayload(
                cardInstanceId,
                domainRow,
                laneIndex,
                auraSourceIds.ToImmutableArray()));

    private static ActionResponse Submit(PlayFixture fixture, JsonElement payload)
    {
        var action = PlayAction(fixture.Session, "player_1");
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "play-card-request",
            fixture.State.MatchId,
            "player_1",
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            payload));
    }

    private static void AssertRejectedImmutable(
        PlayFixture fixture,
        string playerId,
        LegalAction action,
        JsonElement payload,
        string expectedCode,
        int? expectedStateVersion = null)
    {
        var before = Fingerprint(fixture.Session);
        var eventCount = fixture.Session.GetDebugEvents().Length;
        var request = new ActionRequest(
            ContractSchemas.ActionRequest,
            $"reject-{expectedCode}",
            fixture.State.MatchId,
            playerId,
            expectedStateVersion ?? fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            payload);
        var requestBefore = JsonSerializer.Serialize(request);

        var response = fixture.Session.SubmitAction(request);

        Equal(false, response.Accepted, $"{expectedCode} request was accepted.");
        Equal(expectedCode, response.Diagnostics.Single().Code, "Unexpected rejection diagnostic.");
        Equal(before, Fingerprint(fixture.Session), $"{expectedCode} rejection mutated state.");
        Equal(eventCount, fixture.Session.GetDebugEvents().Length, $"{expectedCode} rejection emitted an event.");
        Equal(requestBefore, JsonSerializer.Serialize(request), $"{expectedCode} rejection mutated the request.");
    }

    private static void AssertEnteredDomainCard(
        CardInstanceState card,
        DomainRow expectedRow,
        int expectedLane,
        int expectedTurn)
    {
        Equal("dominion", card.Zone, "Played card zone is invalid.");
        Equal(-1, card.ZoneIndex, "Played card ZoneIndex sentinel is invalid.");
        Equal("public", card.Visibility, "Played card visibility is invalid.");
        Equal("active", card.ActivityState, "Normally summoned Entity must enter active.");
        Equal(expectedRow, card.DomainRow, "Played card Domain row is invalid.");
        Equal(expectedLane, card.DomainLaneIndex, "Played card lane is invalid.");
        Equal(expectedTurn, card.EnteredDomainTurnNumber, "EnteredDomainTurnNumber is invalid.");
    }

    private static void AssertProjectedCard(
        JsonElement board,
        string playerId,
        string row,
        int laneIndex,
        string expectedCardInstanceId)
    {
        var player = board.GetProperty("players").EnumerateArray()
            .Single(item => item.GetProperty("player_id").GetString() == playerId);
        var slot = player.GetProperty(row)[laneIndex];
        Equal(true, slot.GetProperty("occupied").GetBoolean(), "Projected Domain slot is empty.");
        Equal(row, slot.GetProperty("row").GetString(), "Projected row is invalid.");
        Equal(laneIndex, slot.GetProperty("lane_index").GetInt32(), "Projected lane is invalid.");
        Equal(
            expectedCardInstanceId,
            slot.GetProperty("occupant").GetProperty("card_instance_id").GetString(),
            "Projected Domain card identity is invalid.");
        Equal(
            "active",
            slot.GetProperty("occupant").GetProperty("activity_state").GetString(),
            "Projected Domain activity is invalid.");
    }

    private static void AssertDisabled(PlayFixture fixture, string reason, string message)
    {
        var action = PlayAction(fixture.Session, "player_1");
        Equal(false, action.Enabled, message);
        Equal(reason, action.DisabledReason, $"{message} Disabled reason is invalid.");
    }

    private static string Fingerprint(EngineSession session) =>
        JsonSerializer.Serialize(session.GetDebugSnapshot());

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected={expected}; Actual={actual}");
        }
    }

    private static void SequenceEqual<T>(
        IEnumerable<T> expected,
        IEnumerable<T> actual,
        string message)
    {
        var expectedItems = expected.ToArray();
        var actualItems = actual.ToArray();
        if (!expectedItems.SequenceEqual(actualItems))
        {
            throw new InvalidOperationException(
                $"{message} Expected=[{string.Join(",", expectedItems)}]; "
                + $"Actual=[{string.Join(",", actualItems)}]");
        }
    }

    private static void True(bool value, string message)
    {
        if (!value)
        {
            throw new InvalidOperationException(message);
        }
    }

    private sealed record PlayFixture(
        EngineSession Session,
        MatchState State,
        string TargetCardInstanceId,
        string PlayerTwoCardInstanceId,
        ImmutableArray<string> PlayerOneSourceIds,
        ImmutableArray<string> PlayerTwoSourceIds);
}
