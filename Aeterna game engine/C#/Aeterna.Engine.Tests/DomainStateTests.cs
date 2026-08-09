using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.State;

internal static class DomainStateTests
{
    internal static void ExplicitSixBySixTopologyIsInitialized()
    {
        var state = CreateState();
        foreach (var player in state.Players)
        {
            Equal(6, player.Domain.HorizonCardInstanceIds.Count, "Horizon must contain six slots.");
            Equal(6, player.Domain.ZenithCardInstanceIds.Count, "Zenith must contain six slots.");
            True(
                player.Domain.HorizonCardInstanceIds.All(item => item is null),
                "Initial Horizon must be empty.");
            True(
                player.Domain.ZenithCardInstanceIds.All(item => item is null),
                "Initial Zenith must be empty.");
        }

        EngineSession.ValidateState(state);
    }

    internal static void StructuralPlacementEnforcesSingleOccupancy()
    {
        var state = CreateState();
        var player = state.GetPlayer("player_1");
        var cardInstanceId = AddDomainCard(state, player, DomainRow.Horizon, laneIndex: 2);

        Equal(
            false,
            player.Domain.TryOccupy(DomainRow.Zenith, 2, cardInstanceId),
            "One card instance was accepted in two Domain slots.");
        Equal(
            false,
            player.Domain.TryOccupy(DomainRow.Horizon, 2, "ci_other"),
            "An occupied Domain slot accepted another card instance.");
        Equal(cardInstanceId, player.Domain.HorizonCardInstanceIds[2], "Occupied slot changed.");
        Equal(null, player.Domain.ZenithCardInstanceIds[2], "Rejected placement mutated Zenith.");
        AssertThrows<ArgumentOutOfRangeException>(
            () => player.Domain.TryOccupy(DomainRow.Horizon, 6, "ci_other"),
            "Out-of-range Domain placement was accepted.");
        EngineSession.ValidateState(state);
    }

    internal static void PublicProjectionIsCompleteAndViewerIndependent()
    {
        var state = CreateState();
        var playerOne = state.GetPlayer("player_1");
        var horizonCardId = AddDomainCard(
            state,
            playerOne,
            DomainRow.Horizon,
            laneIndex: 1,
            activityState: "active");
        var zenithCardId = AddDomainCard(
            state,
            playerOne,
            DomainRow.Zenith,
            laneIndex: 4,
            activityState: "exhausted");
        var session = new EngineSession(state);

        var playerOneBoard = session.GetPlayerSnapshot("player_1").BoardSummary;
        var playerTwoBoard = session.GetPlayerSnapshot("player_2").BoardSummary;
        Equal(
            playerOneBoard.GetRawText(),
            playerTwoBoard.GetRawText(),
            "Public Domain projection differs by viewer.");
        Equal(
            ContractSchemas.DomainBoardProjection,
            playerOneBoard.GetProperty("schema_version").GetString(),
            "Domain board schema is invalid.");
        Equal("dominion", playerOneBoard.GetProperty("zone").GetString(), "Domain zone is invalid.");
        Equal("public", playerOneBoard.GetProperty("visibility_mode").GetString(), "Domain visibility is invalid.");
        Equal(6, playerOneBoard.GetProperty("lane_count").GetInt32(), "Domain lane count is invalid.");

        var projectedPlayer = playerOneBoard.GetProperty("players")
            .EnumerateArray()
            .Single(item => item.GetProperty("player_id").GetString() == "player_1");
        Equal(6, projectedPlayer.GetProperty("horizon").GetArrayLength(), "Projected Horizon length is invalid.");
        Equal(6, projectedPlayer.GetProperty("zenith").GetArrayLength(), "Projected Zenith length is invalid.");
        Equal(2, projectedPlayer.GetProperty("occupied_slot_count").GetInt32(), "Occupied count is invalid.");
        Equal(10, projectedPlayer.GetProperty("empty_slot_count").GetInt32(), "Empty count is invalid.");

        var horizon = projectedPlayer.GetProperty("horizon")[1];
        Equal(true, horizon.GetProperty("occupied").GetBoolean(), "Horizon occupancy was not projected.");
        Equal("horizon", horizon.GetProperty("row").GetString(), "Horizon row token is invalid.");
        Equal(1, horizon.GetProperty("lane_index").GetInt32(), "Horizon lane is invalid.");
        Equal(
            horizonCardId,
            horizon.GetProperty("occupant").GetProperty("card_instance_id").GetString(),
            "Horizon card instance identity is missing.");
        Equal(
            "active",
            horizon.GetProperty("occupant").GetProperty("activity_state").GetString(),
            "Horizon activity state is invalid.");
        Equal(
            state.TurnNumber,
            horizon.GetProperty("occupant").GetProperty("entered_domain_turn_number").GetInt32(),
            "Horizon entry turn is invalid.");

        var zenith = projectedPlayer.GetProperty("zenith")[4];
        Equal(
            zenithCardId,
            zenith.GetProperty("occupant").GetProperty("card_instance_id").GetString(),
            "Zenith card instance identity is missing.");
        Equal(
            "exhausted",
            zenith.GetProperty("occupant").GetProperty("activity_state").GetString(),
            "Zenith activity state is invalid.");
    }

