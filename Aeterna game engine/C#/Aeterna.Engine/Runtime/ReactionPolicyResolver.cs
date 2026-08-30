using System.Collections.Immutable;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal static class ReactionPolicyIds
{
    internal const string StandardAlternatingResponse = "standard_alternating_response";
    internal const string SingleResponderOnce = "single_responder_once";
    internal const string NoFurtherResponse = "no_further_response";
    internal const string SameZonePresence = "same_zone_presence";
    internal const string PlayedCardResolutionPresence = "played_card_resolution_presence";
    internal const string DifferentTimingFifo = "different_timing_fifo";

    internal static bool IsOpenWindowPolicy(string policyId) => policyId is
        StandardAlternatingResponse or SingleResponderOnce;

    internal static bool IsNextResponsePolicy(string policyId) => policyId is
        StandardAlternatingResponse or NoFurtherResponse;
}

internal enum ReactionResponderScope
{
    BothPlayers,
    NonInitiatorOnly,
}

internal sealed record ReactionOpeningProfileBinding(
    string ReactionProfileId,
    string UnderlyingAbilityId,
    string InitialResponsePolicyId,
    ReactionResponderScope ResponderScope);

internal sealed record ReactionOptionProfileBinding(
    string ReactionProfileId,
    string SourceAbilityId,
    string NextResponsePolicyId,
    string SourceRelevancePolicyId = ReactionPolicyIds.SameZonePresence,
    bool RequiresPostDeclarationChoice = false,
    bool RequiresPaymentSelection = false,
    bool RequiresNestedReactionWindowDuringResolution = false);

internal sealed record ReactionOpeningPlan(
    string ReactionProfileId,
    string InitiatorPlayerId,
    ImmutableArray<string> EligibleResponderPlayerIds,
    string InitialPriorityPlayerId,
    string InitialResponsePolicyId);

internal sealed record ReactionTargetContract(
    CanonicalAbilityTargetDefinition Definition,
    ImmutableArray<CanonicalTargetCandidate> Candidates);

internal sealed record ReactionOption(
    string ReactionOptionId,
    string ReactionProfileId,
    string ControllerPlayerId,
    string SourceCardInstanceId,
    string SourceCardId,
    int SourceZoneSequenceAtDeclaration,
    CanonicalAbilityDefinition Ability,
    string SourceRelevancePolicyId,
    ImmutableArray<ReactionTargetContract> TargetContracts,
    string NextResponsePolicyId,
    bool RequiresPostDeclarationChoice,
    bool RequiresPaymentSelection,
    bool RequiresNestedReactionWindowDuringResolution);

internal sealed class ReactionPolicyResolver
{
    internal static ReactionPolicyResolver Empty { get; } = new([], []);

    private readonly ImmutableDictionary<string, ReactionOpeningProfileBinding> _openingsByAbilityId;
    private readonly ImmutableArray<ReactionOptionProfileBinding> _optionBindings;

    internal ReactionPolicyResolver(
        IEnumerable<ReactionOpeningProfileBinding> openingBindings,
        IEnumerable<ReactionOptionProfileBinding> optionBindings)
    {
        ArgumentNullException.ThrowIfNull(openingBindings);
        ArgumentNullException.ThrowIfNull(optionBindings);
        var openings = openingBindings.ToImmutableArray();
        if (openings.Any(item => string.IsNullOrWhiteSpace(item.ReactionProfileId)
                                 || string.IsNullOrWhiteSpace(item.UnderlyingAbilityId)
                                 || string.IsNullOrWhiteSpace(item.InitialResponsePolicyId))
            || openings.Select(item => item.UnderlyingAbilityId)
                .Distinct(StringComparer.Ordinal).Count() != openings.Length)
        {
            throw new ArgumentException("Reaction opening profile bindings must have unique typed ability identities.");
        }

        _openingsByAbilityId = openings.ToImmutableDictionary(
            item => item.UnderlyingAbilityId,
            StringComparer.Ordinal);
        _optionBindings = optionBindings.ToImmutableArray();
        if (_optionBindings.Any(item => string.IsNullOrWhiteSpace(item.ReactionProfileId)
                                        || string.IsNullOrWhiteSpace(item.SourceAbilityId)
                                        || string.IsNullOrWhiteSpace(item.NextResponsePolicyId)
                                        || string.IsNullOrWhiteSpace(item.SourceRelevancePolicyId))
            || _optionBindings.Select(item => (item.ReactionProfileId, item.SourceAbilityId))
                .Distinct()
                .Count() != _optionBindings.Length)
        {
            throw new ArgumentException(
                "Reaction option profile bindings must be fully typed and unique within profile/ability scope.");
        }
    }

    internal ReactionOpeningPlan? ResolveOpening(
        string underlyingAbilityId,
        string initiatorPlayerId,
        MatchState state)
    {
        ArgumentNullException.ThrowIfNull(state);
        if (!_openingsByAbilityId.TryGetValue(underlyingAbilityId, out var binding))
        {
            return null;
        }

        var nonInitiator = state.GetNextPlayerId(initiatorPlayerId);
        var eligible = binding.ResponderScope switch
        {
            ReactionResponderScope.BothPlayers => state.Players
                .Select(player => player.PlayerId)
                .ToImmutableArray(),
            ReactionResponderScope.NonInitiatorOnly => ImmutableArray.Create(nonInitiator),
            _ => throw new ArgumentOutOfRangeException(nameof(binding.ResponderScope)),
        };
        return new ReactionOpeningPlan(
            binding.ReactionProfileId,
            initiatorPlayerId,
            eligible,
            nonInitiator,
            binding.InitialResponsePolicyId);
    }

