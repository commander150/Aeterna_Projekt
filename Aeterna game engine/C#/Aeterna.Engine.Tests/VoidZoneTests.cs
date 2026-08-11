using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Headless;
using Aeterna.Engine.State;

internal static class VoidZoneTests
{
    internal static void InitialStateAndSerializedContractsUseVoid()
    {
        var fixture = RuntimeComparisonFixture.Load(FixtureLocator.LocateCanonicalFixture());
        var session = new EngineSession();
        var response = session.CreateMatch(fixture.CreateMatchRequest());
        True(response.Accepted, "Canonical fixture match creation failed.");

        var debug = session.GetDebugSnapshot();
        Equal("aeterna-debug-match-snapshot-v3", debug.SchemaVersion, "Debug schema was not bumped.");
        True(debug.Players.All(player => player.VoidCardInstanceIds.IsEmpty), "Initial Void must be empty.");
        var debugJson = JsonSerializer.Serialize(debug);
        True(debugJson.Contains("\"VoidCardInstanceIds\"", StringComparison.Ordinal), "Debug output does not expose Void.");
        False(debugJson.Contains("DiscardCardInstanceIds", StringComparison.Ordinal), "Debug output exposes the retired discard zone field.");

        var snapshot = session.GetPlayerSnapshot("player_1");
        Equal("engine-player-visible-snapshot-v3", snapshot.SchemaVersion, "Player snapshot schema was not bumped.");
        foreach (var player in snapshot.Players)
        {
            Equal("void", player.Void.Zone, "Player snapshot Void zone token is invalid.");
            Equal("public", player.Void.VisibilityMode, "Void must be public.");
            False(player.Void.Redacted, "Void must not be redacted.");
            Equal(0, player.Void.Count, "Initial projected Void must be empty.");
            True(player.Void.Objects.IsEmpty, "Initial projected Void objects must be empty.");
        }

        var snapshotJson = JsonSerializer.Serialize(snapshot);
        True(snapshotJson.Contains("\"void\"", StringComparison.Ordinal), "Player snapshot does not expose Void.");
        False(snapshotJson.Contains("\"discard\"", StringComparison.Ordinal), "Player snapshot exposes the retired discard zone.");
    }

    internal static void VoidListAndRegistryParityIsAccepted()
    {
        var state = CreateState();
        var player = state.GetPlayer("player_1");
        var cardInstanceId = AddVoidCard(state, player);

        EngineSession.ValidateState(state);

        var card = state.GetCardInstance(cardInstanceId);
        Equal("void", card.Zone, "Void card registry zone is invalid.");
        Equal(0, card.ZoneIndex, "Void card zone index is invalid.");
        Equal("public", card.Visibility, "Void card visibility is invalid.");
        Equal<string?>(null, card.ActivityState, "Void card activity state must be null.");
        Equal<DomainRow?>(null, card.DomainRow, "Void card retained a Domain row.");
        Equal<int?>(null, card.DomainLaneIndex, "Void card retained a Domain lane.");
        Equal<int?>(null, card.EnteredDomainTurnNumber, "Void card retained a Domain entry turn.");
    }

    internal static void VoidParityAndCrossZoneViolationsAreRejected()
    {
        var wrongRegistryZone = CreateState();
        var wrongPlayer = wrongRegistryZone.GetPlayer("player_1");
        var wrongCardId = AddVoidCard(wrongRegistryZone, wrongPlayer);
        wrongRegistryZone.GetCardInstance(wrongCardId).Zone = "hand";
        AssertInvariantRejected(wrongRegistryZone, "Void card zone must be void", "Void list accepted a non-void registry zone.");

        var unlistedVoid = CreateState();
        _ = AddVoidCard(unlistedVoid, unlistedVoid.GetPlayer("player_1"), addToList: false);
        AssertInvariantRejected(unlistedVoid, "registry and zones disagree", "Unlisted Void registry card was accepted.");

        var duplicate = CreateState();
        var duplicatePlayer = duplicate.GetPlayer("player_1");
        var duplicateCardId = AddVoidCard(duplicate, duplicatePlayer);
        duplicatePlayer.DeckCardInstanceIds.Add(duplicateCardId);
        AssertInvariantRejected(duplicate, "multiple zones", "Deck/Void duplicate membership was accepted.");
    }

    internal static void RetiredDiscardZoneTokenIsRejected()
    {
        var state = CreateState();
        var player = state.GetPlayer("player_1");
        var cardInstanceId = AddVoidCard(state, player);
        state.GetCardInstance(cardInstanceId).Zone = "discard";

        AssertInvariantRejected(
            state,
            "Void card zone must be void",
            "The retired discard destination-zone token was accepted.");
    }

    private static MatchState CreateState()
    {
        var state = new MatchState
        {
            MatchId = "void-zone-test-match",
            Seed = 1,
            RuntimePackageId = "void-zone-test-package",
            StateVersion = 0,
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        state.Players.Add(new PlayerState
        {
            PlayerId = "player_1",
            DeckId = "void-zone-test-deck-1",
        });
        state.Players.Add(new PlayerState
        {
            PlayerId = "player_2",
            DeckId = "void-zone-test-deck-2",
        });
        return state;
    }

    private static string AddVoidCard(MatchState state, PlayerState player, bool addToList = true)
    {
        var cardInstanceId = $"ci_void_{state.CardInstances.Count + 1:0000}";
        state.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = $"VOID-CARD-{state.CardInstances.Count + 1:0000}",
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "void",
            ZoneIndex = 0,
            Visibility = "public",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "void",
            ActivityState = null,
            DomainRow = null,
            DomainLaneIndex = null,
            EnteredDomainTurnNumber = null,
        });
        if (addToList)
        {
            player.VoidCardInstanceIds.Add(cardInstanceId);
        }

        return cardInstanceId;
    }

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

    private static void False(bool value, string message) => True(!value, message);
}