    internal static void DebugProjectionTracksCoordinatesAndEntryTurn()
    {
        var state = CreateState();
        var player = state.GetPlayer("player_1");
        var cardInstanceId = AddDomainCard(state, player, DomainRow.Horizon, laneIndex: 3);
        var session = new EngineSession(state);

        var debug = session.GetDebugSnapshot();
        var debugPlayer = debug.Players.Single(item => item.PlayerId == player.PlayerId);
        Equal(6, debugPlayer.HorizonCardInstanceIds.Length, "Debug Horizon length is invalid.");
        Equal(6, debugPlayer.ZenithCardInstanceIds.Length, "Debug Zenith length is invalid.");
        Equal(cardInstanceId, debugPlayer.HorizonCardInstanceIds[3], "Debug occupancy is invalid.");
        var card = debug.CardInstances.Single(item => item.CardInstanceId == cardInstanceId);
        Equal("dominion", card.Zone, "Debug card zone is invalid.");
        Equal(-1, card.ZoneIndex, "Debug Domain zone index sentinel is invalid.");
        Equal("horizon", card.DomainRow, "Debug Domain row is invalid.");
        Equal(3, card.DomainLaneIndex, "Debug Domain lane is invalid.");
        Equal(state.TurnNumber, card.EnteredDomainTurnNumber, "Debug Domain entry turn is invalid.");
    }

    internal static void ProjectionIsDefensiveAndNonMutating()
    {
        var state = CreateState();
        var session = new EngineSession(state);
        var before = JsonSerializer.Serialize(session.GetDebugSnapshot());
        var first = session.GetPlayerSnapshot("player_1");
        Equal(before, JsonSerializer.Serialize(session.GetDebugSnapshot()), "Domain projection mutated state.");

        AddDomainCard(state, state.GetPlayer("player_1"), DomainRow.Horizon, laneIndex: 0);
        EngineSession.ValidateState(state);
        var second = session.GetPlayerSnapshot("player_1");
        var firstPlayer = FindBoardPlayer(first.BoardSummary, "player_1");
        var secondPlayer = FindBoardPlayer(second.BoardSummary, "player_1");
        Equal(0, firstPlayer.GetProperty("occupied_slot_count").GetInt32(), "Earlier projection changed.");
        Equal(1, secondPlayer.GetProperty("occupied_slot_count").GetInt32(), "Fresh projection is stale.");
        Equal(0, state.StateVersion, "Projection or synthetic setup changed state_version.");
        Equal(0, state.Events.Count, "Projection or synthetic setup emitted an event.");
    }

    internal static void RowLengthInvariantIsEnforced()
    {
        var state = CreateState();
        state.GetPlayer("player_1").Domain.HorizonCardInstanceIds.RemoveAt(0);
        AssertInvariantRejected(state, "exactly six slots", "Five-slot Horizon was accepted.");
    }

