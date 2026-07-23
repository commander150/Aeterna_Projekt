using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Rules;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

namespace Aeterna.Engine;

public sealed class EngineSession
{
    private static readonly ImmutableHashSet<string> SupportedAuraPaymentCardTypes =
        ImmutableHashSet.Create(
            StringComparer.Ordinal,
            "entity",
            "incantation",
            "ritual",
            "sigil",
            "plane");

    private MatchState? _state;
    private RuntimePackageCatalog? _runtimePackage;

    public EngineSession()
    {
    }

    internal EngineSession(MatchState initialState)
    {
        ArgumentNullException.ThrowIfNull(initialState);
        ValidateState(initialState);
        _state = initialState;
    }

    internal EngineSession(MatchState initialState, RuntimePackageCatalog runtimePackage)
    {
        ArgumentNullException.ThrowIfNull(initialState);
        ArgumentNullException.ThrowIfNull(runtimePackage);
        ValidateState(initialState);
        RuntimePackageLoader.ValidateCatalog(runtimePackage);
        if (!string.Equals(initialState.RuntimePackageId, runtimePackage.PackageId, StringComparison.Ordinal))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_ID_MISMATCH",
                "Runtime package catalog does not match the initial state.");
        }

        _state = initialState;
        _runtimePackage = runtimePackage;
    }

    public CreateMatchResponse CreateMatch(CreateMatchRequest? request)
    {
        if (request is null)
        {
            return RejectCreateMatch(
                matchId: null,
                "CREATE_MATCH_REQUEST_MISSING",
                "Create match request is missing or malformed.");
        }

        if (_state is not null || _runtimePackage is not null)
        {
            return RejectCreateMatch(
                request.MatchId,
                "MATCH_ALREADY_CREATED",
                "The engine session already owns a match.");
        }

        try
        {
            ValidateCreateMatchRequest(request);
            var package = RuntimePackageLoader.Load(request.RuntimePackage);
            var state = BuildInitialState(request, package);
            ValidateState(state);
            _state = state;
            _runtimePackage = package;
            return new CreateMatchResponse(
                ContractSchemas.CreateMatchResponse,
                Accepted: true,
                state.MatchId,
                state.RuntimePackageId,
                state.StateVersion,
                ImmutableArray<EngineDiagnostic>.Empty);
        }
        catch (EngineInputException exception)
        {
            return RejectCreateMatch(request.MatchId, exception.Code, exception.Message);
        }
    }

    public PlayerSnapshot GetPlayerSnapshot(string playerId)
    {
        var state = RequireState();
        RequireKnownPlayer(state, playerId);
        var resourceSummaries = state.Players
            .Select(player => BuildWellspringResourceSummary(state, player))
            .ToImmutableArray();
        var resourceSummariesByPlayerId = resourceSummaries
            .ToDictionary(summary => summary.PlayerId, StringComparer.Ordinal);
        var players = state.Players
            .Select(player => BuildPlayerSnapshotEntry(
                state,
                player,
                playerId,
                resourceSummariesByPlayerId[player.PlayerId]))
            .ToImmutableArray();
        var legalActions = ListLegalActions(playerId).Actions;
        return new PlayerSnapshot(
            ContractSchemas.PlayerSnapshot,
            $"snapshot:{state.MatchId}:{state.StateVersion}:{playerId}",
            state.MatchId,
            playerId,
            state.StateVersion,
            state.TurnNumber,
            state.Phase,
            state.ActivePlayerId,
            state.PriorityPlayerId,
            players,
            legalActions,
            state.Events.Count,
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["status"] = "not_in_c5b_scope",
            }),
            new ResourceSummary(ContractSchemas.ResourceSummary, resourceSummaries),
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["has_pending"] = false,
            }),
            state.Result);
    }

    public LegalActionSpace ListLegalActions(string playerId, bool includeDisabled = false)
    {
        var state = RequireState();
        ValidateState(state);
        var player = RequireKnownPlayer(state, playerId);
        var active = string.Equals(playerId, state.ActivePlayerId, StringComparison.Ordinal);
        var normalInflowUsed = player.NormalInflowUsedTurnNumber == state.TurnNumber;
        var normalInflowEnabled = active
            && !normalInflowUsed
            && player.HandCardInstanceIds.Count > 0;
        var normalInflowDisabledReason = !active
            ? "not_active_player"
            : normalInflowUsed
                ? "normal_inflow_already_used"
                : player.HandCardInstanceIds.Count == 0
                    ? "hand_empty"
                    : null;
        var actions = new[]
        {
            new LegalAction(
                $"end_turn:{state.TurnNumber}:{playerId}",
                "end_turn",
                playerId,
                active,
                100,
                active ? null : "not_active_player",
                ContractJsonValue.EmptyObject()),
            new LegalAction(
                $"normal_inflow:{state.TurnNumber}:{state.StateVersion}:{playerId}",
                "normal_inflow",
                playerId,
                normalInflowEnabled,
                150,
                normalInflowDisabledReason,
                BuildNormalInflowPayloadSchema()),
            new LegalAction(
                $"draw_card:{state.TurnNumber}:{state.StateVersion}:{playerId}",
                "draw_card",
                playerId,
                active && player.DeckCardInstanceIds.Count > 0,
                200,
                active
                    ? player.DeckCardInstanceIds.Count > 0 ? null : "deck_empty"
                    : "not_active_player",
                ContractJsonValue.EmptyObject()),
        };
        var ordered = actions
            .OrderBy(action => action.OrderRank)
            .ThenBy(action => action.ActionType, StringComparer.Ordinal)
            .ThenBy(action => action.ActionId, StringComparer.Ordinal)
            .Where(action => includeDisabled || action.Enabled)
            .Select(CloneLegalAction)
            .ToImmutableArray();
        return new LegalActionSpace(
            ContractSchemas.LegalActionSpace,
            state.MatchId,
            state.StateVersion,
            state.TurnNumber,
            state.Phase,
            state.ActivePlayerId,
            state.PriorityPlayerId,
            playerId,
            ordered);
    }

    public ActionResponse SubmitAction(ActionRequest? request)
    {
        if (request is null)
        {
            return RejectMissingActionRequest(_state);
        }

        var state = RequireState();
        var stateVersionBefore = state.StateVersion;
        if (!string.Equals(request.SchemaVersion, ContractSchemas.ActionRequest, StringComparison.Ordinal))
        {
            return RejectAction(
                state,
                request,
                "request_schema_invalid",
                Diagnostic(
                    "ACTION_REQUEST_SCHEMA_INVALID",
                    "request_validation",
                    "Action request schema is not supported.",
                    "The submitted action request schema_version is not the production C.5B schema.",
                    "fix_request"));
        }

        if (string.IsNullOrWhiteSpace(request.RequestId))
        {
            return RejectAction(
                state,
                request,
                "request_id_invalid",
                Diagnostic(
                    "ACTION_REQUEST_ID_INVALID",
                    "request_validation",
                    "Action request ID is required.",
                    "The submitted request_id is missing, empty, or whitespace.",
                    "fix_request"));
        }

        if (!string.Equals(request.MatchId, state.MatchId, StringComparison.Ordinal))
        {
            return RejectAction(
                state,
                request,
                "match_id_mismatch",
                Diagnostic(
                    "MATCH_ID_MISMATCH",
                    "request_validation",
                    "Action request belongs to another match.",
                    "The submitted match_id differs from the session match_id.",
                    "fix_request"));
        }

        if (state.Players.All(player => !string.Equals(player.PlayerId, request.PlayerId, StringComparison.Ordinal)))
        {
            return RejectAction(
                state,
                request,
                "unknown_player",
                Diagnostic(
                    "UNKNOWN_PLAYER",
                    "request_validation",
                    "Action request player is unknown.",
                    "The submitted player_id is not part of this match.",
                    "fix_request"));
        }

        if (request.ExpectedStateVersion != state.StateVersion)
        {
            return RejectAction(
                state,
                request,
                "stale_state_version",
                Diagnostic(
                    "STALE_STATE_VERSION",
                    "request_validation",
                    "The current game state has changed.",
                    "The submitted expected_state_version does not match the authoritative state version.",
                    "refresh_projection",
                    new Dictionary<string, object?>
                    {
                        ["expected_state_version"] = request.ExpectedStateVersion,
                        ["current_state_version"] = state.StateVersion,
                    }));
        }

        var action = ListLegalActions(request.PlayerId, includeDisabled: true).Actions
            .SingleOrDefault(item => string.Equals(item.ActionId, request.ActionId, StringComparison.Ordinal));
        if (action is null)
        {
            return RejectAction(
                state,
                request,
                "action_not_found",
                Diagnostic(
                    "ACTION_NOT_FOUND",
                    "request_validation",
                    "The requested action is no longer available.",
                    "The submitted action_id is not present in the current legal action space.",
                    "refresh_projection"));
        }

        if (!string.Equals(action.ActionType, request.ActionType, StringComparison.Ordinal))
        {
            return RejectAction(
                state,
                request,
                "action_type_mismatch",
                Diagnostic(
                    "ACTION_TYPE_MISMATCH",
                    "request_validation",
                    "The requested action type is invalid.",
                    "The submitted action_type does not match the current legal action.",
                    "fix_request"));
        }

        var payloadDiagnostic = ValidateActionPayload(request);
        if (payloadDiagnostic is not null)
        {
            return RejectAction(
                state,
                request,
                "action_payload_invalid",
                payloadDiagnostic);
        }

        if (!action.Enabled)
        {
            return RejectAction(
                state,
                request,
                action.DisabledReason ?? "action_disabled",
                Diagnostic(
                    "ACTION_DISABLED",
                    "request_validation",
                    "The requested action is not currently enabled.",
                    $"The current legal action is disabled: {action.DisabledReason}",
                    "refresh_projection"));
        }

        var response = request.ActionType switch
        {
            "draw_card" => ApplyDraw(state, request, stateVersionBefore),
            "normal_inflow" => ApplyNormalInflow(state, request, stateVersionBefore),
            "end_turn" => ApplyEndTurn(state, request, stateVersionBefore),
            _ => RejectAction(
                state,
                request,
                "action_type_unsupported",
                Diagnostic(
                    "ACTION_TYPE_UNSUPPORTED",
                    "request_validation",
                    "The requested action type is not supported.",
                    "The action type is outside the C.5B production rules scope.",
                    "fix_request")),
        };
        ValidateState(state);
        return response;
    }

    public ImmutableArray<EngineEvent> GetEvents(string viewerPlayerId, int afterSequence = 0)
    {
        var state = RequireState();
        RequireKnownPlayer(state, viewerPlayerId);
        return state.Events
            .Where(item => item.EventSequence > afterSequence)
            .Select(item => ProjectEventForViewer(item, viewerPlayerId))
            .ToImmutableArray();
    }

    public MatchResult GetMatchResult()
    {
        var result = RequireState().Result;
        return result with { };
    }

    internal DebugSnapshot GetDebugSnapshot()
    {
        var state = RequireState();
        return new DebugSnapshot(
            ContractSchemas.DebugSnapshot,
            state.MatchId,
            state.Seed,
            state.StateVersion,
            state.TurnNumber,
            state.Phase,
            state.ActivePlayerId,
            state.PriorityPlayerId,
            state.Players.Select(player => new DebugPlayerSnapshot(
                player.PlayerId,
                player.DeckId,
                player.DeckCardInstanceIds.ToImmutableArray(),
                player.HandCardInstanceIds.ToImmutableArray(),
                player.DiscardCardInstanceIds.ToImmutableArray(),
                player.WellspringCardInstanceIds.ToImmutableArray(),
                player.NormalInflowUsedTurnNumber)).ToImmutableArray(),
            state.CardInstances.Values
                .OrderBy(card => card.CreatedSequence)
                .ThenBy(card => card.CardInstanceId, StringComparer.Ordinal)
                .Select(card => new DebugCardInstanceSnapshot(
                    card.CardInstanceId,
                    card.CardId,
                    card.OwnerPlayerId,
                    card.ControllerPlayerId,
                    card.Zone,
                    card.ZoneIndex,
                    card.Visibility,
                    card.CreatedSequence,
                    card.ZoneSequence,
                    card.InitialZone,
                    card.ActivityState))
                .ToImmutableArray(),
            state.Events.Select(CloneEvent).ToImmutableArray(),
            state.Result with { });
    }

    internal ImmutableArray<EngineEvent> GetDebugEvents(int afterSequence = 0)
    {
        var state = RequireState();
        return state.Events
            .Where(item => item.EventSequence > afterSequence)
            .Select(CloneEvent)
            .ToImmutableArray();
    }

    internal ImmutableArray<EngineDiagnostic> GetDebugInvariantDiagnostics()
    {
        try
        {
            ValidateState(RequireState());
            return ImmutableArray<EngineDiagnostic>.Empty;
        }
        catch (EngineStateException exception)
        {
            return ImmutableArray.Create(Diagnostic(
                "STATE_INVARIANT_FAILED",
                "state_invariant",
                "The authoritative game state is inconsistent.",
                exception.Message,
                "engine_bug"));
        }
    }

    internal MagnitudePreflightResult EvaluateMagnitudePreflight(
        string playerId,
        string cardInstanceId)
    {
        var state = RequireState();
        ValidateMagnitudePreflightState(state, playerId, cardInstanceId);
        var runtimePackage = _runtimePackage
            ?? throw new MagnitudePreflightException(
                "MAGNITUDE_PREFLIGHT_RUNTIME_PACKAGE_MISSING",
                "Magnitude preflight requires a validated runtime package catalog.");
        try
        {
            RuntimePackageLoader.ValidateCatalog(runtimePackage);
        }
        catch (EngineInputException exception)
        {
            throw new MagnitudePreflightException(
                "MAGNITUDE_PREFLIGHT_RUNTIME_PACKAGE_INVALID",
                "Magnitude preflight runtime package catalog is invalid.",
                exception);
        }

        if (!string.Equals(runtimePackage.PackageId, state.RuntimePackageId, StringComparison.Ordinal))
        {
            throw new MagnitudePreflightException(
                "MAGNITUDE_PREFLIGHT_RUNTIME_PACKAGE_INVALID",
                "Magnitude preflight runtime package does not match the current state.");
        }

        var player = state.Players.SingleOrDefault(item =>
            string.Equals(item.PlayerId, playerId, StringComparison.Ordinal))
            ?? throw new MagnitudePreflightException(
                "MAGNITUDE_PREFLIGHT_PLAYER_UNKNOWN",
                "Magnitude preflight player is unknown.");
        if (!state.CardInstances.TryGetValue(cardInstanceId, out var card))
        {
            throw new MagnitudePreflightException(
                "MAGNITUDE_PREFLIGHT_CARD_UNKNOWN",
                "Magnitude preflight card instance is unknown.");
        }

        if (!string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal))
        {
            throw new MagnitudePreflightException(
                "MAGNITUDE_PREFLIGHT_CARD_AUTHORITY_INVALID",
                "Magnitude preflight card owner/controller does not match the player.");
        }

        if (!string.Equals(card.Zone, "hand", StringComparison.Ordinal))
        {
            throw new MagnitudePreflightException(
                "MAGNITUDE_PREFLIGHT_CARD_ZONE_INVALID",
                "Magnitude preflight card must be in hand.");
        }

        var handIndex = player.HandCardInstanceIds.IndexOf(card.CardInstanceId);
        if (handIndex < 0 || card.ZoneIndex != handIndex)
        {
            throw new MagnitudePreflightException(
                "MAGNITUDE_PREFLIGHT_HAND_MEMBERSHIP_INVALID",
                "Magnitude preflight card registry and hand membership disagree.");
        }

        if (!runtimePackage.Cards.TryGetValue(card.CardId, out var definition))
        {
            throw new MagnitudePreflightException(
                "MAGNITUDE_PREFLIGHT_RUNTIME_CARD_MISSING",
                "Magnitude preflight runtime card definition is missing.");
        }

        var currentMagnitude = player.WellspringCardInstanceIds.Count;
        var requirementMet = currentMagnitude >= definition.Magnitude;
        return new MagnitudePreflightResult(
            player.PlayerId,
            card.CardInstanceId,
            card.CardId,
            definition.Magnitude,
            currentMagnitude,
            requirementMet,
            requirementMet ? null : "magnitude_requirement_not_met");
    }

    internal AuraPaymentPreflightResult EvaluateAuraPaymentPreflight(
        string playerId,
        string cardInstanceId)
    {
        var state = RequireState();
        ValidateAuraPaymentPreflightState(state, playerId, cardInstanceId);
        var runtimePackage = RequireAuraPaymentRuntimePackage(state);
        var player = state.Players.SingleOrDefault(item =>
            string.Equals(item.PlayerId, playerId, StringComparison.Ordinal))
            ?? throw new AuraPaymentException(
                "AURA_PAYMENT_PLAYER_UNKNOWN",
                "Aura payment player is unknown.");
        if (string.IsNullOrWhiteSpace(cardInstanceId)
            || !state.CardInstances.TryGetValue(cardInstanceId, out var card))
        {
            throw new AuraPaymentException(
                "AURA_PAYMENT_CARD_UNKNOWN",
                "Aura payment target card instance is unknown.");
        }

        if (!string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal))
        {
            throw new AuraPaymentException(
                "AURA_PAYMENT_CARD_AUTHORITY_INVALID",
                "Aura payment target owner/controller does not match the player.");
        }

        if (!string.Equals(card.Zone, "hand", StringComparison.Ordinal))
        {
            throw new AuraPaymentException(
                "AURA_PAYMENT_CARD_ZONE_INVALID",
                "Aura payment target must be in hand.");
        }

        var handIndex = player.HandCardInstanceIds.IndexOf(card.CardInstanceId);
        if (handIndex < 0 || card.ZoneIndex != handIndex)
        {
            throw new AuraPaymentException(
                "AURA_PAYMENT_HAND_MEMBERSHIP_INVALID",
                "Aura payment target registry and hand membership disagree.");
        }

        if (!runtimePackage.Cards.TryGetValue(card.CardId, out var definition))
        {
            throw new AuraPaymentException(
                "AURA_PAYMENT_RUNTIME_CARD_MISSING",
                "Aura payment target runtime card definition is missing.");
        }

        if (!SupportedAuraPaymentCardTypes.Contains(definition.CardType))
        {
            throw new AuraPaymentException(
                "AURA_PAYMENT_CARD_TYPE_UNSUPPORTED",
                "Aura payment policy is not defined for the target card type.");
        }

        var eligibleSources = ImmutableArray.CreateBuilder<AuraSourceCandidate>();
        for (var zoneIndex = 0; zoneIndex < player.WellspringCardInstanceIds.Count; zoneIndex++)
        {
            var sourceInstanceId = player.WellspringCardInstanceIds[zoneIndex];
            if (!state.CardInstances.TryGetValue(sourceInstanceId, out var sourceCard)
                || !string.Equals(sourceCard.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
                || !string.Equals(sourceCard.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal)
                || !string.Equals(sourceCard.Zone, "wellspring", StringComparison.Ordinal)
                || sourceCard.ZoneIndex != zoneIndex
                || !string.Equals(sourceCard.Visibility, "owner_only", StringComparison.Ordinal)
                || sourceCard.ActivityState is not ("active" or "exhausted"))
            {
                throw new AuraPaymentException(
                    "AURA_PAYMENT_STATE_INVALID",
                    "Aura payment Wellspring source state is inconsistent.");
            }

            if (!runtimePackage.Cards.TryGetValue(sourceCard.CardId, out var sourceDefinition))
            {
                throw new AuraPaymentException(
                    "AURA_PAYMENT_RUNTIME_CARD_MISSING",
                    "Aura payment Wellspring source runtime card definition is missing.");
            }

            if (!string.Equals(sourceCard.ActivityState, "active", StringComparison.Ordinal)
                || !IsAuraSourceRealmEligible(definition, sourceDefinition.Realm))
            {
                continue;
            }

            eligibleSources.Add(new AuraSourceCandidate(
                sourceCard.CardInstanceId,
                sourceDefinition.Realm,
                sourceCard.ZoneIndex,
                sourceCard.ActivityState));
        }

        var orderedEligibleSources = eligibleSources
            .OrderBy(source => source.ZoneIndex)
            .ThenBy(source => source.CardInstanceId, StringComparer.Ordinal)
            .ToImmutableArray();
        var normalizedPayableAuraCost = definition.PrintedAuraCost;
        var paymentPossible = orderedEligibleSources.Length >= normalizedPayableAuraCost;
        string? selectionMode;
        ImmutableArray<string> forcedSourceInstanceIds;
        if (normalizedPayableAuraCost == 0)
        {
            selectionMode = "none";
            forcedSourceInstanceIds = ImmutableArray<string>.Empty;
        }
        else if (!paymentPossible)
        {
            selectionMode = null;
            forcedSourceInstanceIds = ImmutableArray<string>.Empty;
        }
        else if (orderedEligibleSources.Length == normalizedPayableAuraCost)
        {
            selectionMode = "forced";
            forcedSourceInstanceIds = orderedEligibleSources
                .Select(source => source.CardInstanceId)
                .ToImmutableArray();
        }
        else
        {
            selectionMode = "choice";
            forcedSourceInstanceIds = ImmutableArray<string>.Empty;
        }

        return new AuraPaymentPreflightResult(
            player.PlayerId,
            card.CardInstanceId,
            card.CardId,
            definition.CardType,
            definition.Realm,
            definition.PrintedAuraCost,
            normalizedPayableAuraCost,
            orderedEligibleSources.Length,
            paymentPossible,
            selectionMode,
            paymentPossible ? null : "insufficient_eligible_aura",
            orderedEligibleSources,
            forcedSourceInstanceIds);
    }

    internal AuraPaymentSelectionValidationResult ValidateAuraPaymentSelection(
        string playerId,
        string cardInstanceId,
        IReadOnlyCollection<string>? selectedSourceInstanceIds)
    {
        var preflight = EvaluateAuraPaymentPreflight(playerId, cardInstanceId);
        var selectedSources = selectedSourceInstanceIds?.ToImmutableArray()
            ?? ImmutableArray<string>.Empty;
        if (!preflight.PaymentPossible)
        {
            return BuildAuraPaymentSelectionResult(
                preflight,
                selectionValid: false,
                failureReason: "payment_not_possible",
                ImmutableArray<string>.Empty);
        }

        if (string.Equals(preflight.SelectionMode, "none", StringComparison.Ordinal))
        {
            return selectedSources.Length == 0
                ? BuildAuraPaymentSelectionResult(
                    preflight,
                    selectionValid: true,
                    failureReason: null,
                    ImmutableArray<string>.Empty)
                : BuildAuraPaymentSelectionResult(
                    preflight,
                    selectionValid: false,
                    failureReason: "unexpected_source_selection",
                    ImmutableArray<string>.Empty);
        }

        if (string.Equals(preflight.SelectionMode, "forced", StringComparison.Ordinal))
        {
            if (selectedSources.Length == 0)
            {
                return BuildAuraPaymentSelectionResult(
                    preflight,
                    selectionValid: true,
                    failureReason: null,
                    preflight.ForcedSourceInstanceIds);
            }

            var explicitSet = selectedSources.ToHashSet(StringComparer.Ordinal);
            var forcedSet = preflight.ForcedSourceInstanceIds.ToHashSet(StringComparer.Ordinal);
            var exactForcedSelection = explicitSet.Count == selectedSources.Length
                && explicitSet.SetEquals(forcedSet);
            return exactForcedSelection
                ? BuildAuraPaymentSelectionResult(
                    preflight,
                    selectionValid: true,
                    failureReason: null,
                    preflight.ForcedSourceInstanceIds)
                : BuildAuraPaymentSelectionResult(
                    preflight,
                    selectionValid: false,
                    failureReason: "forced_source_selection_mismatch",
                    ImmutableArray<string>.Empty);
        }

        if (!string.Equals(preflight.SelectionMode, "choice", StringComparison.Ordinal))
        {
            throw new AuraPaymentException(
                "AURA_PAYMENT_RUNTIME_PACKAGE_INVALID",
                "Aura payment preflight returned an unsupported selection mode.");
        }

        if (selectedSources.Length == 0)
        {
            return BuildAuraPaymentSelectionResult(
                preflight,
                selectionValid: false,
                failureReason: "source_selection_required",
                ImmutableArray<string>.Empty);
        }

        var selectedSet = selectedSources.ToHashSet(StringComparer.Ordinal);
        if (selectedSet.Count != selectedSources.Length)
        {
            return BuildAuraPaymentSelectionResult(
                preflight,
                selectionValid: false,
                failureReason: "duplicate_source_selection",
                ImmutableArray<string>.Empty);
        }

        if (selectedSources.Length != preflight.NormalizedPayableAuraCost)
        {
            return BuildAuraPaymentSelectionResult(
                preflight,
                selectionValid: false,
                failureReason: "source_count_mismatch",
                ImmutableArray<string>.Empty);
        }

        var eligibleIds = preflight.EligibleSources
            .Select(source => source.CardInstanceId)
            .ToHashSet(StringComparer.Ordinal);
        if (selectedSources.Any(sourceId =>
                string.IsNullOrWhiteSpace(sourceId) || !eligibleIds.Contains(sourceId)))
        {
            return BuildAuraPaymentSelectionResult(
                preflight,
                selectionValid: false,
                failureReason: "source_not_eligible",
                ImmutableArray<string>.Empty);
        }

        var resolvedSources = preflight.EligibleSources
            .Where(source => selectedSet.Contains(source.CardInstanceId))
            .Select(source => source.CardInstanceId)
            .ToImmutableArray();
        return BuildAuraPaymentSelectionResult(
            preflight,
            selectionValid: true,
            failureReason: null,
            resolvedSources);
    }

    private static void ValidateCreateMatchRequest(CreateMatchRequest request)
    {
        if (!string.Equals(request.SchemaVersion, ContractSchemas.CreateMatchRequest, StringComparison.Ordinal))
        {
            throw new EngineInputException("CREATE_MATCH_SCHEMA_INVALID", "Create match schema is not supported.");
        }

        if (string.IsNullOrWhiteSpace(request.MatchId))
        {
            throw new EngineInputException("MATCH_ID_INVALID", "Match ID is empty.");
        }

        if (request.StartingHandSize < 0)
        {
            throw new EngineInputException("STARTING_HAND_SIZE_INVALID", "Starting hand size cannot be negative.");
        }

        if (request.RuntimePackage is null)
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_SOURCE_MISSING",
                "Runtime package source is missing.");
        }

        if (request.Players.IsDefault
            || request.Players.Length < 2
            || request.Players.Any(item => item is null
                || string.IsNullOrWhiteSpace(item.PlayerId)
                || string.IsNullOrWhiteSpace(item.DeckId))
            || request.Players.Select(item => item.PlayerId).Distinct(StringComparer.Ordinal).Count() != request.Players.Length)
        {
            throw new EngineInputException("PLAYER_SETUP_INVALID", "At least two distinct valid players are required.");
        }
    }

    private static MatchState BuildInitialState(CreateMatchRequest request, RuntimePackageCatalog package)
    {
        var state = new MatchState
        {
            MatchId = request.MatchId,
            Seed = request.Seed,
            RuntimePackageId = package.PackageId,
            StateVersion = 0,
            ActivePlayerId = request.Players[0].PlayerId,
            PriorityPlayerId = request.Players[0].PlayerId,
        };
        foreach (var setup in request.Players)
        {
            if (!package.Decks.TryGetValue(setup.DeckId, out var deck))
            {
                throw new EngineInputException("DECK_NOT_FOUND", "Player setup references an unknown deck_id.");
            }

            if (deck.OrderedCardIds.Length < request.StartingHandSize)
            {
                throw new EngineInputException("DECK_TOO_SMALL", "Deck is smaller than the requested starting hand.");
            }

            var player = new PlayerState
            {
                PlayerId = setup.PlayerId,
                DeckId = setup.DeckId,
            };
            for (var cardIndex = 0; cardIndex < deck.OrderedCardIds.Length; cardIndex++)
            {
                var cardInstanceId = $"ci_{setup.PlayerId}_{cardIndex + 1:0000}";
                var inHand = cardIndex < request.StartingHandSize;
                var zone = inHand ? "hand" : "deck";
                var zoneIndex = inHand ? cardIndex : cardIndex - request.StartingHandSize;
                state.CardInstances.Add(cardInstanceId, new CardInstanceState
                {
                    CardInstanceId = cardInstanceId,
                    CardId = deck.OrderedCardIds[cardIndex],
                    OwnerPlayerId = setup.PlayerId,
                    ControllerPlayerId = setup.PlayerId,
                    Zone = zone,
                    ZoneIndex = zoneIndex,
                    Visibility = "owner_only",
                    CreatedSequence = cardIndex + 1,
                    ZoneSequence = 1,
                    InitialZone = zone,
                    ActivityState = null,
                });
                (inHand ? player.HandCardInstanceIds : player.DeckCardInstanceIds).Add(cardInstanceId);
            }

            state.Players.Add(player);
        }

        return state;
    }

    private static ActionResponse ApplyDraw(MatchState state, ActionRequest request, int stateVersionBefore)
    {
        var player = state.GetPlayer(request.PlayerId);
        if (player.DeckCardInstanceIds.Count == 0)
        {
            return RejectAction(
                state,
                request,
                "deck_empty",
                Diagnostic(
                    "DRAW_PRECONDITION_FAILED",
                    "transition_validation",
                    "No card can be drawn.",
                    "The authoritative deck is empty.",
                    "refresh_projection"));
        }

        var cardInstanceId = player.DeckCardInstanceIds[0];
        var card = state.GetCardInstance(cardInstanceId);
        var fromZoneIndex = card.ZoneIndex;
        var toZoneIndex = player.HandCardInstanceIds.Count;
        player.DeckCardInstanceIds.RemoveAt(0);
        player.HandCardInstanceIds.Add(cardInstanceId);
        ReindexZone(state, player.DeckCardInstanceIds, "deck");
        card.Zone = "hand";
        card.ZoneIndex = toZoneIndex;
        card.ZoneSequence += 1;
        state.StateVersion += 1;
        var eventSequence = state.Events.Count + 1;
        var payload = new ZoneMovePayload(
            request.ActionId,
            request.ActionType,
            card.CardInstanceId,
            card.CardId,
            card.OwnerPlayerId,
            card.ControllerPlayerId,
            "deck",
            "hand",
            fromZoneIndex,
            toZoneIndex,
            "owner_only",
            "owner_only");
        var engineEvent = new EngineEvent(
            ContractSchemas.EngineEvent,
            $"event_{eventSequence:000000}",
            eventSequence,
            "zone_move",
            state.MatchId,
            state.StateVersion,
            state.TurnNumber,
            request.PlayerId,
            request.ActionType,
            "public",
            ContractJsonValue.From(payload));
        state.Events.Add(engineEvent);
        return AcceptAction(state, request, stateVersionBefore, engineEvent);
    }

    private static ActionResponse ApplyNormalInflow(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore)
    {
        var player = state.GetPlayer(request.PlayerId);
        var payload = ReadNormalInflowPayload(request.Payload);
        if (!state.CardInstances.TryGetValue(payload.CardInstanceId, out var card))
        {
            return RejectAction(
                state,
                request,
                "card_instance_unknown",
                Diagnostic(
                    "NORMAL_INFLOW_CARD_UNKNOWN",
                    "transition_validation",
                    "The selected card is not available.",
                    "The normal_inflow payload references an unknown card_instance_id.",
                    "refresh_projection"));
        }

        if (!string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal))
        {
            return RejectAction(
                state,
                request,
                "card_not_owned_or_controlled",
                Diagnostic(
                    "NORMAL_INFLOW_CARD_AUTHORITY_INVALID",
                    "transition_validation",
                    "The selected card cannot be infused by this player.",
                    "The selected card owner/controller does not match the requesting player.",
                    "refresh_projection"));
        }

        if (!string.Equals(card.Zone, "hand", StringComparison.Ordinal))
        {
            return RejectAction(
                state,
                request,
                "card_not_in_hand",
                Diagnostic(
                    "NORMAL_INFLOW_CARD_ZONE_INVALID",
                    "transition_validation",
                    "The selected card is not in hand.",
                    "The selected card registry zone is not hand.",
                    "refresh_projection"));
        }

        var fromZoneIndex = player.HandCardInstanceIds.IndexOf(card.CardInstanceId);
        if (fromZoneIndex < 0)
        {
            return RejectAction(
                state,
                request,
                "hand_registry_mismatch",
                Diagnostic(
                    "NORMAL_INFLOW_HAND_MEMBERSHIP_INVALID",
                    "transition_validation",
                    "The selected card is not available in hand.",
                    "The card registry says hand, but the requesting player's hand list does not contain it.",
                    "refresh_projection"));
        }

        player.HandCardInstanceIds.RemoveAt(fromZoneIndex);
        ReindexZone(state, player.HandCardInstanceIds, "hand");
        var toZoneIndex = player.WellspringCardInstanceIds.Count;
        player.WellspringCardInstanceIds.Add(card.CardInstanceId);
        card.Zone = "wellspring";
        card.ZoneIndex = toZoneIndex;
        card.Visibility = "owner_only";
        card.ActivityState = "active";
        card.ZoneSequence += 1;
        player.NormalInflowUsedTurnNumber = state.TurnNumber;
        state.StateVersion += 1;

        var eventSequence = state.Events.Count + 1;
        var eventPayload = new ZoneMovePayload(
            request.ActionId,
            request.ActionType,
            card.CardInstanceId,
            card.CardId,
            card.OwnerPlayerId,
            card.ControllerPlayerId,
            "hand",
            "wellspring",
            fromZoneIndex,
            toZoneIndex,
            "owner_only",
            "owner_only");
        var engineEvent = new EngineEvent(
            ContractSchemas.EngineEvent,
            $"event_{eventSequence:000000}",
            eventSequence,
            "zone_move",
            state.MatchId,
            state.StateVersion,
            state.TurnNumber,
            request.PlayerId,
            request.ActionType,
            "public",
            ContractJsonValue.From(eventPayload));
        state.Events.Add(engineEvent);
        return AcceptAction(state, request, stateVersionBefore, engineEvent);
    }

    private static ActionResponse ApplyEndTurn(MatchState state, ActionRequest request, int stateVersionBefore)
    {
        var previousPlayerId = state.ActivePlayerId;
        var nextPlayerId = state.GetNextPlayerId(previousPlayerId);
        var turnBefore = state.TurnNumber;
        if (string.Equals(nextPlayerId, state.Players[0].PlayerId, StringComparison.Ordinal))
        {
            state.TurnNumber += 1;
        }

        state.ActivePlayerId = nextPlayerId;
        state.PriorityPlayerId = nextPlayerId;
        state.StateVersion += 1;
        var eventSequence = state.Events.Count + 1;
        var payload = new TurnTransitionPayload(
            request.ActionId,
            request.ActionType,
            previousPlayerId,
            nextPlayerId,
            previousPlayerId,
            nextPlayerId,
            turnBefore,
            state.TurnNumber,
            state.Phase,
            state.Phase);
        var engineEvent = new EngineEvent(
            ContractSchemas.EngineEvent,
            $"event_{eventSequence:000000}",
            eventSequence,
            "turn_transition",
            state.MatchId,
            state.StateVersion,
            state.TurnNumber,
            previousPlayerId,
            request.ActionType,
            "public",
            ContractJsonValue.From(payload));
        state.Events.Add(engineEvent);
        return AcceptAction(state, request, stateVersionBefore, engineEvent);
    }

    private static ActionResponse AcceptAction(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore,
        EngineEvent engineEvent) => new(
            ContractSchemas.ActionResponse,
            request.RequestId,
            state.MatchId,
            request.PlayerId,
            request.ActionId,
            request.ActionType,
            Accepted: true,
            Reason: null,
            stateVersionBefore,
            state.StateVersion,
            ImmutableArray.Create(CloneEvent(engineEvent)),
            ImmutableArray<EngineDiagnostic>.Empty);

    private static ActionResponse RejectAction(
        MatchState state,
        ActionRequest request,
        string reason,
        EngineDiagnostic diagnostic) => new(
            ContractSchemas.ActionResponse,
            request.RequestId ?? string.Empty,
            state.MatchId,
            request.PlayerId ?? string.Empty,
            request.ActionId ?? string.Empty,
            request.ActionType ?? string.Empty,
            Accepted: false,
            reason,
            state.StateVersion,
            state.StateVersion,
            ImmutableArray<EngineEvent>.Empty,
            ImmutableArray.Create(diagnostic));

    private static ActionResponse RejectMissingActionRequest(MatchState? state) => new(
        ContractSchemas.ActionResponse,
        RequestId: string.Empty,
        MatchId: state?.MatchId ?? string.Empty,
        PlayerId: string.Empty,
        ActionId: string.Empty,
        ActionType: string.Empty,
        Accepted: false,
        Reason: "action_request_missing",
        StateVersionBefore: state?.StateVersion ?? 0,
        StateVersionAfter: state?.StateVersion ?? 0,
        ImmutableArray<EngineEvent>.Empty,
        ImmutableArray.Create(Diagnostic(
            "ACTION_REQUEST_MISSING",
            "request_validation",
            "Action request is required.",
            "The action request is missing, null, or could not be parsed.",
            "fix_request")));

    private static CreateMatchResponse RejectCreateMatch(string? matchId, string code, string message) => new(
        ContractSchemas.CreateMatchResponse,
        Accepted: false,
        matchId,
        RuntimePackageId: null,
        StateVersion: 0,
        ImmutableArray.Create(Diagnostic(
            code,
            "match_creation",
            "The match could not be created.",
            message,
            "fix_request")));

    private static EngineDiagnostic Diagnostic(
        string code,
        string category,
        string safeMessage,
        string developerMessage,
        string retryPolicy,
        IReadOnlyDictionary<string, object?>? details = null) => new(
            ContractSchemas.EngineDiagnostic,
            code,
            "error",
            category,
            Blocking: true,
            safeMessage,
            developerMessage,
            retryPolicy,
            ContractJsonValue.From(details ?? new Dictionary<string, object?>()));

    private static PlayerSnapshotEntry BuildPlayerSnapshotEntry(
        MatchState state,
        PlayerState player,
        string viewerPlayerId,
        WellspringResourceSummary resourceSummary)
    {
        var isViewer = string.Equals(player.PlayerId, viewerPlayerId, StringComparison.Ordinal);
        return new PlayerSnapshotEntry(
            player.PlayerId,
            isViewer ? "self" : "opponent",
            BuildZoneSnapshot(state, "deck", player.DeckCardInstanceIds, "count_only"),
            BuildZoneSnapshot(
                state,
                "hand",
                player.HandCardInstanceIds,
                isViewer ? "owner_visible" : "count_only"),
            BuildZoneSnapshot(state, "discard", player.DiscardCardInstanceIds, "public"),
            BuildWellspringProjection(state, player, isViewer, resourceSummary));
    }

    private static WellspringProjection BuildWellspringProjection(
        MatchState state,
        PlayerState player,
        bool isViewer,
        WellspringResourceSummary resourceSummary)
    {
        var objects = isViewer
            ? player.WellspringCardInstanceIds.Select(cardInstanceId =>
            {
                var card = state.GetCardInstance(cardInstanceId);
                return new WellspringCardProjection(
                    card.CardId,
                    RequireWellspringActivityState(card));
            }).ToImmutableArray()
            : ImmutableArray<WellspringCardProjection>.Empty;
        return new WellspringProjection(
            ContractSchemas.WellspringProjection,
            "wellspring",
            isViewer ? "owner_visible" : "summary_only",
            Redacted: !isViewer,
            resourceSummary.WellspringCardCount,
            resourceSummary.Magnitude,
            resourceSummary.ActiveSourceCount,
            resourceSummary.ExhaustedSourceCount,
            resourceSummary.AvailableAura,
            objects);
    }

    private static WellspringResourceSummary BuildWellspringResourceSummary(
        MatchState state,
        PlayerState player)
    {
        var activeSourceCount = 0;
        var exhaustedSourceCount = 0;
        foreach (var cardInstanceId in player.WellspringCardInstanceIds)
        {
            var card = state.GetCardInstance(cardInstanceId);
            if (string.Equals(RequireWellspringActivityState(card), "active", StringComparison.Ordinal))
            {
                activeSourceCount += 1;
            }
            else
            {
                exhaustedSourceCount += 1;
            }
        }

        var cardCount = player.WellspringCardInstanceIds.Count;
        return new WellspringResourceSummary(
            ContractSchemas.WellspringResourceSummary,
            player.PlayerId,
            cardCount,
            Magnitude: cardCount,
            activeSourceCount,
            exhaustedSourceCount,
            AvailableAura: activeSourceCount);
    }

    private static string RequireWellspringActivityState(CardInstanceState card)
    {
        if (card.ActivityState is not ("active" or "exhausted"))
        {
            throw new EngineStateException("Wellspring card activity state must be active or exhausted.");
        }

        return card.ActivityState;
    }

    private static ZoneSnapshot BuildZoneSnapshot(
        MatchState state,
        string zone,
        IReadOnlyList<string> cardInstanceIds,
        string visibilityMode)
    {
        var visible = visibilityMode is "owner_visible" or "public";
        var objects = visible
            ? cardInstanceIds.Select(cardInstanceId =>
            {
                var card = state.GetCardInstance(cardInstanceId);
                return new CardReference(
                    card.CardInstanceId,
                    card.CardId,
                    card.Zone,
                    card.ZoneSequence,
                    card.ControllerPlayerId,
                    card.Visibility);
            }).ToImmutableArray()
            : ImmutableArray<CardReference>.Empty;
        return new ZoneSnapshot(zone, cardInstanceIds.Count, visibilityMode, !visible, objects);
    }

    private static LegalAction CloneLegalAction(LegalAction action) => action with
    {
        PayloadSchema = ContractJsonValue.Clone(action.PayloadSchema),
    };

    private static EngineEvent CloneEvent(EngineEvent item) => item with
    {
        Payload = ContractJsonValue.Clone(item.Payload),
    };

    private static EngineEvent ProjectEventForViewer(EngineEvent item, string viewerPlayerId)
    {
        if (!string.Equals(item.EventType, "zone_move", StringComparison.Ordinal))
        {
            return CloneEvent(item);
        }

        var ownerPlayerId = ReadEventPayloadString(item.Payload, "owner_player_id");
        if (string.Equals(ownerPlayerId, viewerPlayerId, StringComparison.Ordinal))
        {
            return CloneEvent(item);
        }

        return item with
        {
            Payload = ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["source_action_type"] = ReadEventPayloadString(item.Payload, "source_action_type"),
                ["owner_player_id"] = ownerPlayerId,
                ["from_zone"] = ReadEventPayloadString(item.Payload, "from_zone"),
                ["to_zone"] = ReadEventPayloadString(item.Payload, "to_zone"),
                ["from_zone_count_delta"] = -1,
                ["to_zone_count_delta"] = 1,
                ["identity_redacted"] = true,
            }),
        };
    }

    private static EngineDiagnostic? ValidateActionPayload(ActionRequest request)
    {
        if (request.Payload.ValueKind != JsonValueKind.Object)
        {
            return Diagnostic(
                "ACTION_PAYLOAD_INVALID",
                "request_validation",
                "Action payload must be an object.",
                $"The {request.ActionType ?? "unknown"} payload is missing, null, or not a JSON object.",
                "fix_request");
        }

        if (request.ActionType is "draw_card" or "end_turn"
            && request.Payload.EnumerateObject().Any())
        {
            return Diagnostic(
                "ACTION_PAYLOAD_INVALID",
                "request_validation",
                "Action payload contains unsupported fields.",
                $"The {request.ActionType} action requires an empty payload object in the C.5B scope.",
                "fix_request");
        }

        if (string.Equals(request.ActionType, "normal_inflow", StringComparison.Ordinal))
        {
            var properties = request.Payload.EnumerateObject().ToArray();
            if (properties.Length != 1
                || !string.Equals(properties[0].Name, "card_instance_id", StringComparison.Ordinal)
                || properties[0].Value.ValueKind != JsonValueKind.String
                || string.IsNullOrWhiteSpace(properties[0].Value.GetString()))
            {
                return Diagnostic(
                    "ACTION_PAYLOAD_INVALID",
                    "request_validation",
                    "Normal Inflow requires one selected hand card.",
                    "The normal_inflow payload must contain exactly one non-empty string field: card_instance_id.",
                    "fix_request");
            }
        }

        return null;
    }

    private static JsonElement BuildNormalInflowPayloadSchema() => ContractJsonValue.From(
        new Dictionary<string, object?>
        {
            ["type"] = "object",
            ["required"] = new[] { "card_instance_id" },
            ["additional_properties"] = false,
            ["properties"] = new Dictionary<string, object?>
            {
                ["card_instance_id"] = new Dictionary<string, object?>
                {
                    ["type"] = "string",
                    ["min_length"] = 1,
                    ["source_zone"] = "hand",
                },
            },
        });

    private static NormalInflowActionPayload ReadNormalInflowPayload(JsonElement payload) => new(
        payload.GetProperty("card_instance_id").GetString()!);

    private static string ReadEventPayloadString(JsonElement payload, string propertyName)
    {
        if (payload.ValueKind != JsonValueKind.Object
            || !payload.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw new EngineStateException($"Event payload string is missing: {propertyName}");
        }

        return value.GetString()!;
    }

    private static void ReindexZone(MatchState state, IReadOnlyList<string> cardInstanceIds, string zone)
    {
        for (var index = 0; index < cardInstanceIds.Count; index++)
        {
            var card = state.GetCardInstance(cardInstanceIds[index]);
            card.Zone = zone;
            card.ZoneIndex = index;
        }
    }

    private static PlayerState RequireKnownPlayer(MatchState state, string playerId)
    {
        if (string.IsNullOrWhiteSpace(playerId))
        {
            throw new ArgumentException("Player ID is required.", nameof(playerId));
        }

        return state.Players.SingleOrDefault(player =>
                   string.Equals(player.PlayerId, playerId, StringComparison.Ordinal))
               ?? throw new ArgumentException("Player is not part of this match.", nameof(playerId));
    }

    private MatchState RequireState() => _state
        ?? throw new InvalidOperationException("CreateMatch must succeed before using the engine session.");

    private static void ValidateMagnitudePreflightState(
        MatchState state,
        string playerId,
        string cardInstanceId)
    {
        try
        {
            ValidateState(state);
        }
        catch (EngineStateException exception)
        {
            var player = state.Players.SingleOrDefault(item =>
                string.Equals(item.PlayerId, playerId, StringComparison.Ordinal));
            var handIndex = player?.HandCardInstanceIds.IndexOf(cardInstanceId) ?? -1;
            if (player is not null
                && state.CardInstances.TryGetValue(cardInstanceId, out var card)
                && string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
                && string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal)
                && string.Equals(card.Zone, "hand", StringComparison.Ordinal)
                && (handIndex < 0 || card.ZoneIndex != handIndex))
            {
                throw new MagnitudePreflightException(
                    "MAGNITUDE_PREFLIGHT_HAND_MEMBERSHIP_INVALID",
                    "Magnitude preflight card registry and hand membership disagree.",
                    exception);
            }

            throw new MagnitudePreflightException(
                "MAGNITUDE_PREFLIGHT_STATE_INVALID",
                "Magnitude preflight requires a valid match state.",
                exception);
        }
    }

    private RuntimePackageCatalog RequireAuraPaymentRuntimePackage(MatchState state)
    {
        var runtimePackage = _runtimePackage
            ?? throw new AuraPaymentException(
                "AURA_PAYMENT_RUNTIME_PACKAGE_MISSING",
                "Aura payment requires a validated runtime package catalog.");
        try
        {
            RuntimePackageLoader.ValidateCatalog(runtimePackage);
        }
        catch (EngineInputException exception)
        {
            throw new AuraPaymentException(
                "AURA_PAYMENT_RUNTIME_PACKAGE_INVALID",
                "Aura payment runtime package catalog is invalid.",
                exception);
        }

        if (!string.Equals(runtimePackage.PackageId, state.RuntimePackageId, StringComparison.Ordinal))
        {
            throw new AuraPaymentException(
                "AURA_PAYMENT_RUNTIME_PACKAGE_INVALID",
                "Aura payment runtime package does not match the current state.");
        }

        return runtimePackage;
    }

    private static void ValidateAuraPaymentPreflightState(
        MatchState state,
        string playerId,
        string cardInstanceId)
    {
        try
        {
            ValidateState(state);
        }
        catch (EngineStateException exception)
        {
            var player = state.Players.SingleOrDefault(item =>
                string.Equals(item.PlayerId, playerId, StringComparison.Ordinal));
            var handIndex = player?.HandCardInstanceIds.IndexOf(cardInstanceId) ?? -1;
            if (player is not null
                && !string.IsNullOrWhiteSpace(cardInstanceId)
                && state.CardInstances.TryGetValue(cardInstanceId, out var card)
                && string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
                && string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal)
                && string.Equals(card.Zone, "hand", StringComparison.Ordinal)
                && (handIndex < 0 || card.ZoneIndex != handIndex))
            {
                throw new AuraPaymentException(
                    "AURA_PAYMENT_HAND_MEMBERSHIP_INVALID",
                    "Aura payment target registry and hand membership disagree.",
                    exception);
            }

            throw new AuraPaymentException(
                "AURA_PAYMENT_STATE_INVALID",
                "Aura payment requires a valid match state.",
                exception);
        }
    }

    private static bool IsAuraSourceRealmEligible(
        RuntimeCardDefinition targetDefinition,
        string sourceRealm) =>
        string.Equals(sourceRealm, targetDefinition.Realm, StringComparison.Ordinal)
        || string.Equals(targetDefinition.CardType, "entity", StringComparison.Ordinal)
        && string.Equals(sourceRealm, "aether", StringComparison.Ordinal);

    private static AuraPaymentSelectionValidationResult BuildAuraPaymentSelectionResult(
        AuraPaymentPreflightResult preflight,
        bool selectionValid,
        string? failureReason,
        ImmutableArray<string> resolvedSourceInstanceIds) => new(
            preflight.PlayerId,
            preflight.CardInstanceId,
            preflight.NormalizedPayableAuraCost,
            preflight.SelectionMode,
            selectionValid,
            failureReason,
            resolvedSourceInstanceIds);

    internal static void ValidateState(MatchState state)
    {
        var zoneIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var player in state.Players)
        {
            if (player.NormalInflowUsedTurnNumber is int usedTurnNumber
                && (usedTurnNumber <= 0 || usedTurnNumber > state.TurnNumber))
            {
                throw new EngineStateException(
                    "Normal Inflow used turn number must be positive and cannot be in the future.");
            }

            foreach (var cardInstanceId in player.HandCardInstanceIds
                         .Concat(player.DeckCardInstanceIds)
                         .Concat(player.DiscardCardInstanceIds)
                         .Concat(player.WellspringCardInstanceIds))
            {
                if (!zoneIds.Add(cardInstanceId))
                {
                    throw new EngineStateException("Card instance appears in multiple zones.");
                }

                if (!state.CardInstances.ContainsKey(cardInstanceId))
                {
                    throw new EngineStateException("Zone references an unknown card instance.");
                }
            }

            ValidateHandState(state, player);
            ValidateWellspringState(state, player);
        }

        if (!zoneIds.SetEquals(state.CardInstances.Keys))
        {
            throw new EngineStateException("Card instance registry and zones disagree.");
        }

        var listedWellspringIds = state.Players
            .SelectMany(player => player.WellspringCardInstanceIds)
            .ToHashSet(StringComparer.Ordinal);
        var registeredWellspringIds = state.CardInstances.Values
            .Where(card => string.Equals(card.Zone, "wellspring", StringComparison.Ordinal))
            .Select(card => card.CardInstanceId)
            .ToHashSet(StringComparer.Ordinal);
        if (!listedWellspringIds.SetEquals(registeredWellspringIds))
        {
            throw new EngineStateException("Card instance registry and Wellspring zones disagree.");
        }

        var listedHandIds = state.Players
            .SelectMany(player => player.HandCardInstanceIds)
            .ToHashSet(StringComparer.Ordinal);
        var registeredHandIds = state.CardInstances.Values
            .Where(card => string.Equals(card.Zone, "hand", StringComparison.Ordinal))
            .Select(card => card.CardInstanceId)
            .ToHashSet(StringComparer.Ordinal);
        if (!listedHandIds.SetEquals(registeredHandIds))
        {
            throw new EngineStateException("Card instance registry and Hand zones disagree.");
        }

        if (state.Players.All(player =>
                !string.Equals(player.PlayerId, state.ActivePlayerId, StringComparison.Ordinal)))
        {
            throw new EngineStateException("Active player is unknown.");
        }

        if (state.Players.All(player =>
                !string.Equals(player.PlayerId, state.PriorityPlayerId, StringComparison.Ordinal)))
        {
            throw new EngineStateException("Priority player is unknown.");
        }

        if (state.Events.Select(item => item.EventSequence)
            .Where((sequence, index) => sequence != index + 1)
            .Any())
        {
            throw new EngineStateException("Event sequence is not contiguous.");
        }
    }

    private static void ValidateHandState(MatchState state, PlayerState player)
    {
        for (var zoneIndex = 0; zoneIndex < player.HandCardInstanceIds.Count; zoneIndex++)
        {
            var card = state.GetCardInstance(player.HandCardInstanceIds[zoneIndex]);
            if (!string.Equals(card.Zone, "hand", StringComparison.Ordinal))
            {
                throw new EngineStateException("Hand card zone must be hand.");
            }

            if (card.ZoneIndex != zoneIndex)
            {
                throw new EngineStateException("Hand card zone index must match list order.");
            }

            if (!string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
                || !string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal))
            {
                throw new EngineStateException("Hand card owner and controller must match the player state.");
            }

            if (!string.Equals(card.Visibility, "owner_only", StringComparison.Ordinal))
            {
                throw new EngineStateException("Hand card visibility must be owner_only.");
            }

            if (card.ActivityState is not null)
            {
                throw new EngineStateException("Hand card activity state must be null.");
            }
        }
    }

    private static void ValidateWellspringState(MatchState state, PlayerState player)
    {
        var activeSourceCount = 0;
        var exhaustedSourceCount = 0;
        for (var zoneIndex = 0; zoneIndex < player.WellspringCardInstanceIds.Count; zoneIndex++)
        {
            var card = state.GetCardInstance(player.WellspringCardInstanceIds[zoneIndex]);
            if (!string.Equals(card.Zone, "wellspring", StringComparison.Ordinal))
            {
                throw new EngineStateException("Wellspring card zone must be wellspring.");
            }

            if (card.ZoneIndex != zoneIndex)
            {
                throw new EngineStateException("Wellspring card zone index must match list order.");
            }

            if (!string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal))
            {
                throw new EngineStateException("Wellspring card controller must match the player state.");
            }

            if (!string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal))
            {
                throw new EngineStateException("Wellspring card owner must match the player state.");
            }

            if (!string.Equals(card.Visibility, "owner_only", StringComparison.Ordinal))
            {
                throw new EngineStateException("Wellspring card visibility must be owner_only.");
            }

            switch (card.ActivityState)
            {
                case "active":
                    activeSourceCount += 1;
                    break;
                case "exhausted":
                    exhaustedSourceCount += 1;
                    break;
                default:
                    throw new EngineStateException(
                        "Wellspring card activity state must be active or exhausted.");
            }
        }

        if (activeSourceCount + exhaustedSourceCount != player.WellspringCardInstanceIds.Count)
        {
            throw new EngineStateException(
                "Wellspring active and exhausted source counts must equal the card count.");
        }
    }
}

public sealed class EngineStateException : Exception
{
    public EngineStateException(string message)
        : base(message)
    {
    }
}
