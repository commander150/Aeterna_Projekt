using System.Collections.Immutable;
using Aeterna.Engine.Runtime;

internal static class CanonicalCardCatalogTests
{
    internal static void TypedStatsAndNullContractMaterializeDeterministically()
    {
        var first = CanonicalCardMaterializer.Materialize(CanonicalAbilityCatalogTests.CreatePackage());
        var second = CanonicalCardMaterializer.Materialize(CanonicalAbilityCatalogTests.CreatePackage());
        var entity = first.DefinitionsById["IGN-LAN-003"];
        Equal("entity", entity.CardType, "Entity canonical card type was not materialized.");
        Equal(2, entity.PrintedAtk, "Entity printed ATK was not materialized.");
        Equal(2, entity.PrintedHp, "Entity printed HP was not materialized.");
        var spell = first.DefinitionsById["AQU-ART-044"];
        Equal("spell", spell.CardType, "Spell canonical card type was not materialized.");
        Equal(null, spell.PrintedAtk, "Non-Entity ATK must remain canonical null.");
        Equal(null, spell.PrintedHp, "Non-Entity HP must remain canonical null.");
        SequenceEqual(
            first.Definitions.Select(card => card.CardId),
            second.Definitions.Select(card => card.CardId),
            "Canonical card materialization order is not deterministic.");
        Equal(StringComparer.Ordinal, first.DefinitionsById.KeyComparer, "Canonical card lookup is not ordinal.");
    }

    internal static void DuplicateAndMalformedCardsAreRejected()
    {
        var package = CanonicalAbilityCatalogTests.CreatePackage();
        var cards = package.Tables[CanonicalAbilityTableIds.Cards];
        var duplicateTable = cards with { Records = cards.Records.Add(cards.Records[0]) };
        ThrowsCode(
            "CANONICAL_CARD_DUPLICATE_ID",
            () => CanonicalCardMaterializer.Materialize(package with
            {
                Tables = package.Tables.SetItem(CanonicalAbilityTableIds.Cards, duplicateTable),
            }));
        ThrowsCode(
            "CANONICAL_CARD_FIELD_INVALID",
            () => CanonicalCardMaterializer.Materialize(CanonicalAbilityCatalogTests.SetField(
                package,
                CanonicalAbilityTableIds.Cards,
                "IGN-LAN-003",
                "hp",
                "2")));
        ThrowsCode(
            "CANONICAL_CARD_FIELD_INVALID",
            () => CanonicalCardMaterializer.Materialize(CanonicalAbilityCatalogTests.SetField(
                package,
                CanonicalAbilityTableIds.Cards,
                "AQU-ART-044",
                "hp",
                2)));
        ThrowsCode(
            "CANONICAL_CARD_VOCABULARY_UNKNOWN",
            () => CanonicalCardMaterializer.Materialize(CanonicalAbilityCatalogTests.SetField(
                package,
                CanonicalAbilityTableIds.Cards,
                "IGN-LAN-003",
                "realm_id",
                "unknown_realm")));
    }

    internal static void LegacyOverlapMatchesAndMismatchRejects()
    {
        var cards = CanonicalCardMaterializer.Materialize(CanonicalAbilityCatalogTests.CreatePackage());
        var matching = Runtime("IGN-HAM-005", "entity", "ignis", 0, 0);
        cards.ValidateRuntimeOverlap(matching);
        cards.ValidateRuntimeOverlap(Runtime("AQU-ART-044", "incantation", "aqua", 5, 4));

        ThrowsCode(
            "CANONICAL_RUNTIME_CARD_OVERLAP_MISMATCH",
            () => cards.ValidateRuntimeOverlap(Runtime("IGN-HAM-005", "entity", "aqua", 0, 0)));
        ThrowsCode(
            "CANONICAL_RUNTIME_CARD_DEFINITION_MISSING",
            () => cards.ValidateRuntimeOverlap(Runtime("UNKNOWN-CARD", "entity", "ignis", 0, 0)));
    }

    private static RuntimePackageCatalog Runtime(
        string cardId,
        string cardType,
        string realm,
        int magnitude,
        int auraCost)
    {
        var realms = ImmutableDictionary.CreateRange(StringComparer.Ordinal, new Dictionary<string, string>
        {
            ["ignis"] = "ignis",
            ["aqua"] = "aqua",
        });
        var cardTypes = ImmutableDictionary.CreateRange(StringComparer.Ordinal, new Dictionary<string, string>
        {
            ["entity"] = "entity",
            ["incantation"] = "incantation",
            ["ritual"] = "ritual",
            ["sigil"] = "sigil",
            ["plane"] = "plane",
        });
        var lookups = ImmutableDictionary.CreateBuilder<string, RuntimeLookupGroup>(StringComparer.Ordinal);
        lookups["realm"] = new RuntimeLookupGroup("realm", realms);
        lookups["card_type"] = new RuntimeLookupGroup("card_type", cardTypes);
        return new RuntimePackageCatalog(
            "test-runtime",
            ImmutableDictionary.CreateRange(StringComparer.Ordinal, new[]
            {
                new KeyValuePair<string, RuntimeCardDefinition>(
                    cardId,
                    new RuntimeCardDefinition(cardId, magnitude, auraCost, realm, cardType)),
            }),
            ImmutableDictionary<string, RuntimeDeckDefinition>.Empty.WithComparers(StringComparer.Ordinal),
            new RuntimeLookupCatalog(lookups.ToImmutable()));
    }

    private static void ThrowsCode(string expectedCode, Action action)
    {
        try
        {
            action();
        }
        catch (EngineInputException exception)
        {
            Equal(expectedCode, exception.Code, "Canonical card rejection code is invalid.");
            return;
        }

        throw new InvalidOperationException($"Expected EngineInputException: {expectedCode}");
    }

    private static void SequenceEqual<T>(IEnumerable<T> expected, IEnumerable<T> actual, string message)
    {
        if (!expected.SequenceEqual(actual))
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected={expected}; Actual={actual}");
        }
    }
}