    internal static void DuplicateAndCrossZoneInvariantsAreEnforced()
    {
        var duplicate = CreateState();
        var duplicatePlayer = duplicate.GetPlayer("player_1");
        var duplicateCardId = AddDomainCard(duplicate, duplicatePlayer, DomainRow.Horizon, 0);
        duplicatePlayer.Domain.ZenithCardInstanceIds[0] = duplicateCardId;
        AssertInvariantRejected(duplicate, "multiple zones or Domain slots", "Duplicate Domain occupancy was accepted.");

        var crossZone = CreateState();
        var crossZonePlayer = crossZone.GetPlayer("player_1");
        var crossZoneCardId = AddDomainCard(crossZone, crossZonePlayer, DomainRow.Horizon, 0);
        var crossZoneCard = crossZone.GetCardInstance(crossZoneCardId);
        crossZoneCard.Zone = "hand";
        crossZoneCard.ZoneIndex = 0;
        crossZoneCard.Visibility = "owner_only";
        crossZoneCard.ActivityState = null;
        crossZonePlayer.HandCardInstanceIds.Add(crossZoneCardId);
        AssertInvariantRejected(crossZone, "multiple zones or Domain slots", "Cross-zone Domain card was accepted.");
    }

    internal static void RegistryAndOccupancyInvariantsAreEnforced()
    {
        var unknown = CreateState();
        unknown.GetPlayer("player_1").Domain.HorizonCardInstanceIds[0] = "ci_unknown";
        AssertInvariantRejected(unknown, "unknown card instance", "Unknown Domain occupant was accepted.");

        var unlisted = CreateState();
        AddUnlistedDomainCard(unlisted, unlisted.GetPlayer("player_1"));
        AssertInvariantRejected(unlisted, "registry and zones disagree", "Unlisted Domain registry card was accepted.");
    }

    internal static void AuthorityVisibilityAndActivityInvariantsAreEnforced()
    {
        var wrongController = CreateState();
        _ = AddDomainCard(
            wrongController,
            wrongController.GetPlayer("player_1"),
            DomainRow.Horizon,
            0,
            controllerPlayerId: "player_2");
        AssertInvariantRejected(wrongController, "controller", "Wrong Domain controller was accepted.");

        var unknownOwner = CreateState();
        _ = AddDomainCard(
            unknownOwner,
            unknownOwner.GetPlayer("player_1"),
            DomainRow.Horizon,
            0,
            ownerPlayerId: "player_unknown");
        AssertInvariantRejected(unknownOwner, "owner", "Unknown Domain owner was accepted.");

        var hidden = CreateState();
        var hiddenCard = AddDomainCard(hidden, hidden.GetPlayer("player_1"), DomainRow.Horizon, 0);
        hidden.GetCardInstance(hiddenCard).Visibility = "owner_only";
        AssertInvariantRejected(hidden, "visibility", "Hidden Domain card was accepted.");

        var badActivity = CreateState();
        var activityCard = AddDomainCard(badActivity, badActivity.GetPlayer("player_1"), DomainRow.Horizon, 0);
        badActivity.GetCardInstance(activityCard).ActivityState = "ready";
        AssertInvariantRejected(badActivity, "activity state", "Unknown Domain activity state was accepted.");
    }

    internal static void CoordinateAndEntryInvariantsAreEnforced()
    {
        var wrongRow = CreateState();
        var rowCard = AddDomainCard(wrongRow, wrongRow.GetPlayer("player_1"), DomainRow.Horizon, 0);
        wrongRow.GetCardInstance(rowCard).DomainRow = DomainRow.Zenith;
        AssertInvariantRejected(wrongRow, "row and lane", "Wrong Domain row coordinate was accepted.");

        var wrongLane = CreateState();
        var laneCard = AddDomainCard(wrongLane, wrongLane.GetPlayer("player_1"), DomainRow.Horizon, 0);
        wrongLane.GetCardInstance(laneCard).DomainLaneIndex = 5;
        AssertInvariantRejected(wrongLane, "row and lane", "Wrong Domain lane coordinate was accepted.");

        var futureEntry = CreateState();
        var entryCard = AddDomainCard(futureEntry, futureEntry.GetPlayer("player_1"), DomainRow.Horizon, 0);
        futureEntry.GetCardInstance(entryCard).EnteredDomainTurnNumber = futureEntry.TurnNumber + 1;
        AssertInvariantRejected(futureEntry, "cannot be in the future", "Future Domain entry turn was accepted.");
    }

    internal static void NonDomainCoordinatesAreRejected()
    {
        var state = CreateState();
        var player = state.GetPlayer("player_1");
        var cardInstanceId = AddHandCard(state, player);
        var card = state.GetCardInstance(cardInstanceId);
        card.DomainRow = DomainRow.Horizon;
        card.DomainLaneIndex = 0;
        card.EnteredDomainTurnNumber = state.TurnNumber;
        AssertInvariantRejected(state, "Non-Domain card", "Hand card retained Domain coordinates.");
    }

