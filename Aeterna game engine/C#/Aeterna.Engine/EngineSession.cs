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
    private CanonicalAbilityRuntimeContext? _canonicalRuntime;
    private ImmutableArray<CanonicalTriggeredAbilityDiscovery> _canonicalTriggerDiscoveries =
        ImmutableArray<CanonicalTriggeredAbilityDiscovery>.Empty;
    private ImmutableArray<CanonicalAbilityResolutionRecord> _canonicalAbilityResolutions =
        ImmutableArray<CanonicalAbilityResolutionRecord>.Empty;
    private readonly bool _legacyActionCompatibility;
    private readonly ReactionPolicyResolver _reactionPolicyResolver = ReactionPolicyResolver.Empty;

    public EngineSession()
    {
    }

    internal EngineSession(bool legacyActionCompatibility)
    {
        _legacyActionCompatibility = legacyActionCompatibility;
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
        CanonicalCardCatalog? canonicalCards,
        ReactionPolicyResolver? reactionPolicyResolver = null)
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
        _reactionPolicyResolver = reactionPolicyResolver ?? ReactionPolicyResolver.Empty;
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
            state.StartingPlayerId,
            state.ActivePlayerId,
            state.PriorityPlayerId,
            players,
            legalActions,
            state.Events.Count,
            ContractJsonValue.From(BuildDomainBoardProjection(state)),
            new ResourceSummary(ContractSchemas.ResourceSummary, resourceSummaries),
            BuildPendingDecisionSummary(state, playerId),
            state.Result);
    }

    public LegalActionSpace ListLegalActions(string playerId, bool includeDisabled = false)
    {
        var state = RequireState();
        ValidateState(state, _canonicalRuntime?.Cards, _canonicalRuntime?.Abilities);
        var player = RequireKnownPlayer(state, playerId);
        var baseActions = _legacyActionCompatibility
            ? BuildLegacyActions(state, player)
            : BuildCanonicalPhaseActions(state, player);
        if (state.ReactionWindow is not null)
        {
            return BuildReactionLegalActionSpace(
                state,
                player,
                baseActions,
                includeDisabled);
        }

        if (state.PendingTriggerWindow is not null)
        {
            return BuildPendingTriggerLegalActionSpace(
                state,
                player,
                baseActions,
                includeDisabled);
        }

        return BuildLegalActionSpace(state, player.PlayerId, baseActions, includeDisabled);
    }

    private ImmutableArray<LegalAction> BuildCanonicalPhaseActions(
        MatchState state,
        PlayerState player)
    {
        var active = string.Equals(player.PlayerId, state.ActivePlayerId, StringComparison.Ordinal);
        var actions = ImmutableArray.CreateBuilder<LegalAction>();
        actions.Add(new LegalAction(
            $"advance_phase:{state.TurnNumber}:{state.StateVersion}:{state.Phase}:{player.PlayerId}",
            "advance_phase",
            player.PlayerId,
            active,
            100,
            active ? null : "not_active_player",
            ContractJsonValue.EmptyObject()));

        if (string.Equals(state.Phase, CanonicalPhaseIds.Infusion, StringComparison.Ordinal))
        {
            var used = player.NormalInflowUsedTurnNumber == state.TurnNumber;
            var enabled = active && !used && player.HandCardInstanceIds.Count > 0;
            var disabledReason = !active
                ? "not_active_player"
                : used
                    ? "normal_inflow_already_used"
                    : player.HandCardInstanceIds.Count == 0
                        ? "hand_empty"
                        : null;
            actions.Add(new LegalAction(
                $"normal_inflow:{state.TurnNumber}:{state.StateVersion}:{player.PlayerId}",
                "normal_inflow",
                player.PlayerId,
                enabled,
                150,
                disabledReason,
                BuildNormalInflowPayloadSchema()));
        }
        else if (string.Equals(state.Phase, CanonicalPhaseIds.Manifestation, StringComparison.Ordinal))
        {
            var availability = EvaluatePlayCardAvailability(state, player, active);
            actions.Add(new LegalAction(
                $"play_card:{state.TurnNumber}:{state.StateVersion}:{player.PlayerId}",
                "play_card",
                player.PlayerId,
                availability.Enabled,
                175,
                availability.DisabledReason,
                BuildPlayCardPayloadSchema(state, player)));
        }

        return actions.ToImmutable();
    }

    private ImmutableArray<LegalAction> BuildLegacyActions(MatchState state, PlayerState player)
    {
        var active = string.Equals(player.PlayerId, state.ActivePlayerId, StringComparison.Ordinal);
        var used = player.NormalInflowUsedTurnNumber == state.TurnNumber;
        var normalInflowEnabled = active && !used && player.HandCardInstanceIds.Count > 0;
        var normalInflowDisabledReason = !active
            ? "not_active_player"
            : used
                ? "normal_inflow_already_used"
                : player.HandCardInstanceIds.Count == 0
                    ? "hand_empty"
                    : null;
        var playCardAvailability = EvaluatePlayCardAvailability(state, player, active);
        return
        [
            new LegalAction(
                $"end_turn:{state.TurnNumber}:{player.PlayerId}",
                "end_turn",
                player.PlayerId,
                active,
                100,
                active ? null : "not_active_player",
                ContractJsonValue.EmptyObject()),
            new LegalAction(
                $"normal_inflow:{state.TurnNumber}:{state.StateVersion}:{player.PlayerId}",
                "normal_inflow",
                player.PlayerId,
                normalInflowEnabled,
                150,
                normalInflowDisabledReason,
                BuildNormalInflowPayloadSchema()),
            new LegalAction(
                $"play_card:{state.TurnNumber}:{state.StateVersion}:{player.PlayerId}",
                "play_card",
                player.PlayerId,
                playCardAvailability.Enabled,
                175,
                playCardAvailability.DisabledReason,
                BuildPlayCardPayloadSchema(state, player)),
            new LegalAction(
                $"draw_card:{state.TurnNumber}:{state.StateVersion}:{player.PlayerId}",
                "draw_card",
                player.PlayerId,
                active && player.DeckCardInstanceIds.Count > 0,
                200,
                active
                    ? player.DeckCardInstanceIds.Count > 0 ? null : "deck_empty"
                    : "not_active_player",
                ContractJsonValue.EmptyObject()),
        ];
    }

    private LegalActionSpace BuildReactionLegalActionSpace(
        MatchState state,
        PlayerState player,
        ImmutableArray<LegalAction> baseActions,
        bool includeDisabled)
    {
        var window = state.ReactionWindow
            ?? throw new EngineStateException("Reaction legal action space requires an open window.");
        var hasPriority = string.Equals(
            player.PlayerId,
            state.PriorityPlayerId,
            StringComparison.Ordinal);
        var options = hasPriority
            ? ResolveCurrentReactionOptions(state, player.PlayerId)
            : ImmutableArray<ReactionOption>.Empty;
        var actions = baseActions
            .Select(action => action with
            {
                Enabled = false,
                DisabledReason = "reaction_window_open",
            })
            .Prepend(new LegalAction(
                $"react:{window.ReactionWindowId}:{state.StateVersion}:{player.PlayerId}",
                "react",
                player.PlayerId,
                hasPriority && options.Length > 0,
                25,
                !hasPriority ? "not_priority_player" : options.Length == 0 ? "no_legal_reaction" : null,
                hasPriority
                    ? BuildReactPayloadSchema(options)
                    : BuildUnavailableReactionPayloadSchema()))
            .Prepend(new LegalAction(
                $"pass_priority:{window.ReactionWindowId}:{state.StateVersion}:{player.PlayerId}",
                "pass_priority",
                player.PlayerId,
                hasPriority,
                20,
                hasPriority ? null : "not_priority_player",
                ContractJsonValue.EmptyObject()))
            .ToImmutableArray();
        return BuildLegalActionSpace(state, player.PlayerId, actions, includeDisabled);
    }

    private ImmutableArray<ReactionOption> ResolveCurrentReactionOptions(
        MatchState state,
        string playerId)
    {
        var window = state.ReactionWindow
            ?? throw new EngineStateException("Reaction options require an open window.");
        var runtimePackage = _runtimePackage
            ?? throw new EngineStateException(
                "REACTION_RUNTIME_PACKAGE_MISSING",
                "Reaction options require the validated gameplay runtime package.");
        var canonicalRuntime = _canonicalRuntime
            ?? throw new EngineStateException(
                "REACTION_CANONICAL_RUNTIME_MISSING",
                "Reaction options require canonical ability authority.");
        return _reactionPolicyResolver.ResolveOptions(
            window,
            playerId,
            state,
            runtimePackage,
            canonicalRuntime.Cards,
            canonicalRuntime.Abilities);
    }

    private static JsonElement BuildReactPayloadSchema(ImmutableArray<ReactionOption> options) =>
        ContractJsonValue.From(new Dictionary<string, object?>
        {
            ["type"] = "object",
            ["required"] = new[] { "reaction_option_id", "target_selections" },
            ["additional_properties"] = false,
            ["properties"] = new Dictionary<string, object?>
            {
                ["reaction_option_id"] = new Dictionary<string, object?>
                {
                    ["type"] = "string",
                    ["enum"] = options.Select(option => option.ReactionOptionId).ToArray(),
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
            ["reaction_options"] = options.Select(option => new Dictionary<string, object?>
            {
                ["reaction_option_id"] = option.ReactionOptionId,
                ["source_card_instance_id"] = option.SourceCardInstanceId,
                ["source_card_id"] = option.SourceCardId,
                ["ability_id"] = option.Ability.AbilityId,
                ["target_contracts"] = option.TargetContracts.Select(contract =>
                    new Dictionary<string, object?>
                    {
                        ["target_id"] = contract.Definition.TargetId,
                        ["minimum_targets"] = contract.Definition.MinimumTargets,
                        ["maximum_targets"] = contract.Definition.MaximumTargets,
                        ["selection_method_id"] = contract.Definition.SelectionMethodId,
                        ["candidate_card_instance_ids"] = contract.Candidates
                            .Select(candidate => candidate.CardInstanceId)
                            .ToArray(),
                    }).ToArray(),
                ["next_response_policy_id"] = option.NextResponsePolicyId,
            }).ToArray(),
        });

    private static JsonElement BuildUnavailableReactionPayloadSchema() =>
        ContractJsonValue.From(new Dictionary<string, object?>
        {
            ["type"] = "object",
            ["available"] = false,
        });

    private LegalActionSpace BuildPendingTriggerLegalActionSpace(
        MatchState state,
        PlayerState player,
        ImmutableArray<LegalAction> baseActions,
        bool includeDisabled)
    {
        // This remains the narrow mandatory-trigger gate. Phase advancement cannot
        // bypass it, and no reaction/priority protocol is introduced here.
        var window = state.PendingTriggerWindow
            ?? throw new EngineStateException("Pending trigger legal action space requires a pending window.");
        var isController = string.Equals(
            player.PlayerId,
            window.ControllerPlayerId,
            StringComparison.Ordinal);
        var actions = baseActions
            .Select(action => action with
            {
                Enabled = false,
                DisabledReason = "pending_trigger_resolution_required",
            })
            .Prepend(new LegalAction(
                $"resolve_triggered_ability:{state.StateVersion}:{player.PlayerId}",
                "resolve_triggered_ability",
                player.PlayerId,
                isController,
                50,
                isController ? null : "not_pending_trigger_controller",
                isController
                    ? BuildResolveTriggeredAbilityPayloadSchema(state, window)
                    : BuildUnavailableResolveTriggeredAbilityPayloadSchema()))
            .ToImmutableArray();
        return BuildLegalActionSpace(state, player.PlayerId, actions, includeDisabled);
    }

    private static LegalActionSpace BuildLegalActionSpace(
        MatchState state,
        string playerId,
        IEnumerable<LegalAction> actions,
        bool includeDisabled)
    {
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
                .Where(CanonicalTargetResolver.IsClientSelectable)
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
                            canonicalRuntime.Cards,
                            canonicalRuntime.Abilities)
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

    private static JsonElement BuildPendingDecisionSummary(MatchState state, string viewerPlayerId)
    {
        var reaction = state.ReactionWindow;
        if (reaction is not null)
        {
            return ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["has_pending"] = true,
                ["pending_type"] = "reaction_window",
                ["pending_window_id"] = reaction.ReactionWindowId,
                ["reaction_subject_id"] = reaction.ReactionSubjectId,
                ["originating_event_id"] = reaction.OriginatingEventId,
                ["priority_player_id"] = state.PriorityPlayerId,
                ["viewer_is_priority_player"] = string.Equals(
                    viewerPlayerId,
                    state.PriorityPlayerId,
                    StringComparison.Ordinal),
                ["viewer_is_eligible_responder"] = reaction.EligibleResponderPlayerIds.Contains(
                    viewerPlayerId,
                    StringComparer.Ordinal),
                ["response_policy_id"] = reaction.CurrentResponsePolicyId,
                ["consecutive_pass_count"] = reaction.ConsecutivePassCount,
                ["stack_depth"] = state.ResolutionStack.Count,
                ["resolution_zone"] = BuildZoneSnapshot(
                    state,
                    "resolution",
                    state.ResolutionCardInstanceIds,
                    "public"),
            });
        }

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
            && state.PendingTriggerWindow is null
            && state.ReactionWindow is null;
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
            "advance_phase" => ApplyAdvancePhase(state, request, stateVersionBefore),
            "draw_card" => ApplyDraw(state, request, stateVersionBefore),
            "normal_inflow" => ApplyNormalInflow(state, request, stateVersionBefore),
            "play_card" => ApplyPlayCard(state, request, stateVersionBefore),
            "resolve_triggered_ability" => ApplyResolveTriggeredAbility(state, request, stateVersionBefore),
            "pass_priority" => ApplyPassPriority(state, request, stateVersionBefore),
            "react" => ApplyReact(state, request, stateVersionBefore),
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
        var reactionLifecycleHandled = request.ActionType is "pass_priority" or "react";
        var triggerEvents = response.Accepted && !reactionLifecycleHandled
            ? DiscoverCanonicalTriggers(state, response.Events)
            : ImmutableArray<EngineEvent>.Empty;
        if (response.Accepted)
        {
            ProcessQueuedTriggerCheckpoint(state);
        }

        ValidateState(state, _canonicalRuntime?.Cards, _canonicalRuntime?.Abilities);
        var materializedResponse = triggerEvents.IsDefaultOrEmpty
            ? response
            : response with { Events = response.Events.AddRange(triggerEvents) };
        return ProjectActionResponseForViewer(materializedResponse, request.PlayerId);
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
            state.StartingPlayerId,
            state.ActivePlayerId,
            state.PriorityPlayerId,
            state.ResolutionCardInstanceIds.ToImmutableArray(),
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
            BuildPendingDecisionSummary(state, state.PriorityPlayerId),
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

        if (!string.Equals(state.Phase, CanonicalPhaseIds.Manifestation, StringComparison.Ordinal)
            && !(_legacyActionCompatibility
                 && string.Equals(state.Phase, CanonicalPhaseIds.LegacyMain, StringComparison.Ordinal)))
        {
            return new PlayCardAvailability(false, "phase_not_manifestation");
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
                var targets = CanonicalTargetResolver.GetSupportedTargets(resolutionAbility);
                var collectionTargetsResolvable = targets
                    .Where(target => CanonicalTargetResolver.IsClientSelectable(target)
                                     || CanonicalTargetResolver.IsAutomaticCollection(target))
                    .All(target => CanonicalTargetResolver.ResolveCandidates(
                        target,
                        resolutionAbility,
                        player.PlayerId,
                        state,
                        runtimePackage,
                        _canonicalRuntime.Cards,
                        _canonicalRuntime.Abilities).Length >= target.MinimumTargets);
                var contracts = targets
                    .Where(CanonicalTargetResolver.IsClientSelectable)
                    .Select(target => new PlayCardTargetContractOption(
                        target,
                        CanonicalTargetResolver.ResolveCandidates(
                            target,
                            resolutionAbility,
                            player.PlayerId,
                            state,
                            runtimePackage,
                            _canonicalRuntime.Cards,
                            _canonicalRuntime.Abilities)))
                    .ToImmutableArray();
                if (collectionTargetsResolvable)
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

        if (string.IsNullOrWhiteSpace(request.StartingPlayerId)
            || request.Players.IsDefault
            || request.Players.Count(player => player is not null
                && string.Equals(
                    player.PlayerId,
                    request.StartingPlayerId,
                    StringComparison.Ordinal)) != 1)
        {
            throw new EngineInputException(
                "STARTING_PLAYER_INVALID",
                "Starting player must identify exactly one configured player.");
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

    private MatchState BuildInitialState(CreateMatchRequest request, RuntimePackageCatalog package)
    {
        var state = new MatchState
        {
            MatchId = request.MatchId,
            Seed = request.Seed,
            RuntimePackageId = package.PackageId,
            StateVersion = 0,
            Phase = _legacyActionCompatibility
                ? CanonicalPhaseIds.LegacyMain
                : CanonicalPhaseIds.Awakening,
            LegacyPhaseCompatibility = _legacyActionCompatibility,
            StartingPlayerId = request.StartingPlayerId,
            ActivePlayerId = request.StartingPlayerId,
            PriorityPlayerId = request.StartingPlayerId,
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

        if (!_legacyActionCompatibility)
        {
            var initialEntry = CanonicalPhaseLifecycle.PlanAwakeningEntry(
                state,
                state.StartingPlayerId,
                drawCount: 0);
            CanonicalPhaseLifecycle.ApplyAwakeningEntry(state, initialEntry);
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

        var transition = CanonicalDrawTransition.PlanTopCard(
            state,
            player.PlayerId,
            player.DeckCardInstanceIds,
            player.HandCardInstanceIds.Count);
        CanonicalDrawTransition.Apply(state, transition);
        state.StateVersion += 1;
        var eventSequence = state.Events.Count + 1;
        var payload = new ZoneMovePayload(
            request.ActionId,
            request.ActionType,
            transition.CardInstanceId,
            transition.CardId,
            transition.PlayerId,
            transition.PlayerId,
            "deck",
            "hand",
            transition.FromZoneIndex,
            transition.ToZoneIndex,
            transition.VisibilityBefore,
            transition.VisibilityAfter);
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

        if (plan.Resolution is not null)
        {
            var opening = _reactionPolicyResolver.ResolveOpening(
                plan.Resolution.EffectPlan.Context.Ability.AbilityId,
                request.PlayerId,
                state);
            if (opening is not null)
            {
                return ApplyReactablePlayCard(state, request, stateVersionBefore, plan, opening);
            }
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
            MovePlayedCardFromHandToResolution(
                state,
                plan.Player,
                plan.Card,
                plan.HandIndex);
            CanonicalEffectExecutor.Apply(state, plan.Resolution.EffectPlan);
            MovePlayedCardFromResolutionToVoid(state, plan.Card);
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

    private ActionResponse ApplyReactablePlayCard(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore,
        PlayCardPlan plan,
        ReactionOpeningPlan opening)
    {
        if (!ReactionPolicyIds.IsOpenWindowPolicy(opening.InitialResponsePolicyId)
            || opening.EligibleResponderPlayerIds.IsDefaultOrEmpty
            || opening.EligibleResponderPlayerIds.Distinct(StringComparer.Ordinal).Count()
            != opening.EligibleResponderPlayerIds.Length
            || opening.EligibleResponderPlayerIds.Any(playerId => state.Players.All(player =>
                !string.Equals(player.PlayerId, playerId, StringComparison.Ordinal)))
            || !opening.EligibleResponderPlayerIds.Contains(
                opening.InitialPriorityPlayerId,
                StringComparer.Ordinal))
        {
            return RejectAction(
                state,
                request,
                "reaction_response_policy_unsupported",
                Diagnostic(
                    "REACTION_RESPONSE_POLICY_UNSUPPORTED",
                    "transition_validation",
                    "The configured reaction response policy is unsupported.",
                    "The explicit Reaction opening profile does not produce a supported responder policy.",
                    "fix_runtime_package"));
        }

        var policyShapeValid = string.Equals(
                opening.InitialResponsePolicyId,
                ReactionPolicyIds.StandardAlternatingResponse,
                StringComparison.Ordinal)
            ? opening.EligibleResponderPlayerIds.Length == state.Players.Count
              && state.Players.All(player => opening.EligibleResponderPlayerIds.Contains(
                  player.PlayerId,
                  StringComparer.Ordinal))
            : opening.EligibleResponderPlayerIds.Length == 1;
        if (!policyShapeValid)
        {
            return RejectAction(
                state,
                request,
                "reaction_response_policy_unsupported",
                Diagnostic(
                    "REACTION_RESPONSE_POLICY_UNSUPPORTED",
                    "transition_validation",
                    "The configured reaction response policy is unsupported.",
                    "The explicit Reaction opening responder set conflicts with its typed response policy.",
                    "fix_runtime_package"));
        }

        if (state.PendingTriggerWindow is not null
            || state.ReactionWindow is not null
            || state.ResolutionStack.Count != 0
            || state.QueuedTriggerBatches.Count != 0)
        {
            return RejectAction(
                state,
                request,
                "reaction_pending_conflict",
                Diagnostic(
                    "REACTION_PENDING_CONFLICT",
                    "transition_validation",
                    "A reaction window cannot open while another decision is pending.",
                    "The v1 Reaction profile reached a conflicting pending family or unresolved queue.",
                    "refresh_projection"));
        }

        if (state.NextReactionWindowSequence == int.MaxValue
            || state.NextReactionSubjectSequence == int.MaxValue
            || state.NextResolutionSequence == int.MaxValue)
        {
            return RejectAction(
                state,
                request,
                "reaction_identity_exhausted",
                Diagnostic(
                    "REACTION_RESOLUTION_UNSUPPORTED",
                    "transition_validation",
                    "The reaction transition cannot allocate deterministic identities.",
                    "A MatchState-owned Reaction identity sequence reached its supported integer boundary.",
                    "engine_bug"));
        }

        var effectPlan = plan.Resolution?.EffectPlan
            ?? throw new EngineStateException("Reactable play requires a canonical resolution plan.");
        var resolutionSequence = state.NextResolutionSequence;
        var resolutionId = $"resolution:{state.MatchId}:{resolutionSequence:000000}";
        var reactionWindowId = $"reaction-window:{state.MatchId}:{state.NextReactionWindowSequence:000000}";
        var reactionSubjectId = $"reaction-subject:{state.MatchId}:{state.NextReactionSubjectSequence:000000}";
        var stateVersionAfter = state.StateVersion + 1;

        foreach (var source in plan.AuraSources)
        {
            source.ActivityState = "exhausted";
        }

        MovePlayedCardFromHandToResolution(
            state,
            plan.Player,
            plan.Card,
            plan.HandIndex);
        var targetStates = CaptureDeclaredTargetStates(effectPlan, state);

        var abilityState = new CanonicalAbilityResolutionState(
            CanonicalEffectExecutor.PlayedCardOriginId,
            request.ActionId,
            request.ActionType,
            effectPlan.Context.Ability.AbilityId,
            plan.Card.CardInstanceId,
            plan.Card.CardId,
            plan.Card.Zone,
            plan.Card.ZoneSequence,
            ReactionPolicyIds.PlayedCardResolutionPresence,
            request.PlayerId,
            effectPlan.Context.TargetSelections,
            targetStates,
            PendingTriggerId: null,
            TriggerId: null,
            DeclarationStateVersion: stateVersionAfter);
        state.ResolutionStack.Add(new ResolutionStackEntryState
        {
            ResolutionId = resolutionId,
            Sequence = resolutionSequence,
            EntryKindId = "underlying_resolution",
            ReactionWindowId = reactionWindowId,
            ReactionSubjectId = reactionSubjectId,
            ParentResolutionId = null,
            AbilityResolution = abilityState,
        });
        var window = new ReactionWindowState
        {
            ReactionWindowId = reactionWindowId,
            ReactionSubjectId = reactionSubjectId,
            OriginatingEventId = null,
            OriginatingEventSequence = null,
            UnderlyingResolutionId = resolutionId,
            InitiatorPlayerId = request.PlayerId,
            CurrentResponsePolicyId = opening.InitialResponsePolicyId,
            ConsecutivePassCount = 0,
            OpenedAtStateVersion = stateVersionAfter,
            ReactionProfileId = opening.ReactionProfileId,
        };
        window.EligibleResponderPlayerIds.AddRange(opening.EligibleResponderPlayerIds);
        state.ReactionWindow = window;
        state.PriorityPlayerId = opening.InitialPriorityPlayerId;
        state.NextResolutionSequence += 1;
        state.NextReactionWindowSequence += 1;
        state.NextReactionSubjectSequence += 1;
        state.StateVersion = stateVersionAfter;

        var events = ImmutableArray.CreateBuilder<EngineEvent>();
        foreach (var source in plan.AuraSources)
        {
            events.Add(CreatePlayCardEvent(
                state,
                request,
                stateVersionAfter,
                state.Events.Count + events.Count + 1,
                "aura_source_exhausted",
                ContractJsonValue.From(new AuraSourceExhaustedPayload(
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
                    AuraUnits: 1))));
        }

        events.Add(CreatePlayCardEvent(
            state,
            request,
            stateVersionAfter,
            state.Events.Count + events.Count + 1,
            "zone_move",
            ContractJsonValue.From(new ZoneMovePayload(
                request.ActionId,
                request.ActionType,
                plan.Card.CardInstanceId,
                plan.Card.CardId,
                plan.Card.OwnerPlayerId,
                plan.Card.ControllerPlayerId,
                "hand",
                "resolution",
                plan.HandIndex,
                plan.Card.ZoneIndex,
                "owner_only",
                "public"))));
        events.Add(CreatePlayCardEvent(
            state,
            request,
            stateVersionAfter,
            state.Events.Count + events.Count + 1,
            "reaction_window_opened",
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["reaction_window_id"] = reactionWindowId,
                ["reaction_subject_id"] = reactionSubjectId,
                ["originating_event_id"] = null,
                ["originating_event_sequence"] = null,
                ["underlying_resolution_id"] = resolutionId,
                ["initiator_player_id"] = request.PlayerId,
                ["priority_player_id"] = opening.InitialPriorityPlayerId,
                ["response_policy_id"] = opening.InitialResponsePolicyId,
            })));
        var materialized = events.ToImmutable();
        state.Events.AddRange(materialized);
        return AcceptAction(state, request, stateVersionBefore, materialized);
    }

    private ActionResponse ApplyPassPriority(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore)
    {
        var window = state.ReactionWindow;
        if (window is null
            || !string.Equals(state.PriorityPlayerId, request.PlayerId, StringComparison.Ordinal))
        {
            return RejectAction(
                state,
                request,
                "reaction_window_invalid",
                Diagnostic(
                    "REACTION_SUBJECT_CLOSED",
                    "transition_validation",
                    "The reaction window is no longer available to this player.",
                    "pass_priority requires the current open window and its authoritative priority player.",
                    "refresh_projection"));
        }

        var closureThreshold = window.CurrentResponsePolicyId switch
        {
            ReactionPolicyIds.StandardAlternatingResponse => 2,
            ReactionPolicyIds.SingleResponderOnce => 1,
            _ => 0,
        };
        if (closureThreshold == 0)
        {
            return RejectAction(
                state,
                request,
                "reaction_response_policy_unsupported",
                Diagnostic(
                    "REACTION_RESPONSE_POLICY_UNSUPPORTED",
                    "transition_validation",
                    "The current reaction response policy is unsupported.",
                    $"Open ReactionWindow policy is unsupported: {window.CurrentResponsePolicyId}",
                    "engine_bug"));
        }

        var nextPassCount = window.ConsecutivePassCount + 1;
        var closes = nextPassCount >= closureThreshold;
        var unwindPlan = ImmutableArray<PlannedReactionResolutionStep>.Empty;
        if (closes && !TryBuildReactionUnwindPlan(
                state,
                ProspectiveTopResolutionId: null,
                ProspectiveTopPlan: null,
                out unwindPlan))
        {
            return RejectReactionTriggerOrdering(state, request);
        }

        var nextPriorityPlayerId = closes ? null : state.GetNextPlayerId(request.PlayerId);
        state.StateVersion += 1;
        window.ConsecutivePassCount = nextPassCount;
        if (nextPriorityPlayerId is not null)
        {
            state.PriorityPlayerId = nextPriorityPlayerId;
        }

        var events = ImmutableArray.CreateBuilder<EngineEvent>();
        AppendCommittedReactionEvent(
            state,
            events,
            "priority_passed",
            request.PlayerId,
            request.ActionType,
            new Dictionary<string, object?>
            {
                ["reaction_window_id"] = window.ReactionWindowId,
                ["reaction_subject_id"] = window.ReactionSubjectId,
                ["passing_player_id"] = request.PlayerId,
                ["consecutive_pass_count"] = nextPassCount,
                ["next_priority_player_id"] = nextPriorityPlayerId,
                ["window_closed"] = closes,
            });
        if (closes)
        {
            CloseReactionWindowAndUnwind(
                state,
                request,
                window,
                "passes_complete",
                unwindPlan,
                events);
        }

        return AcceptAction(state, request, stateVersionBefore, events.ToImmutable());
    }

    private ActionResponse ApplyReact(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore)
    {
        var window = state.ReactionWindow;
        if (window is null
            || !string.Equals(state.PriorityPlayerId, request.PlayerId, StringComparison.Ordinal))
        {
            return RejectAction(
                state,
                request,
                "reaction_window_invalid",
                Diagnostic(
                    "REACTION_SUBJECT_CLOSED",
                    "transition_validation",
                    "The reaction window is no longer available to this player.",
                    "react requires the current open window and its authoritative priority player.",
                    "refresh_projection"));
        }

        var payload = ReadReactPayload(request.Payload);
        var option = ResolveCurrentReactionOptions(state, request.PlayerId)
            .SingleOrDefault(candidate => string.Equals(
                candidate.ReactionOptionId,
                payload.ReactionOptionId,
                StringComparison.Ordinal));
        if (option is null)
        {
            return RejectAction(
                state,
                request,
                "reaction_option_invalid",
                Diagnostic(
                    "REACTION_OPTION_INVALID",
                    "transition_validation",
                    "The selected reaction option is no longer legal.",
                    "reaction_option_id is not present in the current player/window/state-bound option set.",
                    "refresh_projection"));
        }

        if (option.RequiresPostDeclarationChoice || option.RequiresPaymentSelection)
        {
            return RejectAction(
                state,
                request,
                "reaction_resolution_unsupported",
                Diagnostic(
                    "REACTION_RESOLUTION_UNSUPPORTED",
                    "transition_validation",
                    "This reaction requires a choice that is outside the current protocol.",
                    "Reaction v1 does not support post-declaration payment, mode, or target choices.",
                    "choose_another_action"));
        }

        if (option.RequiresNestedReactionWindowDuringResolution)
        {
            return RejectAction(
                state,
                request,
                "reaction_nested_window_unsupported",
                Diagnostic(
                    "REACTION_NESTED_WINDOW_DURING_RESOLUTION_UNSUPPORTED",
                    "transition_validation",
                    "This reaction requires unsupported nested timing during resolution.",
                    "Reaction v1 cannot open a new externally blocking window while the stack unwinds.",
                    "choose_another_action"));
        }

        if (!ReactionPolicyIds.IsNextResponsePolicy(option.NextResponsePolicyId))
        {
            return RejectAction(
                state,
                request,
                "reaction_response_policy_unsupported",
                Diagnostic(
                    "REACTION_RESPONSE_POLICY_UNSUPPORTED",
                    "transition_validation",
                    "The configured reaction response policy is unsupported.",
                    $"Reaction option next response policy is unsupported: {option.NextResponsePolicyId}",
                    "fix_runtime_package"));
        }

        if (state.NextResolutionSequence == int.MaxValue)
        {
            return RejectAction(
                state,
                request,
                "reaction_resolution_unsupported",
                Diagnostic(
                    "REACTION_RESOLUTION_UNSUPPORTED",
                    "transition_validation",
                    "The reaction cannot allocate a deterministic resolution identity.",
                    "MatchState.NextResolutionSequence reached its supported integer boundary.",
                    "engine_bug"));
        }

        var runtimePackage = _runtimePackage
            ?? throw new EngineStateException("Reaction resolution requires a gameplay runtime package.");
        var canonicalRuntime = _canonicalRuntime
            ?? throw new EngineStateException("Reaction resolution requires canonical runtime data.");
        var resolutionSequence = state.NextResolutionSequence;
        var resolutionId = $"resolution:{state.MatchId}:{resolutionSequence:000000}";
        var context = new CanonicalAbilityResolutionContext(
            resolutionId,
            CanonicalResolutionOrigin.Reaction,
            request.ActionId,
            request.ActionType,
            option.Ability,
            option.SourceCardInstanceId,
            option.SourceCardId,
            option.ControllerPlayerId,
            payload.TargetSelections,
            PendingTriggerId: null,
            TriggerId: null);
        CanonicalEffectExecutionPlan effectPlan;
        try
        {
            effectPlan = CanonicalEffectExecutor.BuildPlan(
                context,
                state,
                runtimePackage,
                canonicalRuntime.Cards,
                canonicalRuntime.Abilities);
        }
        catch (CanonicalAbilityExecutionException exception)
        {
            return RejectAction(
                state,
                request,
                "reaction_target_invalid",
                Diagnostic(
                    "REACTION_TARGET_INVALID",
                    "transition_validation",
                    "The selected reaction targets are no longer legal.",
                    $"Reaction declaration target validation failed with {exception.Code}: {exception.Message}",
                    "refresh_projection"));
        }

        var terminalUnwindPlan = ImmutableArray<PlannedReactionResolutionStep>.Empty;
        if (string.Equals(
                option.NextResponsePolicyId,
                ReactionPolicyIds.NoFurtherResponse,
                StringComparison.Ordinal)
            && !TryBuildReactionUnwindPlan(
                state,
                resolutionId,
                effectPlan,
                out terminalUnwindPlan))
        {
            return RejectReactionTriggerOrdering(state, request);
        }

        if (!state.CardInstances.TryGetValue(option.SourceCardInstanceId, out var source)
            || !string.Equals(source.CardId, option.SourceCardId, StringComparison.Ordinal)
            || !string.Equals(source.ControllerPlayerId, option.ControllerPlayerId, StringComparison.Ordinal)
            || !string.Equals(source.Zone, "dominion", StringComparison.Ordinal)
            || source.ZoneSequence != option.SourceZoneSequenceAtDeclaration)
        {
            return RejectAction(
                state,
                request,
                "reaction_option_invalid",
                Diagnostic(
                    "REACTION_OPTION_INVALID",
                    "transition_validation",
                    "The selected reaction source is no longer current.",
                    "The same-zone source presence bound to reaction_option_id has changed.",
                    "refresh_projection"));
        }

        var parentResolutionId = state.ResolutionStack[^1].ResolutionId;
        var declaredTargets = CaptureDeclaredTargetStates(effectPlan, state);
        state.StateVersion += 1;
        state.ResolutionStack.Add(new ResolutionStackEntryState
        {
            ResolutionId = resolutionId,
            Sequence = resolutionSequence,
            EntryKindId = "reaction",
            ReactionWindowId = window.ReactionWindowId,
            ReactionSubjectId = window.ReactionSubjectId,
            ParentResolutionId = parentResolutionId,
            AbilityResolution = new CanonicalAbilityResolutionState(
                CanonicalEffectExecutor.ReactionOriginId,
                request.ActionId,
                request.ActionType,
                option.Ability.AbilityId,
                option.SourceCardInstanceId,
                option.SourceCardId,
                source.Zone,
                source.ZoneSequence,
                option.SourceRelevancePolicyId,
                option.ControllerPlayerId,
                payload.TargetSelections,
                declaredTargets,
                PendingTriggerId: null,
                TriggerId: null,
                DeclarationStateVersion: state.StateVersion),
            ReactionOptionId = option.ReactionOptionId,
            NextResponsePolicyId = option.NextResponsePolicyId,
        });
        state.NextResolutionSequence += 1;
        window.ConsecutivePassCount = 0;

        var events = ImmutableArray.CreateBuilder<EngineEvent>();
        AppendCommittedReactionEvent(
            state,
            events,
            "reaction_declared",
            request.PlayerId,
            request.ActionType,
            new Dictionary<string, object?>
            {
                ["reaction_window_id"] = window.ReactionWindowId,
                ["reaction_subject_id"] = window.ReactionSubjectId,
                ["resolution_id"] = resolutionId,
                ["parent_resolution_id"] = parentResolutionId,
                ["controller_player_id"] = request.PlayerId,
                ["reaction_option_id"] = option.ReactionOptionId,
                ["source_card_instance_id"] = option.SourceCardInstanceId,
                ["source_ability_id"] = option.Ability.AbilityId,
                ["next_response_policy_id"] = option.NextResponsePolicyId,
            });
        if (string.Equals(
                option.NextResponsePolicyId,
                ReactionPolicyIds.StandardAlternatingResponse,
                StringComparison.Ordinal))
        {
            window.CurrentResponsePolicyId = ReactionPolicyIds.StandardAlternatingResponse;
            window.EligibleResponderPlayerIds.Clear();
            window.EligibleResponderPlayerIds.AddRange(state.Players.Select(player => player.PlayerId));
            state.PriorityPlayerId = state.GetNextPlayerId(request.PlayerId);
        }
        else
        {
            CloseReactionWindowAndUnwind(
                state,
                request,
                window,
                "no_further_response",
                terminalUnwindPlan,
                events);
        }

        return AcceptAction(state, request, stateVersionBefore, events.ToImmutable());
    }

    private bool TryBuildReactionUnwindPlan(
        MatchState state,
        string? ProspectiveTopResolutionId,
        CanonicalEffectExecutionPlan? ProspectiveTopPlan,
        out ImmutableArray<PlannedReactionResolutionStep> unwindPlan)
    {
        var canonicalRuntime = _canonicalRuntime
            ?? throw new EngineStateException("Reaction trigger-ordering validation requires canonical runtime data.");
        if ((ProspectiveTopResolutionId is null) != (ProspectiveTopPlan is null))
        {
            throw new EngineStateException("Prospective Reaction resolution identity and plan must be supplied together.");
        }

        var simulation = CloneMatchStateForSimulation(state);
        var steps = ImmutableArray.CreateBuilder<PlannedReactionResolutionStep>();
        if (ProspectiveTopPlan is not null)
        {
            if (!ApplyReactionPlanToSimulation(
                    simulation,
                    ProspectiveTopPlan,
                    canonicalRuntime))
            {
                unwindPlan = ImmutableArray<PlannedReactionResolutionStep>.Empty;
                return false;
            }

            steps.Add(new PlannedReactionResolutionStep(
                ProspectiveTopResolutionId!,
                ProspectiveTopPlan,
                InvalidationReasonCode: null));
        }

        foreach (var entry in simulation.ResolutionStack.AsEnumerable().Reverse())
        {
            if (!TryBuildPersistedResolutionPlan(
                    simulation,
                    entry,
                    out var plan,
                    out var safeReasonCode))
            {
                steps.Add(new PlannedReactionResolutionStep(
                    entry.ResolutionId,
                    EffectPlan: null,
                    safeReasonCode));
                if (string.Equals(
                        entry.EntryKindId,
                        "underlying_resolution",
                        StringComparison.Ordinal))
                {
                    MovePlayedCardFromResolutionToVoid(
                        simulation,
                        simulation.GetCardInstance(entry.AbilityResolution.SourceCardInstanceId));
                }

                continue;
            }

            if (!ApplyReactionPlanToSimulation(simulation, plan!, canonicalRuntime))
            {
                unwindPlan = ImmutableArray<PlannedReactionResolutionStep>.Empty;
                return false;
            }

            steps.Add(new PlannedReactionResolutionStep(
                entry.ResolutionId,
                plan,
                InvalidationReasonCode: null));
            if (string.Equals(
                    entry.EntryKindId,
                    "underlying_resolution",
                    StringComparison.Ordinal))
            {
                MovePlayedCardFromResolutionToVoid(
                    simulation,
                    simulation.GetCardInstance(entry.AbilityResolution.SourceCardInstanceId));
            }
        }

        unwindPlan = steps.ToImmutable();
        return true;
    }

    private bool ApplyReactionPlanToSimulation(
        MatchState simulation,
        CanonicalEffectExecutionPlan plan,
        CanonicalAbilityRuntimeContext canonicalRuntime)
    {
        var runtimePackage = _runtimePackage
            ?? throw new EngineStateException(
                "Reaction simulation requires a gameplay runtime package.");
        CanonicalEffectExecutor.Apply(simulation, plan);
        var events = ImmutableArray.CreateBuilder<EngineEvent>();
        AppendCanonicalEffectEvents(
            events,
            plan,
            (_, eventType, payload) => CreateCanonicalRuntimeEvent(
                simulation,
                events.Count,
                eventType,
                plan.Context.ControllerPlayerId,
                plan.Context.SourceActionType,
                payload));
        events.Add(CreateCanonicalRuntimeEvent(
            simulation,
            events.Count,
            "canonical_ability_resolved",
            plan.Context.ControllerPlayerId,
            plan.Context.SourceActionType,
            ContractJsonValue.From(new CanonicalAbilityResolvedPayload(
                plan.Context.ResolutionId,
                CanonicalEffectExecutor.OriginId(plan.Context.Origin),
                plan.Context.Ability.AbilityId,
                plan.Context.SourceCardInstanceId,
                plan.Context.SourceCardId,
                plan.Context.ControllerPlayerId,
                CanonicalEffectExecutor.AppliedOutcome,
                plan.AppliedMutationCount,
                plan.Context.SourceActionId,
                plan.Context.PendingTriggerId,
                plan.Context.TriggerId))));
        var materialized = events.ToImmutable();
        simulation.Events.AddRange(materialized);

        foreach (var engineEvent in materialized)
        {
            var discoveries = CanonicalTriggerResolver.Resolve(
                canonicalRuntime.Abilities,
                engineEvent,
                simulation);
            if (discoveries.Length > 1)
            {
                return false;
            }

            foreach (var discovery in discoveries)
            {
                var ability = canonicalRuntime.Abilities.AbilitiesById[discovery.AbilityId];
                if (!CanonicalEffectExecutor.IsSupportedGraph(ability))
                {
                    continue;
                }

                foreach (var target in CanonicalTargetResolver.GetSupportedTargets(ability)
                             .Where(target => CanonicalTargetResolver.IsClientSelectable(target)
                                              || CanonicalTargetResolver.IsAutomaticCollection(target)))
                {
                    _ = CanonicalTargetResolver.ResolveCandidates(
                        target,
                        ability,
                        discovery.ControllerPlayerId,
                        simulation,
                        runtimePackage,
                        canonicalRuntime.Cards,
                        canonicalRuntime.Abilities);
                }
            }
        }

        return true;
    }

    private static ActionResponse RejectReactionTriggerOrdering(
        MatchState state,
        ActionRequest request) => RejectAction(
        state,
        request,
        "reaction_trigger_batch_ordering_unsupported",
        Diagnostic(
            "REACTION_TRIGGER_BATCH_ORDERING_UNSUPPORTED",
            "transition_validation",
            "The reaction stack would create an unsupported simultaneous trigger batch.",
            "Reaction v1 supports zero or one discovered trigger per committed trigger-source event and does not infer generic ordering.",
            "choose_another_action"));

    private void CloseReactionWindowAndUnwind(
        MatchState state,
        ActionRequest request,
        ReactionWindowState window,
        string closureReason,
        ImmutableArray<PlannedReactionResolutionStep> unwindPlan,
        ImmutableArray<EngineEvent>.Builder responseEvents)
    {
        AppendCommittedReactionEvent(
            state,
            responseEvents,
            "reaction_window_closed",
            request.PlayerId,
            request.ActionType,
            new Dictionary<string, object?>
            {
                ["reaction_window_id"] = window.ReactionWindowId,
                ["reaction_subject_id"] = window.ReactionSubjectId,
                ["closure_reason"] = closureReason,
                ["stack_depth"] = state.ResolutionStack.Count,
            });
        state.ReactionWindow = null;

        var stepIndex = 0;
        while (state.ResolutionStack.Count > 0)
        {
            var entry = state.ResolutionStack[^1];
            if (stepIndex >= unwindPlan.Length
                || !string.Equals(
                    unwindPlan[stepIndex].ResolutionId,
                    entry.ResolutionId,
                    StringComparison.Ordinal))
            {
                throw new EngineStateException(
                    "Prepared Reaction unwind plan does not match the authoritative stack.");
            }

            var step = unwindPlan[stepIndex];
            stepIndex += 1;
            AppendCommittedReactionEvent(
                state,
                responseEvents,
                "resolution_entry_started",
                entry.AbilityResolution.ControllerPlayerId,
                request.ActionType,
                new Dictionary<string, object?>
                {
                    ["reaction_window_id"] = entry.ReactionWindowId,
                    ["reaction_subject_id"] = entry.ReactionSubjectId,
                    ["resolution_id"] = entry.ResolutionId,
                    ["entry_kind_id"] = entry.EntryKindId,
                });

            if (step.EffectPlan is null)
            {
                AppendCommittedReactionEvent(
                    state,
                    responseEvents,
                    "resolution_entry_invalidated",
                    entry.AbilityResolution.ControllerPlayerId,
                    request.ActionType,
                    new Dictionary<string, object?>
                    {
                        ["reaction_window_id"] = entry.ReactionWindowId,
                        ["reaction_subject_id"] = entry.ReactionSubjectId,
                        ["resolution_id"] = entry.ResolutionId,
                        ["entry_kind_id"] = entry.EntryKindId,
                        ["safe_reason_code"] = step.InvalidationReasonCode,
                    });
                CompleteUnderlyingPlayedCardLifecycleIfRequired(
                    state,
                    request,
                    entry,
                    responseEvents);
                state.ResolutionStack.RemoveAt(state.ResolutionStack.Count - 1);
                continue;
            }

            var plan = step.EffectPlan;
            CanonicalEffectExecutor.Apply(state, plan);
            var gameplayEvents = ImmutableArray.CreateBuilder<EngineEvent>();
            AppendCanonicalEffectEvents(
                gameplayEvents,
                plan,
                (_, eventType, payload) => CreateCanonicalRuntimeEvent(
                    state,
                    gameplayEvents.Count,
                    eventType,
                    entry.AbilityResolution.ControllerPlayerId,
                    request.ActionType,
                    payload));
            gameplayEvents.Add(CreateCanonicalRuntimeEvent(
                state,
                gameplayEvents.Count,
                "canonical_ability_resolved",
                entry.AbilityResolution.ControllerPlayerId,
                request.ActionType,
                ContractJsonValue.From(new CanonicalAbilityResolvedPayload(
                    entry.ResolutionId,
                    entry.AbilityResolution.ResolutionOriginId,
                    entry.AbilityResolution.AbilityId,
                    entry.AbilityResolution.SourceCardInstanceId,
                    entry.AbilityResolution.SourceCardId,
                    entry.AbilityResolution.ControllerPlayerId,
                    CanonicalEffectExecutor.AppliedOutcome,
                    plan.AppliedMutationCount,
                    entry.AbilityResolution.SourceActionId,
                    entry.AbilityResolution.PendingTriggerId,
                    entry.AbilityResolution.TriggerId))));
            var committedGameplayEvents = gameplayEvents.ToImmutable();
            state.Events.AddRange(committedGameplayEvents);
            responseEvents.AddRange(committedGameplayEvents);
            _canonicalAbilityResolutions = _canonicalAbilityResolutions.Add(
                new CanonicalAbilityResolutionRecord(
                    entry.ResolutionId,
                    entry.AbilityResolution.ResolutionOriginId,
                    entry.AbilityResolution.AbilityId,
                    entry.AbilityResolution.SourceCardInstanceId,
                    entry.AbilityResolution.SourceCardId,
                    entry.AbilityResolution.ControllerPlayerId,
                    CanonicalEffectExecutor.AppliedOutcome,
                    plan.AppliedMutationCount,
                    entry.AbilityResolution.SourceActionId,
                    entry.AbilityResolution.PendingTriggerId,
                    entry.AbilityResolution.TriggerId));
            var triggerEvents = DiscoverCanonicalTriggers(state, committedGameplayEvents);
            responseEvents.AddRange(triggerEvents);
            AppendCommittedReactionEvent(
                state,
                responseEvents,
                "resolution_entry_resolved",
                entry.AbilityResolution.ControllerPlayerId,
                request.ActionType,
                new Dictionary<string, object?>
                {
                    ["reaction_window_id"] = entry.ReactionWindowId,
                    ["reaction_subject_id"] = entry.ReactionSubjectId,
                    ["resolution_id"] = entry.ResolutionId,
                    ["entry_kind_id"] = entry.EntryKindId,
                    ["result"] = "resolved",
                });
            CompleteUnderlyingPlayedCardLifecycleIfRequired(
                state,
                request,
                entry,
                responseEvents);
            state.ResolutionStack.RemoveAt(state.ResolutionStack.Count - 1);
        }

        if (stepIndex != unwindPlan.Length)
        {
            throw new EngineStateException(
                "Prepared Reaction unwind plan retained entries after the authoritative stack closed.");
        }

        state.ClosedReactionSubjectIds.Add(window.ReactionSubjectId);
    }

    private bool TryBuildPersistedResolutionPlan(
        MatchState state,
        ResolutionStackEntryState entry,
        out CanonicalEffectExecutionPlan? plan,
        out string safeReasonCode)
    {
        plan = null;
        safeReasonCode = "reaction_resolution_invalidated";
        var persisted = entry.AbilityResolution;
        if (!state.CardInstances.TryGetValue(persisted.SourceCardInstanceId, out var source)
            || !string.Equals(source.CardId, persisted.SourceCardId, StringComparison.Ordinal)
            || !string.Equals(source.ControllerPlayerId, persisted.ControllerPlayerId, StringComparison.Ordinal)
            || !string.Equals(source.Zone, persisted.SourceZoneIdAtDeclaration, StringComparison.Ordinal)
            || source.ZoneSequence != persisted.SourceZoneSequenceAtDeclaration)
        {
            safeReasonCode = "source_relevance_invalid";
            return false;
        }

        var relevancePolicyValid = string.Equals(
                entry.EntryKindId,
                "underlying_resolution",
                StringComparison.Ordinal)
            ? string.Equals(
                  persisted.SourceRelevancePolicyId,
                  ReactionPolicyIds.PlayedCardResolutionPresence,
                  StringComparison.Ordinal)
              && string.Equals(source.Zone, "resolution", StringComparison.Ordinal)
              && source.ZoneIndex >= 0
              && source.ZoneIndex < state.ResolutionCardInstanceIds.Count
              && string.Equals(
                  state.ResolutionCardInstanceIds[source.ZoneIndex],
                  source.CardInstanceId,
                  StringComparison.Ordinal)
            : string.Equals(
                persisted.SourceRelevancePolicyId,
                ReactionPolicyIds.SameZonePresence,
                StringComparison.Ordinal);
        if (!relevancePolicyValid)
        {
            safeReasonCode = "source_relevance_policy_invalid";
            return false;
        }

        var canonicalRuntime = _canonicalRuntime
            ?? throw new EngineStateException("Persisted Reaction resolution requires canonical runtime data.");
        var runtimePackage = _runtimePackage
            ?? throw new EngineStateException("Persisted Reaction resolution requires a gameplay runtime package.");
        if (!canonicalRuntime.Abilities.AbilitiesById.TryGetValue(persisted.AbilityId, out var ability)
            || !string.Equals(ability.CardId, persisted.SourceCardId, StringComparison.Ordinal))
        {
            safeReasonCode = "ability_definition_invalid";
            return false;
        }

        var origin = persisted.ResolutionOriginId switch
        {
            CanonicalEffectExecutor.PlayedCardOriginId => CanonicalResolutionOrigin.PlayedCard,
            CanonicalEffectExecutor.ReactionOriginId => CanonicalResolutionOrigin.Reaction,
            _ => (CanonicalResolutionOrigin?)null,
        };
        if (origin is null)
        {
            safeReasonCode = "resolution_origin_unsupported";
            return false;
        }

        try
        {
            var context = new CanonicalAbilityResolutionContext(
                entry.ResolutionId,
                origin.Value,
                persisted.SourceActionId,
                persisted.SourceActionType,
                ability,
                persisted.SourceCardInstanceId,
                persisted.SourceCardId,
                persisted.ControllerPlayerId,
                persisted.DeclaredTargetSelections,
                persisted.PendingTriggerId,
                persisted.TriggerId);
            plan = CanonicalEffectExecutor.BuildPlan(
                context,
                state,
                runtimePackage,
                canonicalRuntime.Cards,
                canonicalRuntime.Abilities);
        }
        catch (CanonicalAbilityExecutionException exception)
        {
            safeReasonCode = exception.Code;
            return false;
        }

        if (!DeclaredTargetStatesMatch(
                CaptureDeclaredTargetStates(plan, state),
                persisted.DeclaredTargetStates))
        {
            plan = null;
            safeReasonCode = "target_object_context_invalid";
            return false;
        }

        return true;
    }

    private static ImmutableArray<DeclaredTargetSelectionState> CaptureDeclaredTargetStates(
        CanonicalEffectExecutionPlan plan,
        MatchState state) => plan.TargetSelections
            .Select(selection => new DeclaredTargetSelectionState(
                selection.Definition.TargetId,
                selection.SelectedCards.Select(card => new DeclaredTargetObjectState(
                    card.CardInstanceId,
                    state.GetCardInstance(card.CardInstanceId).ZoneSequence)).ToImmutableArray()))
            .ToImmutableArray();

    private static bool DeclaredTargetStatesMatch(
        ImmutableArray<DeclaredTargetSelectionState> current,
        ImmutableArray<DeclaredTargetSelectionState> declared)
    {
        if (current.Length != declared.Length)
        {
            return false;
        }

        for (var index = 0; index < current.Length; index += 1)
        {
            if (!string.Equals(current[index].TargetId, declared[index].TargetId, StringComparison.Ordinal)
                || current[index].SelectedObjects.Length != declared[index].SelectedObjects.Length)
            {
                return false;
            }

            for (var objectIndex = 0; objectIndex < current[index].SelectedObjects.Length; objectIndex += 1)
            {
                if (current[index].SelectedObjects[objectIndex]
                    != declared[index].SelectedObjects[objectIndex])
                {
                    return false;
                }
            }
        }

        return true;
    }

    private static void AppendCommittedReactionEvent(
        MatchState state,
        ImmutableArray<EngineEvent>.Builder responseEvents,
        string eventType,
        string actorPlayerId,
        string causeActionType,
        IReadOnlyDictionary<string, object?> payload)
    {
        var engineEvent = CreateCanonicalRuntimeEvent(
            state,
            additionalEventOffset: 0,
            eventType,
            actorPlayerId,
            causeActionType,
            ContractJsonValue.From(payload));
        state.Events.Add(engineEvent);
        responseEvents.Add(engineEvent);
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
            var queueForPostResolutionCheckpoint = state.ReactionWindow is not null
                || state.ResolutionStack.Count > 0
                || state.QueuedTriggerBatches.Count > 0;
            if (queueForPostResolutionCheckpoint && discoveries.Length > 1)
            {
                throw new EngineStateException(
                    "REACTION_TRIGGER_BATCH_ORDERING_UNSUPPORTED",
                    "Reaction v1 cannot queue more than one discovered trigger from the same committed source event.");
            }

            _canonicalTriggerDiscoveries = _canonicalTriggerDiscoveries.AddRange(discoveries);
            var queuedForEvent = new List<PendingTriggeredAbilityState>();
            foreach (var discovery in discoveries)
            {
                var ability = canonicalRuntime.Abilities.AbilitiesById[discovery.AbilityId];
                if (!CanonicalEffectExecutor.IsSupportedGraph(ability))
                {
                    continue;
                }

                var targets = CanonicalTargetResolver.GetSupportedTargets(ability);
                var hasRequiredLegalTargets = targets
                    .Where(target => CanonicalTargetResolver.IsClientSelectable(target)
                                     || CanonicalTargetResolver.IsAutomaticCollection(target))
                    .All(target =>
                    CanonicalTargetResolver.ResolveCandidates(
                        target,
                        ability,
                        discovery.ControllerPlayerId,
                        state,
                        runtimePackage,
                        canonicalRuntime.Cards,
                        canonicalRuntime.Abilities).Length >= target.MinimumTargets);
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

                var pending = new PendingTriggeredAbilityState(
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
                    discovery.SourceZoneTransitionInstanceId);
                if (queueForPostResolutionCheckpoint)
                {
                    queuedForEvent.Add(pending);
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

                window.PendingTriggers.Add(pending);
            }

            if (queuedForEvent.Count > 1)
            {
                throw new EngineStateException(
                    "REACTION_TRIGGER_BATCH_ORDERING_UNSUPPORTED",
                    "Reaction v1 cannot activate a same-time trigger batch that requires generic ordering.");
            }

            if (queuedForEvent.Count == 1)
            {
                var batch = new QueuedTriggerBatchState
                {
                    TriggerBatchId = $"trigger-batch:{engineEvent.EventId}",
                    OriginatingEventId = engineEvent.EventId,
                    OriginatingEventSequence = engineEvent.EventSequence,
                    BatchOrderPolicyId = ReactionPolicyIds.DifferentTimingFifo,
                };
                batch.Triggers.Add(queuedForEvent[0]);
                state.QueuedTriggerBatches.Add(batch);
            }
        }

        var materialized = consequenceEvents.ToImmutable();
        state.Events.AddRange(materialized);
        return materialized;
    }

    private static void ProcessQueuedTriggerCheckpoint(MatchState state)
    {
        if (state.ReactionWindow is not null
            || state.ResolutionStack.Count != 0
            || state.PendingTriggerWindow is not null)
        {
            return;
        }

        while (state.QueuedTriggerBatches.Count > 0)
        {
            var batch = state.QueuedTriggerBatches
                .OrderBy(item => item.OriginatingEventSequence)
                .ThenBy(item => item.TriggerBatchId, StringComparer.Ordinal)
                .First();
            if (!string.Equals(
                    batch.BatchOrderPolicyId,
                    ReactionPolicyIds.DifferentTimingFifo,
                    StringComparison.Ordinal)
                || batch.Triggers.Count != 1)
            {
                throw new EngineStateException(
                    "REACTION_TRIGGER_BATCH_ORDERING_UNSUPPORTED",
                    "Reaction v1 queued trigger checkpoint supports exactly one trigger per committed source event.");
            }

            state.QueuedTriggerBatches.Remove(batch);
            var pending = batch.Triggers[0];
            var window = new PendingTriggerWindowState
            {
                PendingWindowId = $"pending_window_{batch.OriginatingEventSequence:000000}",
                ControllerPlayerId = pending.ControllerPlayerId,
            };
            window.PendingTriggers.Add(pending);
            state.PendingTriggerWindow = window;
            return;
        }
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

        if (!string.Equals(state.Phase, CanonicalPhaseIds.Manifestation, StringComparison.Ordinal)
            && !(_legacyActionCompatibility
                 && string.Equals(state.Phase, CanonicalPhaseIds.LegacyMain, StringComparison.Ordinal)))
        {
            throw PlayCardValidationException.Create(
                "phase_invalid",
                "PLAY_CARD_PHASE_INVALID",
                "A card cannot be played in the current phase.",
                $"The production play_card action requires phase={CanonicalPhaseIds.Manifestation}.",
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
            var planningState = CloneMatchStateForSimulation(state);
            var planningPlayer = planningState.GetPlayer(player.PlayerId);
            var planningCard = planningState.GetCardInstance(card.CardInstanceId);
            MovePlayedCardFromHandToResolution(
                planningState,
                planningPlayer,
                planningCard,
                handIndex);
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
                planningState,
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
                    : string.Equals(
                        exception.Code,
                        CanonicalEffectExecutor.DrawRefreshPenaltyUnsupportedCode,
                        StringComparison.Ordinal)
                        ? "refresh_projection"
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
            events.Add(CreatePlayCardEvent(
                state,
                request,
                stateVersionAfter,
                state.Events.Count + events.Count + 1,
                "zone_move",
                ContractJsonValue.From(new ZoneMovePayload(
                    request.ActionId,
                    request.ActionType,
                    plan.Card.CardInstanceId,
                    plan.Card.CardId,
                    plan.Card.OwnerPlayerId,
                    plan.Card.ControllerPlayerId,
                    "hand",
                    "resolution",
                    plan.HandIndex,
                    state.ResolutionCardInstanceIds.Count,
                    "owner_only",
                    "public"))));
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
                "resolution",
                "void",
                state.ResolutionCardInstanceIds.Count,
                plan.Player.VoidCardInstanceIds.Count,
                "public",
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
                case CanonicalDrawMutation draw:
                    events.Add(createEvent(
                        events.Count,
                        "zone_move",
                        ContractJsonValue.From(new ZoneMovePayload(
                            context.SourceActionId ?? context.ResolutionId,
                            context.SourceActionType,
                            draw.CardInstanceId,
                            draw.CardId,
                            draw.PlayerId,
                            draw.PlayerId,
                            "deck",
                            "hand",
                            draw.Transition.FromZoneIndex,
                            draw.Transition.ToZoneIndex,
                            draw.Transition.VisibilityBefore,
                            draw.Transition.VisibilityAfter))));
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

    private ActionResponse ApplyAdvancePhase(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore)
    {
        if (!CanonicalPhaseIds.IsCanonical(state.Phase))
        {
            return RejectAction(
                state,
                request,
                "phase_invalid",
                Diagnostic(
                    "ADVANCE_PHASE_STATE_INVALID",
                    "transition_validation",
                    "The current phase cannot be advanced.",
                    "The authoritative state is outside the canonical phase vocabulary.",
                    "refresh_projection"));
        }

        if (string.Equals(state.Phase, CanonicalPhaseIds.Incursion, StringComparison.Ordinal))
        {
            return ApplyDistributionEntry(state, request, stateVersionBefore);
        }

        if (string.Equals(state.Phase, CanonicalPhaseIds.Distribution, StringComparison.Ordinal))
        {
            try
            {
                return ApplyNextPlayerAwakening(state, request, stateVersionBefore);
            }
            catch (CanonicalAwakeningEntryException exception)
            {
                return RejectAction(
                    state,
                    request,
                    "awakening_draw_unavailable",
                    Diagnostic(
                        exception.Code,
                        "transition_validation",
                        "The next Awakening cannot be completed.",
                        exception.Message,
                        "refresh_projection",
                        new Dictionary<string, object?>
                        {
                            ["player_id"] = exception.PlayerId,
                            ["required_draw_count"] = exception.RequiredDrawCount,
                            ["available_deck_count"] = exception.AvailableDeckCount,
                        }));
            }
        }

        var phaseBefore = state.Phase;
        state.Phase = CanonicalPhaseIds.Next(phaseBefore);
        state.StateVersion += 1;
        var transitionEvent = CreatePhaseTransitionEvent(
            state,
            request,
            eventOffset: 0,
            phaseBefore,
            state.Phase);
        state.Events.Add(transitionEvent);
        return AcceptAction(state, request, stateVersionBefore, transitionEvent);
    }

    private ActionResponse ApplyDistributionEntry(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore)
    {
        var activePlayerId = state.ActivePlayerId;
        var turnNumber = state.TurnNumber;
        var cleanup = ApplyTurnEndCleanup(state);

        state.Phase = CanonicalPhaseIds.Distribution;
        state.StateVersion += 1;
        var events = ImmutableArray.CreateBuilder<EngineEvent>();
        events.Add(CreatePhaseTransitionEvent(
            state,
            request,
            events.Count,
            CanonicalPhaseIds.Incursion,
            CanonicalPhaseIds.Distribution));
        AppendTurnEndCleanupEvents(
            state,
            request,
            turnNumber,
            activePlayerId,
            events,
            cleanup,
            "distribution_phase_cleanup");

        var materializedEvents = events.ToImmutable();
        state.Events.AddRange(materializedEvents);
        return AcceptAction(state, request, stateVersionBefore, materializedEvents);
    }

    private static ActionResponse ApplyNextPlayerAwakening(
        MatchState state,
        ActionRequest request,
        int stateVersionBefore)
    {
        var previousPlayerId = state.ActivePlayerId;
        var nextPlayerId = state.GetNextPlayerId(previousPlayerId);
        var turnBefore = state.TurnNumber;
        var turnAfter = string.Equals(nextPlayerId, state.StartingPlayerId, StringComparison.Ordinal)
            ? checked(turnBefore + 1)
            : turnBefore;
        var entryPlan = CanonicalPhaseLifecycle.PlanAwakeningEntry(
            state,
            nextPlayerId,
            drawCount: 2);

        state.TurnNumber = turnAfter;
        state.ActivePlayerId = nextPlayerId;
        state.PriorityPlayerId = nextPlayerId;
        state.Phase = CanonicalPhaseIds.Awakening;
        CanonicalPhaseLifecycle.ApplyAwakeningEntry(state, entryPlan);
        state.StateVersion += 1;

        var events = ImmutableArray.CreateBuilder<EngineEvent>();
        var transitionSequence = state.Events.Count + 1;
        events.Add(new EngineEvent(
            ContractSchemas.EngineEvent,
            $"event_{transitionSequence:000000}",
            transitionSequence,
            "turn_transition",
            state.MatchId,
            state.StateVersion,
            state.TurnNumber,
            previousPlayerId,
            request.ActionType,
            "public",
            ContractJsonValue.From(new TurnTransitionPayload(
                request.ActionId,
                request.ActionType,
                previousPlayerId,
                nextPlayerId,
                previousPlayerId,
                nextPlayerId,
                turnBefore,
                state.TurnNumber,
                CanonicalPhaseIds.Distribution,
                CanonicalPhaseIds.Awakening))));

        foreach (var cardInstanceId in entryPlan.ReadyCardInstanceIds)
        {
            var card = state.GetCardInstance(cardInstanceId);
            var eventSequence = state.Events.Count + events.Count + 1;
            events.Add(new EngineEvent(
                ContractSchemas.EngineEvent,
                $"event_{eventSequence:000000}",
                eventSequence,
                "card_readied",
                state.MatchId,
                state.StateVersion,
                state.TurnNumber,
                nextPlayerId,
                request.ActionType,
                "public",
                ContractJsonValue.From(new AwakeningCardReadiedPayload(
                    request.ActionId,
                    request.ActionType,
                    card.CardInstanceId,
                    card.CardId,
                    card.OwnerPlayerId,
                    card.ControllerPlayerId,
                    card.Zone,
                    "exhausted",
                    "active",
                    CanonicalPhaseIds.Awakening))));
        }

        foreach (var draw in entryPlan.DrawTransitions)
        {
            var eventSequence = state.Events.Count + events.Count + 1;
            events.Add(new EngineEvent(
                ContractSchemas.EngineEvent,
                $"event_{eventSequence:000000}",
                eventSequence,
                "zone_move",
                state.MatchId,
                state.StateVersion,
                state.TurnNumber,
                nextPlayerId,
                request.ActionType,
                "public",
                ContractJsonValue.From(new ZoneMovePayload(
                    request.ActionId,
                    request.ActionType,
                    draw.CardInstanceId,
                    draw.CardId,
                    draw.PlayerId,
                    draw.PlayerId,
                    "deck",
                    "hand",
                    draw.FromZoneIndex,
                    draw.ToZoneIndex,
                    draw.VisibilityBefore,
                    draw.VisibilityAfter))));
        }

        var materializedEvents = events.ToImmutable();
        state.Events.AddRange(materializedEvents);
        return AcceptAction(state, request, stateVersionBefore, materializedEvents);
    }

    private static EngineEvent CreatePhaseTransitionEvent(
        MatchState state,
        ActionRequest request,
        int eventOffset,
        string phaseBefore,
        string phaseAfter)
    {
        var eventSequence = state.Events.Count + eventOffset + 1;
        return new EngineEvent(
            ContractSchemas.EngineEvent,
            $"event_{eventSequence:000000}",
            eventSequence,
            "phase_transition",
            state.MatchId,
            state.StateVersion,
            state.TurnNumber,
            state.ActivePlayerId,
            request.ActionType,
            "public",
            ContractJsonValue.From(new PhaseTransitionPayload(
                request.ActionId,
                request.ActionType,
                state.ActivePlayerId,
                state.TurnNumber,
                phaseBefore,
                phaseAfter)));
    }

    private TurnEndCleanupResult ApplyTurnEndCleanup(MatchState state)
    {
        var continuousEffectPlan = CanonicalContinuousEffects.BuildEndTurnPlan(
            state,
            _canonicalRuntime?.Cards,
            _canonicalRuntime?.Abilities);
        var expiryLethalTargets = continuousEffectPlan.LethalMutations
            .Select(mutation => mutation.TargetCardInstanceId)
            .ToHashSet(StringComparer.Ordinal);
        var damagedSurvivors = state.Players
            .SelectMany(player => player.Domain.HorizonCardInstanceIds
                .Concat(player.Domain.ZenithCardInstanceIds))
            .Where(cardInstanceId => cardInstanceId is not null)
            .Select(cardInstanceId => state.GetCardInstance(cardInstanceId!))
            .Where(card => card.DamageMarked > 0
                           && !expiryLethalTargets.Contains(card.CardInstanceId))
            .Select(card => new TurnEndDamageCleanup(card, card.DamageMarked))
            .ToImmutableArray();

        CanonicalContinuousEffects.ApplyEndTurnPlan(state, continuousEffectPlan);
        foreach (var damaged in damagedSurvivors)
        {
            damaged.Card.DamageMarked = 0;
        }

        return new TurnEndCleanupResult(continuousEffectPlan, damagedSurvivors);
    }

    private static void AppendTurnEndCleanupEvents(
        MatchState state,
        ActionRequest request,
        int turnNumber,
        string activePlayerId,
        ImmutableArray<EngineEvent>.Builder events,
        TurnEndCleanupResult cleanup,
        string damageRemovalReasonId)
    {
        foreach (var expiration in cleanup.ContinuousEffectPlan.Expirations)
        {
            AppendContinuousEffectExpirationEvent(
                state,
                request,
                turnNumber,
                activePlayerId,
                events,
                expiration);
        }

        foreach (var lethal in cleanup.ContinuousEffectPlan.LethalMutations)
        {
            AppendExpiryLethalEvents(
                state,
                request,
                turnNumber,
                activePlayerId,
                events,
                lethal);
        }

        foreach (var damaged in cleanup.DamagedSurvivors)
        {
            var eventSequence = state.Events.Count + events.Count + 1;
            events.Add(new EngineEvent(
                ContractSchemas.EngineEvent,
                $"event_{eventSequence:000000}",
                eventSequence,
                "damage_removed",
                state.MatchId,
                state.StateVersion,
                turnNumber,
                activePlayerId,
                request.ActionType,
                "public",
                ContractJsonValue.From(new DamageRemovedPayload(
                    $"damage_removal_{eventSequence:000000}",
                    damaged.Card.CardInstanceId,
                    null,
                    damaged.DamageBefore,
                    damaged.DamageBefore,
                    damaged.DamageBefore,
                    0,
                    false,
                    null,
                    damaged.Card.CardId,
                    damageRemovalReasonId))));
        }
    }

    private sealed record TurnEndCleanupResult(
        CanonicalEndTurnContinuousEffectPlan ContinuousEffectPlan,
        ImmutableArray<TurnEndDamageCleanup> DamagedSurvivors);

    private sealed record TurnEndDamageCleanup(
        CardInstanceState Card,
        int DamageBefore);

    private ActionResponse ApplyEndTurn(MatchState state, ActionRequest request, int stateVersionBefore)
    {
        var previousPlayerId = state.ActivePlayerId;
        var nextPlayerId = state.GetNextPlayerId(previousPlayerId);
        var turnBefore = state.TurnNumber;
        // The historical oracle action retains its event contract while sharing
        // the same authoritative turn-end cleanup primitive as Distribution.
        var cleanup = ApplyTurnEndCleanup(state);

        if (string.Equals(nextPlayerId, state.StartingPlayerId, StringComparison.Ordinal))
        {
            state.TurnNumber += 1;
        }

        state.ActivePlayerId = nextPlayerId;
        state.PriorityPlayerId = nextPlayerId;
        state.StateVersion += 1;
        var events = ImmutableArray.CreateBuilder<EngineEvent>();
        AppendTurnEndCleanupEvents(
            state,
            request,
            turnBefore,
            previousPlayerId,
            events,
            cleanup,
            "temporary_end_turn_dissipation_proxy");

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

    private static ActionResponse ProjectActionResponseForViewer(
        ActionResponse response,
        string viewerPlayerId) => response with
        {
            Events = response.Events
                .Select(item => ProjectEventForViewer(item, viewerPlayerId))
                .ToImmutableArray(),
        };

    private static EngineEvent ProjectEventForViewer(EngineEvent item, string viewerPlayerId)
    {
        if (string.Equals(item.EventType, "card_readied", StringComparison.Ordinal))
        {
            var readyOwnerPlayerId = ReadEventPayloadString(item.Payload, "owner_player_id");
            var zone = ReadEventPayloadString(item.Payload, "zone");
            if (string.Equals(readyOwnerPlayerId, viewerPlayerId, StringComparison.Ordinal)
                || string.Equals(zone, "dominion", StringComparison.Ordinal))
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
                    ["owner_player_id"] = readyOwnerPlayerId,
                    ["zone"] = zone,
                    ["activity_state_before"] = ReadEventPayloadString(
                        item.Payload,
                        "activity_state_before"),
                    ["activity_state_after"] = ReadEventPayloadString(
                        item.Payload,
                        "activity_state_after"),
                    ["phase"] = ReadEventPayloadString(item.Payload, "phase"),
                    ["identity_redacted"] = true,
                }),
            };
        }

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
        if (string.Equals(toZone, "resolution", StringComparison.Ordinal))
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

        if (request.ActionType is "advance_phase" or "draw_card" or "end_turn" or "pass_priority"
            && request.Payload.EnumerateObject().Any())
        {
            return Diagnostic(
                "ACTION_PAYLOAD_INVALID",
                "request_validation",
                "Action payload contains unsupported fields.",
                $"The {request.ActionType} action requires an empty payload object.",
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

        if (string.Equals(request.ActionType, "react", StringComparison.Ordinal))
        {
            var properties = request.Payload.EnumerateObject().ToArray();
            var names = properties.Select(property => property.Name).ToHashSet(StringComparer.Ordinal);
            var targetSelections = default(JsonElement);
            var valid = properties.Length == 2
                && names.SetEquals(new[] { "reaction_option_id", "target_selections" })
                && request.Payload.TryGetProperty("reaction_option_id", out var reactionOptionId)
                && reactionOptionId.ValueKind == JsonValueKind.String
                && !string.IsNullOrWhiteSpace(reactionOptionId.GetString())
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
                    "Reaction requires an engine option and structured target selections.",
                    "The react payload must contain exactly reaction_option_id and target_selections; "
                    + "every selection must contain target_id and card_instance_ids.",
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

    private static ReactActionPayload ReadReactPayload(JsonElement payload) => new(
        payload.GetProperty("reaction_option_id").GetString()!,
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

    private static void MovePlayedCardFromHandToResolution(
        MatchState state,
        PlayerState player,
        CardInstanceState card,
        int handIndex)
    {
        if (handIndex < 0
            || handIndex >= player.HandCardInstanceIds.Count
            || !string.Equals(
                player.HandCardInstanceIds[handIndex],
                card.CardInstanceId,
                StringComparison.Ordinal)
            || !string.Equals(card.Zone, "hand", StringComparison.Ordinal)
            || card.ZoneIndex != handIndex
            || !string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal))
        {
            throw new EngineStateException(
                "Played-card hand-to-resolution transition no longer matches authoritative state.");
        }

        player.HandCardInstanceIds.RemoveAt(handIndex);
        ReindexZone(state, player.HandCardInstanceIds, "hand");
        card.Zone = "resolution";
        card.ZoneIndex = state.ResolutionCardInstanceIds.Count;
        card.Visibility = "public";
        card.ActivityState = null;
        card.DomainRow = null;
        card.DomainLaneIndex = null;
        card.EnteredDomainTurnNumber = null;
        card.DamageMarked = 0;
        card.ZoneSequence = checked(card.ZoneSequence + 1);
        state.ResolutionCardInstanceIds.Add(card.CardInstanceId);
    }

    private static void MovePlayedCardFromResolutionToVoid(
        MatchState state,
        CardInstanceState card)
    {
        if (!string.Equals(card.Zone, "resolution", StringComparison.Ordinal)
            || card.ZoneIndex < 0
            || card.ZoneIndex >= state.ResolutionCardInstanceIds.Count
            || !string.Equals(
                state.ResolutionCardInstanceIds[card.ZoneIndex],
                card.CardInstanceId,
                StringComparison.Ordinal))
        {
            throw new EngineStateException(
                "Played-card resolution-to-void transition no longer matches authoritative state.");
        }

        var owner = state.GetPlayer(card.OwnerPlayerId);
        state.ResolutionCardInstanceIds.RemoveAt(card.ZoneIndex);
        ReindexZone(state, state.ResolutionCardInstanceIds, "resolution");
        card.Zone = "void";
        card.ZoneIndex = owner.VoidCardInstanceIds.Count;
        card.Visibility = "public";
        card.ActivityState = null;
        card.DomainRow = null;
        card.DomainLaneIndex = null;
        card.EnteredDomainTurnNumber = null;
        card.DamageMarked = 0;
        card.ZoneSequence = checked(card.ZoneSequence + 1);
        owner.VoidCardInstanceIds.Add(card.CardInstanceId);
    }

    private static void CompleteUnderlyingPlayedCardLifecycleIfRequired(
        MatchState state,
        ActionRequest request,
        ResolutionStackEntryState entry,
        ImmutableArray<EngineEvent>.Builder responseEvents)
    {
        if (!string.Equals(
                entry.EntryKindId,
                "underlying_resolution",
                StringComparison.Ordinal))
        {
            return;
        }

        var card = state.GetCardInstance(entry.AbilityResolution.SourceCardInstanceId);
        var fromZoneIndex = card.ZoneIndex;
        var toZoneIndex = state.GetPlayer(card.OwnerPlayerId).VoidCardInstanceIds.Count;
        MovePlayedCardFromResolutionToVoid(state, card);
        var lifecycleEvent = CreateCanonicalRuntimeEvent(
            state,
            additionalEventOffset: 0,
            "zone_move",
            entry.AbilityResolution.ControllerPlayerId,
            request.ActionType,
            ContractJsonValue.From(new ZoneMovePayload(
                entry.AbilityResolution.SourceActionId ?? request.ActionId,
                entry.AbilityResolution.SourceActionType,
                card.CardInstanceId,
                card.CardId,
                card.OwnerPlayerId,
                card.ControllerPlayerId,
                "resolution",
                "void",
                fromZoneIndex,
                toZoneIndex,
                "public",
                "public")));
        state.Events.Add(lifecycleEvent);
        responseEvents.Add(lifecycleEvent);
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

    private static MatchState CloneMatchStateForSimulation(MatchState source)
    {
        var clone = new MatchState
        {
            MatchId = source.MatchId,
            Seed = source.Seed,
            RuntimePackageId = source.RuntimePackageId,
            StateVersion = source.StateVersion,
            TurnNumber = source.TurnNumber,
            Phase = source.Phase,
            LegacyPhaseCompatibility = source.LegacyPhaseCompatibility,
            StartingPlayerId = source.StartingPlayerId,
            ActivePlayerId = source.ActivePlayerId,
            PriorityPlayerId = source.PriorityPlayerId,
            NextContinuousEffectSequence = source.NextContinuousEffectSequence,
            NextReactionWindowSequence = source.NextReactionWindowSequence,
            NextReactionSubjectSequence = source.NextReactionSubjectSequence,
            NextResolutionSequence = source.NextResolutionSequence,
        };

        foreach (var sourcePlayer in source.Players)
        {
            var player = new PlayerState
            {
                PlayerId = sourcePlayer.PlayerId,
                DeckId = sourcePlayer.DeckId,
                NormalInflowUsedTurnNumber = sourcePlayer.NormalInflowUsedTurnNumber,
            };
            player.DeckCardInstanceIds.AddRange(sourcePlayer.DeckCardInstanceIds);
            player.HandCardInstanceIds.AddRange(sourcePlayer.HandCardInstanceIds);
            player.VoidCardInstanceIds.AddRange(sourcePlayer.VoidCardInstanceIds);
            player.WellspringCardInstanceIds.AddRange(sourcePlayer.WellspringCardInstanceIds);
            for (var lane = 0; lane < DomainState.LaneCount; lane += 1)
            {
                player.Domain.HorizonCardInstanceIds[lane] =
                    sourcePlayer.Domain.HorizonCardInstanceIds[lane];
                player.Domain.ZenithCardInstanceIds[lane] =
                    sourcePlayer.Domain.ZenithCardInstanceIds[lane];
            }

            clone.Players.Add(player);
        }

        foreach (var sourceCard in source.CardInstances.Values)
        {
            clone.CardInstances.Add(sourceCard.CardInstanceId, new CardInstanceState
            {
                CardInstanceId = sourceCard.CardInstanceId,
                CardId = sourceCard.CardId,
                OwnerPlayerId = sourceCard.OwnerPlayerId,
                ControllerPlayerId = sourceCard.ControllerPlayerId,
                Zone = sourceCard.Zone,
                ZoneIndex = sourceCard.ZoneIndex,
                Visibility = sourceCard.Visibility,
                CreatedSequence = sourceCard.CreatedSequence,
                ZoneSequence = sourceCard.ZoneSequence,
                InitialZone = sourceCard.InitialZone,
                ActivityState = sourceCard.ActivityState,
                DomainRow = sourceCard.DomainRow,
                DomainLaneIndex = sourceCard.DomainLaneIndex,
                EnteredDomainTurnNumber = sourceCard.EnteredDomainTurnNumber,
                DamageMarked = sourceCard.DamageMarked,
            });
        }

        foreach (var (instanceId, instance) in source.ModifierInstances)
        {
            clone.ModifierInstances.Add(instanceId, instance with { });
        }

        foreach (var (instanceId, instance) in source.KeywordGrantInstances)
        {
            clone.KeywordGrantInstances.Add(instanceId, instance with { });
        }

        clone.Events.AddRange(source.Events.Select(CloneEvent));
        clone.ResolutionCardInstanceIds.AddRange(source.ResolutionCardInstanceIds);
        clone.ClosedReactionSubjectIds.UnionWith(source.ClosedReactionSubjectIds);

        if (source.PendingTriggerWindow is not null)
        {
            var pending = new PendingTriggerWindowState
            {
                PendingWindowId = source.PendingTriggerWindow.PendingWindowId,
                ControllerPlayerId = source.PendingTriggerWindow.ControllerPlayerId,
            };
            pending.PendingTriggers.AddRange(source.PendingTriggerWindow.PendingTriggers);
            clone.PendingTriggerWindow = pending;
        }

        if (source.ReactionWindow is not null)
        {
            var reaction = new ReactionWindowState
            {
                ReactionWindowId = source.ReactionWindow.ReactionWindowId,
                ReactionSubjectId = source.ReactionWindow.ReactionSubjectId,
                OriginatingEventId = source.ReactionWindow.OriginatingEventId,
                OriginatingEventSequence = source.ReactionWindow.OriginatingEventSequence,
                UnderlyingResolutionId = source.ReactionWindow.UnderlyingResolutionId,
                InitiatorPlayerId = source.ReactionWindow.InitiatorPlayerId,
                CurrentResponsePolicyId = source.ReactionWindow.CurrentResponsePolicyId,
                ConsecutivePassCount = source.ReactionWindow.ConsecutivePassCount,
                OpenedAtStateVersion = source.ReactionWindow.OpenedAtStateVersion,
                ReactionProfileId = source.ReactionWindow.ReactionProfileId,
            };
            reaction.EligibleResponderPlayerIds.AddRange(
                source.ReactionWindow.EligibleResponderPlayerIds);
            clone.ReactionWindow = reaction;
        }

        foreach (var sourceEntry in source.ResolutionStack)
        {
            clone.ResolutionStack.Add(new ResolutionStackEntryState
            {
                ResolutionId = sourceEntry.ResolutionId,
                Sequence = sourceEntry.Sequence,
                EntryKindId = sourceEntry.EntryKindId,
                ReactionWindowId = sourceEntry.ReactionWindowId,
                ReactionSubjectId = sourceEntry.ReactionSubjectId,
                ParentResolutionId = sourceEntry.ParentResolutionId,
                AbilityResolution = sourceEntry.AbilityResolution with { },
                ReactionOptionId = sourceEntry.ReactionOptionId,
                NextResponsePolicyId = sourceEntry.NextResponsePolicyId,
            });
        }

        foreach (var sourceBatch in source.QueuedTriggerBatches)
        {
            var batch = new QueuedTriggerBatchState
            {
                TriggerBatchId = sourceBatch.TriggerBatchId,
                OriginatingEventId = sourceBatch.OriginatingEventId,
                OriginatingEventSequence = sourceBatch.OriginatingEventSequence,
                BatchOrderPolicyId = sourceBatch.BatchOrderPolicyId,
            };
            batch.Triggers.AddRange(sourceBatch.Triggers);
            clone.QueuedTriggerBatches.Add(batch);
        }

        return clone;
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
        if (state.TurnNumber <= 0)
        {
            throw new EngineStateException("Turn number must be positive.");
        }

        var isAllowedLegacyPhase = state.LegacyPhaseCompatibility
            && string.Equals(state.Phase, CanonicalPhaseIds.LegacyMain, StringComparison.Ordinal);
        if (!CanonicalPhaseIds.IsCanonical(state.Phase) && !isAllowedLegacyPhase)
        {
            throw new EngineStateException("Match phase must use the canonical phase vocabulary.");
        }

        CanonicalContinuousEffects.ValidateState(state, canonicalCards, canonicalAbilities);
        var zoneIds = new HashSet<string>(StringComparer.Ordinal);
        var knownPlayerIds = state.Players
            .Select(player => player.PlayerId)
            .ToHashSet(StringComparer.Ordinal);
        if (!knownPlayerIds.Contains(state.StartingPlayerId))
        {
            throw new EngineStateException("Starting player is unknown.");
        }

        foreach (var cardInstanceId in state.ResolutionCardInstanceIds)
        {
            if (!zoneIds.Add(cardInstanceId))
            {
                throw new EngineStateException("Card instance appears in multiple zones.");
            }

            if (!state.CardInstances.ContainsKey(cardInstanceId))
            {
                throw new EngineStateException("Resolution zone references an unknown card instance.");
            }
        }

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

        var listedResolutionIds = state.ResolutionCardInstanceIds.ToHashSet(StringComparer.Ordinal);
        var registeredResolutionIds = state.CardInstances.Values
            .Where(card => string.Equals(card.Zone, "resolution", StringComparison.Ordinal))
            .Select(card => card.CardInstanceId)
            .ToHashSet(StringComparer.Ordinal);
        if (!listedResolutionIds.SetEquals(registeredResolutionIds))
        {
            throw new EngineStateException("Card instance registry and Resolution zone disagree.");
        }

        ValidateResolutionState(state, knownPlayerIds);

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

            if (card.Zone is not ("deck" or "hand" or "void" or "wellspring" or "dominion" or "resolution"))
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
        ValidateReactionState(state, knownPlayerIds);
    }

    private static void ValidateReactionState(
        MatchState state,
        IReadOnlySet<string> knownPlayerIds)
    {
        if (state.NextReactionWindowSequence < 1
            || state.NextReactionSubjectSequence < 1
            || state.NextResolutionSequence < 1)
        {
            throw new EngineStateException("Reaction identity sequences must be positive.");
        }

        if (state.ReactionWindow is not null && state.PendingTriggerWindow is not null)
        {
            throw new EngineStateException("ReactionWindow and PendingTriggerWindow cannot both block input.");
        }

        var window = state.ReactionWindow;
        if (window is null)
        {
            if (state.ResolutionStack.Count != 0)
            {
                throw new EngineStateException("A public state without ReactionWindow cannot retain resolution entries.");
            }

            if (state.ResolutionCardInstanceIds.Count != 0)
            {
                throw new EngineStateException("A public state without ReactionWindow cannot retain resolution cards.");
            }
        }
        else
        {
            if (string.IsNullOrWhiteSpace(window.ReactionWindowId)
                || string.IsNullOrWhiteSpace(window.ReactionSubjectId)
                || string.IsNullOrWhiteSpace(window.UnderlyingResolutionId)
                || string.IsNullOrWhiteSpace(window.ReactionProfileId)
                || !knownPlayerIds.Contains(window.InitiatorPlayerId)
                || !ReactionPolicyIds.IsOpenWindowPolicy(window.CurrentResponsePolicyId)
                || window.EligibleResponderPlayerIds.Count is < 1 or > 2
                || window.EligibleResponderPlayerIds.Distinct(StringComparer.Ordinal).Count()
                != window.EligibleResponderPlayerIds.Count
                || window.EligibleResponderPlayerIds.Any(playerId => !knownPlayerIds.Contains(playerId))
                || !window.EligibleResponderPlayerIds.Contains(state.PriorityPlayerId, StringComparer.Ordinal)
                || window.ConsecutivePassCount < 0
                || window.OpenedAtStateVersion < 1
                || window.OpenedAtStateVersion > state.StateVersion
                || state.ClosedReactionSubjectIds.Contains(window.ReactionSubjectId))
            {
                throw new EngineStateException("Open ReactionWindow identity, responder, policy, or version state is invalid.");
            }

            var expectedPassLimit = string.Equals(
                window.CurrentResponsePolicyId,
                ReactionPolicyIds.StandardAlternatingResponse,
                StringComparison.Ordinal)
                ? 1
                : 0;
            if (window.ConsecutivePassCount > expectedPassLimit)
            {
                throw new EngineStateException("Open ReactionWindow retained a completed pass cycle.");
            }

            if (state.ResolutionStack.Count < 1
                || !string.Equals(
                    state.ResolutionStack[0].EntryKindId,
                    "underlying_resolution",
                    StringComparison.Ordinal)
                || !string.Equals(
                    state.ResolutionStack[0].ResolutionId,
                    window.UnderlyingResolutionId,
                    StringComparison.Ordinal))
            {
                throw new EngineStateException("ReactionWindow underlying resolution is not the bottom stack entry.");
            }


            if (state.ResolutionCardInstanceIds.Count != 1
                || !string.Equals(
                    state.ResolutionCardInstanceIds[0],
                    state.ResolutionStack[0].AbilityResolution.SourceCardInstanceId,
                    StringComparison.Ordinal))
            {
                throw new EngineStateException(
                    "ReactionWindow underlying played card is not the authoritative Resolution-zone object.");
            }
        }

        if (state.ResolutionStack.Select(entry => entry.ResolutionId)
            .Distinct(StringComparer.Ordinal).Count() != state.ResolutionStack.Count)
        {
            throw new EngineStateException("Reaction resolution IDs must be unique.");
        }

        for (var index = 0; index < state.ResolutionStack.Count; index += 1)
        {
            var entry = state.ResolutionStack[index];
            var resolution = entry.AbilityResolution;
            if (window is null
                || string.IsNullOrWhiteSpace(entry.ResolutionId)
                || entry.Sequence < 1
                || index > 0 && entry.Sequence <= state.ResolutionStack[index - 1].Sequence
                || entry.EntryKindId is not ("underlying_resolution" or "reaction")
                || !string.Equals(entry.ReactionWindowId, window.ReactionWindowId, StringComparison.Ordinal)
                || !string.Equals(entry.ReactionSubjectId, window.ReactionSubjectId, StringComparison.Ordinal)
                || !(index == 0
                    ? string.Equals(
                        resolution.SourceRelevancePolicyId,
                        ReactionPolicyIds.PlayedCardResolutionPresence,
                        StringComparison.Ordinal)
                    : string.Equals(
                        resolution.SourceRelevancePolicyId,
                        ReactionPolicyIds.SameZonePresence,
                        StringComparison.Ordinal))
                || string.IsNullOrWhiteSpace(resolution.AbilityId)
                || string.IsNullOrWhiteSpace(resolution.SourceCardInstanceId)
                || string.IsNullOrWhiteSpace(resolution.SourceCardId)
                || string.IsNullOrWhiteSpace(resolution.SourceZoneIdAtDeclaration)
                || resolution.SourceZoneSequenceAtDeclaration < 1
                || !knownPlayerIds.Contains(resolution.ControllerPlayerId)
                || resolution.DeclarationStateVersion < 1
                || resolution.DeclarationStateVersion > state.StateVersion
                || resolution.DeclaredTargetSelections.IsDefault
                || resolution.DeclaredTargetStates.IsDefault)
            {
                throw new EngineStateException("Reaction resolution stack entry state is invalid.");
            }

            if (index == 0
                ? entry.ParentResolutionId is not null || entry.ReactionOptionId is not null
                : !string.Equals(
                      entry.ParentResolutionId,
                      state.ResolutionStack[index - 1].ResolutionId,
                      StringComparison.Ordinal)
                  || string.IsNullOrWhiteSpace(entry.ReactionOptionId)
                  || !ReactionPolicyIds.IsNextResponsePolicy(entry.NextResponsePolicyId ?? string.Empty))
            {
                throw new EngineStateException("Reaction resolution stack parent or option correlation is invalid.");
            }
        }

        if (state.QueuedTriggerBatches.Select(batch => batch.TriggerBatchId)
            .Distinct(StringComparer.Ordinal).Count() != state.QueuedTriggerBatches.Count)
        {
            throw new EngineStateException("Queued trigger batch IDs must be unique.");
        }

        foreach (var batch in state.QueuedTriggerBatches)
        {
            if (string.IsNullOrWhiteSpace(batch.TriggerBatchId)
                || string.IsNullOrWhiteSpace(batch.OriginatingEventId)
                || batch.OriginatingEventSequence < 1
                || batch.OriginatingEventSequence > state.Events.Count
                || !string.Equals(
                    batch.BatchOrderPolicyId,
                    ReactionPolicyIds.DifferentTimingFifo,
                    StringComparison.Ordinal)
                || batch.Triggers.Count != 1)
            {
                throw new EngineStateException("Queued Reaction trigger batch identity or first-slice membership is invalid.");
            }

            var sourceEvent = state.Events[batch.OriginatingEventSequence - 1];
            var trigger = batch.Triggers[0];
            if (!string.Equals(sourceEvent.EventId, batch.OriginatingEventId, StringComparison.Ordinal)
                || !string.Equals(trigger.SourceEngineEventId, batch.OriginatingEventId, StringComparison.Ordinal)
                || trigger.SourceEngineEventSequence != batch.OriginatingEventSequence)
            {
                throw new EngineStateException("Queued Reaction trigger batch event correlation is invalid.");
            }
        }

        if (state.ReactionWindow is null
            && state.ResolutionStack.Count == 0
            && state.PendingTriggerWindow is null
            && state.QueuedTriggerBatches.Count > 0)
        {
            throw new EngineStateException("A stable public boundary left queued triggers without checkpoint activation.");
        }
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

    private static void ValidateResolutionState(
        MatchState state,
        IReadOnlySet<string> knownPlayerIds)
    {
        for (var zoneIndex = 0; zoneIndex < state.ResolutionCardInstanceIds.Count; zoneIndex += 1)
        {
            var card = state.GetCardInstance(state.ResolutionCardInstanceIds[zoneIndex]);
            if (!string.Equals(card.Zone, "resolution", StringComparison.Ordinal)
                || card.ZoneIndex != zoneIndex
                || !knownPlayerIds.Contains(card.OwnerPlayerId)
                || !knownPlayerIds.Contains(card.ControllerPlayerId)
                || !string.Equals(card.Visibility, "public", StringComparison.Ordinal)
                || card.ActivityState is not null)
            {
                throw new EngineStateException(
                    "Resolution card zone, order, controller, visibility, or activity state is invalid.");
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

    private sealed record PlannedReactionResolutionStep(
        string ResolutionId,
        CanonicalEffectExecutionPlan? EffectPlan,
        string? InvalidationReasonCode);

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
