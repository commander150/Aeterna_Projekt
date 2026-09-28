using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

public sealed record CanonicalCardDefinition(
    string CardId,
    string CardType,
    string Realm,
    int Magnitude,
    int PrintedAuraCost,
    int? PrintedAtk,
    int? PrintedHp,
    string Status,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed class CanonicalCardCatalog
{
    internal CanonicalCardCatalog(
        ImmutableDictionary<string, CanonicalCardDefinition> definitionsById)
    {
        DefinitionsById = definitionsById;
        Definitions = definitionsById.Values
            .OrderBy(definition => definition.CardId, StringComparer.Ordinal)
            .ToImmutableArray();
    }

    public ImmutableArray<CanonicalCardDefinition> Definitions { get; }

    public ImmutableDictionary<string, CanonicalCardDefinition> DefinitionsById { get; }

    internal void ValidateRuntimeOverlap(RuntimePackageCatalog runtimePackage)
    {
        ArgumentNullException.ThrowIfNull(runtimePackage);
        foreach (var legacy in runtimePackage.Cards.Values.OrderBy(card => card.CardId, StringComparer.Ordinal))
        {
            if (!DefinitionsById.TryGetValue(legacy.CardId, out var canonical)
                || !string.Equals(canonical.Status, "active", StringComparison.Ordinal))
            {
                throw new EngineInputException(
                    "CANONICAL_RUNTIME_CARD_DEFINITION_MISSING",
                    $"Active canonical card definition is missing for runtime card: {legacy.CardId}");
            }

            var canonicalRuntimeCardType = canonical.CardType switch
            {
                "entity" => "entity",
                "spell" => "incantation",
                "ritual" => "ritual",
                "sign" => "sigil",
                "plane" => "plane",
                _ => null,
            };
            if (canonicalRuntimeCardType is null
                || !string.Equals(canonicalRuntimeCardType, legacy.CardType, StringComparison.Ordinal)
                || !string.Equals(canonical.Realm, legacy.Realm, StringComparison.Ordinal)
                || canonical.Magnitude != legacy.Magnitude
                || canonical.PrintedAuraCost != legacy.PrintedAuraCost)
            {
                throw new EngineInputException(
                    "CANONICAL_RUNTIME_CARD_OVERLAP_MISMATCH",
                    $"Canonical and legacy runtime card definitions disagree for card: {legacy.CardId}");
            }
        }
    }
}

public static class CanonicalCardMaterializer
{
    private const string FieldInvalidCode = "CANONICAL_CARD_FIELD_INVALID";

    public static CanonicalCardCatalog Materialize(CanonicalCardDatabasePackage cardDatabase)
    {
        ArgumentNullException.ThrowIfNull(cardDatabase);
        if (!cardDatabase.Tables.TryGetValue(CanonicalAbilityTableIds.Cards, out var cards))
        {
            throw new EngineInputException(
                "CANONICAL_CARD_TABLE_MISSING",
                "Canonical CARDDATABASE package does not contain the cards table.");
        }

        var vocabulary = ReadVocabulary(cardDatabase.Registry);
        var definitions = ImmutableDictionary.CreateBuilder<string, CanonicalCardDefinition>(StringComparer.Ordinal);
        foreach (var record in cards.Records)
        {
            var cardId = ReadRequiredString(record, "card_id");
            var cardType = ReadRequiredVocabulary(record, "card_type_id", "card_type", vocabulary);
            var realm = ReadRequiredVocabulary(record, "realm_id", "realm", vocabulary);
            var status = ReadRequiredVocabulary(record, "status", "record_status", vocabulary);
            var magnitude = ReadRequiredInteger(record, "magnitude");
            var auraCost = ReadRequiredInteger(record, "aura_cost");
            var atk = ReadOptionalInteger(record, "atk");
            var hp = ReadOptionalInteger(record, "hp");
            if (magnitude < 0 || auraCost < 0)
            {
                throw Invalid("Canonical card magnitude and aura_cost must be non-negative integers.");
            }

            if (string.Equals(cardType, "entity", StringComparison.Ordinal))
            {
                if (atk is null || hp is null || atk < 0 || hp <= 0)
                {
                    throw Invalid("Canonical Entity cards require non-negative ATK and positive HP.");
                }
            }
            else if (atk is not null || hp is not null)
            {
                throw Invalid("Canonical non-Entity cards require explicit null ATK and HP.");
            }

            var definition = new CanonicalCardDefinition(
                cardId,
                cardType,
                realm,
                magnitude,
                auraCost,
                atk,
                hp,
                status,
                record.Fields);
            if (!definitions.TryAdd(cardId, definition))
            {
                throw new EngineInputException(
                    "CANONICAL_CARD_DUPLICATE_ID",
                    $"Canonical cards table contains duplicate card_id: {cardId}");
            }
        }

        return new CanonicalCardCatalog(definitions.ToImmutable());
    }

    private static ImmutableDictionary<string, ImmutableHashSet<string>> ReadVocabulary(
        CanonicalRegistryPackage registry)
    {
        if (!registry.Tables.TryGetValue("value_registry", out var table))
        {
            throw new EngineInputException(
                "CANONICAL_CARD_VOCABULARY_MISSING",
                "Canonical REGISTRY package does not contain value_registry.");
        }

        return table.Records
            .GroupBy(record => ReadRequiredString(record, "group_id"), StringComparer.Ordinal)
            .ToImmutableDictionary(
                group => group.Key,
                group => group.Select(record => ReadRequiredString(record, "value_id"))
                    .ToImmutableHashSet(StringComparer.Ordinal),
                StringComparer.Ordinal);
    }

    private static string ReadRequiredVocabulary(
        CanonicalRecord record,
        string fieldName,
        string groupId,
        ImmutableDictionary<string, ImmutableHashSet<string>> vocabulary)
    {
        var value = ReadRequiredString(record, fieldName);
        if (!vocabulary.TryGetValue(groupId, out var values) || !values.Contains(value))
        {
            throw new EngineInputException(
                "CANONICAL_CARD_VOCABULARY_UNKNOWN",
                $"Canonical card vocabulary value is unknown for cards.{fieldName}: {value}");
        }

        return value;
    }

    private static string ReadRequiredString(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw Invalid($"Canonical card field must be a non-empty string: {fieldName}");
        }

        return value.GetString()!;
    }

    private static int ReadRequiredInteger(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var result))
        {
            throw Invalid($"Canonical card field must be an integer: {fieldName}");
        }

        return result;
    }

    private static int? ReadOptionalInteger(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        if (value.ValueKind != JsonValueKind.Number || !value.TryGetInt32(out var result))
        {
            throw Invalid($"Canonical card field must be an integer or null: {fieldName}");
        }

        return result;
    }

    private static EngineInputException Invalid(string message) => new(FieldInvalidCode, message);
}

