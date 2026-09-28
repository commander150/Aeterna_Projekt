using System.Collections.Immutable;
using System.Reflection;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Headless;
using Aeterna.Engine.Rules;
using Aeterna.Engine.State;

internal static class MatchSetupSealFoundationTests
{
    internal static void CanonicalCreateMatchOpensProphecyGate()
    {
        using var package = CreatePackage();
        var session = CreateSession(package, seed: 101);
        var debug = session.GetDebugSnapshot();
        Equal(ContractSchemas.DebugSnapshotWithSeals, debug.SchemaVersion, "Canonical setup debug schema is invalid.");
        Equal(0, debug.StateVersion, "Canonical setup must start at state version zero.");
        Equal(CanonicalPhaseIds.Awakening, debug.Phase, "Prophecy must not create a gameplay phase.");
        Equal(5, Player(debug, "player_1").HandCardInstanceIds.Length, "Player one opening hand is invalid.");
        Equal(5, Player(debug, "player_2").HandCardInstanceIds.Length, "Player two opening hand is invalid.");
        Equal(35, Player(debug, "player_1").DeckCardInstanceIds.Length, "Player one opening Deck is invalid.");

        var enabled = session.ListLegalActions("player_1").Actions;
        Equal(1, enabled.Length, "Only the current Prophecy decision may be enabled during setup.");
        var prophecy = enabled.Single();
        Equal("resolve_prophecy", prophecy.ActionType, "Canonical setup action type is invalid.");
        Equal(false, prophecy.PayloadSchema.GetProperty("additional_properties").GetBoolean(), "Prophecy payload must reject additional properties.");
        Equal(5, prophecy.PayloadSchema.GetProperty("properties").GetProperty("card_instance_ids").GetProperty("maximum_items").GetInt32(), "Prophecy payload cardinality is invalid.");
        Equal(0, session.ListLegalActions("player_2").Actions.Length, "The non-decision player received an enabled setup action.");

        var allActions = session.ListLegalActions("player_1", includeDisabled: true).Actions;
        True(allActions.Single(item => item.ActionType == "advance_phase").DisabledReason == "match_setup_pending", "Normal phase action was not explicitly setup-gated.");
        Equal("prophecy", session.GetPlayerSnapshot("player_1").PendingDecisionSummary.GetProperty("pending_type").GetString(), "Pending setup projection is invalid.");
    }