    internal static void DomainZoneIndexSentinelIsEnforced()
    {
        var state = CreateState();
        var cardInstanceId = AddDomainCard(
            state,
            state.GetPlayer("player_1"),
            DomainRow.Horizon,
            0);
        state.GetCardInstance(cardInstanceId).ZoneIndex = 0;
        AssertInvariantRejected(state, "sentinel -1", "Domain lane was ambiguously stored in zone_index.");
    }

    private static MatchState CreateState()
    {
        var state = new MatchState
        {
            MatchId = "domain-state-test-match",
            Seed = 1,
            RuntimePackageId = "domain-state-test-package",
            StateVersion = 0,
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        state.Players.Add(new PlayerState
        {
            PlayerId = "player_1",
            DeckId = "test-deck-player-1",
        });
        state.Players.Add(new PlayerState
        {
            PlayerId = "player_2",
            DeckId = "test-deck-player-2",
        });
        return state;
    }

    private static string AddDomainCard(
        MatchState state,
        PlayerState domainPlayer,
        DomainRow row,
        int laneIndex,
        string activityState = "active",
        string? controllerPlayerId = null,
        string? ownerPlayerId = null)
    {
        var cardInstanceId = $"ci_domain_{state.CardInstances.Count + 1:0000}";
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = $"DOMAIN-CARD-{state.CardInstances.Count + 1:0000}",
            OwnerPlayerId = ownerPlayerId ?? domainPlayer.PlayerId,
            ControllerPlayerId = controllerPlayerId ?? domainPlayer.PlayerId,
            Zone = "dominion",
            ZoneIndex = -1,
            Visibility = "public",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 2,
            InitialZone = "hand",
            ActivityState = activityState,
            DomainRow = row,
            DomainLaneIndex = laneIndex,
            EnteredDomainTurnNumber = state.TurnNumber,
        });
        True(
            domainPlayer.Domain.TryOccupy(row, laneIndex, cardInstanceId),
            "Synthetic Domain setup could not occupy its requested slot.");
        return cardInstanceId;
    }

    private static void AddUnlistedDomainCard(MatchState state, PlayerState player)
    {
        const string cardInstanceId = "ci_unlisted_domain";
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = "UNLISTED-DOMAIN-CARD",
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "dominion",
            ZoneIndex = -1,
            Visibility = "public",
            CreatedSequence = 1,
            ZoneSequence = 2,
            InitialZone = "hand",
            ActivityState = "active",
            DomainRow = DomainRow.Horizon,
            DomainLaneIndex = 0,
            EnteredDomainTurnNumber = state.TurnNumber,
        });
    }

    private static string AddHandCard(MatchState state, PlayerState player)
    {
        var cardInstanceId = $"ci_hand_{state.CardInstances.Count + 1:0000}";
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = $"HAND-CARD-{state.CardInstances.Count + 1:0000}",
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "hand",
            ZoneIndex = player.HandCardInstanceIds.Count,
            Visibility = "owner_only",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "hand",
            ActivityState = null,
        });
        player.HandCardInstanceIds.Add(cardInstanceId);
        return cardInstanceId;
    }

    private static JsonElement FindBoardPlayer(JsonElement board, string playerId) => board
        .GetProperty("players")
        .EnumerateArray()
        .Single(item => item.GetProperty("player_id").GetString() == playerId);

    private static void AssertInvariantRejected(
        MatchState state,
        string expectedMessageFragment,
        string message)
    {
        try
        {
            EngineSession.ValidateState(state);
        }
        catch (EngineStateException exception)
        {
            True(
                exception.Message.Contains(expectedMessageFragment, StringComparison.OrdinalIgnoreCase),
                $"{message} Unexpected invariant: {exception.Message}");
            return;
        }

        throw new InvalidOperationException(message);
    }

    private static void AssertThrows<TException>(Action action, string message)
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

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected={expected}; Actual={actual}");
        }
    }

    private static void True(bool value, string message)
    {
        if (!value)
        {
            throw new InvalidOperationException(message);
        }
    }
}
