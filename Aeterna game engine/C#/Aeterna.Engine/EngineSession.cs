using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Rules;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

namespace Aeterna.Engine;

public sealed class EngineSession
{
    // Transitional production migration boundary. The official phase name is
    // Manifesztáció, but the current production state contract still uses "main".
    private const string TransitionalMainPhase = "main";

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
    private CanonicalAbilityRuntimeContext? _canonicalRuntime;
    private ImmutableArray<CanonicalTriggeredAbilityDiscovery> _canonicalTriggerDiscoveries =
        ImmutableArray<CanonicalTriggeredAbilityDiscovery>.Empty;
    private ImmutableArray<CanonicalAbilityResolutionRecord> _canonicalAbilityResolutions =
        ImmutableArray<CanonicalAbilityResolutionRecord>.Empty;

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
        : this(initialState, runtimePackage, canonicalAbilities: null)
    {
    }

    internal EngineSession(
        MatchState initialState,
        RuntimePackageCatalog runtimePackage,
        CanonicalAbilityCatalog? canonicalAbilities)
        : this(initialState, runtimePackage, canonicalAbilities, canonicalCards: null)
    {
    }

    internal EngineSession(
        MatchState initialState,
        RuntimePackageCatalog runtimePackage,
        CanonicalAbilityCatalog? canonicalAbilities,
        CanonicalCardCatalog? canonicalCards)
    {
        ArgumentNullException.ThrowIfNull(initialState);
        ArgumentNullException.ThrowIfNull(runtimePackage);
        ValidateState(initialState, canonicalCards, canonicalAbilities);
        RuntimePackageLoader.ValidateCatalog(runtimePackage);
        if (!string.Equals(initialState.RuntimePackageId, runtimePackage.PackageId, StringComparison.Ordinal))
        {
            throw new EngineInputException(
                "RUNTIME_PACKAGE_ID_MISMATCH",
                "Runtime package catalog does not match the initial state.");
        }

        _state = initialState;
        _runtimePackage = runtimePackage;
        if (canonicalAbilities is not null)
        {
            _canonicalRuntime = new CanonicalAbilityRuntimeContext(
                "injected-registry",
                "0.0.0",
                "0.0.0",
                "injected-carddatabase",
                "0.0.0",
                "0.0.0",
                CanonicalPackageValidationMode.Development,
                canonicalCards,
                canonicalAbilities);
        }
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

        if (_state is not null || _runtimePackage is not null || _canonicalRuntime is not null)
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
            var canonicalRuntime = LoadCanonicalRuntime(request.CanonicalData);
            canonicalRuntime?.Cards?.ValidateRuntimeOverlap(package);
            ValidateState(state, canonicalRuntime?.Cards, canonicalRuntime?.Abilities);
            _state = state;
            _runtimePackage = package;
            _canonicalRuntime = canonicalRuntime;
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
        ValidateState(state, _canonicalRuntime?.Cards, _canonicalRuntime?.Abilities);
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
            ContractJsonValue.From(BuildDomainBoardProjection(state)),
            new ResourceSummary(ContractSchemas.ResourceSummary, resourceSummaries),
            BuildPendingTriggerSummary(state),
            state.Result);
    }

    public LegalActionSpace ListLegalActions(string playerId, bool includeDisabled = false)
    {
        var state = RequireState();
        ValidateState(state, _canonicalRuntime?.Cards, _canonicalRuntime?.Abilities);
        var player = RequireKnownPlayer(state, playerId);
        if (state.PendingTriggerWindow is not null)
        {
            return BuildPendingTriggerLegalActionSpace(state, player, includeDisabled);
        }

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
        var playCardAvailability = EvaluatePlayCardAvailability(state, player, active);
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
                $"play_card:{state.TurnNumber}:{state.StateVersion}:{playerId}",
                "play_card",
                playerId,
                playCardAvailability.Enabled,
                175,
                playCardAvailability.DisabledReason,
                BuildPlayCardPayloadSchema(state, player)),
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

    private LegalActionSpace BuildPendingTriggerLegalActionSpace(
        MatchState state,
        PlayerState player,
        bool includeDisabled)
    {
        // Temporary production migration boundary: unresolved mandatory canonical
        // triggers gate normal gameplay until the future reaction/priority engine
        // replaces this narrow controller-only window.
        var window = state.PendingTriggerWindow
            ?? throw new EngineStateException("Pending trigger legal action space requires a pending window.");
        var isController = string.Equals(
            player.PlayerId,
            window.ControllerPlayerId,
            StringComparison.Ordinal);
        var blockedReason = "pending_trigger_resolution_required";
        var actions = new[]
        {
            new LegalAction(
                $"resolve_triggered_ability:{state.StateVersion}:{player.PlayerId}",
                "resolve_triggered_ability",
                player.PlayerId,
                isController,
                50,
                isController ? null : "not_pending_trigger_controller",
                isController
                    ? BuildResolveTriggeredAbilityPayloadSchema(state, window)
                    : BuildUnavailableResolveTriggeredAbilityPayloadSchema()),
            new LegalAction(
                $"end_turn:{state.TurnNumber}:{player.PlayerId}",
                "end_turn",
                player.PlayerId,
                Enabled: false,
                100,
                blockedReason,
                ContractJsonValue.EmptyObject()),
            new LegalAction(
                $"normal_inflow:{state.TurnNumber}:{state.StateVersion}:{player.PlayerId}",
                "normal_inflow",
                player.PlayerId,
                Enabled: false,
                150,
                blockedReason,
                BuildNormalInflowPayloadSchema()),
            new LegalAction(
                $"play_card:{state.TurnNumber}:{state.StateVersion}:{player.PlayerId}",
                "play_card",
                player.PlayerId,
                Enabled: false,
                175,
                blockedReason,
                BuildPlayCardPayloadSchema(state, player)),
            new LegalAction(
                $"draw_card:{state.TurnNumber}:{state.StateVersion}:{player.PlayerId}",
                "draw_card",
                player.PlayerId,
                Enabled: false,
                200,
                blockedReason,
                ContractJsonValue.EmptyObject()),
        };
        var ordered = actions
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
            player.PlayerId,
            ordered);
    }

    private JsonElement BuildResolveTriggeredAbilityPayloadSchema(
        MatchState state,
        PendingTriggerWindowState window)
    {
        var canonicalRuntime = _canonicalRuntime
            ?? throw new EngineStateException("Pending trigger window has no canonical runtime context.");
        var runtimePackage = _runtimePackage
            ?? throw new EngineStateException("Pending trigger window has no gameplay runtime package.");
        var options = window.PendingTriggers.Select(pending =>
        {
            var ability = canonicalRuntime.Abilities.AbilitiesById[pending.AbilityId];
            var targetContracts = CanonicalTargetResolver.GetSupportedTargets(ability)
                .Select(target => new Dictionary<string, object?>
                {
                    ["target_id"] = target.TargetId,
                    ["minimum_targets"] = target.MinimumTargets,
                    ["maximum_targets"] = target.MaximumTargets,
                    ["selection_method_id"] = target.SelectionMethodId,
                    ["candidate_card_instance_ids"] = CanonicalTargetResolver.ResolveCandidates(
                            target,
                            ability,
                            pending.ControllerPlayerId,
                            state,
                            runtimePackage,
                            canonicalRuntime.Cards)
                        .Select(candidate => candidate.CardInstanceId)
                        .ToArray(),
                }).ToArray();
            return new Dictionary<string, object?>
            {
                ["pending_trigger_id"] = pending.PendingTriggerId,
                ["ability_id"] = pending.AbilityId,
                ["source_card_instance_id"] = pending.SourceCardInstanceId,
                ["source_card_id"] = pending.SourceCardId,
                ["target_contracts"] = targetContracts,
            };
        }).ToArray();
        return ContractJsonValue.From(new Dictionary<string, object?>
        {
            ["type"] = "object",
            ["required"] = new[] { "pending_trigger_id", "target_selections" },
            ["additional_properties"] = false,
            ["properties"] = new Dictionary<string, object?>
            {
                ["pending_trigger_id"] = new Dictionary<string, object?>
                {
                    ["type"] = "string",
                    ["enum"] = window.PendingTriggers.Select(item => item.PendingTriggerId).ToArray(),
                },
                ["target_selections"] = new Dictionary<string, object?>
                {
                    ["type"] = "array",
                    ["items"] = new Dictionary<string, object?>
                    {
                        ["type"] = "object",
                        ["required"] = new[] { "target_id", "card_instance_ids" },
                        ["additional_properties"] = false,
                    },
                },
            },
            ["pending_trigger_options"] = options,
        });
    }

    private static JsonElement BuildUnavailableResolveTriggeredAbilityPayloadSchema() =>
        ContractJsonValue.From(new Dictionary<string, object?>
        {
            ["type"] = "object",
            ["available"] = false,
        });

    private static JsonElement BuildPendingTriggerSummary(MatchState state)
    {
        var window = state.PendingTriggerWindow;
        if (window is null)
        {
            return ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["has_pending"] = false,
            });
        }

        return ContractJsonValue.From(new Dictionary<string, object?>
        {
            ["has_pending"] = true,
            ["pending_type"] = "triggered_ability",
            ["pending_window_id"] = window.PendingWindowId,
            ["controller_player_id"] = window.ControllerPlayerId,
            ["pending_trigger_count"] = window.PendingTriggers.Count,
            ["pending_triggers"] = window.PendingTriggers.Select(pending => new Dictionary<string, object?>
            {
                ["pending_trigger_id"] = pending.PendingTriggerId,
                ["ability_id"] = pending.AbilityId,
                ["trigger_id"] = pending.TriggerId,
                ["source_card_instance_id"] = pending.SourceCardInstanceId,
                ["source_card_id"] = pending.SourceCardId,
            }).ToArray(),
        });
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

        var disabledPlayMayUseDetailedValidation = string.Equals(
                action.ActionType,
                "play_card",
                StringComparison.Ordinal)
            && state.PendingTriggerWindow is null;
        if (!action.Enabled
            && !disabledPlayMayUseDetailedValidation
            && !string.Equals(action.ActionType, "resolve_triggered_ability", StringComparison.Ordinal))
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
            "play_card" => ApplyPlayCard(state, request, stateVersionBefore),
            "resolve_triggered_ability" => ApplyResolveTriggeredAbility(state, request, stateVersionBefore),
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
        ValidateState(state, _canonicalRuntime?.Cards, _canonicalRuntime?.Abilities);
        var triggerEvents = DiscoverCanonicalTriggers(state, response.Events);
        ValidateState(state, _canonicalRuntime?.Cards, _canonicalRuntime?.Abilities);
        return triggerEvents.IsDefaultOrEmpty
            ? response
            : response with { Events = response.Events.AddRange(triggerEvents) };
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
                player.VoidCardInstanceIds.ToImmutableArray(),
                player.WellspringCardInstanceIds.ToImmutableArray(),
                player.Domain.HorizonCardInstanceIds.ToImmutableArray(),
                player.Domain.ZenithCardInstanceIds.ToImmutableArray(),
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
                    card.ActivityState,
                    card.DomainRow?.ToString().ToLowerInvariant(),
                    card.DomainLaneIndex,
                    card.EnteredDomainTurnNumber,
                    card.DamageMarked))
                .ToImmutableArray(),
            state.ModifierInstances.Values
                .OrderBy(instance => instance.CreatedSequence)
                .ThenBy(instance => instance.ModifierInstanceId, StringComparer.Ordinal)
                .Select(instance => new DebugModifierInstanceSnapshot(
                    instance.ModifierInstanceId,
                    instance.SourceAbilityId,
                    instance.SourceEffectId,
                    instance.SourceResolutionId,
                    instance.SourceCardInstanceId,
                    instance.ControllerPlayerId,
                    instance.TargetCardInstanceId,
                    instance.TargetZoneSequence,
                    instance.ModifierTypeId,
                    instance.AffectedFieldId,
                    instance.IntegerValue,
                    instance.DurationId,
                    instance.DurationPolicyId,
                    instance.DurationInstanceId,
                    instance.TurnInstanceId,
                    instance.PhaseInstanceId,
                    instance.CreatedTurnNumber,
                    instance.CreatedActivePlayerId,
                    instance.CreatedStateVersion,
                    instance.CreatedSequence))
                .ToImmutableArray(),
            state.KeywordGrantInstances.Values
                .OrderBy(instance => instance.CreatedSequence)
                .ThenBy(instance => instance.KeywordGrantInstanceId, StringComparer.Ordinal)
                .Select(instance => new DebugKeywordGrantInstanceSnapshot(
                    instance.KeywordGrantInstanceId,
                    instance.SourceAbilityId,
                    instance.SourceEffectId,
                    instance.SourceResolutionId,
                    instance.SourceCardInstanceId,
                    instance.ControllerPlayerId,
                    instance.TargetCardInstanceId,
                    instance.TargetZoneSequence,
                    instance.KeywordId,
                    instance.DurationId,
                    instance.DurationPolicyId,
                    instance.DurationInstanceId,
                    instance.TurnInstanceId,
                    instance.PhaseInstanceId,
                    instance.CreatedTurnNumber,
                    instance.CreatedActivePlayerId,
                    instance.CreatedStateVersion,
                    instance.CreatedSequence))
                .ToImmutableArray(),
            state.Events.Select(CloneEvent).ToImmutableArray(),
            BuildPendingTriggerSummary(state),
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

    internal CanonicalAbilityRuntimeStatus GetDebugCanonicalAbilityRuntimeStatus()
    {
        var runtime = _canonicalRuntime;
        return runtime is null
            ? new CanonicalAbilityRuntimeStatus(false, null, null, null, 0)
            : new CanonicalAbilityRuntimeStatus(
                true,
                runtime.RegistryPackageId,
                runtime.CardDatabasePackageId,
                runtime.ValidationMode,
                runtime.Abilities.AbilitiesById.Count);
    }

    internal ImmutableArray<CanonicalTriggeredAbilityDiscovery> GetDebugCanonicalTriggerDiscoveries() =>
        _canonicalTriggerDiscoveries;

    internal ImmutableArray<CanonicalAbilityResolutionRecord> GetDebugCanonicalAbilityResolutions() =>
        _canonicalAbilityResolutions;

    internal ImmutableArray<EngineDiagnostic> GetDebugInvariantDiagnostics()
    {
        try
        {
            ValidateState(RequireState(), _canonicalRuntime?.Cards, _canonicalRuntime?.Abilities);
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
        ValidateMagnitudePreflightState(state, playerId, cardInstanceId, _canonicalRuntime?.Cards);
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
        ValidateAuraPaymentPreflightState(state, playerId, cardInstanceId, _canonicalRuntime?.Cards);
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

    private PlayCardAvailability EvaluatePlayCardAvailability(
        MatchState state,
        PlayerState player,
        bool active)
    {
        if (!active)
        {
            return new PlayCardAvailability(false, "not_active_player");
        }

        if (!string.Equals(state.Phase, TransitionalMainPhase, StringComparison.Ordinal))
        {
            return new PlayCardAvailability(false, "phase_not_main");
        }

        if (_runtimePackage is null)
        {
            return new PlayCardAvailability(false, "runtime_package_missing");
        }

        try
        {
            RuntimePackageLoader.ValidateCatalog(_runtimePackage);
        }
        catch (EngineInputException)
        {
            return new PlayCardAvailability(false, "runtime_package_invalid");
        }

        if (!string.Equals(_runtimePackage.PackageId, state.RuntimePackageId, StringComparison.Ordinal))
        {
            return new PlayCardAvailability(false, "runtime_package_invalid");
        }

        return BuildPlayableCardOptions(state, player).Length > 0
            ? new PlayCardAvailability(true, null)
            : new PlayCardAvailability(false, "no_playable_card");
    }

    private ImmutableArray<PlayCardOption> BuildPlayableCardOptions(
        MatchState state,
        PlayerState player)
    {
        var runtimePackage = _runtimePackage;
        if (runtimePackage is null)
        {
            return ImmutableArray<PlayCardOption>.Empty;
        }

        var options = ImmutableArray.CreateBuilder<PlayCardOption>();
        foreach (var cardInstanceId in player.HandCardInstanceIds)
        {
            var card = state.GetCardInstance(cardInstanceId);
            if (!runtimePackage.Cards.TryGetValue(card.CardId, out var definition))
            {
                continue;
            }

            MagnitudePreflightResult magnitude;
            AuraPaymentPreflightResult aura;
            try
            {
                magnitude = EvaluateMagnitudePreflight(player.PlayerId, card.CardInstanceId);
                aura = EvaluateAuraPaymentPreflight(player.PlayerId, card.CardInstanceId);
            }
            catch (MagnitudePreflightException)
            {
                continue;
            }
            catch (AuraPaymentException)
            {
                continue;
            }

            if (!magnitude.RequirementMet || !aura.PaymentPossible)
            {
                continue;
            }

            if (string.Equals(definition.CardType, "entity", StringComparison.Ordinal))
            {
                var placements = new[] { DomainRow.Horizon, DomainRow.Zenith }
                    .SelectMany(row => player.Domain.GetSlots(row)
                        .Select((occupant, laneIndex) => new { occupant, laneIndex })
                        .Where(slot => slot.occupant is null)
                        .Select(slot => new PlayCardPlacementOption(row, slot.laneIndex)))
                    .ToImmutableArray();
                if (placements.Length > 0)
                {
                    options.Add(new PlayCardOption(
                        card,
                        definition,
                        magnitude,
                        aura,
                        placements,
                        ResolutionAbility: null,
                        ImmutableArray<PlayCardTargetContractOption>.Empty));
                }

                continue;
            }

            if (definition.CardType is not ("incantation" or "ritual")
                || _canonicalRuntime is null
                || !_canonicalRuntime.Abilities.AbilitiesByCardId.TryGetValue(
                    card.CardId,
                    out var abilities))
            {
                continue;
            }

            var resolutionAbilities = abilities.Where(ability =>
                    string.Equals(ability.Status, "active", StringComparison.Ordinal)
                    && string.Equals(ability.AbilityKindId, "resolution", StringComparison.Ordinal))
                .ToImmutableArray();
            if (resolutionAbilities.Length != 1)
            {
                continue;
            }

            var resolutionAbility = resolutionAbilities[0];
            try
            {
                CanonicalEffectExecutor.ValidateSupportedPlayedCardGraph(resolutionAbility);
                var contracts = CanonicalTargetResolver.GetSupportedTargets(resolutionAbility)
                    .Select(target => new PlayCardTargetContractOption(
                        target,
                        CanonicalTargetResolver.ResolveCandidates(
                            target,
                            resolutionAbility,
                            player.PlayerId,
                            state,
                            runtimePackage,
                            _canonicalRuntime.Cards)))
                    .ToImmutableArray();
                if (contracts.All(contract =>
                        contract.Candidates.Length >= contract.Definition.MinimumTargets))
                {
                    options.Add(new PlayCardOption(
                        card,
                        definition,
                        magnitude,
                        aura,
                        ImmutableArray<PlayCardPlacementOption>.Empty,
                        resolutionAbility,
                        contracts));
                }
            }
            catch (CanonicalAbilityExecutionException)
            {
                // Unsupported canonical candidates remain explicit unavailable edges.
            }
        }

        return options.ToImmutable();
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

    private static CanonicalAbilityRuntimeContext? LoadCanonicalRuntime(CanonicalRuntimeSource? source)
    {
        if (source is null)
        {
            return null;
        }

        if (string.IsNullOrWhiteSpace(source.RegistryPackageDirectory)
            || string.IsNullOrWhiteSpace(source.CardDatabasePackageDirectory)
            || string.IsNullOrWhiteSpace(source.ValidationMode))
        {
            throw new EngineInputException(
                "CANONICAL_RUNTIME_SOURCE_INVALID",
                "Canonical runtime source directories and validation_mode are required.");
        }

        var validationMode = source.ValidationMode switch
        {
            "production" => CanonicalPackageValidationMode.Production,
            "development" => CanonicalPackageValidationMode.Development,
            _ => throw new EngineInputException(
                "CANONICAL_RUNTIME_SOURCE_INVALID",
                "Canonical runtime validation_mode must be production or development."),
        };

        CanonicalRegistryPackage registry;
        CanonicalCardDatabasePackage cardDatabase;
        try
        {
            registry = CanonicalPackageLoader.LoadRegistry(source.RegistryPackageDirectory, validationMode);
            cardDatabase = CanonicalPackageLoader.LoadCardDatabase(
                source.CardDatabasePackageDirectory,
                registry,
                validationMode);
        }
        catch (EngineInputException exception)
        {
            throw new EngineInputException(
                "CANONICAL_RUNTIME_LOAD_FAILED",
                $"Canonical runtime package loading failed with {exception.Code}: {exception.Message}",
                exception);
        }
        catch (Exception exception) when (exception is IOException
            or UnauthorizedAccessException
            or ArgumentException
            or NotSupportedException)
        {
            throw new EngineInputException(
                "CANONICAL_RUNTIME_LOAD_FAILED",
                "Canonical runtime package loading failed.",
                exception);
        }

        CanonicalCardCatalog cards;
        CanonicalAbilityCatalog abilities;
        try
        {
            cards = CanonicalCardMaterializer.Materialize(cardDatabase);
            abilities = CanonicalAbilityMaterializer.Materialize(cardDatabase);
        }
        catch (EngineInputException exception)
        {
            throw new EngineInputException(
                "CANONICAL_RUNTIME_MATERIALIZATION_FAILED",
                $"Canonical ability materialization failed with {exception.Code}: {exception.Message}",
                exception);
        }

        return new CanonicalAbilityRuntimeContext(
            registry.PackageId,
            registry.SchemaVersion,
            registry.DataVersion,
            cardDatabase.PackageId,
            cardDatabase.SchemaVersion,
            cardDatabase.DataVersion,
            validationMode,
            cards,
            abilities);
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

    private ActionResponse ApplyPlayCard(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore)
    {
        PlayCardPlan plan;
        try
        {
            plan = BuildPlayCardPlan(state, request);
        }
        catch (PlayCardValidationException exception)
        {
            return RejectAction(
                state,
                request,
                exception.Reason,
                Diagnostic(
                    exception.Code,
                    "transition_validation",
                    exception.SafeMessage,
                    exception.Message,
                    exception.RetryPolicy));
        }

        var events = BuildPlayCardEvents(state, request, plan);

        // Commit contains no normal rule rejection: every authoritative input used
        // below was revalidated while building the immutable transition plan.
        foreach (var source in plan.AuraSources)
        {
            source.ActivityState = "exhausted";
        }

        if (plan.Resolution is null)
        {
            var domainRow = plan.DomainRow
                ?? throw new EngineStateException("Entity play plan has no Domain row.");
            var laneIndex = plan.LaneIndex
                ?? throw new EngineStateException("Entity play plan has no Domain lane.");
            plan.Player.HandCardInstanceIds.RemoveAt(plan.HandIndex);
            ReindexZone(state, plan.Player.HandCardInstanceIds, "hand");
            plan.Player.Domain.GetSlots(domainRow)[laneIndex] = plan.Card.CardInstanceId;
            plan.Card.Zone = "dominion";
            plan.Card.ZoneIndex = -1;
            plan.Card.Visibility = "public";
            plan.Card.ActivityState = "active";
            plan.Card.DomainRow = domainRow;
            plan.Card.DomainLaneIndex = laneIndex;
            plan.Card.EnteredDomainTurnNumber = state.TurnNumber;
            plan.Card.ZoneSequence += 1;
        }
        else
        {
            CanonicalEffectExecutor.Apply(state, plan.Resolution.EffectPlan);
            plan.Player.HandCardInstanceIds.RemoveAt(plan.HandIndex);
            ReindexZone(state, plan.Player.HandCardInstanceIds, "hand");
            plan.Card.Zone = "void";
            plan.Card.ZoneIndex = plan.Player.VoidCardInstanceIds.Count;
            plan.Card.Visibility = "public";
            plan.Card.ActivityState = null;
            plan.Card.DomainRow = null;
            plan.Card.DomainLaneIndex = null;
            plan.Card.EnteredDomainTurnNumber = null;
            plan.Card.ZoneSequence += 1;
            plan.Player.VoidCardInstanceIds.Add(plan.Card.CardInstanceId);
            var context = plan.Resolution.EffectPlan.Context;
            _canonicalAbilityResolutions = _canonicalAbilityResolutions.Add(
                new CanonicalAbilityResolutionRecord(
                    context.ResolutionId,
                    CanonicalEffectExecutor.OriginId(context.Origin),
                    context.Ability.AbilityId,
                    context.SourceCardInstanceId,
                    context.SourceCardId,
                    context.ControllerPlayerId,
                    CanonicalEffectExecutor.AppliedOutcome,
                    plan.Resolution.EffectPlan.AppliedMutationCount,
                    context.SourceActionId,
                    context.PendingTriggerId,
                    context.TriggerId));
        }

        state.StateVersion += 1;
        state.Events.AddRange(events);
        return AcceptAction(state, request, stateVersionBefore, events);
    }

    private ImmutableArray<EngineEvent> DiscoverCanonicalTriggers(
        MatchState state,
        ImmutableArray<EngineEvent> committedEvents)
    {
        var canonicalRuntime = _canonicalRuntime;
        if (canonicalRuntime is null || committedEvents.IsDefaultOrEmpty)
        {
            return ImmutableArray<EngineEvent>.Empty;
        }

        var runtimePackage = _runtimePackage
            ?? throw new EngineStateException(
                "CANONICAL_RUNTIME_LEGACY_PACKAGE_MISSING",
                "Canonical trigger promotion requires the validated gameplay runtime package.");
        var consequenceEvents = ImmutableArray.CreateBuilder<EngineEvent>();
        foreach (var engineEvent in committedEvents)
        {
            var discoveries = CanonicalTriggerResolver.Resolve(
                canonicalRuntime.Abilities,
                engineEvent,
                state);
            _canonicalTriggerDiscoveries = _canonicalTriggerDiscoveries.AddRange(discoveries);
            foreach (var discovery in discoveries)
            {
                var ability = canonicalRuntime.Abilities.AbilitiesById[discovery.AbilityId];
                if (!CanonicalEffectExecutor.IsSupportedGraph(ability))
                {
                    continue;
                }

                var targets = CanonicalTargetResolver.GetSupportedTargets(ability);
                var hasRequiredLegalTargets = targets.All(target =>
                    CanonicalTargetResolver.ResolveCandidates(
                        target,
                        ability,
                        discovery.ControllerPlayerId,
                        state,
                        runtimePackage,
                        canonicalRuntime.Cards).Length >= target.MinimumTargets);
                var pendingTriggerId = CreatePendingTriggerId(discovery, engineEvent);
                consequenceEvents.Add(CreateCanonicalRuntimeEvent(
                    state,
                    consequenceEvents.Count,
                    "canonical_ability_triggered",
                    discovery.ControllerPlayerId,
                    engineEvent.CauseActionType,
                    ContractJsonValue.From(new CanonicalAbilityTriggeredPayload(
                        pendingTriggerId,
                        discovery.AbilityId,
                        discovery.TriggerId,
                        discovery.SourceCardInstanceId,
                        discovery.SourceCardId,
                        discovery.ControllerPlayerId,
                        engineEvent.EventId,
                        engineEvent.EventSequence,
                        discovery.CanonicalEventTypeId))));

                if (!hasRequiredLegalTargets)
                {
                    consequenceEvents.Add(CreateCanonicalRuntimeEvent(
                        state,
                        consequenceEvents.Count,
                        "canonical_ability_resolved",
                        discovery.ControllerPlayerId,
                        engineEvent.CauseActionType,
                        ContractJsonValue.From(new CanonicalAbilityResolvedPayload(
                            pendingTriggerId,
                            CanonicalEffectExecutor.TriggeredAbilityOriginId,
                            discovery.AbilityId,
                            discovery.SourceCardInstanceId,
                            discovery.SourceCardId,
                            discovery.ControllerPlayerId,
                            CanonicalEffectExecutor.NoLegalTargetOutcome,
                            0,
                            null,
                            pendingTriggerId,
                            discovery.TriggerId))));
                    _canonicalAbilityResolutions = _canonicalAbilityResolutions.Add(
                        new CanonicalAbilityResolutionRecord(
                            pendingTriggerId,
                            CanonicalEffectExecutor.TriggeredAbilityOriginId,
                            discovery.AbilityId,
                            discovery.SourceCardInstanceId,
                            discovery.SourceCardId,
                            discovery.ControllerPlayerId,
                            CanonicalEffectExecutor.NoLegalTargetOutcome,
                            0,
                            null,
                            pendingTriggerId,
                            discovery.TriggerId));
                    continue;
                }

                var window = state.PendingTriggerWindow;
                if (window is null)
                {
                    window = new PendingTriggerWindowState
                    {
                        PendingWindowId = $"pending_window_{engineEvent.EventSequence:000000}",
                        ControllerPlayerId = discovery.ControllerPlayerId,
                    };
                    state.PendingTriggerWindow = window;
                }
                else if (!string.Equals(
                             window.ControllerPlayerId,
                             discovery.ControllerPlayerId,
                             StringComparison.Ordinal))
                {
                    throw new EngineStateException(
                        "CANONICAL_PENDING_CROSS_PLAYER_UNSUPPORTED",
                        "The temporary trigger window cannot combine different controllers.");
                }

                window.PendingTriggers.Add(new PendingTriggeredAbilityState(
                    pendingTriggerId,
                    discovery.AbilityId,
                    discovery.TriggerId,
                    discovery.SourceCardInstanceId,
                    discovery.SourceCardId,
                    discovery.ControllerPlayerId,
                    engineEvent.EventId,
                    engineEvent.EventSequence,
                    discovery.CanonicalEventTypeId,
                    discovery.SourceFromZoneId,
                    discovery.SourceToZoneId,
                    discovery.SourceZoneTransitionInstanceId));
            }
        }

        var materialized = consequenceEvents.ToImmutable();
        state.Events.AddRange(materialized);
        return materialized;
    }

    private ActionResponse ApplyResolveTriggeredAbility(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore)
    {
        TriggeredAbilityResolutionPlan plan;
        try
        {
            plan = BuildTriggeredAbilityResolutionPlan(state, request);
        }
        catch (CanonicalAbilityExecutionException exception)
        {
            return RejectAction(
                state,
                request,
                "triggered_ability_resolution_invalid",
                Diagnostic(
                    exception.Code,
                    "transition_validation",
                    "The pending triggered ability cannot be resolved with this selection.",
                    exception.Message,
                    "fix_request"));
        }

        CanonicalEffectExecutor.Apply(state, plan.EffectPlan);
        var window = state.PendingTriggerWindow
            ?? throw new EngineStateException("Pending trigger window disappeared during resolution commit.");
        var removed = window.PendingTriggers.Remove(plan.PendingTrigger);
        if (!removed)
        {
            throw new EngineStateException("Pending trigger disappeared during resolution commit.");
        }

        if (window.PendingTriggers.Count == 0)
        {
            state.PendingTriggerWindow = null;
        }

        state.StateVersion += 1;
        var events = ImmutableArray.CreateBuilder<EngineEvent>();
        AppendCanonicalEffectEvents(
            events,
            plan.EffectPlan,
            (offset, eventType, payload) => CreateCanonicalRuntimeEvent(
                state,
                offset,
                eventType,
                request.PlayerId,
                request.ActionType,
                payload));

        events.Add(CreateCanonicalRuntimeEvent(
            state,
            events.Count,
            "canonical_ability_resolved",
            request.PlayerId,
            request.ActionType,
            ContractJsonValue.From(new CanonicalAbilityResolvedPayload(
                plan.PendingTrigger.PendingTriggerId,
                CanonicalEffectExecutor.TriggeredAbilityOriginId,
                plan.PendingTrigger.AbilityId,
                plan.PendingTrigger.SourceCardInstanceId,
                plan.PendingTrigger.SourceCardId,
                plan.PendingTrigger.ControllerPlayerId,
                CanonicalEffectExecutor.AppliedOutcome,
                plan.EffectPlan.AppliedMutationCount,
                null,
                plan.PendingTrigger.PendingTriggerId,
                plan.PendingTrigger.TriggerId))));
        var materializedEvents = events.ToImmutable();
        state.Events.AddRange(materializedEvents);
        _canonicalAbilityResolutions = _canonicalAbilityResolutions.Add(
            new CanonicalAbilityResolutionRecord(
                plan.PendingTrigger.PendingTriggerId,
                CanonicalEffectExecutor.TriggeredAbilityOriginId,
                plan.PendingTrigger.AbilityId,
                plan.PendingTrigger.SourceCardInstanceId,
                plan.PendingTrigger.SourceCardId,
                plan.PendingTrigger.ControllerPlayerId,
                CanonicalEffectExecutor.AppliedOutcome,
                plan.EffectPlan.AppliedMutationCount,
                null,
                plan.PendingTrigger.PendingTriggerId,
                plan.PendingTrigger.TriggerId));
        return AcceptAction(state, request, stateVersionBefore, materializedEvents);
    }

    private TriggeredAbilityResolutionPlan BuildTriggeredAbilityResolutionPlan(
        MatchState state,
        ActionRequest request)
    {
        var payload = ReadResolveTriggeredAbilityPayload(request.Payload);
        var window = state.PendingTriggerWindow;
        var pending = window?.PendingTriggers.SingleOrDefault(item => string.Equals(
            item.PendingTriggerId,
            payload.PendingTriggerId,
            StringComparison.Ordinal));
        if (pending is null)
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_PENDING_UNKNOWN",
                "The requested pending_trigger_id does not exist in the current trigger window.");
        }

        if (!string.Equals(pending.ControllerPlayerId, request.PlayerId, StringComparison.Ordinal))
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_PLAYER_INVALID",
                "Only the pending triggered ability controller can resolve it.");
        }

        var canonicalRuntime = _canonicalRuntime
            ?? throw new EngineStateException(
                "CANONICAL_RUNTIME_NOT_CONFIGURED",
                "Pending canonical trigger exists without a canonical runtime context.");
        var runtimePackage = _runtimePackage
            ?? throw new EngineStateException(
                "CANONICAL_RUNTIME_LEGACY_PACKAGE_MISSING",
                "Pending canonical trigger exists without a gameplay runtime package.");
        if (!canonicalRuntime.Abilities.AbilitiesById.TryGetValue(pending.AbilityId, out var ability)
            || !canonicalRuntime.Abilities.TriggersById.TryGetValue(pending.TriggerId, out var trigger)
            || !string.Equals(trigger.AbilityId, ability.AbilityId, StringComparison.Ordinal))
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_DEFINITION_MISSING",
                "Pending trigger canonical ability or trigger definition is unavailable.");
        }

        if (!state.CardInstances.TryGetValue(pending.SourceCardInstanceId, out var source)
            || !string.Equals(ability.CardId, pending.SourceCardId, StringComparison.Ordinal)
            || !string.Equals(source.CardId, pending.SourceCardId, StringComparison.Ordinal)
            || !string.Equals(source.ControllerPlayerId, pending.ControllerPlayerId, StringComparison.Ordinal))
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_SOURCE_INVALID",
                "Pending trigger source card is no longer consistent with its canonical definition.");
        }

        if (pending.SourceEngineEventSequence < 1
            || pending.SourceEngineEventSequence > state.Events.Count)
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_SOURCE_EVENT_INVALID",
                "Pending trigger source engine event sequence is invalid.");
        }

        var sourceEvent = state.Events[pending.SourceEngineEventSequence - 1];
        if (!string.Equals(sourceEvent.EventId, pending.SourceEngineEventId, StringComparison.Ordinal)
            || !string.Equals(
                CanonicalTriggerResolver.MapEngineEventType(sourceEvent.EventType),
                pending.CanonicalEventTypeId,
                StringComparison.Ordinal))
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_SOURCE_EVENT_INVALID",
                "Pending trigger source engine event identity is invalid.");
        }

        var zoneChanged = string.Equals(
            pending.CanonicalEventTypeId,
            CanonicalTriggerResolver.ZoneChangedCanonicalEventTypeId,
            StringComparison.Ordinal);
        if (zoneChanged)
        {
            var sourceEventPayload = sourceEvent.Payload;
            if (pending.SourceFromZoneId is null
                || pending.SourceToZoneId is null
                || pending.SourceZoneTransitionInstanceId is null
                || !string.Equals(ability.ActiveZoneId, pending.SourceFromZoneId, StringComparison.Ordinal)
                || !string.Equals(source.Zone, pending.SourceToZoneId, StringComparison.Ordinal)
                || !sourceEventPayload.TryGetProperty("card_instance_id", out var eventCardInstance)
                || !string.Equals(eventCardInstance.GetString(), pending.SourceCardInstanceId, StringComparison.Ordinal)
                || !sourceEventPayload.TryGetProperty("from_zone_id", out var fromZone)
                || !string.Equals(fromZone.GetString(), pending.SourceFromZoneId, StringComparison.Ordinal)
                || !sourceEventPayload.TryGetProperty("to_zone_id", out var toZone)
                || !string.Equals(toZone.GetString(), pending.SourceToZoneId, StringComparison.Ordinal)
                || !sourceEventPayload.TryGetProperty("zone_transition_instance_id", out var transition)
                || !string.Equals(
                    transition.GetString(),
                    pending.SourceZoneTransitionInstanceId,
                    StringComparison.Ordinal))
            {
                throw new CanonicalAbilityExecutionException(
                    "RESOLVE_TRIGGER_SOURCE_EVENT_INVALID",
                    "Pending zone-change trigger context no longer matches its authoritative event.");
            }
        }
        else if (!string.Equals(source.Zone, ability.ActiveZoneId, StringComparison.Ordinal))
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_SOURCE_INVALID",
                "Pending trigger source card is no longer in its canonical active zone.");
        }

        var context = new CanonicalAbilityResolutionContext(
            pending.PendingTriggerId,
            CanonicalResolutionOrigin.TriggeredAbility,
            null,
            request.ActionType,
            ability,
            pending.SourceCardInstanceId,
            pending.SourceCardId,
            pending.ControllerPlayerId,
            payload.TargetSelections,
            pending.PendingTriggerId,
            pending.TriggerId);
        var effectPlan = CanonicalEffectExecutor.BuildPlan(
            context,
            state,
            runtimePackage,
            canonicalRuntime.Cards,
            canonicalRuntime.Abilities);
        return new TriggeredAbilityResolutionPlan(pending, ability, effectPlan);
    }

    private static string CreatePendingTriggerId(
        CanonicalTriggeredAbilityDiscovery discovery,
        EngineEvent sourceEvent) =>
        $"pending_trigger_{sourceEvent.EventSequence:000000}_{discovery.AbilityIndex:000}_{discovery.TriggerSequence:000}";

    private static EngineEvent CreateCanonicalRuntimeEvent(
        MatchState state,
        int additionalEventOffset,
        string eventType,
        string actorPlayerId,
        string causeActionType,
        JsonElement payload)
    {
        var eventSequence = state.Events.Count + additionalEventOffset + 1;
        return new EngineEvent(
            ContractSchemas.EngineEvent,
            $"event_{eventSequence:000000}",
            eventSequence,
            eventType,
            state.MatchId,
            state.StateVersion,
            state.TurnNumber,
            actorPlayerId,
            causeActionType,
            "public",
            payload);
    }

    private PlayCardPlan BuildPlayCardPlan(MatchState state, ActionRequest request)
    {
        var player = state.GetPlayer(request.PlayerId);
        if (!string.Equals(state.ActivePlayerId, player.PlayerId, StringComparison.Ordinal))
        {
            throw PlayCardValidationException.Create(
                "player_not_active",
                "PLAY_CARD_PLAYER_INVALID",
                "Only the active player can play a card.",
                "The play_card request player is not the active player.",
                "refresh_projection");
        }

        if (!string.Equals(state.Phase, TransitionalMainPhase, StringComparison.Ordinal))
        {
            throw PlayCardValidationException.Create(
                "phase_invalid",
                "PLAY_CARD_PHASE_INVALID",
                "A card cannot be played in the current phase.",
                $"The transitional production play_card action requires phase={TransitionalMainPhase}.",
                "refresh_projection");
        }

        var payload = ReadPlayCardPayload(request.Payload);
        if (!state.CardInstances.TryGetValue(payload.CardInstanceId, out var card))
        {
            throw PlayCardValidationException.Create(
                "card_instance_unknown",
                "PLAY_CARD_CARD_UNKNOWN",
                "The selected card is not available.",
                "The play_card payload references an unknown card_instance_id.",
                "refresh_projection");
        }

        if (!string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal))
        {
            throw PlayCardValidationException.Create(
                "card_not_owned_or_controlled",
                "PLAY_CARD_CARD_AUTHORITY_INVALID",
                "The selected card cannot be played by this player.",
                "The selected card owner/controller does not match the requesting player.",
                "refresh_projection");
        }

        var handIndex = player.HandCardInstanceIds.IndexOf(card.CardInstanceId);
        if (!string.Equals(card.Zone, "hand", StringComparison.Ordinal)
            || handIndex < 0
            || card.ZoneIndex != handIndex)
        {
            throw PlayCardValidationException.Create(
                "card_not_in_hand",
                "PLAY_CARD_CARD_ZONE_INVALID",
                "The selected card is not available in hand.",
                "The selected card zone, hand membership, or hand index is inconsistent.",
                "refresh_projection");
        }

        var runtimePackage = RequirePlayCardRuntimePackage(state);
        if (!runtimePackage.Cards.TryGetValue(card.CardId, out var definition))
        {
            throw PlayCardValidationException.Create(
                "runtime_card_missing",
                "PLAY_CARD_RUNTIME_CARD_MISSING",
                "The selected card cannot be played.",
                "The selected card has no runtime definition in the current package.",
                "fix_runtime_package");
        }

        if (definition.CardType is not ("entity" or "incantation" or "ritual"))
        {
            throw PlayCardValidationException.Create(
                "card_type_unsupported",
                "PLAY_CARD_CARD_TYPE_UNSUPPORTED",
                "This card type is not supported by Play Card yet.",
                "The current production play_card slice supports Entity, Incantation, and Ritual cards.",
                "choose_another_action");
        }

        MagnitudePreflightResult magnitude;
        try
        {
            magnitude = EvaluateMagnitudePreflight(player.PlayerId, card.CardInstanceId);
        }
        catch (MagnitudePreflightException exception)
        {
            throw PlayCardValidationException.Create(
                "magnitude_preflight_invalid",
                "PLAY_CARD_MAGNITUDE_PREFLIGHT_INVALID",
                "The card's Magnitude requirement could not be validated.",
                $"Magnitude preflight failed with {exception.Code}: {exception.Message}",
                "refresh_projection");
        }

        if (!magnitude.RequirementMet)
        {
            throw PlayCardValidationException.Create(
                "magnitude_requirement_not_met",
                "PLAY_CARD_MAGNITUDE_REQUIREMENT_NOT_MET",
                "The card's Magnitude requirement is not met.",
                $"Required Magnitude is {magnitude.RequiredMagnitude}; current Magnitude is {magnitude.CurrentMagnitude}.",
                "choose_another_action");
        }

        AuraPaymentPreflightResult auraPreflight;
        try
        {
            auraPreflight = EvaluateAuraPaymentPreflight(player.PlayerId, card.CardInstanceId);
        }
        catch (AuraPaymentException exception)
        {
            throw PlayCardValidationException.Create(
                "aura_preflight_invalid",
                "PLAY_CARD_AURA_PREFLIGHT_INVALID",
                "The card's Aura payment could not be validated.",
                $"Aura preflight failed with {exception.Code}: {exception.Message}",
                "refresh_projection");
        }

        if (!auraPreflight.PaymentPossible)
        {
            throw PlayCardValidationException.Create(
                "aura_insufficient",
                "PLAY_CARD_AURA_INSUFFICIENT",
                "There is not enough eligible active Aura to play this card.",
                "Aura payment preflight found fewer eligible active sources than the payable cost.",
                "choose_another_action");
        }

        if (payload.AuraSourceCardInstanceIds.Length != auraPreflight.NormalizedPayableAuraCost
            || payload.AuraSourceCardInstanceIds.Distinct(StringComparer.Ordinal).Count()
            != payload.AuraSourceCardInstanceIds.Length)
        {
            throw PlayCardValidationException.Create(
                "aura_selection_invalid",
                "PLAY_CARD_AURA_SELECTION_INVALID",
                "The selected Aura sources do not exactly match the card's cost.",
                "The play_card Aura source list must be unique and contain exactly the payable Aura cost.",
                "fix_request");
        }

        var eligibleAuraSourceIds = auraPreflight.EligibleSources
            .Select(source => source.CardInstanceId)
            .ToHashSet(StringComparer.Ordinal);
        if (payload.AuraSourceCardInstanceIds.Any(sourceId =>
                string.IsNullOrWhiteSpace(sourceId) || !eligibleAuraSourceIds.Contains(sourceId)))
        {
            throw PlayCardValidationException.Create(
                "aura_source_invalid",
                "PLAY_CARD_AURA_SOURCE_INVALID",
                "One or more selected Aura sources are no longer eligible.",
                "Every selected source must still be an eligible active source from the requesting player's Wellspring.",
                "refresh_projection");
        }

        AuraPaymentSelectionValidationResult auraSelection;
        try
        {
            auraSelection = ValidateAuraPaymentSelection(
                player.PlayerId,
                card.CardInstanceId,
                payload.AuraSourceCardInstanceIds);
        }
        catch (AuraPaymentException exception)
        {
            throw PlayCardValidationException.Create(
                "aura_source_invalid",
                "PLAY_CARD_AURA_SOURCE_INVALID",
                "One or more selected Aura sources are no longer eligible.",
                $"Aura selection revalidation failed with {exception.Code}: {exception.Message}",
                "refresh_projection");
        }

        if (!auraSelection.SelectionValid)
        {
            var invalidSource = string.Equals(
                auraSelection.FailureReason,
                "source_not_eligible",
                StringComparison.Ordinal);
            throw PlayCardValidationException.Create(
                invalidSource ? "aura_source_invalid" : "aura_selection_invalid",
                invalidSource
                    ? "PLAY_CARD_AURA_SOURCE_INVALID"
                    : "PLAY_CARD_AURA_SELECTION_INVALID",
                invalidSource
                    ? "One or more selected Aura sources are no longer eligible."
                    : "The selected Aura sources are invalid.",
                $"Aura selection validation failed: {auraSelection.FailureReason}",
                invalidSource ? "refresh_projection" : "fix_request");
        }

        var auraSources = auraSelection.ResolvedSourceInstanceIds
            .Select(state.GetCardInstance)
            .OrderBy(source => source.ZoneIndex)
            .ThenBy(source => source.CardInstanceId, StringComparer.Ordinal)
            .ToImmutableArray();
        if (string.Equals(definition.CardType, "entity", StringComparison.Ordinal))
        {
            if (payload.TargetSelections is not null
                || payload.DomainRow is null
                || payload.LaneIndex is null)
            {
                throw PlayCardValidationException.Create(
                    "payload_card_type_mismatch",
                    "PLAY_CARD_PAYLOAD_CARD_TYPE_MISMATCH",
                    "Entity play requires a Domain destination and no resolution targets.",
                    "Entity play_card payload must use domain_row/lane_index and must not contain target_selections.",
                    "fix_request");
            }

            var domainRow = payload.DomainRow switch
            {
                "horizon" => DomainRow.Horizon,
                "zenith" => DomainRow.Zenith,
                _ => throw PlayCardValidationException.Create(
                    "destination_row_invalid",
                    "PLAY_CARD_DESTINATION_ROW_INVALID",
                    "The selected Domain row is invalid.",
                    "domain_row must be exactly horizon or zenith.",
                    "fix_request"),
            };
            if (payload.LaneIndex is < 0 or >= DomainState.LaneCount)
            {
                throw PlayCardValidationException.Create(
                    "destination_lane_invalid",
                    "PLAY_CARD_DESTINATION_LANE_INVALID",
                    "The selected Domain lane is invalid.",
                    $"lane_index must be between 0 and {DomainState.LaneCount - 1}.",
                    "fix_request");
            }

            var laneIndex = payload.LaneIndex.Value;
            if (player.Domain.GetSlots(domainRow)[laneIndex] is not null)
            {
                throw PlayCardValidationException.Create(
                    "destination_occupied",
                    "PLAY_CARD_DESTINATION_OCCUPIED",
                    "The selected Domain slot is occupied.",
                    "The requested own Domain row/lane is no longer empty.",
                    "refresh_projection");
            }

            return new PlayCardPlan(
                player,
                card,
                handIndex,
                auraSources,
                domainRow,
                laneIndex,
                Resolution: null);
        }

        if (payload.DomainRow is not null
            || payload.LaneIndex is not null
            || payload.TargetSelections is null)
        {
            throw PlayCardValidationException.Create(
                "payload_card_type_mismatch",
                "PLAY_CARD_PAYLOAD_CARD_TYPE_MISMATCH",
                "Resolution card play requires target selections and no Domain destination.",
                "Incantation/Ritual play_card payload must use target_selections and must not contain domain_row/lane_index.",
                "fix_request");
        }

        var canonicalRuntime = _canonicalRuntime;
        if (canonicalRuntime is null)
        {
            throw PlayCardValidationException.Create(
                "canonical_runtime_missing",
                "PLAY_CARD_CANONICAL_RUNTIME_MISSING",
                "This resolution card cannot be played without canonical runtime data.",
                "The session has no canonical REGISTRY/CARDDATABASE runtime context.",
                "fix_runtime_package");
        }

        if (!canonicalRuntime.Abilities.AbilitiesByCardId.TryGetValue(card.CardId, out var abilities))
        {
            throw PlayCardValidationException.Create(
                "canonical_resolution_missing",
                "PLAY_CARD_CANONICAL_RESOLUTION_MISSING",
                "This resolution card has no supported canonical resolution ability.",
                "No canonical ability graph exists for the selected card ID.",
                "choose_another_action");
        }

        var resolutionAbilities = abilities.Where(ability =>
                string.Equals(ability.Status, "active", StringComparison.Ordinal)
                && string.Equals(ability.AbilityKindId, "resolution", StringComparison.Ordinal))
            .ToImmutableArray();
        if (resolutionAbilities.Length != 1)
        {
            throw PlayCardValidationException.Create(
                "canonical_resolution_ambiguous",
                "PLAY_CARD_CANONICAL_RESOLUTION_AMBIGUOUS",
                "This resolution card does not have exactly one playable canonical resolution ability.",
                $"Expected one active resolution ability; found {resolutionAbilities.Length}.",
                "fix_runtime_package");
        }

        var ability = resolutionAbilities[0];
        CanonicalEffectExecutionPlan effectPlan;
        try
        {
            CanonicalEffectExecutor.ValidateSupportedPlayedCardGraph(ability);
            var context = new CanonicalAbilityResolutionContext(
                $"resolution_play_{state.Events.Count + 1:000000}_{ability.AbilityIndex:000}",
                CanonicalResolutionOrigin.PlayedCard,
                request.ActionId,
                request.ActionType,
                ability,
                card.CardInstanceId,
                card.CardId,
                player.PlayerId,
                payload.TargetSelections.Value,
                PendingTriggerId: null,
                TriggerId: null);
            effectPlan = CanonicalEffectExecutor.BuildPlan(
                context,
                state,
                runtimePackage,
                canonicalRuntime.Cards,
                canonicalRuntime.Abilities);
        }
        catch (CanonicalAbilityExecutionException exception)
        {
            throw PlayCardValidationException.Create(
                "canonical_resolution_invalid",
                exception.Code,
                "This resolution card cannot be resolved with the submitted canonical selection.",
                exception.Message,
                exception.Code.StartsWith("PLAY_CARD_TARGET_", StringComparison.Ordinal)
                    ? "fix_request"
                    : "fix_runtime_package");
        }

        return new PlayCardPlan(
            player,
            card,
            handIndex,
            auraSources,
            DomainRow: null,
            LaneIndex: null,
            Resolution: new PlayedCardResolutionPlan(effectPlan));
    }

    private RuntimePackageCatalog RequirePlayCardRuntimePackage(MatchState state)
    {
        var runtimePackage = _runtimePackage;
        if (runtimePackage is null)
        {
            throw PlayCardValidationException.Create(
                "runtime_package_missing",
                "PLAY_CARD_RUNTIME_PACKAGE_INVALID",
                "Cards cannot be played without a runtime package.",
                "The session has no validated runtime package catalog.",
                "fix_runtime_package");
        }

        try
        {
            RuntimePackageLoader.ValidateCatalog(runtimePackage);
        }
        catch (EngineInputException exception)
        {
            throw PlayCardValidationException.Create(
                "runtime_package_invalid",
                "PLAY_CARD_RUNTIME_PACKAGE_INVALID",
                "Cards cannot be played with the current runtime package.",
                $"Runtime package validation failed with {exception.Code}: {exception.Message}",
                "fix_runtime_package");
        }

        if (!string.Equals(runtimePackage.PackageId, state.RuntimePackageId, StringComparison.Ordinal))
        {
            throw PlayCardValidationException.Create(
                "runtime_package_invalid",
                "PLAY_CARD_RUNTIME_PACKAGE_INVALID",
                "Cards cannot be played with the current runtime package.",
                "Runtime package identity does not match the authoritative match state.",
                "fix_runtime_package");
        }

        return runtimePackage;
    }

    private static ImmutableArray<EngineEvent> BuildPlayCardEvents(
        MatchState state,
        ActionRequest request,
        PlayCardPlan plan)
    {
        var events = ImmutableArray.CreateBuilder<EngineEvent>();
        var stateVersionAfter = state.StateVersion + 1;
        foreach (var source in plan.AuraSources)
        {
            var payload = new AuraSourceExhaustedPayload(
                request.ActionId,
                request.ActionType,
                plan.Card.CardInstanceId,
                source.CardInstanceId,
                source.CardId,
                source.OwnerPlayerId,
                source.ControllerPlayerId,
                source.ZoneIndex,
                "active",
                "exhausted",
                AuraUnits: 1);
            events.Add(CreatePlayCardEvent(
                state,
                request,
                stateVersionAfter,
                state.Events.Count + events.Count + 1,
                "aura_source_exhausted",
                ContractJsonValue.From(payload)));
        }

        if (plan.Resolution is not null)
        {
            var context = plan.Resolution.EffectPlan.Context;
            var originId = CanonicalEffectExecutor.OriginId(context.Origin);
            AppendCanonicalEffectEvents(
                events,
                plan.Resolution.EffectPlan,
                (_, eventType, payload) => CreatePlayCardEvent(
                    state,
                    request,
                    stateVersionAfter,
                    state.Events.Count + events.Count + 1,
                    eventType,
                    payload));

            events.Add(CreatePlayCardEvent(
                state,
                request,
                stateVersionAfter,
                state.Events.Count + events.Count + 1,
                "canonical_ability_resolved",
                ContractJsonValue.From(new CanonicalAbilityResolvedPayload(
                    context.ResolutionId,
                    originId,
                    context.Ability.AbilityId,
                    context.SourceCardInstanceId,
                    context.SourceCardId,
                    context.ControllerPlayerId,
                    CanonicalEffectExecutor.AppliedOutcome,
                    plan.Resolution.EffectPlan.AppliedMutationCount,
                    context.SourceActionId,
                    PendingTriggerId: null,
                    TriggerId: null))));
            var voidMove = new ZoneMovePayload(
                request.ActionId,
                request.ActionType,
                plan.Card.CardInstanceId,
                plan.Card.CardId,
                plan.Card.OwnerPlayerId,
                plan.Card.ControllerPlayerId,
                "hand",
                "void",
                plan.HandIndex,
                plan.Player.VoidCardInstanceIds.Count,
                "owner_only",
                "public");
            events.Add(CreatePlayCardEvent(
                state,
                request,
                stateVersionAfter,
                state.Events.Count + events.Count + 1,
                "zone_move",
                ContractJsonValue.From(voidMove)));
            return events.ToImmutable();
        }

        var domainRow = plan.DomainRow
            ?? throw new EngineStateException("Entity play event plan has no Domain row.");
        var laneIndex = plan.LaneIndex
            ?? throw new EngineStateException("Entity play event plan has no Domain lane.");
        var rowToken = domainRow == DomainRow.Horizon ? "horizon" : "zenith";
        var zoneMovePayload = new DomainZoneMovePayload(
            request.ActionId,
            request.ActionType,
            plan.Card.CardInstanceId,
            plan.Card.CardId,
            plan.Card.OwnerPlayerId,
            plan.Card.ControllerPlayerId,
            "hand",
            "dominion",
            plan.HandIndex,
            rowToken,
            laneIndex,
            "owner_only",
            "public");
        events.Add(CreatePlayCardEvent(
            state,
            request,
            stateVersionAfter,
            state.Events.Count + events.Count + 1,
            "zone_move",
            ContractJsonValue.From(zoneMovePayload)));

        var enteredPlayPayload = new CardEnteredPlayPayload(
            request.ActionId,
            request.ActionType,
            plan.Card.CardInstanceId,
            plan.Card.CardId,
            plan.Card.OwnerPlayerId,
            plan.Card.ControllerPlayerId,
            rowToken,
            laneIndex,
            "active",
            state.TurnNumber);
        events.Add(CreatePlayCardEvent(
            state,
            request,
            stateVersionAfter,
            state.Events.Count + events.Count + 1,
            "card_entered_play",
            ContractJsonValue.From(enteredPlayPayload)));
        return events.ToImmutable();
    }

    private static void AppendCanonicalEffectEvents(
        ImmutableArray<EngineEvent>.Builder events,
        CanonicalEffectExecutionPlan plan,
        Func<int, string, JsonElement, EngineEvent> createEvent)
    {
        var context = plan.Context;
        var originId = CanonicalEffectExecutor.OriginId(context.Origin);
        foreach (var mutation in plan.Mutations)
        {
            switch (mutation)
            {
                case CanonicalCardActivityMutation activity:
                    events.Add(createEvent(
                        events.Count,
                        "card_activity_changed",
                        ContractJsonValue.From(new CardActivityChangedPayload(
                            activity.CardInstanceId,
                            activity.CardId,
                            activity.FromActivityState,
                            activity.ToActivityState,
                            context.Ability.AbilityId,
                            activity.EffectId,
                            context.ResolutionId,
                            originId,
                            context.PendingTriggerId))));
                    break;
                case CanonicalDamageMutation damage:
                    events.Add(createEvent(
                        events.Count,
                        "damage_dealt",
                        ContractJsonValue.From(new DamageDealtPayload(
                            damage.DamageInstanceId,
                            damage.CardInstanceId,
                            damage.SourceCardInstanceId,
                            damage.DamageKindId,
                            damage.Amount,
                            damage.Amount,
                            0,
                            damage.Amount,
                            damage.DamageBefore,
                            damage.DamageAfter,
                            null,
                            damage.SourceCardId,
                            damage.CardId,
                            context.Ability.AbilityId,
                            damage.EffectId,
                            context.ResolutionId,
                            originId,
                            damage.EffectiveMaxHp,
                            damage.Lethal))));
                    if (damage.Destruction is not { } destruction)
                    {
                        break;
                    }

                    events.Add(createEvent(
                        events.Count,
                        "entity_destroyed",
                        ContractJsonValue.From(new EntityDestroyedPayload(
                            destruction.DestructionInstanceId,
                            damage.CardInstanceId,
                            destruction.DestructionCauseKindId,
                            destruction.SourceCardInstanceId,
                            destruction.CauseInstanceId,
                            damage.CardId,
                            context.Ability.AbilityId,
                            damage.EffectId,
                            context.ResolutionId))));
                    AppendZoneChangeEvent(
                        events,
                        createEvent,
                        context,
                        damage.EffectId,
                        destruction.ZoneTransition);
                    break;
                case CanonicalDestroyEffectMutation destroy:
                    events.Add(createEvent(
                        events.Count,
                        "entity_destroyed",
                        ContractJsonValue.From(new EntityDestroyedPayload(
                            destroy.Destruction.DestructionInstanceId,
                            destroy.CardInstanceId,
                            destroy.Destruction.DestructionCauseKindId,
                            destroy.Destruction.SourceCardInstanceId,
                            destroy.Destruction.CauseInstanceId,
                            destroy.CardId,
                            context.Ability.AbilityId,
                            destroy.EffectId,
                            context.ResolutionId))));
                    AppendZoneChangeEvent(
                        events,
                        createEvent,
                        context,
                        destroy.EffectId,
                        destroy.Destruction.ZoneTransition);
                    break;
                case CanonicalHealMutation heal:
                    if (heal.RemovedAmount > 0)
                    {
                        events.Add(createEvent(
                            events.Count,
                            "damage_removed",
                            ContractJsonValue.From(new DamageRemovedPayload(
                                heal.DamageRemovalInstanceId,
                                heal.CardInstanceId,
                                heal.SourceCardInstanceId,
                                heal.RequestedAmount,
                                heal.RemovedAmount,
                                heal.DamageBefore,
                                heal.DamageAfter,
                                heal.MiasmaRemoved,
                                context.ResolutionId,
                                heal.CardId,
                                CanonicalEffectExecutor.HealEntityEffectActionTypeId))));
                    }

                    break;
                case CanonicalMoveCardMutation move:
                    AppendZoneChangeEvent(
                        events,
                        createEvent,
                        context,
                        move.EffectId,
                        move.ZoneTransition);
                    break;
                case CanonicalModifierMutation modifier:
                    events.Add(createEvent(
                        events.Count,
                        "modifier_applied",
                        ContractJsonValue.From(new ModifierAppliedPayload(
                            $"modifier_application_{modifier.Instance.ModifierInstanceId}",
                            modifier.Instance.ModifierInstanceId,
                            modifier.Instance.ModifierTypeId,
                            modifier.Instance.TargetCardInstanceId,
                            modifier.Instance.SourceCardInstanceId,
                            modifier.Instance.AffectedFieldId,
                            modifier.Instance.IntegerValue,
                            modifier.ResolvedValueBefore,
                            modifier.ResolvedValueAfter,
                            modifier.Instance.DurationPolicyId,
                            modifier.Instance.DurationInstanceId,
                            CauseEventId: null,
                            modifier.Instance.TurnInstanceId,
                            modifier.Instance.PhaseInstanceId))));
                    break;
                case CanonicalKeywordGrantMutation grant:
                    events.Add(createEvent(
                        events.Count,
                        "keyword_granted",
                        ContractJsonValue.From(new KeywordGrantedPayload(
                            $"keyword_change_{grant.Instance.KeywordGrantInstanceId}",
                            grant.Instance.KeywordGrantInstanceId,
                            grant.Instance.TargetCardInstanceId,
                            grant.Instance.KeywordId,
                            grant.Instance.SourceCardInstanceId,
                            grant.Instance.DurationPolicyId,
                            grant.Instance.DurationInstanceId,
                            grant.EffectiveKeywordPresentBefore,
                            grant.EffectiveKeywordPresentAfter,
                            CauseEventId: null,
                            grant.Instance.TurnInstanceId,
                            grant.Instance.PhaseInstanceId))));
                    break;
                default:
                    throw new EngineStateException("Unknown canonical effect mutation event type.");
            }
        }
    }

    private static void AppendZoneChangeEvent(
        ImmutableArray<EngineEvent>.Builder events,
        Func<int, string, JsonElement, EngineEvent> createEvent,
        CanonicalAbilityResolutionContext context,
        string effectId,
        CanonicalZoneTransitionPlan transitionPlan)
    {
        var transition = transitionPlan.Actual;
        events.Add(createEvent(
            events.Count,
            "card_zone_changed",
            ContractJsonValue.From(new CardZoneChangedPayload(
                transition.ZoneTransitionInstanceId,
                transition.CardInstanceId,
                transition.FromZoneId,
                transition.ToZoneId,
                transition.FromZonePresenceInstanceId,
                transition.ToZonePresenceInstanceId,
                transition.CauseInstanceId,
                transition.CardId,
                transition.OwnerPlayerId,
                transition.ControllerPlayerIdBefore,
                transition.FromDomainRow == DomainRow.Horizon ? "horizont" : "zenit",
                transition.FromDomainLaneIndex,
                transition.ToZoneIndex,
                transition.VisibilityBefore,
                transition.VisibilityAfter,
                context.Ability.AbilityId,
                effectId,
                context.ResolutionId))));
    }

    private static EngineEvent CreatePlayCardEvent(
        MatchState state,
        ActionRequest request,
        int stateVersionAfter,
        int eventSequence,
        string eventType,
        JsonElement payload) => new(
            ContractSchemas.EngineEvent,
            $"event_{eventSequence:000000}",
            eventSequence,
            eventType,
            state.MatchId,
            stateVersionAfter,
            state.TurnNumber,
            request.PlayerId,
            request.ActionType,
            "public",
            payload);

    private ActionResponse ApplyEndTurn(MatchState state, ActionRequest request, int stateVersionBefore)
    {
        var previousPlayerId = state.ActivePlayerId;
        var nextPlayerId = state.GetNextPlayerId(previousPlayerId);
        var turnBefore = state.TurnNumber;
        var continuousEffectPlan = CanonicalContinuousEffects.BuildEndTurnPlan(
            state,
            _canonicalRuntime?.Cards,
            _canonicalRuntime?.Abilities);
        var expiryLethalTargets = continuousEffectPlan.LethalMutations
            .Select(mutation => mutation.TargetCardInstanceId)
            .ToHashSet(StringComparer.Ordinal);
        var damagedSurvivors = state.Players
            .SelectMany(player => new[]
            {
                player.Domain.HorizonCardInstanceIds,
                player.Domain.ZenithCardInstanceIds,
            })
            .SelectMany(row => row)
            .Where(cardInstanceId => cardInstanceId is not null)
            .Select(cardInstanceId => state.GetCardInstance(cardInstanceId!))
            .Where(card => card.DamageMarked > 0
                           && !expiryLethalTargets.Contains(card.CardInstanceId))
            .Select(card => (Card: card, DamageBefore: card.DamageMarked))
            .ToImmutableArray();

        // Temporary until the explicit phase engine exists: today's end_turn is
        // the end of the active player's complete turn, so it is the production
        // proxy for the official Eloszlas boundary: contribution expiry and any
        // resulting lethal transitions precede survivor-damage cleanup.
        CanonicalContinuousEffects.ApplyEndTurnPlan(state, continuousEffectPlan);
        foreach (var damaged in damagedSurvivors)
        {
            damaged.Card.DamageMarked = 0;
        }

        if (string.Equals(nextPlayerId, state.Players[0].PlayerId, StringComparison.Ordinal))
        {
            state.TurnNumber += 1;
        }

        state.ActivePlayerId = nextPlayerId;
        state.PriorityPlayerId = nextPlayerId;
        state.StateVersion += 1;
        var events = ImmutableArray.CreateBuilder<EngineEvent>();
        foreach (var expiration in continuousEffectPlan.Expirations)
        {
            AppendContinuousEffectExpirationEvent(
                state,
                request,
                turnBefore,
                previousPlayerId,
                events,
                expiration);
        }

        foreach (var lethal in continuousEffectPlan.LethalMutations)
        {
            AppendExpiryLethalEvents(
                state,
                request,
                turnBefore,
                previousPlayerId,
                events,
                lethal);
        }

        foreach (var damaged in damagedSurvivors)
        {
            var card = damaged.Card;
            var eventSequence = state.Events.Count + events.Count + 1;
            events.Add(new EngineEvent(
                ContractSchemas.EngineEvent,
                $"event_{eventSequence:000000}",
                eventSequence,
                "damage_removed",
                state.MatchId,
                state.StateVersion,
                turnBefore,
                previousPlayerId,
                request.ActionType,
                "public",
                ContractJsonValue.From(new DamageRemovedPayload(
                    $"damage_removal_{eventSequence:000000}",
                    card.CardInstanceId,
                    null,
                    damaged.DamageBefore,
                    damaged.DamageBefore,
                    damaged.DamageBefore,
                    0,
                    false,
                    null,
                    card.CardId,
                    "temporary_end_turn_dissipation_proxy"))));
        }

        var transitionEventSequence = state.Events.Count + events.Count + 1;
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
        events.Add(new EngineEvent(
            ContractSchemas.EngineEvent,
            $"event_{transitionEventSequence:000000}",
            transitionEventSequence,
            "turn_transition",
            state.MatchId,
            state.StateVersion,
            state.TurnNumber,
            previousPlayerId,
            request.ActionType,
            "public",
            ContractJsonValue.From(payload)));
        var materializedEvents = events.ToImmutable();
        state.Events.AddRange(materializedEvents);
        return AcceptAction(state, request, stateVersionBefore, materializedEvents);
    }

    private static void AppendContinuousEffectExpirationEvent(
        MatchState state,
        ActionRequest request,
        int turnBefore,
        string previousPlayerId,
        ImmutableArray<EngineEvent>.Builder events,
        CanonicalContinuousEffectExpiration expiration)
    {
        switch (expiration)
        {
            case CanonicalModifierExpiration modifier:
                events.Add(CreateEndTurnEvent(
                    state,
                    request,
                    turnBefore,
                    previousPlayerId,
                    events.Count,
                    "modifier_removed",
                    ContractJsonValue.From(new ModifierRemovedPayload(
                        $"modifier_removal_{modifier.Instance.ModifierInstanceId}",
                        modifier.Instance.ModifierInstanceId,
                        modifier.Instance.ModifierTypeId,
                        modifier.Instance.TargetCardInstanceId,
                        modifier.Instance.SourceCardInstanceId,
                        modifier.Instance.AffectedFieldId,
                        modifier.Instance.IntegerValue,
                        modifier.ResolvedValueBefore,
                        modifier.ResolvedValueAfter,
                        CanonicalContinuousEffects.DurationExpiredRemovalReasonId,
                        modifier.Instance.DurationPolicyId,
                        modifier.Instance.DurationInstanceId,
                        CauseEventId: null,
                        modifier.Instance.TurnInstanceId,
                        modifier.Instance.PhaseInstanceId))));
                break;
            case CanonicalKeywordGrantExpiration grant:
                events.Add(CreateEndTurnEvent(
                    state,
                    request,
                    turnBefore,
                    previousPlayerId,
                    events.Count,
                    "keyword_removed",
                    ContractJsonValue.From(new KeywordRemovedPayload(
                        $"keyword_change_{grant.Instance.KeywordGrantInstanceId}_expired",
                        grant.Instance.KeywordGrantInstanceId,
                        grant.Instance.TargetCardInstanceId,
                        grant.Instance.KeywordId,
                        grant.Instance.SourceCardInstanceId,
                        CanonicalContinuousEffects.DurationExpiredRemovalReasonId,
                        grant.Instance.DurationPolicyId,
                        grant.Instance.DurationInstanceId,
                        grant.EffectiveKeywordPresentBefore,
                        grant.EffectiveKeywordPresentAfter,
                        CauseEventId: null,
                        grant.Instance.TurnInstanceId,
                        grant.Instance.PhaseInstanceId))));
                break;
            default:
                throw new EngineStateException("Unknown continuous-effect expiration event type.");
        }
    }

    private static void AppendExpiryLethalEvents(
        MatchState state,
        ActionRequest request,
        int turnBefore,
        string previousPlayerId,
        ImmutableArray<EngineEvent>.Builder events,
        CanonicalExpiryLethalMutation lethal)
    {
        var destruction = lethal.Destruction;
        events.Add(CreateEndTurnEvent(
            state,
            request,
            turnBefore,
            previousPlayerId,
            events.Count,
            "entity_destroyed",
            ContractJsonValue.From(new EntityDestroyedPayload(
                destruction.DestructionInstanceId,
                lethal.TargetCardInstanceId,
                destruction.DestructionCauseKindId,
                destruction.SourceCardInstanceId,
                destruction.CauseInstanceId,
                lethal.TargetCardId,
                lethal.CauseModifier.SourceAbilityId,
                lethal.CauseModifier.SourceEffectId,
                lethal.CauseModifier.SourceResolutionId))));

        var transition = destruction.ZoneTransition.Actual;
        events.Add(CreateEndTurnEvent(
            state,
            request,
            turnBefore,
            previousPlayerId,
            events.Count,
            "card_zone_changed",
            ContractJsonValue.From(new CardZoneChangedPayload(
                transition.ZoneTransitionInstanceId,
                transition.CardInstanceId,
                transition.FromZoneId,
                transition.ToZoneId,
                transition.FromZonePresenceInstanceId,
                transition.ToZonePresenceInstanceId,
                transition.CauseInstanceId,
                transition.CardId,
                transition.OwnerPlayerId,
                transition.ControllerPlayerIdBefore,
                transition.FromDomainRow == DomainRow.Horizon ? "horizont" : "zenit",
                transition.FromDomainLaneIndex,
                transition.ToZoneIndex,
                transition.VisibilityBefore,
                transition.VisibilityAfter,
                lethal.CauseModifier.SourceAbilityId,
                lethal.CauseModifier.SourceEffectId,
                lethal.CauseModifier.SourceResolutionId))));
    }

    private static EngineEvent CreateEndTurnEvent(
        MatchState state,
        ActionRequest request,
        int turnBefore,
        string previousPlayerId,
        int pendingEventCount,
        string eventType,
        JsonElement payload)
    {
        var eventSequence = state.Events.Count + pendingEventCount + 1;
        return new EngineEvent(
            ContractSchemas.EngineEvent,
            $"event_{eventSequence:000000}",
            eventSequence,
            eventType,
            state.MatchId,
            state.StateVersion,
            turnBefore,
            previousPlayerId,
            request.ActionType,
            "public",
            payload);
    }

    private static ActionResponse AcceptAction(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore,
        EngineEvent engineEvent) => AcceptAction(
            state,
            request,
            stateVersionBefore,
            ImmutableArray.Create(engineEvent));

    private static ActionResponse AcceptAction(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore,
        ImmutableArray<EngineEvent> engineEvents) => new(
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
            engineEvents.Select(CloneEvent).ToImmutableArray(),
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
            BuildZoneSnapshot(state, "void", player.VoidCardInstanceIds, "public"),
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

    private DomainBoardProjection BuildDomainBoardProjection(MatchState state)
    {
        var players = state.Players
            .Select(player =>
            {
                var horizon = BuildDomainRowProjection(
                    state,
                    player,
                    DomainRow.Horizon,
                    player.Domain.HorizonCardInstanceIds);
                var zenith = BuildDomainRowProjection(
                    state,
                    player,
                    DomainRow.Zenith,
                    player.Domain.ZenithCardInstanceIds);
                var occupiedSlotCount = horizon.Count(slot => slot.Occupied)
                    + zenith.Count(slot => slot.Occupied);
                return new PlayerDomainProjection(
                    player.PlayerId,
                    occupiedSlotCount,
                    DomainState.LaneCount * 2 - occupiedSlotCount,
                    horizon,
                    zenith);
            })
            .ToImmutableArray();
        return new DomainBoardProjection(
            ContractSchemas.DomainBoardProjection,
            "dominion",
            "public",
            DomainState.LaneCount,
            players);
    }

    private ImmutableArray<DomainSlotProjection> BuildDomainRowProjection(
        MatchState state,
        PlayerState player,
        DomainRow row,
        IReadOnlyList<string?> cardInstanceIds) => Enumerable
        .Range(0, DomainState.LaneCount)
        .Select(laneIndex =>
        {
            var cardInstanceId = cardInstanceIds[laneIndex];
            DomainCardProjection? occupant = null;
            if (cardInstanceId is not null)
            {
                var card = state.GetCardInstance(cardInstanceId);
                int? effectiveAtk = null;
                int? effectiveMaxHp = null;
                var effectiveKeywords = ImmutableArray<string>.Empty;
                if (_canonicalRuntime?.Cards is { } canonicalCards
                    && canonicalCards.DefinitionsById.TryGetValue(card.CardId, out var canonicalDefinition)
                    && string.Equals(canonicalDefinition.CardType, "entity", StringComparison.Ordinal))
                {
                    effectiveAtk = CanonicalVitals.GetEffectiveAtk(state, card, canonicalCards);
                    effectiveMaxHp = CanonicalVitals.GetEffectiveMaxHp(state, card, canonicalCards);
                    effectiveKeywords = CanonicalContinuousEffects.GetEffectiveKeywords(
                        state,
                        card,
                        _canonicalRuntime.Abilities);
                }

                occupant = new DomainCardProjection(
                    card.CardInstanceId,
                    card.CardId,
                    card.OwnerPlayerId,
                    card.ControllerPlayerId,
                    card.Zone,
                    card.ZoneSequence,
                    card.Visibility,
                    card.ActivityState
                    ?? throw new EngineStateException("Domain card activity state is missing."),
                    card.EnteredDomainTurnNumber
                    ?? throw new EngineStateException("Domain entry turn is missing."),
                    effectiveAtk,
                    effectiveMaxHp,
                    card.DamageMarked,
                    effectiveMaxHp - card.DamageMarked,
                    effectiveKeywords);
            }

            return new DomainSlotProjection(
                row == DomainRow.Horizon ? "horizon" : "zenith",
                laneIndex,
                cardInstanceId is not null,
                occupant);
        })
        .ToImmutableArray();

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
        if (string.Equals(item.EventType, "aura_source_exhausted", StringComparison.Ordinal))
        {
            var sourceOwnerPlayerId = ReadEventPayloadString(item.Payload, "owner_player_id");
            if (string.Equals(sourceOwnerPlayerId, viewerPlayerId, StringComparison.Ordinal))
            {
                return CloneEvent(item);
            }

            return item with
            {
                Payload = ContractJsonValue.From(new Dictionary<string, object?>
                {
                    ["source_action_type"] = ReadEventPayloadString(
                        item.Payload,
                        "source_action_type"),
                    ["owner_player_id"] = sourceOwnerPlayerId,
                    ["activity_state_before"] = ReadEventPayloadString(
                        item.Payload,
                        "activity_state_before"),
                    ["activity_state_after"] = ReadEventPayloadString(
                        item.Payload,
                        "activity_state_after"),
                    ["aura_units"] = ReadEventPayloadInt(item.Payload, "aura_units"),
                    ["identity_redacted"] = true,
                }),
            };
        }

        if (!string.Equals(item.EventType, "zone_move", StringComparison.Ordinal))
        {
            return CloneEvent(item);
        }

        var ownerPlayerId = ReadEventPayloadString(item.Payload, "owner_player_id");
        if (string.Equals(ownerPlayerId, viewerPlayerId, StringComparison.Ordinal))
        {
            return CloneEvent(item);
        }

        var toZone = ReadEventPayloadString(item.Payload, "to_zone");
        if (string.Equals(toZone, "dominion", StringComparison.Ordinal))
        {
            return item with
            {
                Payload = ContractJsonValue.From(new Dictionary<string, object?>
                {
                    ["source_action_id"] = ReadEventPayloadString(
                        item.Payload,
                        "source_action_id"),
                    ["source_action_type"] = ReadEventPayloadString(
                        item.Payload,
                        "source_action_type"),
                    ["card_instance_id"] = ReadEventPayloadString(
                        item.Payload,
                        "card_instance_id"),
                    ["card_id"] = ReadEventPayloadString(item.Payload, "card_id"),
                    ["owner_player_id"] = ownerPlayerId,
                    ["controller_player_id"] = ReadEventPayloadString(
                        item.Payload,
                        "controller_player_id"),
                    ["from_zone"] = ReadEventPayloadString(item.Payload, "from_zone"),
                    ["to_zone"] = toZone,
                    ["domain_row"] = ReadEventPayloadString(item.Payload, "domain_row"),
                    ["lane_index"] = ReadEventPayloadInt(item.Payload, "lane_index"),
                    ["visibility_after"] = ReadEventPayloadString(
                        item.Payload,
                        "visibility_after"),
                    ["identity_redacted"] = false,
                }),
            };
        }

        if (string.Equals(toZone, "void", StringComparison.Ordinal))
        {
            return item with
            {
                Payload = ContractJsonValue.From(new Dictionary<string, object?>
                {
                    ["source_action_id"] = ReadEventPayloadString(
                        item.Payload,
                        "source_action_id"),
                    ["source_action_type"] = ReadEventPayloadString(
                        item.Payload,
                        "source_action_type"),
                    ["card_instance_id"] = ReadEventPayloadString(
                        item.Payload,
                        "card_instance_id"),
                    ["card_id"] = ReadEventPayloadString(item.Payload, "card_id"),
                    ["owner_player_id"] = ownerPlayerId,
                    ["controller_player_id"] = ReadEventPayloadString(
                        item.Payload,
                        "controller_player_id"),
                    ["from_zone"] = ReadEventPayloadString(item.Payload, "from_zone"),
                    ["to_zone"] = toZone,
                    ["to_zone_index"] = ReadEventPayloadInt(item.Payload, "to_zone_index"),
                    ["visibility_after"] = ReadEventPayloadString(
                        item.Payload,
                        "visibility_after"),
                    ["identity_redacted"] = false,
                }),
            };
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

        if (string.Equals(request.ActionType, "play_card", StringComparison.Ordinal))
        {
            var properties = request.Payload.EnumerateObject().ToArray();
            var names = properties.Select(property => property.Name).ToHashSet(StringComparer.Ordinal);
            var entityShape = properties.Length == 4
                && names.SetEquals(new[]
                {
                    "card_instance_id",
                    "aura_source_card_instance_ids",
                    "domain_row",
                    "lane_index",
                });
            var resolutionShape = properties.Length == 3
                && names.SetEquals(new[]
                {
                    "card_instance_id",
                    "aura_source_card_instance_ids",
                    "target_selections",
                });
            var valid = (entityShape || resolutionShape)
                && request.Payload.TryGetProperty("card_instance_id", out var cardInstanceId)
                && cardInstanceId.ValueKind == JsonValueKind.String
                && !string.IsNullOrWhiteSpace(cardInstanceId.GetString())
                && request.Payload.TryGetProperty(
                    "aura_source_card_instance_ids",
                    out var auraSourceIds)
                && auraSourceIds.ValueKind == JsonValueKind.Array
                && !auraSourceIds.EnumerateArray().Any(item =>
                    item.ValueKind != JsonValueKind.String
                    || string.IsNullOrWhiteSpace(item.GetString()));
            if (valid && entityShape)
            {
                valid = request.Payload.TryGetProperty("domain_row", out var domainRow)
                    && domainRow.ValueKind == JsonValueKind.String
                    && request.Payload.TryGetProperty("lane_index", out var laneIndex)
                    && laneIndex.ValueKind == JsonValueKind.Number
                    && laneIndex.TryGetInt32(out _);
            }

            if (valid && resolutionShape)
            {
                valid = request.Payload.TryGetProperty("target_selections", out var targetSelections)
                    && targetSelections.ValueKind == JsonValueKind.Array;
                if (valid)
                {
                    foreach (var selection in targetSelections.EnumerateArray())
                    {
                        if (selection.ValueKind != JsonValueKind.Object)
                        {
                            valid = false;
                            break;
                        }

                        var selectionProperties = selection.EnumerateObject().ToArray();
                        var selectionNames = selectionProperties
                            .Select(property => property.Name)
                            .ToHashSet(StringComparer.Ordinal);
                        if (selectionProperties.Length != 2
                            || !selectionNames.SetEquals(new[] { "target_id", "card_instance_ids" })
                            || !selection.TryGetProperty("target_id", out var targetId)
                            || targetId.ValueKind != JsonValueKind.String
                            || string.IsNullOrWhiteSpace(targetId.GetString())
                            || !selection.TryGetProperty("card_instance_ids", out var cardInstanceIds)
                            || cardInstanceIds.ValueKind != JsonValueKind.Array
                            || cardInstanceIds.EnumerateArray().Any(item =>
                                item.ValueKind != JsonValueKind.String
                                || string.IsNullOrWhiteSpace(item.GetString())))
                        {
                            valid = false;
                            break;
                        }
                    }
                }
            }

            if (!valid)
            {
                return Diagnostic(
                    "ACTION_PAYLOAD_INVALID",
                    "request_validation",
                    "Play Card payload does not match a supported card lifecycle.",
                    "The play_card payload must be exactly the Entity destination shape or the "
                    + "Incantation/Ritual target-selection shape with their required JSON types.",
                    "fix_request");
            }
        }

        if (string.Equals(request.ActionType, "resolve_triggered_ability", StringComparison.Ordinal))
        {
            var properties = request.Payload.EnumerateObject().ToArray();
            var names = properties.Select(property => property.Name).ToHashSet(StringComparer.Ordinal);
            var targetSelections = default(JsonElement);
            var valid = properties.Length == 2
                && names.SetEquals(new[] { "pending_trigger_id", "target_selections" })
                && request.Payload.TryGetProperty("pending_trigger_id", out var pendingTriggerId)
                && pendingTriggerId.ValueKind == JsonValueKind.String
                && !string.IsNullOrWhiteSpace(pendingTriggerId.GetString())
                && request.Payload.TryGetProperty("target_selections", out targetSelections)
                && targetSelections.ValueKind == JsonValueKind.Array;
            if (valid)
            {
                foreach (var selection in targetSelections.EnumerateArray())
                {
                    if (selection.ValueKind != JsonValueKind.Object)
                    {
                        valid = false;
                        break;
                    }

                    var selectionProperties = selection.EnumerateObject().ToArray();
                    var selectionNames = selectionProperties
                        .Select(property => property.Name)
                        .ToHashSet(StringComparer.Ordinal);
                    if (selectionProperties.Length != 2
                        || !selectionNames.SetEquals(new[] { "target_id", "card_instance_ids" })
                        || !selection.TryGetProperty("target_id", out var targetId)
                        || targetId.ValueKind != JsonValueKind.String
                        || string.IsNullOrWhiteSpace(targetId.GetString())
                        || !selection.TryGetProperty("card_instance_ids", out var cardInstanceIds)
                        || cardInstanceIds.ValueKind != JsonValueKind.Array
                        || cardInstanceIds.EnumerateArray().Any(item =>
                            item.ValueKind != JsonValueKind.String
                            || string.IsNullOrWhiteSpace(item.GetString())))
                    {
                        valid = false;
                        break;
                    }
                }
            }

            if (!valid)
            {
                return Diagnostic(
                    "ACTION_PAYLOAD_INVALID",
                    "request_validation",
                    "Triggered ability resolution requires a pending trigger and structured target selections.",
                    "The resolve_triggered_ability payload must contain exactly pending_trigger_id and "
                    + "target_selections; every selection must contain target_id and card_instance_ids.",
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

    private JsonElement BuildPlayCardPayloadSchema(MatchState state, PlayerState player)
    {
        var options = BuildPlayableCardOptions(state, player).Select(option =>
        {
            var value = new Dictionary<string, object?>
            {
                ["card_instance_id"] = option.Card.CardInstanceId,
                ["card_id"] = option.Card.CardId,
                ["card_type"] = option.Definition.CardType,
                ["required_magnitude"] = option.Magnitude.RequiredMagnitude,
                ["current_magnitude"] = option.Magnitude.CurrentMagnitude,
                ["printed_aura_cost"] = option.Aura.PrintedAuraCost,
                ["payable_aura_cost"] = option.Aura.NormalizedPayableAuraCost,
                ["aura_selection_mode"] = option.Aura.SelectionMode,
                ["eligible_aura_source_card_instance_ids"] = option.Aura.EligibleSources
                    .Select(source => source.CardInstanceId)
                    .ToArray(),
                ["forced_aura_source_card_instance_ids"] = option.Aura.ForcedSourceInstanceIds.ToArray(),
            };
            if (string.Equals(option.Definition.CardType, "entity", StringComparison.Ordinal))
            {
                value["entity_placements"] = option.Placements.Select(placement =>
                    new Dictionary<string, object?>
                    {
                        ["domain_row"] = placement.DomainRow == DomainRow.Horizon
                            ? "horizon"
                            : "zenith",
                        ["lane_index"] = placement.LaneIndex,
                    }).ToArray();
            }
            else
            {
                value["ability_id"] = option.ResolutionAbility!.AbilityId;
                value["resolution_target_contracts"] = option.TargetContracts.Select(contract =>
                    new Dictionary<string, object?>
                    {
                        ["target_id"] = contract.Definition.TargetId,
                        ["minimum_targets"] = contract.Definition.MinimumTargets,
                        ["maximum_targets"] = contract.Definition.MaximumTargets,
                        ["selection_method_id"] = contract.Definition.SelectionMethodId,
                        ["candidate_card_instance_ids"] = contract.Candidates
                            .Select(candidate => candidate.CardInstanceId)
                            .ToArray(),
                    }).ToArray();
            }

            return value;
        }).ToArray();
        return ContractJsonValue.From(new Dictionary<string, object?>
        {
            ["type"] = "object",
            ["required"] = new[] { "card_instance_id", "aura_source_card_instance_ids" },
            ["additional_properties"] = false,
            ["properties"] = new Dictionary<string, object?>
            {
                ["card_instance_id"] = new Dictionary<string, object?>
                {
                    ["type"] = "string",
                    ["min_length"] = 1,
                    ["source_zone"] = "hand",
                    ["supported_card_types"] = new[] { "entity", "incantation", "ritual" },
                },
                ["aura_source_card_instance_ids"] = new Dictionary<string, object?>
                {
                    ["type"] = "array",
                    ["unique_items"] = true,
                    ["items"] = new Dictionary<string, object?>
                    {
                        ["type"] = "string",
                        ["min_length"] = 1,
                        ["source_zone"] = "wellspring",
                    },
                },
                ["domain_row"] = new Dictionary<string, object?>
                {
                    ["type"] = "string",
                    ["enum"] = new[] { "horizon", "zenith" },
                    ["destination_zone"] = "dominion",
                    ["applies_to_card_type"] = "entity",
                },
                ["lane_index"] = new Dictionary<string, object?>
                {
                    ["type"] = "integer",
                    ["minimum"] = 0,
                    ["maximum"] = DomainState.LaneCount - 1,
                    ["applies_to_card_type"] = "entity",
                },
                ["target_selections"] = new Dictionary<string, object?>
                {
                    ["type"] = "array",
                    ["applies_to_card_types"] = new[] { "incantation", "ritual" },
                    ["items"] = new Dictionary<string, object?>
                    {
                        ["type"] = "object",
                        ["required"] = new[] { "target_id", "card_instance_ids" },
                        ["additional_properties"] = false,
                    },
                },
            },
            ["one_of"] = new object[]
            {
                new Dictionary<string, object?>
                {
                    ["card_type"] = "entity",
                    ["required"] = new[]
                    {
                        "card_instance_id",
                        "aura_source_card_instance_ids",
                        "domain_row",
                        "lane_index",
                    },
                    ["forbidden"] = new[] { "target_selections" },
                },
                new Dictionary<string, object?>
                {
                    ["card_types"] = new[] { "incantation", "ritual" },
                    ["required"] = new[]
                    {
                        "card_instance_id",
                        "aura_source_card_instance_ids",
                        "target_selections",
                    },
                    ["forbidden"] = new[] { "domain_row", "lane_index" },
                },
            },
            ["play_options"] = options,
        });
    }

    private static NormalInflowActionPayload ReadNormalInflowPayload(JsonElement payload) => new(
        payload.GetProperty("card_instance_id").GetString()!);

    private static PlayCardActionPayload ReadPlayCardPayload(JsonElement payload) => new(
        payload.GetProperty("card_instance_id").GetString()!,
        payload.TryGetProperty("domain_row", out var domainRow)
            ? domainRow.GetString()
            : null,
        payload.TryGetProperty("lane_index", out var laneIndex)
            ? laneIndex.GetInt32()
            : null,
        payload.GetProperty("aura_source_card_instance_ids")
            .EnumerateArray()
            .Select(item => item.GetString()!)
            .ToImmutableArray(),
        payload.TryGetProperty("target_selections", out var targetSelections)
            ? targetSelections.EnumerateArray()
                .Select(selection => new CanonicalTargetSelectionPayload(
                    selection.GetProperty("target_id").GetString()!,
                    selection.GetProperty("card_instance_ids")
                        .EnumerateArray()
                        .Select(item => item.GetString()!)
                        .ToImmutableArray()))
                .ToImmutableArray()
            : null);

    private static ResolveTriggeredAbilityActionPayload ReadResolveTriggeredAbilityPayload(
        JsonElement payload) => new(
        payload.GetProperty("pending_trigger_id").GetString()!,
        payload.GetProperty("target_selections")
            .EnumerateArray()
            .Select(selection => new CanonicalTargetSelectionPayload(
                selection.GetProperty("target_id").GetString()!,
                selection.GetProperty("card_instance_ids")
                    .EnumerateArray()
                    .Select(item => item.GetString()!)
                    .ToImmutableArray()))
            .ToImmutableArray());

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

    private static int ReadEventPayloadInt(JsonElement payload, string propertyName)
    {
        if (payload.ValueKind != JsonValueKind.Object
            || !payload.TryGetProperty(propertyName, out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var result))
        {
            throw new EngineStateException($"Event payload integer is missing: {propertyName}");
        }

        return result;
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
        string cardInstanceId,
        CanonicalCardCatalog? canonicalCards)
    {
        try
        {
            ValidateState(state, canonicalCards);
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
        string cardInstanceId,
        CanonicalCardCatalog? canonicalCards)
    {
        try
        {
            ValidateState(state, canonicalCards);
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

    internal static void ValidateState(
        MatchState state,
        CanonicalCardCatalog? canonicalCards = null,
        CanonicalAbilityCatalog? canonicalAbilities = null)
    {
        CanonicalContinuousEffects.ValidateState(state, canonicalCards, canonicalAbilities);
        var zoneIds = new HashSet<string>(StringComparer.Ordinal);
        var knownPlayerIds = state.Players
            .Select(player => player.PlayerId)
            .ToHashSet(StringComparer.Ordinal);
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
                         .Concat(player.VoidCardInstanceIds)
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

            ValidateDomainRowLengths(player);
            ValidateDeckState(state, player);
            ValidateHandState(state, player);
            ValidateVoidState(state, player);
            ValidateWellspringState(state, player);
            ValidateDomainState(state, player, knownPlayerIds, zoneIds);
        }

        if (!zoneIds.SetEquals(state.CardInstances.Keys))
        {
            throw new EngineStateException("Card instance registry and zones disagree.");
        }

        var listedDeckIds = state.Players
            .SelectMany(player => player.DeckCardInstanceIds)
            .ToHashSet(StringComparer.Ordinal);
        var registeredDeckIds = state.CardInstances.Values
            .Where(card => string.Equals(card.Zone, "deck", StringComparison.Ordinal))
            .Select(card => card.CardInstanceId)
            .ToHashSet(StringComparer.Ordinal);
        if (!listedDeckIds.SetEquals(registeredDeckIds))
        {
            throw new EngineStateException("Card instance registry and Deck zones disagree.");
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

        var listedVoidIds = state.Players
            .SelectMany(player => player.VoidCardInstanceIds)
            .ToHashSet(StringComparer.Ordinal);
        var registeredVoidIds = state.CardInstances.Values
            .Where(card => string.Equals(card.Zone, "void", StringComparison.Ordinal))
            .Select(card => card.CardInstanceId)
            .ToHashSet(StringComparer.Ordinal);
        if (!listedVoidIds.SetEquals(registeredVoidIds))
        {
            throw new EngineStateException("Card instance registry and Void zones disagree.");
        }

        var listedDomainIds = state.Players
            .SelectMany(player => player.Domain.HorizonCardInstanceIds
                .Concat(player.Domain.ZenithCardInstanceIds))
            .Where(cardInstanceId => cardInstanceId is not null)
            .Select(cardInstanceId => cardInstanceId!)
            .ToHashSet(StringComparer.Ordinal);
        var registeredDomainIds = state.CardInstances.Values
            .Where(card => string.Equals(card.Zone, "dominion", StringComparison.Ordinal))
            .Select(card => card.CardInstanceId)
            .ToHashSet(StringComparer.Ordinal);
        if (!listedDomainIds.SetEquals(registeredDomainIds))
        {
            throw new EngineStateException("Card instance registry and Domain zones disagree.");
        }

        foreach (var card in state.CardInstances.Values)
        {
            if (card.DamageMarked < 0)
            {
                throw new EngineStateException("Card damage_marked cannot be negative.");
            }

            if (card.Zone is not ("deck" or "hand" or "void" or "wellspring" or "dominion"))
            {
                throw new EngineStateException("Card instance zone must use an active production zone token.");
            }

            if (string.Equals(card.Zone, "dominion", StringComparison.Ordinal))
            {
                if (card.DomainRow is null
                    || card.DomainLaneIndex is null
                    || card.EnteredDomainTurnNumber is null)
                {
                    throw new EngineStateException(
                        "Domain card position and entry turn must be explicit.");
                }


                if (canonicalCards is not null)
                {
                    var effectiveMaxHp = CanonicalVitals.GetEffectiveMaxHp(state, card, canonicalCards);
                    if (card.DamageMarked >= effectiveMaxHp)
                    {
                        throw new EngineStateException(
                            "Committed Dominion Entity cannot have lethal accumulated damage.");
                    }
                }
                else if (card.DamageMarked > 0)
                {
                    throw new EngineStateException(
                        "Positive damage_marked requires canonical card-stat authority.");
                }

                continue;
            }

            if (card.DomainRow is not null
                || card.DomainLaneIndex is not null
                || card.EnteredDomainTurnNumber is not null)
            {
                throw new EngineStateException(
                    "Non-Domain card cannot carry Domain position or entry state.");
            }


            if (card.DamageMarked != 0)
            {
                throw new EngineStateException(
                    "Non-Domain card damage_marked must be zero in the current runtime slice.");
            }
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

        ValidatePendingTriggerWindow(state, knownPlayerIds);
    }

    private static void ValidatePendingTriggerWindow(
        MatchState state,
        IReadOnlySet<string> knownPlayerIds)
    {
        var window = state.PendingTriggerWindow;
        if (window is null)
        {
            return;
        }

        if (string.IsNullOrWhiteSpace(window.PendingWindowId)
            || !knownPlayerIds.Contains(window.ControllerPlayerId)
            || window.PendingTriggers.Count == 0
            || window.PendingTriggers.Select(item => item.PendingTriggerId)
                .Distinct(StringComparer.Ordinal).Count() != window.PendingTriggers.Count)
        {
            throw new EngineStateException("Pending canonical trigger window identity or membership is invalid.");
        }

        foreach (var pending in window.PendingTriggers)
        {
            if (string.IsNullOrWhiteSpace(pending.PendingTriggerId)
                || string.IsNullOrWhiteSpace(pending.AbilityId)
                || string.IsNullOrWhiteSpace(pending.TriggerId)
                || string.IsNullOrWhiteSpace(pending.CanonicalEventTypeId)
                || !string.Equals(
                    pending.ControllerPlayerId,
                    window.ControllerPlayerId,
                    StringComparison.Ordinal)
                || !state.CardInstances.TryGetValue(pending.SourceCardInstanceId, out var source)
                || !string.Equals(source.CardId, pending.SourceCardId, StringComparison.Ordinal)
                || !string.Equals(
                    source.ControllerPlayerId,
                    pending.ControllerPlayerId,
                    StringComparison.Ordinal)
                || pending.SourceEngineEventSequence < 1
                || pending.SourceEngineEventSequence > state.Events.Count)
            {
                throw new EngineStateException("Pending canonical trigger source identity is invalid.");
            }

            var sourceEvent = state.Events[pending.SourceEngineEventSequence - 1];
            if (!string.Equals(sourceEvent.EventId, pending.SourceEngineEventId, StringComparison.Ordinal)
                || !string.Equals(
                    CanonicalTriggerResolver.MapEngineEventType(sourceEvent.EventType),
                    pending.CanonicalEventTypeId,
                    StringComparison.Ordinal))
            {
                throw new EngineStateException("Pending canonical trigger source event is invalid.");
            }

            var zoneChanged = string.Equals(
                pending.CanonicalEventTypeId,
                CanonicalTriggerResolver.ZoneChangedCanonicalEventTypeId,
                StringComparison.Ordinal);
            if (zoneChanged
                    ? pending.SourceFromZoneId is null
                      || pending.SourceToZoneId is null
                      || pending.SourceZoneTransitionInstanceId is null
                      || !string.Equals(source.Zone, pending.SourceToZoneId, StringComparison.Ordinal)
                    : pending.SourceFromZoneId is not null
                      || pending.SourceToZoneId is not null
                      || pending.SourceZoneTransitionInstanceId is not null)
            {
                throw new EngineStateException("Pending canonical trigger event context is invalid.");
            }
        }
    }

    private static void ValidateDomainRowLengths(PlayerState player)
    {
        if (player.Domain.HorizonCardInstanceIds.Count != DomainState.LaneCount
            || player.Domain.ZenithCardInstanceIds.Count != DomainState.LaneCount)
        {
            throw new EngineStateException(
                "Domain Horizon and Zenith rows must each contain exactly six slots.");
        }
    }

    private static void ValidateDomainState(
        MatchState state,
        PlayerState player,
        IReadOnlySet<string> knownPlayerIds,
        ISet<string> zoneIds)
    {
        ValidateDomainRowState(
            state,
            player,
            DomainRow.Horizon,
            player.Domain.HorizonCardInstanceIds,
            knownPlayerIds,
            zoneIds);
        ValidateDomainRowState(
            state,
            player,
            DomainRow.Zenith,
            player.Domain.ZenithCardInstanceIds,
            knownPlayerIds,
            zoneIds);
    }

    private static void ValidateDomainRowState(
        MatchState state,
        PlayerState player,
        DomainRow row,
        IReadOnlyList<string?> slots,
        IReadOnlySet<string> knownPlayerIds,
        ISet<string> zoneIds)
    {
        for (var laneIndex = 0; laneIndex < slots.Count; laneIndex++)
        {
            var cardInstanceId = slots[laneIndex];
            if (cardInstanceId is null)
            {
                continue;
            }

            if (string.IsNullOrWhiteSpace(cardInstanceId))
            {
                throw new EngineStateException("Occupied Domain slot card instance ID is invalid.");
            }

            if (!zoneIds.Add(cardInstanceId))
            {
                throw new EngineStateException("Card instance appears in multiple zones or Domain slots.");
            }

            if (!state.CardInstances.TryGetValue(cardInstanceId, out var card))
            {
                throw new EngineStateException("Domain slot references an unknown card instance.");
            }

            if (!knownPlayerIds.Contains(card.OwnerPlayerId))
            {
                throw new EngineStateException("Domain card owner must be a known player.");
            }

            if (!string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal))
            {
                throw new EngineStateException(
                    "Domain card controller must match the occupying player state.");
            }

            if (!string.Equals(card.Zone, "dominion", StringComparison.Ordinal))
            {
                throw new EngineStateException("Domain card zone must be dominion.");
            }

            if (card.ZoneIndex != -1)
            {
                throw new EngineStateException("Domain card zone index must be the non-applicable sentinel -1.");
            }

            if (!string.Equals(card.Visibility, "public", StringComparison.Ordinal))
            {
                throw new EngineStateException("Domain card visibility must be public.");
            }

            if (card.ActivityState is not ("active" or "exhausted"))
            {
                throw new EngineStateException("Domain card activity state must be active or exhausted.");
            }

            if (card.DomainRow != row || card.DomainLaneIndex != laneIndex)
            {
                throw new EngineStateException(
                    "Domain card row and lane coordinates must match occupancy.");
            }

            if (card.EnteredDomainTurnNumber is not int enteredTurnNumber
                || enteredTurnNumber <= 0
                || enteredTurnNumber > state.TurnNumber)
            {
                throw new EngineStateException(
                    "Domain card entered turn must be positive and cannot be in the future.");
            }
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

    private static void ValidateDeckState(MatchState state, PlayerState player)
    {
        for (var zoneIndex = 0; zoneIndex < player.DeckCardInstanceIds.Count; zoneIndex++)
        {
            var card = state.GetCardInstance(player.DeckCardInstanceIds[zoneIndex]);
            if (!string.Equals(card.Zone, "deck", StringComparison.Ordinal))
            {
                throw new EngineStateException("Deck card zone must be deck.");
            }

            if (card.ZoneIndex != zoneIndex)
            {
                throw new EngineStateException("Deck card zone index must match list order.");
            }

            if (!string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
                || !string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal))
            {
                throw new EngineStateException("Deck card owner and controller must match the player state.");
            }

            if (!string.Equals(card.Visibility, "owner_only", StringComparison.Ordinal))
            {
                throw new EngineStateException("Deck card visibility must be owner_only.");
            }

            if (card.ActivityState is not null)
            {
                throw new EngineStateException("Deck card activity state must be null.");
            }
        }
    }

    private static void ValidateVoidState(MatchState state, PlayerState player)
    {
        for (var zoneIndex = 0; zoneIndex < player.VoidCardInstanceIds.Count; zoneIndex++)
        {
            var card = state.GetCardInstance(player.VoidCardInstanceIds[zoneIndex]);
            if (!string.Equals(card.Zone, "void", StringComparison.Ordinal))
            {
                throw new EngineStateException("Void card zone must be void.");
            }

            if (card.ZoneIndex != zoneIndex)
            {
                throw new EngineStateException("Void card zone index must match list order.");
            }

            if (!string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal))
            {
                throw new EngineStateException("Void card owner must match the player state.");
            }

            if (!string.Equals(card.Visibility, "public", StringComparison.Ordinal))
            {
                throw new EngineStateException("Void card visibility must be public.");
            }

            if (card.ActivityState is not null)
            {
                throw new EngineStateException("Void card activity state must be null.");
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

    private sealed record PlayCardAvailability(bool Enabled, string? DisabledReason);

    private sealed record PlayCardPlacementOption(DomainRow DomainRow, int LaneIndex);

    private sealed record PlayCardTargetContractOption(
        CanonicalAbilityTargetDefinition Definition,
        ImmutableArray<CanonicalTargetCandidate> Candidates);

    private sealed record PlayCardOption(
        CardInstanceState Card,
        RuntimeCardDefinition Definition,
        MagnitudePreflightResult Magnitude,
        AuraPaymentPreflightResult Aura,
        ImmutableArray<PlayCardPlacementOption> Placements,
        CanonicalAbilityDefinition? ResolutionAbility,
        ImmutableArray<PlayCardTargetContractOption> TargetContracts);

    private sealed record PlayCardPlan(
        PlayerState Player,
        CardInstanceState Card,
        int HandIndex,
        ImmutableArray<CardInstanceState> AuraSources,
        DomainRow? DomainRow,
        int? LaneIndex,
        PlayedCardResolutionPlan? Resolution);

    private sealed record PlayedCardResolutionPlan(CanonicalEffectExecutionPlan EffectPlan);

    private sealed record TriggeredAbilityResolutionPlan(
        PendingTriggeredAbilityState PendingTrigger,
        CanonicalAbilityDefinition Ability,
        CanonicalEffectExecutionPlan EffectPlan);

    private sealed class PlayCardValidationException : Exception
    {
        private PlayCardValidationException(
            string reason,
            string code,
            string safeMessage,
            string developerMessage,
            string retryPolicy)
            : base(developerMessage)
        {
            Reason = reason;
            Code = code;
            SafeMessage = safeMessage;
            RetryPolicy = retryPolicy;
        }

        public string Reason { get; }

        public string Code { get; }

        public string SafeMessage { get; }

        public string RetryPolicy { get; }

        public static PlayCardValidationException Create(
            string reason,
            string code,
            string safeMessage,
            string developerMessage,
            string retryPolicy) => new(
                reason,
                code,
                safeMessage,
                developerMessage,
                retryPolicy);
    }
}

public sealed class EngineStateException : Exception
{
    public EngineStateException(string message)
        : base(message)
    {
        Code = "STATE_INVARIANT_FAILED";
    }

    public EngineStateException(string code, string message)
        : base(message)
    {
        Code = code;
    }

    public string Code { get; }
}