    internal static void SetupGateAndStaleRequestsAreAtomic()
    {
        using var package = CreatePackage();
        var session = CreateSession(package, seed: 102);
        var before = Fingerprint(session);
        var bypass = session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "setup-bypass",
            "setup-seal-match",
            "player_1",
            0,
            "advance_phase:1:0:awakening:player_1",
            "advance_phase",
            ContractJsonValue.EmptyObject()));
        False(bypass.Accepted, "A direct phase action bypassed pending setup.");
        Equal("ACTION_DISABLED", bypass.Diagnostics.Single().Code, "Setup bypass diagnostic is invalid.");
        Equal("match_setup_pending", bypass.Reason, "Setup bypass reason is invalid.");
        Equal(before, Fingerprint(session), "Rejected setup bypass mutated state.");

        var prophecy = EnabledProphecy(session, "player_1");
        var stale = session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "stale-prophecy",
            "setup-seal-match",
            "player_1",
            -1,
            prophecy.ActionId,
            prophecy.ActionType,
            ProphecyPayload([])));
        False(stale.Accepted, "A stale Prophecy request was accepted.");
        Equal("STALE_STATE_VERSION", stale.Diagnostics.Single().Code, "Stale Prophecy diagnostic is invalid.");
        Equal(before, Fingerprint(session), "Rejected stale Prophecy mutated state.");
    }

    internal static void ShuffleStreamsAreSeededDeterministicAndDistinct()
    {
        using var package = CreatePackage();
        var first = CreateSession(package, seed: 9001, matchId: "deterministic-match");
        var second = CreateSession(package, seed: 9001, matchId: "deterministic-match");
        Equal(CardOrder(first), CardOrder(second), "Equal seed and input produced different opening shuffles.");

        var differentSeed = CreateSession(package, seed: 9002, matchId: "deterministic-match");
        NotEqual(CardOrder(first), CardOrder(differentSeed), "Different seeds produced the same authoritative card order.");

        Equal(3, State(first).NextShuffleSequence, "Initial player shuffles did not consume distinct stream sequences.");
        var selected = Player(first.GetDebugSnapshot(), "player_1").HandCardInstanceIds.Take(2).ToArray();
        True(SubmitProphecy(first, "player_1", selected, "shuffle-prophecy-one").Accepted, "First multi-card Prophecy failed.");
        Equal(4, State(first).NextShuffleSequence, "Prophecy reused an initial shuffle sequence.");
        var secondSelected = Player(first.GetDebugSnapshot(), "player_2").HandCardInstanceIds.Take(2).ToArray();
        True(SubmitProphecy(first, "player_2", secondSelected, "shuffle-prophecy-two").Accepted, "Second multi-card Prophecy failed.");
        Equal(5, State(first).NextShuffleSequence, "Second Prophecy reused an earlier shuffle sequence.");
    }

    internal static void ZeroAndMultiCardProphecyFollowCanonicalFlow()
    {
        using var package = CreatePackage();
        var zero = CreateSession(package, seed: 103);
        var zeroBefore = Player(zero.GetDebugSnapshot(), "player_1");
        var zeroResponse = SubmitProphecy(zero, "player_1", [], "zero-prophecy");
        True(zeroResponse.Accepted, "Zero-card Prophecy was rejected.");
        Equal(5, Player(zero.GetDebugSnapshot(), "player_1").HandCardInstanceIds.Length, "Zero-card Prophecy changed hand size.");
        SequenceEqual(zeroBefore.HandCardInstanceIds, Player(zero.GetDebugSnapshot(), "player_1").HandCardInstanceIds, "Zero-card Prophecy changed hand order.");
        Equal(3, State(zero).NextShuffleSequence, "Zero-card Prophecy consumed an unnecessary shuffle stream.");

        var multi = CreateSession(package, seed: 104);
        var selected = Player(multi.GetDebugSnapshot(), "player_1").HandCardInstanceIds.Take(3).ToArray();
        var multiResponse = SubmitProphecy(multi, "player_1", selected, "multi-prophecy");
        True(multiResponse.Accepted, "Multi-card Prophecy was rejected.");
        Equal(5, Player(multi.GetDebugSnapshot(), "player_1").HandCardInstanceIds.Length, "Multi-card Prophecy did not redraw the exact count.");
        Equal(35, Player(multi.GetDebugSnapshot(), "player_1").DeckCardInstanceIds.Length, "Multi-card Prophecy changed total Deck membership.");
        Equal(3, multiResponse.Events.Single().Payload.GetProperty("returned_card_count").GetInt32(), "Prophecy event count is invalid.");
        False(multiResponse.Events.Single().Payload.TryGetProperty("card_instance_ids", out _), "Prophecy event leaked selected card identities.");

        var observedReturnedCardRedraw = false;
        for (var seed = 200; seed < 240 && !observedReturnedCardRedraw; seed += 1)
        {
            var redraw = CreateSession(package, seed, matchId: $"redraw-{seed}");
            var returnedIds = Player(redraw.GetDebugSnapshot(), "player_1").HandCardInstanceIds.ToArray();
            True(SubmitProphecy(redraw, "player_1", returnedIds, $"redraw-{seed}").Accepted, "Full-hand Prophecy failed.");
            var redrawnIds = Player(redraw.GetDebugSnapshot(), "player_1").HandCardInstanceIds;
            observedReturnedCardRedraw = returnedIds.Intersect(redrawnIds, StringComparer.Ordinal).Any();
        }

        True(observedReturnedCardRedraw, "The deterministic Prophecy flow never allowed a returned card to be redrawn.");
    }

    internal static void InvalidProphecySelectionsAreControlledAndAtomic()
    {
        using var package = CreatePackage();
        var session = CreateSession(package, seed: 105);
        var debug = session.GetDebugSnapshot();
        var ownHand = Player(debug, "player_1").HandCardInstanceIds;
        var opponentHand = Player(debug, "player_2").HandCardInstanceIds;
        var ownDeck = Player(debug, "player_1").DeckCardInstanceIds;

        AssertRejectedSelection(session, [ownHand[0], ownHand[0]], "PROPHECY_SELECTION_DUPLICATE");
        AssertRejectedSelection(session, ["ci_unknown"], "PROPHECY_CARD_UNKNOWN");
        AssertRejectedSelection(session, [opponentHand[0]], "PROPHECY_CARD_AUTHORITY_INVALID");
        AssertRejectedSelection(session, [ownDeck[0]], "PROPHECY_CARD_ZONE_INVALID");

        var action = EnabledProphecy(session, "player_1");
        var before = Fingerprint(session);
        var malformed = session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "malformed-prophecy",
            "setup-seal-match",
            "player_1",
            0,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["card_instance_ids"] = Array.Empty<string>(),
                ["unexpected"] = true,
            })));
        False(malformed.Accepted, "Prophecy accepted an additional payload property.");
        Equal("ACTION_PAYLOAD_INVALID", malformed.Diagnostics.Single().Code, "Malformed Prophecy diagnostic is invalid.");
        Equal(before, Fingerprint(session), "Malformed Prophecy mutated state.");
    }

    internal static void ProphecyHandoffAndViewerPrivacyAreExact()
    {
        using var package = CreatePackage();
        var session = CreateSession(package, seed: 106);
        var hiddenHandIds = Player(session.GetDebugSnapshot(), "player_1").HandCardInstanceIds;
        var opponentPending = session.GetPlayerSnapshot("player_2");
        Equal("player_1", opponentPending.PendingDecisionSummary.GetProperty("decision_player_id").GetString(), "Initial Prophecy decision player is invalid.");
        False(opponentPending.PendingDecisionSummary.GetProperty("viewer_is_decision_player").GetBoolean(), "Opponent was projected as Prophecy decision player.");
        var opponentJson = JsonSerializer.Serialize(opponentPending);
        False(hiddenHandIds.Any(opponentJson.Contains), "Opponent projection leaked a pending Prophecy hand identity.");

        True(SubmitProphecy(session, "player_1", [], "handoff-one").Accepted, "First Prophecy failed.");
        var playerOneView = session.GetPlayerSnapshot("player_1");
        var playerTwoView = session.GetPlayerSnapshot("player_2");
        Equal("player_2", playerOneView.PendingDecisionSummary.GetProperty("decision_player_id").GetString(), "Prophecy did not hand off to the second player.");
        False(playerOneView.PendingDecisionSummary.GetProperty("viewer_is_decision_player").GetBoolean(), "Completed player retained decision authority.");
        True(playerTwoView.PendingDecisionSummary.GetProperty("viewer_is_decision_player").GetBoolean(), "Second player did not receive decision authority.");
        Equal(0, session.ListLegalActions("player_1").Actions.Length, "Completed Prophecy player retained an enabled setup action.");
        Equal("resolve_prophecy", session.ListLegalActions("player_2").Actions.Single().ActionType, "Second player Prophecy legal action is missing.");

        var reversed = CreateSession(
            package,
            seed: 206,
            matchId: "reverse-prophecy-order",
            startingPlayerId: "player_2");
        Equal("player_2", reversed.GetPlayerSnapshot("player_1").PendingDecisionSummary.GetProperty("decision_player_id").GetString(), "Configured second player did not receive the first Prophecy decision.");
        True(SubmitProphecy(reversed, "player_2", [], "reverse-handoff").Accepted, "Reversed first Prophecy failed.");
        Equal("player_1", reversed.GetPlayerSnapshot("player_2").PendingDecisionSummary.GetProperty("decision_player_id").GetString(), "Reversed Prophecy order did not hand off to the other player.");
    }

    internal static void SetupCompletionInitializesMappedSealsAndAwakening()
    {
        using var package = CreatePackage();
        var session = CreateSession(package, seed: 107);
        True(SubmitProphecy(session, "player_1", [], "complete-one").Accepted, "First Prophecy failed.");
        var beforeCompletion = session.GetDebugSnapshot().Players.ToDictionary(
            player => player.PlayerId,
            player => player.DeckCardInstanceIds.Take(6).ToArray(),
            StringComparer.Ordinal);
        var completion = SubmitProphecy(session, "player_2", [], "complete-two");
        True(completion.Accepted, "Second Prophecy failed.");
        SequenceEqual(
            ["prophecy_resolved", "seals_initialized", "match_setup_completed"],
            completion.Events.Select(item => item.EventType),
            "Setup completion event order is invalid.");

        var debug = session.GetDebugSnapshot();
        Equal(CanonicalPhaseIds.Awakening, debug.Phase, "Setup did not continue into first Awakening.");
        Equal("player_1", debug.ActivePlayerId, "Setup changed the configured starting player.");
        Equal("player_1", debug.PriorityPlayerId, "Setup completion did not restore starting-player priority.");
        Equal(2, debug.StateVersion, "Each Prophecy decision must advance state exactly once.");
        foreach (var player in debug.Players)
        {
            Equal(6, player.SealSlots.Length, "Completed setup did not create exactly six Seals.");
            Equal(29, player.DeckCardInstanceIds.Length, "Seal cards were not removed from the Deck.");
            for (var laneIndex = 0; laneIndex < 6; laneIndex += 1)
            {
                var slot = player.SealSlots[laneIndex];
                Equal(laneIndex, slot.LaneIndex, "Seal lane mapping is invalid.");
                Equal($"seal:{player.PlayerId}:{laneIndex + 1:00}", slot.SealSlotId, "Seal slot identity is unstable.");
                Equal("standing", slot.Status, "Initialized Seal is not standing.");
                Equal(beforeCompletion[player.PlayerId][laneIndex], slot.CardInstanceId, "Deck top-to-lane Seal mapping is invalid.");
                var card = debug.CardInstances.Single(item => item.CardInstanceId == slot.CardInstanceId);
                Equal("seal", card.Zone, "Seal card retained normal Deck membership.");
                Equal(laneIndex, card.ZoneIndex, "Seal card authoritative lane index is invalid.");
                Equal("hidden", card.Visibility, "Standing Seal card is not hidden from both players.");
            }
        }

        False(debug.PendingTriggerSummary.GetProperty("has_pending").GetBoolean(), "Completed setup retained a pending setup decision.");
        True(session.ListLegalActions("player_1").Actions.Any(item => item.ActionType == "advance_phase"), "First Awakening lifecycle did not resume after setup.");
    }

    internal static void SealProjectionIsViewerSafeAndDebugAuthoritative()
    {
        using var package = CreatePackage();
        var session = CompleteSetup(package, seed: 108, matchId: "seal-privacy-match");
        var debug = session.GetDebugSnapshot();
        var hiddenInstanceIds = debug.Players.SelectMany(player => player.SealSlots)
            .Select(slot => slot.CardInstanceId!)
            .ToArray();
        var playerOne = session.GetPlayerSnapshot("player_1");
        var playerTwo = session.GetPlayerSnapshot("player_2");
        Equal(ContractSchemas.DomainBoardProjectionWithSeals, playerOne.BoardSummary.GetProperty("schema_version").GetString(), "Seal board projection schema is invalid.");
        Equal(playerOne.BoardSummary.GetRawText(), playerTwo.BoardSummary.GetRawText(), "Public Seal projection differs by viewer.");
        foreach (var projectedPlayer in playerOne.BoardSummary.GetProperty("players").EnumerateArray())
        {
            foreach (var seal in projectedPlayer.GetProperty("seals").EnumerateArray())
            {
                var propertyNames = seal.EnumerateObject().Select(property => property.Name).ToHashSet(StringComparer.Ordinal);
                True(propertyNames.SetEquals(new[] { "seal_slot_id", "owner_player_id", "lane_index", "status" }), "Standing Seal projection exposed a hidden identity field.");
            }
        }

        var publicBoardJson = playerOne.BoardSummary.GetRawText();
        False(hiddenInstanceIds.Any(publicBoardJson.Contains), "Public Seal projection leaked an authoritative card_instance_id.");
        True(debug.Players.SelectMany(player => player.SealSlots).All(slot => slot.CardInstanceId is not null), "Debug projection lost authoritative Seal identities.");
        var publicEvents = JsonSerializer.Serialize(session.GetEvents("player_1"));
        False(hiddenInstanceIds.Any(publicEvents.Contains), "Setup events leaked a hidden Seal card_instance_id.");
        False(publicEvents.Contains("\"card_id\"", StringComparison.Ordinal), "Setup events leaked a hidden Seal card_id field.");
    }

    internal static void SetupAndSealInvariantsRejectCorruption()
    {
        using var package = CreatePackage();
        var pending = CreateSession(package, seed: 109, matchId: "pending-invariant");
        State(pending).Setup!.CurrentProphecyPlayerId = "player_2";
        AssertInvariantRejected(State(pending), "Pending canonical setup", "Invalid current Prophecy player was accepted.");

        var missing = CompleteSetup(package, seed: 110, matchId: "missing-seal");
        State(missing).GetPlayer("player_1").SealSlots.RemoveAt(0);
        AssertInvariantRejected(State(missing), "exactly six Seal", "Five-slot Seal state was accepted.");

        var duplicateLane = CompleteSetup(package, seed: 111, matchId: "duplicate-lane");
        var duplicatePlayer = State(duplicateLane).GetPlayer("player_1");
        duplicatePlayer.SealSlots.RemoveAt(1);
        duplicatePlayer.SealSlots.Add(new SealSlotState
        {
            SealSlotId = "seal:player_1:02",
            OwnerPlayerId = "player_1",
            LaneIndex = 0,
            Status = "broken",
            CardInstanceId = null,
        });
        AssertInvariantRejected(State(duplicateLane), "lane indices", "Duplicate Seal lane was accepted.");

        var visible = CompleteSetup(package, seed: 112, matchId: "visible-seal");
        var visibleSlot = State(visible).GetPlayer("player_1").SealSlots[0];
        State(visible).GetCardInstance(visibleSlot.CardInstanceId!).Visibility = "owner_only";
        AssertInvariantRejected(State(visible), "standing Seal", "Owner-visible standing Seal identity was accepted.");

        var crossZone = CompleteSetup(package, seed: 113, matchId: "cross-zone-seal");
        var crossPlayer = State(crossZone).GetPlayer("player_1");
        crossPlayer.DeckCardInstanceIds.Add(crossPlayer.SealSlots[0].CardInstanceId!);
        AssertInvariantRejected(State(crossZone), "multiple zones", "Seal card retained Deck membership.");
    }

    internal static void BrokenSealShapeIsRepresentableWithoutHp()
    {
        using var package = CreatePackage();
        var session = CompleteSetup(package, seed: 114, matchId: "broken-seal-shape");
        var state = State(session);
        var player = state.GetPlayer("player_1");
        var slot = player.SealSlots[0];
        var card = state.GetCardInstance(slot.CardInstanceId!);
        slot.Status = "broken";
        slot.CardInstanceId = null;
        card.Zone = "hand";
        card.ZoneIndex = player.HandCardInstanceIds.Count;
        card.Visibility = "owner_only";
        card.ZoneSequence += 1;
        player.HandCardInstanceIds.Add(card.CardInstanceId);
        EngineSession.ValidateState(state);
        Equal(0, card.DamageMarked, "Seal lifecycle introduced HP/damage state.");
    }

    internal static void HistoricalV2FixtureRemainsExplicitlyCompatible()
    {
        var fixture = RuntimeComparisonFixture.Load(FixtureLocator.LocateCanonicalFixture());
        Equal(ContractSchemas.CreateMatchRequest, fixture.CreateMatchRequest().SchemaVersion, "Historical fixture schema changed.");
        var session = new EngineSession();
        True(session.CreateMatch(fixture.CreateMatchRequest()).Accepted, "Historical one-card fixture no longer creates a match.");
        var debug = session.GetDebugSnapshot();
        Equal(ContractSchemas.DebugSnapshot, debug.SchemaVersion, "Historical debug schema changed.");
        False(JsonSerializer.Serialize(debug).Contains("\"seal_slots\"", StringComparison.Ordinal), "Historical debug v4 JSON was silently extended with Seal state.");
        True(debug.Players.All(player => player.HandCardInstanceIds.Length == 1), "Historical starting hand changed.");
        True(debug.Players.All(player => player.SealSlots.IsDefaultOrEmpty), "Historical fixture was forced into canonical Seal setup.");
        Equal(ContractSchemas.DomainBoardProjection, session.GetPlayerSnapshot("player_1").BoardSummary.GetProperty("schema_version").GetString(), "Historical fixture was forced onto board schema v2.");
        True(session.ListLegalActions("player_1").Actions.Any(item => item.ActionType == "advance_phase"), "Historical phase fixture was setup-gated.");
    }

    internal static void CanonicalSetupContractRejectsNonCanonicalShapes()
    {
        using var package = CreatePackage();
        var missingMode = new EngineSession().CreateMatch(CanonicalRequest(package, seed: 115) with { SetupMode = null });
        False(missingMode.Accepted, "Canonical request without setup_mode was accepted.");
        Equal("CREATE_MATCH_SETUP_MODE_INVALID", missingMode.Diagnostics.Single().Code, "Missing setup mode diagnostic is invalid.");

        var wrongHand = new EngineSession().CreateMatch(CanonicalRequest(package, seed: 115) with { StartingHandSize = 4 });
        False(wrongHand.Accepted, "Canonical request with a four-card hand was accepted.");
        Equal("STARTING_HAND_SIZE_INVALID", wrongHand.Diagnostics.Single().Code, "Canonical hand-size diagnostic is invalid.");

        var v2Mode = new EngineSession().CreateMatch(CanonicalRequest(package, seed: 115) with
        {
            SchemaVersion = ContractSchemas.CreateMatchRequest,
            SetupMode = "canonical",
        });
        False(v2Mode.Accepted, "Historical v2 request accepted a canonical setup mode extension.");
        Equal("CREATE_MATCH_SETUP_MODE_INVALID", v2Mode.Diagnostics.Single().Code, "Historical setup-mode diagnostic is invalid.");
    }

    internal static void CompletedSetupProtocolIsRepeatedRunDeterministic()
    {
        using var package = CreatePackage();
        var first = CreateSession(package, seed: 116, matchId: "repeated-setup");
        var second = CreateSession(package, seed: 116, matchId: "repeated-setup");
        foreach (var playerId in new[] { "player_1", "player_2" })
        {
            var firstSelection = Player(first.GetDebugSnapshot(), playerId).HandCardInstanceIds.Take(3).ToArray();
            var secondSelection = Player(second.GetDebugSnapshot(), playerId).HandCardInstanceIds.Take(3).ToArray();
            SequenceEqual(firstSelection, secondSelection, "Repeated setup diverged before Prophecy.");
            True(SubmitProphecy(first, playerId, firstSelection, $"repeat-{playerId}").Accepted, "First repeated Prophecy failed.");
            True(SubmitProphecy(second, playerId, secondSelection, $"repeat-{playerId}").Accepted, "Second repeated Prophecy failed.");
        }

        Equal(Fingerprint(first), Fingerprint(second), "Repeated canonical setup is not deterministic.");
    }

    private static ProductionEngineTests.TemporaryRuntimePackage CreatePackage()
    {
        var cardIds = Enumerable.Range(1, 40).Select(index => $"SETUP-CARD-{index:000}").ToArray();
        var cardRecords = cardIds.Select(cardId => JsonSerializer.Serialize(new Dictionary<string, object?>
        {
            ["card_id"] = cardId,
            ["magnitude"] = 0,
            ["aura_cost"] = 0,
            ["realm"] = "ignis",
            ["card_type"] = "entity",
        })).ToArray();
        return ProductionEngineTests.TemporaryRuntimePackage.Create(cardRecords, cardIds);
    }

    private static EngineSession CreateSession(
        ProductionEngineTests.TemporaryRuntimePackage package,
        int seed,
        string matchId = "setup-seal-match",
        string startingPlayerId = "player_1")
    {
        var session = new EngineSession();
        var response = session.CreateMatch(CanonicalRequest(package, seed, matchId, startingPlayerId));
        True(response.Accepted, response.Diagnostics.FirstOrDefault()?.DeveloperMessage ?? "Canonical CreateMatch failed.");
        return session;
    }

    private static CreateMatchRequest CanonicalRequest(
        ProductionEngineTests.TemporaryRuntimePackage package,
        int seed,
        string matchId = "setup-seal-match",
        string startingPlayerId = "player_1") => new(
            ContractSchemas.CanonicalCreateMatchRequest,
            matchId,
            seed,
            ImmutableArray.Create(
                new PlayerSetup("player_1", "test-deck"),
                new PlayerSetup("player_2", "test-deck")),
            StartingHandSize: 5,
            startingPlayerId,
            package.Source,
            CanonicalData: null,
            SetupMode: "canonical");

    private static EngineSession CompleteSetup(
        ProductionEngineTests.TemporaryRuntimePackage package,
        int seed,
        string matchId)
    {
        var session = CreateSession(package, seed, matchId);
        True(SubmitProphecy(session, "player_1", [], $"{matchId}-one").Accepted, "First setup decision failed.");
        True(SubmitProphecy(session, "player_2", [], $"{matchId}-two").Accepted, "Second setup decision failed.");
        return session;
    }

    private static ActionResponse SubmitProphecy(
        EngineSession session,
        string playerId,
        IReadOnlyList<string> cardInstanceIds,
        string requestId)
    {
        var action = EnabledProphecy(session, playerId);
        return session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            requestId,
            session.GetDebugSnapshot().MatchId,
            playerId,
            session.GetDebugSnapshot().StateVersion,
            action.ActionId,
            action.ActionType,
            ProphecyPayload(cardInstanceIds)));
    }

    private static LegalAction EnabledProphecy(EngineSession session, string playerId) =>
        session.ListLegalActions(playerId).Actions.Single(item => item.ActionType == "resolve_prophecy");

    private static JsonElement ProphecyPayload(IReadOnlyList<string> cardInstanceIds) =>
        ContractJsonValue.From(new Dictionary<string, object?>
        {
            ["card_instance_ids"] = cardInstanceIds,
        });

    private static void AssertRejectedSelection(
        EngineSession session,
        IReadOnlyList<string> selectedIds,
        string expectedCode)
    {
        var before = Fingerprint(session);
        var response = SubmitProphecy(session, "player_1", selectedIds, $"reject-{expectedCode}");
        False(response.Accepted, $"Invalid Prophecy selection was accepted: {expectedCode}");
        Equal(expectedCode, response.Diagnostics.Single().Code, "Invalid Prophecy selection diagnostic is wrong.");
        Equal(before, Fingerprint(session), "Rejected Prophecy selection mutated state.");
    }

    private static MatchState State(EngineSession session) =>
        (MatchState)(typeof(EngineSession)
            .GetField("_state", BindingFlags.Instance | BindingFlags.NonPublic)!
            .GetValue(session)
            ?? throw new InvalidOperationException("Engine state is unavailable."));

    private static DebugPlayerSnapshot Player(DebugSnapshot snapshot, string playerId) =>
        snapshot.Players.Single(player => player.PlayerId == playerId);

    private static string CardOrder(EngineSession session) => string.Join(
        "|",
        session.GetDebugSnapshot().Players.SelectMany(player =>
            player.HandCardInstanceIds.Concat(player.DeckCardInstanceIds)));

    private static string Fingerprint(EngineSession session) =>
        JsonSerializer.Serialize(session.GetDebugSnapshot());

    private static void AssertInvariantRejected(
        MatchState state,
        string expectedMessagePart,
        string message)
    {
        try
        {
            EngineSession.ValidateState(state);
        }
        catch (EngineStateException exception)
        {
            True(exception.Message.Contains(expectedMessagePart, StringComparison.OrdinalIgnoreCase), $"{message} Actual: {exception.Message}");
            return;
        }

        throw new InvalidOperationException(message);
    }

    private static void True(bool value, string message)
    {
        if (!value)
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void False(bool value, string message) => True(!value, message);

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected={expected}; Actual={actual}");
        }
    }

    private static void NotEqual<T>(T unexpected, T actual, string message)
    {
        if (EqualityComparer<T>.Default.Equals(unexpected, actual))
        {
            throw new InvalidOperationException($"{message} Unexpected={unexpected}");
        }
    }

    private static void SequenceEqual<T>(
        IEnumerable<T> expected,
        IEnumerable<T> actual,
        string message)
    {
        if (!expected.SequenceEqual(actual))
        {
            throw new InvalidOperationException(message);
        }
    }
}