internal static class CanonicalVitals
{
    internal static int GetEffectiveMaxHp(CardInstanceState card, CanonicalCardCatalog cards)
        => GetPrintedMaxHp(card, cards);

    internal static int GetEffectiveMaxHp(
        MatchState state,
        CardInstanceState card,
        CanonicalCardCatalog cards,
        IReadOnlySet<string>? excludedModifierIds = null)
    {
        var printedHp = GetPrintedMaxHp(card, cards);
        return AddSupportedModifierTotal(
            printedHp,
            CanonicalContinuousEffects.ModifierTotal(
                state,
                card,
                CanonicalContinuousEffects.MaxHpFieldId,
                excludedModifierIds));
    }

    internal static int GetEffectiveAtk(
        MatchState state,
        CardInstanceState card,
        CanonicalCardCatalog cards,
        IReadOnlySet<string>? excludedModifierIds = null)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(card);
        ArgumentNullException.ThrowIfNull(cards);
        if (!cards.DefinitionsById.TryGetValue(card.CardId, out var definition)
            || !string.Equals(definition.Status, "active", StringComparison.Ordinal)
            || !string.Equals(definition.CardType, "entity", StringComparison.Ordinal)
            || definition.PrintedAtk is not int printedAtk
            || printedAtk < 0)
        {
            throw new EngineStateException(
                "CANONICAL_CARD_STATS_INVALID",
                "Entity ATK requires an active canonical Entity definition with non-negative printed ATK.");
        }

        return AddSupportedModifierTotal(
            printedAtk,
            CanonicalContinuousEffects.ModifierTotal(
                state,
                card,
                CanonicalContinuousEffects.AttackFieldId,
                excludedModifierIds),
            allowZero: true);
    }

    private static int GetPrintedMaxHp(CardInstanceState card, CanonicalCardCatalog cards)
    {
        ArgumentNullException.ThrowIfNull(card);
        ArgumentNullException.ThrowIfNull(cards);
        if (!cards.DefinitionsById.TryGetValue(card.CardId, out var definition)
            || !string.Equals(definition.Status, "active", StringComparison.Ordinal)
            || !string.Equals(definition.CardType, "entity", StringComparison.Ordinal)
            || definition.PrintedHp is not int printedHp
            || printedHp <= 0)
        {
            throw new EngineStateException(
                "CANONICAL_CARD_STATS_INVALID",
                "Entity HP requires an active canonical Entity definition with positive printed HP.");
        }

        return printedHp;
    }

    private static int AddSupportedModifierTotal(
        int printedValue,
        int modifierTotal,
        bool allowZero = false)
    {
        var effective = (long)printedValue + modifierTotal;
        if (effective > int.MaxValue || (allowZero ? effective < 0 : effective <= 0))
        {
            throw new EngineStateException(
                "CANONICAL_EFFECTIVE_STAT_INVALID",
                "Effective canonical Entity stat is outside its supported integer range.");
        }

        return (int)effective;
    }
}
