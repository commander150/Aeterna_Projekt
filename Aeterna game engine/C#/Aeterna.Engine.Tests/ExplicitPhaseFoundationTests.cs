using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Headless;
using Aeterna.Engine.Rules;
using Aeterna.Engine.State;

internal static class ExplicitPhaseFoundationTests
{
    internal static void PhaseOrderAndLegalActionMatrix()
    {
        var (session, fixture) = CreatePublicSession("player_1");
        AssertState(session, 1, CanonicalPhaseIds.Awakening, "player_1");
        AssertActionTypes(session, "player_1", ["advance_phase"]);
        AssertRetiredActionsAbsent(session, "player_1");

        var malformed = SubmitAdvance(
            session,
            "player_1",
            "phase-target-rejected",
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["target_phase"] = CanonicalPhaseIds.Distribution,
            }));
        False(malformed.Accepted, "advance_phase accepted a client-selected target phase.");
        Equal("ACTION_PAYLOAD_INVALID", malformed.Diagnostics.Single().Code, "Target-phase rejection code is invalid.");
        AssertState(session, 1, CanonicalPhaseIds.Awakening, "player_1");

        True(Advance(session, "player_1", "to-infusion").Accepted, "Awakening advance failed.");
        AssertState(session, 1, CanonicalPhaseIds.Infusion, "player_1");
        AssertActionTypes(session, "player_1", ["advance_phase", "normal_inflow"]);

        True(Advance(session, "player_1", "skip-infusion").Accepted, "Infusion skip failed.");
        AssertState(session, 1, CanonicalPhaseIds.Manifestation, "player_1");
        AssertActionTypes(session, "player_1", ["advance_phase", "play_card"]);

        True(Advance(session, "player_1", "to-incursion").Accepted, "Manifestation advance failed.");
        AssertState(session, 1, CanonicalPhaseIds.Incursion, "player_1");
        AssertActionTypes(session, "player_1", ["advance_phase"]);

        var distribution = Advance(session, "player_1", "to-distribution");
        True(distribution.Accepted, "Incursion advance failed.");
        SequenceEqual(["phase_transition"], distribution.Events.Select(item => item.EventType), "Distribution entry event order is invalid.");
        AssertState(session, 1, CanonicalPhaseIds.Distribution, "player_1");
        AssertActionTypes(session, "player_1", ["advance_phase"]);

        var awakening = Advance(session, "player_1", "to-next-awakening");
        True(awakening.Accepted, "Distribution advance failed.");
        SequenceEqual(
            ["turn_transition", "zone_move", "zone_move"],
            awakening.Events.Select(item => item.EventType),
            "Next-player Awakening event order is invalid.");
        AssertState(session, 1, CanonicalPhaseIds.Awakening, "player_2");
        Equal(3, session.GetDebugSnapshot().Players.Single(player => player.PlayerId == "player_2").HandCardInstanceIds.Length, "Next player did not draw exactly two cards.");
        AssertRetiredActionsAbsent(session, "player_2");
        Equal(fixture.MatchId, session.GetDebugSnapshot().MatchId, "Fixture match identity changed.");
    }

    internal static void ExplicitStartingPlayerAndFirstAwakeningDraws()
    {
        var (session, _) = CreatePublicSession("player_2");
        var initial = session.GetDebugSnapshot();
        Equal("player_2", initial.StartingPlayerId, "Starting player was inferred from player collection order.");
        Equal("player_2", initial.ActivePlayerId, "Explicit starting player is not active.");
        Equal(1, initial.Players.Single(player => player.PlayerId == "player_2").HandCardInstanceIds.Length, "Starting player first Awakening incorrectly drew cards.");

        AdvanceWholeTurn(session, "player_2", "starting-player-first-turn");
        var otherFirstAwakening = session.GetDebugSnapshot();
        Equal("player_1", otherFirstAwakening.ActivePlayerId, "Other player did not become active.");
        Equal(1, otherFirstAwakening.TurnNumber, "Round counter advanced before returning to the starting player.");
        Equal(3, otherFirstAwakening.Players.Single(player => player.PlayerId == "player_1").HandCardInstanceIds.Length, "Other player's first Awakening did not draw two.");

        AdvanceWholeTurn(session, "player_1", "other-player-first-turn");
        var startingPlayerSecondAwakening = session.GetDebugSnapshot();
        Equal("player_2", startingPlayerSecondAwakening.ActivePlayerId, "Starting player did not become active again.");
        Equal(2, startingPlayerSecondAwakening.TurnNumber, "Round counter did not advance on return to explicit starting player.");
        Equal(3, startingPlayerSecondAwakening.Players.Single(player => player.PlayerId == "player_2").HandCardInstanceIds.Length, "Starting player's later Awakening did not draw two.");

        var fixture = RuntimeComparisonFixture.Load(FixtureLocator.LocateCanonicalFixture());
        var invalid = new EngineSession().CreateMatch(fixture.CreateMatchRequest() with
        {
            StartingPlayerId = "unknown-player",
        });
        False(invalid.Accepted, "Unknown explicit starting player was accepted.");
        Equal("STARTING_PLAYER_INVALID", invalid.Diagnostics.Single().Code, "Starting-player diagnostic is invalid.");
    }

    internal static void AwakeningReadiesOnceAndPreservesOpponentState()
    {
        var fixture = CreateDistributionFixture(nextPlayerDeckCount: 2);
        var beforeProjection = Fingerprint(fixture.Session);
        fixture.Session.ListLegalActions("player_2");
        fixture.Session.GetPlayerSnapshot("player_1");
        Equal(beforeProjection, Fingerprint(fixture.Session), "Distribution projection mutated state.");

        var response = Advance(fixture.Session, "player_2", "ready-and-draw");
        True(response.Accepted, "Awakening ready/draw transition failed.");
        SequenceEqual(
            ["turn_transition", "card_readied", "card_readied", "zone_move", "zone_move"],
            response.Events.Select(item => item.EventType),
            "Awakening ready/draw event ordering is invalid.");
        Equal("active", fixture.State.GetCardInstance("p1-domain").ActivityState, "Own Domain card was not readied.");
        Equal("active", fixture.State.GetCardInstance("p1-wellspring").ActivityState, "Own Wellspring card was not readied.");
        Equal("exhausted", fixture.State.GetCardInstance("p2-domain").ActivityState, "Opponent Domain card was changed.");
        Equal(2, fixture.State.GetPlayer("player_1").HandCardInstanceIds.Count, "Awakening did not draw two.");
        Equal(1, fixture.State.GetCardInstance("p1-domain").EnteredDomainTurnNumber, "Awakening changed Domain entry turn semantics.");

        var afterTransition = Fingerprint(fixture.Session);
        fixture.Session.ListLegalActions("player_1");
        fixture.Session.GetPlayerSnapshot("player_1");
        fixture.Session.GetPlayerSnapshot("player_2");
        Equal(afterTransition, Fingerprint(fixture.Session), "Repeated Awakening projection reran entry semantics.");

        var opponentReadyEvent = fixture.Session.GetEvents("player_2")
            .Single(item => item.EventType == "card_readied"
                            && item.Payload.TryGetProperty("zone", out var zone)
                            && zone.GetString() == "wellspring");
        False(opponentReadyEvent.Payload.TryGetProperty("card_instance_id", out _), "Private Wellspring ready event leaked identity.");
        True(opponentReadyEvent.Payload.GetProperty("identity_redacted").GetBoolean(), "Private ready event lacks redaction marker.");
    }

    internal static void ActionResponseUsesSubmittingPlayerProjectionAcrossSwitch()
    {
        var fixture = CreateDistributionFixture(nextPlayerDeckCount: 2, activePlayerId: "player_1");

        var response = Advance(fixture.Session, "player_1", "submitting-viewer-privacy");

        True(response.Accepted, "Distribution-to-Awakening transition failed.");
        Equal("player_1", response.PlayerId, "Action response lost the submitting-player viewer identity.");
        Equal("player_2", fixture.State.ActivePlayerId, "Fixture did not switch to the next active player.");
        SequenceEqual(
            ["turn_transition", "card_readied", "card_readied", "zone_move", "zone_move"],
            response.Events.Select(item => item.EventType),
            "Viewer projection changed canonical Awakening event ordering.");

        var responsePrivateReady = response.Events.Single(item =>
            item.EventType == "card_readied"
            && item.Payload.GetProperty("zone").GetString() == "wellspring");
        AssertIdentityRedacted(responsePrivateReady, "ActionResponse leaked the next player's Wellspring identity.");
        var responseDraws = response.Events.Where(item =>
            item.EventType == "zone_move"
            && item.Payload.GetProperty("to_zone").GetString() == "hand").ToArray();
        Equal(2, responseDraws.Length, "ActionResponse draw event count is invalid.");
        foreach (var draw in responseDraws)
        {
            AssertIdentityRedacted(draw, "ActionResponse leaked the next player's hand identity.");
            False(draw.Payload.TryGetProperty("from_zone_index", out _), "ActionResponse leaked private Deck order.");
        }

        var submittingPlayerEvents = fixture.Session.GetEvents("player_1");
        Equal(
            JsonSerializer.Serialize(submittingPlayerEvents),
            JsonSerializer.Serialize(response.Events),
            "ActionResponse does not reuse the submitting player's canonical event projection.");

        var nextPlayerEvents = fixture.Session.GetEvents("player_2");
        var ownerReady = nextPlayerEvents.Single(item =>
            item.EventType == "card_readied"
            && item.Payload.GetProperty("zone").GetString() == "wellspring");
        True(ownerReady.Payload.TryGetProperty("card_instance_id", out _), "Owner projection lost Wellspring instance identity.");
        True(ownerReady.Payload.TryGetProperty("card_id", out _), "Owner projection lost Wellspring card identity.");
        True(nextPlayerEvents.Where(item => item.EventType == "zone_move").All(item =>
            item.Payload.TryGetProperty("card_instance_id", out _)
            && item.Payload.TryGetProperty("card_id", out _)), "Owner projection lost drawn-card identity.");

        var internalEvents = fixture.Session.GetDebugEvents();
        var internalReady = internalEvents.Single(item =>
            item.EventType == "card_readied"
            && item.Payload.GetProperty("zone").GetString() == "wellspring");
        True(internalReady.Payload.TryGetProperty("card_instance_id", out _), "Internal event store lost Wellspring identity.");
        True(internalReady.Payload.TryGetProperty("card_id", out _), "Internal event store lost Wellspring card identity.");
        True(internalEvents.Where(item => item.EventType == "zone_move").All(item =>
            item.Payload.TryGetProperty("card_instance_id", out _)
            && item.Payload.TryGetProperty("card_id", out _)), "Internal event store lost drawn-card identity.");
    }

    internal static void DirectRetiredAndWrongPhaseActionsAreRejectedAtomically()
    {
        var (session, _) = CreatePublicSession("player_1");
        var legalAdvance = session.ListLegalActions("player_1").Actions.Single(item =>
            item.Enabled && item.ActionType == "advance_phase");

        foreach (var actionType in new[] { "draw_card", "end_turn", "normal_inflow" })
        {
            var before = Fingerprint(session);
            var response = session.SubmitAction(new ActionRequest(
                ContractSchemas.ActionRequest,
                $"direct-illegal-{actionType}",
                session.GetDebugSnapshot().MatchId,
                "player_1",
                ExpectedStateVersion: 0,
                legalAdvance.ActionId,
                actionType,
                ContractJsonValue.EmptyObject()));

            False(response.Accepted, $"Direct {actionType} bypass was accepted.");
            Equal("ACTION_TYPE_MISMATCH", response.Diagnostics.Single().Code, $"Direct {actionType} rejection code is invalid.");
            Equal(0, response.StateVersionBefore, $"Direct {actionType} changed response before-version.");
            Equal(0, response.StateVersionAfter, $"Direct {actionType} changed response after-version.");
            Equal(0, response.Events.Length, $"Direct {actionType} emitted response events.");
            Equal(before, Fingerprint(session), $"Direct {actionType} rejection mutated authoritative state or event history.");
        }
    }

    internal static void AwakeningDrawFailureIsAtomic()
    {
        var fixture = CreateDistributionFixture(nextPlayerDeckCount: 1);
        var before = Fingerprint(fixture.Session);
        var response = Advance(fixture.Session, "player_2", "insufficient-awakening-draw");

        False(response.Accepted, "Insufficient mandatory Awakening draw was accepted.");
        Equal("awakening_draw_unavailable", response.Reason, "Awakening rejection reason is invalid.");
        Equal(
            "CANONICAL_DRAW_REFRESH_PENALTY_UNSUPPORTED",
            response.Diagnostics.Single().Code,
            "Awakening Refresh boundary code is invalid.");
        Equal(before, Fingerprint(fixture.Session), "Failed Awakening transition partially mutated state.");
        Equal(CanonicalPhaseIds.Distribution, fixture.State.Phase, "Failed transition changed phase.");
        Equal("player_2", fixture.State.ActivePlayerId, "Failed transition changed active player.");
        Equal(1, fixture.State.TurnNumber, "Failed transition changed turn number.");
        Equal("exhausted", fixture.State.GetCardInstance("p1-domain").ActivityState, "Failed transition readied a Domain card.");
        Equal("exhausted", fixture.State.GetCardInstance("p1-wellspring").ActivityState, "Failed transition readied a Wellspring card.");
    }

    internal static void DistributionIsObservableAndSwitchesOnlyOnExit()
    {
        var fixture = CreateDistributionFixture(nextPlayerDeckCount: 2);
        fixture.State.Phase = CanonicalPhaseIds.Incursion;
        var distribution = Advance(fixture.Session, "player_2", "enter-observable-distribution");
        True(distribution.Accepted, "Distribution entry failed.");
        Equal(CanonicalPhaseIds.Distribution, fixture.State.Phase, "Distribution is not observable.");
        Equal("player_2", fixture.State.ActivePlayerId, "Distribution entry switched player early.");
        Equal(1, fixture.State.TurnNumber, "Distribution entry advanced turn number early.");

        var awakening = Advance(fixture.Session, "player_2", "leave-observable-distribution");
        True(awakening.Accepted, "Distribution exit failed.");
        Equal(CanonicalPhaseIds.Awakening, fixture.State.Phase, "Distribution exit did not enter Awakening.");
        Equal("player_1", fixture.State.ActivePlayerId, "Distribution exit did not switch player.");
        Equal("player_1", fixture.State.PriorityPlayerId, "Priority owner did not follow active player.");
        Equal(2, fixture.State.TurnNumber, "Explicit starting-player round semantics are invalid.");
        Equal("turn_transition", awakening.Events[0].EventType, "Player-switch event ordering is invalid.");
    }

    internal static void PhaseVocabularyAndEventDeterminism()
    {
        var invalid = CreateDistributionFixture(nextPlayerDeckCount: 2);
        invalid.State.Phase = "combat";
        Throws<EngineStateException>(
            () => EngineSession.ValidateState(invalid.State),
            "Unknown phase token was accepted.");

        invalid.State.Phase = "main";
        Throws<EngineStateException>(
            () => EngineSession.ValidateState(invalid.State),
            "Retired main phase was accepted outside the isolated oracle adapter.");

        string Run()
        {
            var fixture = CreateDistributionFixture(nextPlayerDeckCount: 2);
            var response = Advance(fixture.Session, "player_2", "deterministic-awakening");
            return JsonSerializer.Serialize(new
            {
                Response = response,
                Snapshot = fixture.Session.GetDebugSnapshot(),
            });
        }

        Equal(Run(), Run(), "Equivalent phase transitions are not deterministic.");
    }

    private static (EngineSession Session, RuntimeComparisonFixture Fixture) CreatePublicSession(
        string startingPlayerId)
    {
        var fixture = RuntimeComparisonFixture.Load(FixtureLocator.LocateCanonicalFixture());
        var session = new EngineSession();
        var response = session.CreateMatch(fixture.CreateMatchRequest() with
        {
            StartingPlayerId = startingPlayerId,
        });
        True(response.Accepted, "Phase fixture match creation failed.");
        return (session, fixture);
    }

    private static void AdvanceWholeTurn(EngineSession session, string playerId, string prefix)
    {
        for (var index = 0; index < CanonicalPhaseIds.Ordered.Length; index += 1)
        {
            True(Advance(session, playerId, $"{prefix}-{index + 1}").Accepted, "Whole-turn phase advance failed.");
        }
    }

    private static ActionResponse Advance(EngineSession session, string playerId, string requestId) =>
        SubmitAdvance(session, playerId, requestId, ContractJsonValue.EmptyObject());

    private static ActionResponse SubmitAdvance(
        EngineSession session,
        string playerId,
        string requestId,
        JsonElement payload)
    {
        var state = session.GetDebugSnapshot();
        var action = session.ListLegalActions(playerId).Actions.Single(item =>
            item.ActionType == "advance_phase" && item.Enabled);
        return session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            requestId,
            state.MatchId,
            playerId,
            state.StateVersion,
            action.ActionId,
            action.ActionType,
            payload));
    }

    private static void AssertActionTypes(
        EngineSession session,
        string playerId,
        IEnumerable<string> expected) => SequenceEqual(
        expected,
        session.ListLegalActions(playerId, includeDisabled: true).Actions
            .Select(item => item.ActionType),
        "Phase legal action matrix is invalid.");

    private static void AssertRetiredActionsAbsent(EngineSession session, string playerId)
    {
        var actionTypes = session.ListLegalActions(playerId, includeDisabled: true).Actions
            .Select(item => item.ActionType)
            .ToHashSet(StringComparer.Ordinal);
        False(actionTypes.Contains("draw_card"), "draw_card remained a public production action.");
        False(actionTypes.Contains("end_turn"), "end_turn remained a public production action.");
    }

    private static void AssertState(
        EngineSession session,
        int turnNumber,
        string phase,
        string activePlayerId)
    {
        var state = session.GetDebugSnapshot();
        Equal(turnNumber, state.TurnNumber, "Turn number is invalid.");
        Equal(phase, state.Phase, "Phase is invalid.");
        Equal(activePlayerId, state.ActivePlayerId, "Active player is invalid.");
    }

    private static PhaseFixture CreateDistributionFixture(
        int nextPlayerDeckCount,
        string activePlayerId = "player_2")
    {
        var state = new MatchState
        {
            MatchId = "explicit-phase-fixture",
            Seed = 211,
            RuntimePackageId = "explicit-phase-runtime",
            StateVersion = 0,
            TurnNumber = 1,
            Phase = CanonicalPhaseIds.Distribution,
            StartingPlayerId = "player_1",
            ActivePlayerId = activePlayerId,
            PriorityPlayerId = activePlayerId,
        };
        var playerOne = new PlayerState { PlayerId = "player_1", DeckId = "deck-1" };
        var playerTwo = new PlayerState { PlayerId = "player_2", DeckId = "deck-2" };
        state.Players.Add(playerOne);
        state.Players.Add(playerTwo);
        var activePlayer = state.GetPlayer(activePlayerId);
        var nextPlayer = state.GetPlayer(state.GetNextPlayerId(activePlayerId));
        var activePrefix = activePlayer.PlayerId == "player_1" ? "p1" : "p2";
        var nextPrefix = nextPlayer.PlayerId == "player_1" ? "p1" : "p2";
        for (var index = 0; index < nextPlayerDeckCount; index += 1)
        {
            AddDeckCard(state, nextPlayer, $"{nextPrefix}-deck-{index + 1}");
        }

        AddDomainCard(state, nextPlayer, $"{nextPrefix}-domain", DomainRow.Horizon, 0, "exhausted");
        AddWellspringCard(state, nextPlayer, $"{nextPrefix}-wellspring", "exhausted");
        AddDomainCard(state, activePlayer, $"{activePrefix}-domain", DomainRow.Horizon, 0, "exhausted");
        EngineSession.ValidateState(state);
        return new PhaseFixture(new EngineSession(state), state);
    }

    private static void AddDeckCard(MatchState state, PlayerState player, string cardInstanceId)
    {
        var index = player.DeckCardInstanceIds.Count;
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = $"CARD-{cardInstanceId}",
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "deck",
            ZoneIndex = index,
            Visibility = "owner_only",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "deck",
            ActivityState = null,
        });
        player.DeckCardInstanceIds.Add(cardInstanceId);
    }

    private static void AddWellspringCard(
        MatchState state,
        PlayerState player,
        string cardInstanceId,
        string activityState)
    {
        var index = player.WellspringCardInstanceIds.Count;
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = $"CARD-{cardInstanceId}",
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
    }

    private static void AddDomainCard(
        MatchState state,
        PlayerState player,
        string cardInstanceId,
        DomainRow row,
        int laneIndex,
        string activityState)
    {
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = $"CARD-{cardInstanceId}",
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "dominion",
            ZoneIndex = -1,
            Visibility = "public",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "dominion",
            ActivityState = activityState,
            DomainRow = row,
            DomainLaneIndex = laneIndex,
            EnteredDomainTurnNumber = 1,
        });
        True(player.Domain.TryOccupy(row, laneIndex, cardInstanceId), "Phase fixture Domain placement failed.");
    }

    private static string Fingerprint(EngineSession session) =>
        JsonSerializer.Serialize(session.GetDebugSnapshot());

    private static void AssertIdentityRedacted(EngineEvent engineEvent, string message)
    {
        False(engineEvent.Payload.TryGetProperty("card_instance_id", out _), message);
        False(engineEvent.Payload.TryGetProperty("card_id", out _), message);
        True(engineEvent.Payload.GetProperty("identity_redacted").GetBoolean(), message);
    }

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
                $"{message} Expected=[{string.Join(',', expectedItems)}]; Actual=[{string.Join(',', actualItems)}]");
        }
    }

    private static void True(bool value, string message)
    {
        if (!value)
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void False(bool value, string message) => True(!value, message);

    private static void Throws<TException>(Action action, string message)
        where TException : Exception
    {
        try
        {
            action();
        }
        catch (TException)
        {
            return;
        }

        throw new InvalidOperationException(message);
    }

    private sealed record PhaseFixture(EngineSession Session, MatchState State);
}