    internal ImmutableArray<ReactionOption> ResolveOptions(
        ReactionWindowState window,
        string playerId,
        MatchState state,
        RuntimePackageCatalog runtimePackage,
        CanonicalCardCatalog? canonicalCards,
        CanonicalAbilityCatalog canonicalAbilities)
    {
        ArgumentNullException.ThrowIfNull(window);
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(runtimePackage);
        ArgumentNullException.ThrowIfNull(canonicalAbilities);
        if (!string.Equals(state.PriorityPlayerId, playerId, StringComparison.Ordinal)
            || !window.EligibleResponderPlayerIds.Contains(playerId, StringComparer.Ordinal))
        {
            return ImmutableArray<ReactionOption>.Empty;
        }

        var bindings = _optionBindings
            .Where(binding => string.Equals(
                binding.ReactionProfileId,
                window.ReactionProfileId,
                StringComparison.Ordinal))
            .OrderBy(binding => binding.SourceAbilityId, StringComparer.Ordinal)
            .ThenBy(binding => binding.NextResponsePolicyId, StringComparer.Ordinal)
            .ToImmutableArray();
        var options = ImmutableArray.CreateBuilder<ReactionOption>();
        foreach (var source in state.CardInstances.Values
                     .Where(card => string.Equals(card.ControllerPlayerId, playerId, StringComparison.Ordinal)
                                    && string.Equals(card.Zone, "dominion", StringComparison.Ordinal)
                                    && string.Equals(card.Visibility, "public", StringComparison.Ordinal))
                     .OrderBy(card => card.CreatedSequence)
                     .ThenBy(card => card.CardInstanceId, StringComparer.Ordinal))
        {
            if (!canonicalAbilities.AbilitiesByCardId.TryGetValue(source.CardId, out var abilities))
            {
                continue;
            }

            foreach (var binding in bindings)
            {
                var ability = abilities.SingleOrDefault(candidate => string.Equals(
                    candidate.AbilityId,
                    binding.SourceAbilityId,
                    StringComparison.Ordinal));
                if (ability is null
                    || !string.Equals(ability.Status, "active", StringComparison.Ordinal)
                    || !string.Equals(ability.ActiveZoneId, source.Zone, StringComparison.Ordinal)
                    || !string.Equals(
                        binding.SourceRelevancePolicyId,
                        ReactionPolicyIds.SameZonePresence,
                        StringComparison.Ordinal)
                    || !CanonicalEffectExecutor.IsSupportedGraph(ability))
                {
                    continue;
                }

                var contracts = CanonicalTargetResolver.GetSupportedTargets(ability)
                    .Select(target => new ReactionTargetContract(
                        target,
                        CanonicalTargetResolver.ResolveCandidates(
                            target,
                            ability,
                            playerId,
                            state,
                            runtimePackage,
                            canonicalCards,
                            canonicalAbilities)))
                    .ToImmutableArray();
                if (contracts.Any(contract => contract.Candidates.Any(candidate =>
                    !IsVisibleToPlayer(state.GetCardInstance(candidate.CardInstanceId), playerId))))
                {
                    continue;
                }

                if (contracts.Where(contract => CanonicalTargetResolver.IsClientSelectable(contract.Definition)
                                                || CanonicalTargetResolver.IsAutomaticCollection(contract.Definition))
                    .Any(contract => contract.Candidates.Length < contract.Definition.MinimumTargets))
                {
                    continue;
                }

                var candidateFingerprint = string.Join(
                    ";",
                    contracts.Select(contract => $"{contract.Definition.TargetId}=" + string.Join(
                        ",",
                        contract.Candidates.Select(candidate =>
                            $"{candidate.CardInstanceId}@{state.GetCardInstance(candidate.CardInstanceId).ZoneSequence}"))));
                var optionId = string.Join(
                    ":",
                    "reaction-option",
                    window.ReactionWindowId,
                    state.StateVersion,
                    playerId,
                    binding.SourceAbilityId,
                    source.CardInstanceId,
                    source.ZoneSequence,
                    StableToken(candidateFingerprint));
                options.Add(new ReactionOption(
                    optionId,
                    binding.ReactionProfileId,
                    playerId,
                    source.CardInstanceId,
                    source.CardId,
                    source.ZoneSequence,
                    ability,
                    binding.SourceRelevancePolicyId,
                    contracts,
                    binding.NextResponsePolicyId,
                    binding.RequiresPostDeclarationChoice,
                    binding.RequiresPaymentSelection,
                    binding.RequiresNestedReactionWindowDuringResolution));
            }
        }

        return options.ToImmutable();
    }

    private static bool IsVisibleToPlayer(CardInstanceState card, string playerId) =>
        string.Equals(card.Visibility, "public", StringComparison.Ordinal)
        || string.Equals(card.OwnerPlayerId, playerId, StringComparison.Ordinal);

    private static string StableToken(string value)
    {
        var hash = 2166136261u;
        foreach (var character in value)
        {
            hash ^= character;
            hash *= 16777619u;
        }

        return hash.ToString("x8", System.Globalization.CultureInfo.InvariantCulture);
    }
}
