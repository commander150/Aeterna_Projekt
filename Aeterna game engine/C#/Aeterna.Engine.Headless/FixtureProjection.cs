using System.Collections.Immutable;
using System.Text.Json.Nodes;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Serialization;

namespace Aeterna.Engine.Headless;

internal static class FixtureProjection
{
    private static readonly string[] RequiredRequestFields =
    [
        "request_id",
        "match_id",
        "player_id",
        "action_id",
        "action_type",
        "expected_state_version",
        "payload",
    ];

    public static JsonObject BuildCanonicalState(DebugSnapshot state)
    {
        var players = new JsonArray();
        foreach (var player in state.Players)
        {
            players.Add(new JsonObject
            {
                ["player_id"] = player.PlayerId,
                ["deck_id"] = player.DeckId,
                ["deck_card_instance_ids"] = StringArray(player.DeckCardInstanceIds),
                ["hand_card_instance_ids"] = StringArray(player.HandCardInstanceIds),
                ["discard_card_instance_ids"] = StringArray(player.DiscardCardInstanceIds),
            });
        }

        var cardInstances = new JsonArray();
        foreach (var card in state.CardInstances
                     .OrderBy(card => card.CreatedSequence)
                     .ThenBy(card => card.CardInstanceId, StringComparer.Ordinal))
        {
            cardInstances.Add(BuildCanonicalCardInstance(card));
        }

        var topologyEntries = new JsonArray();
        var occupancyEntries = new JsonArray();
        foreach (var player in state.Players)
        {
            topologyEntries.Add(new JsonObject
            {
                ["player_id"] = player.PlayerId,
                ["topology"] = BuildTopology(player.PlayerId),
            });
            occupancyEntries.Add(new JsonObject
            {
                ["player_id"] = player.PlayerId,
                ["occupancy"] = BuildOccupancy(player.PlayerId),
            });
        }

        return new JsonObject
        {
            ["schema_version"] = "aeterna-canonical-match-state-v1",
            ["contract_type"] = "canonical_match_state",
            ["match_id"] = state.MatchId,
            ["state_version"] = state.StateVersion,
            ["turn_number"] = state.TurnNumber,
            ["phase"] = state.Phase,
            ["active_player_id"] = state.ActivePlayerId,
            ["priority_player_id"] = state.PriorityPlayerId,
            ["priority_model"] = "minimal_priority_model_v1",
            ["players"] = players,
            ["card_instances"] = cardInstances,
            ["domain_topologies"] = topologyEntries,
            ["domain_occupancies"] = occupancyEntries,
            ["event_log"] = CanonicalEvents(state.Events),
            ["semantic_metadata"] = new JsonObject(),
        };
    }

    public static JsonObject BuildActionSpace(DebugSnapshot state, LegalActionSpace actionSpace)
    {
        var actionRecords = new JsonArray();
        foreach (var action in actionSpace.Actions)
        {
            actionRecords.Add(new JsonObject
            {
                ["action_id"] = action.ActionId,
                ["action_type"] = action.ActionType,
                ["player_id"] = action.PlayerId,
                ["enabled"] = action.Enabled,
                ["order_rank"] = action.OrderRank,
                ["disabled_reason"] = action.DisabledReason,
                ["request_template"] = new JsonObject
                {
                    ["action_type"] = action.ActionType,
                    ["player_id"] = action.PlayerId,
                    ["expected_state_version"] = state.StateVersion,
                    ["payload"] = new JsonObject(),
                    ["required_fields"] = StringArray(RequiredRequestFields),
                },
                ["metadata"] = new JsonObject
                {
                    ["rules_scope"] = "minimal_end_turn_smoke",
                    ["ordering_profile"] = "canonical_legal_action_ordering_v1",
                },
            });
        }

        return new JsonObject
        {
            ["schema_version"] = "minimal-legal-action-space-v0",
            ["contract_type"] = "legal_action_space",
            ["match_id"] = state.MatchId,
            ["state_version"] = state.StateVersion,
            ["turn"] = state.TurnNumber,
            ["phase"] = state.Phase,
            ["active_player_id"] = state.ActivePlayerId,
            ["priority_player_id"] = state.PriorityPlayerId,
            ["player_id"] = actionSpace.PlayerId,
            ["actions"] = actionRecords,
            ["enabled_action_count"] = actionSpace.Actions.Count(action => action.Enabled),
            ["disabled_action_count"] = actionSpace.Actions.Count(action => !action.Enabled),
            ["metadata"] = new JsonObject
            {
                ["rules_scope"] = "minimal_end_turn_smoke",
            },
        };
    }

    public static JsonObject BuildCheckpoint(
        DebugSnapshot state,
        string checkpointId,
        LegalActionSpace actionSpace,
        bool stateUnchanged)
    {
        var canonicalState = BuildCanonicalState(state);
        var orderingActions = new JsonArray();
        foreach (var action in actionSpace.Actions)
        {
            orderingActions.Add(new JsonObject
            {
                ["action_type"] = action.ActionType,
                ["action_id"] = action.ActionId,
                ["order_rank"] = action.OrderRank,
            });
        }

        return new JsonObject
        {
            ["checkpoint_id"] = checkpointId,
            ["state_version"] = state.StateVersion,
            ["player_id"] = actionSpace.PlayerId,
            ["action_space"] = BuildActionSpace(state, actionSpace),
            ["canonical_action_ordering"] = new JsonObject
            {
                ["profile"] = "canonical_legal_action_ordering_v1",
                ["keys"] = StringArray(["order_rank", "action_type", "action_id"]),
                ["actions"] = orderingActions,
            },
            ["state_unchanged"] = stateUnchanged,
            ["state_sha256"] = CanonicalJson.Sha256(CanonicalJson.Serialize(canonicalState)),
        };
    }

    public static JsonObject BuildPlayerSnapshot(
        PlayerSnapshot snapshot,
        LegalActionSpace viewerActions,
        ImmutableArray<EngineEvent> visibleEvents,
        ImmutableArray<EngineDiagnostic> invariantDiagnostics)
    {
        var players = new JsonArray();
        foreach (var player in snapshot.Players)
        {
            players.Add(BuildPlayerProjection(player));
        }

        var actionTypes = viewerActions.Actions
            .Select(action => action.ActionType)
            .Distinct(StringComparer.Ordinal)
            .OrderBy(value => value, StringComparer.Ordinal);
        var lastEvent = visibleEvents.LastOrDefault();
        var invariantErrorCount = invariantDiagnostics.Count(item => item.Severity == "error");
        return new JsonObject
        {
            ["schema_version"] = "engine-player-visible-snapshot-v2",
            ["contract_type"] = "engine_player_visible_snapshot",
            ["snapshot_type"] = "player_visible_snapshot",
            ["visibility_mode"] = "player",
            ["player_id"] = snapshot.ViewerPlayerId,
            ["match_id"] = snapshot.MatchId,
            ["state_version"] = snapshot.StateVersion,
            ["turn"] = snapshot.TurnNumber,
            ["turn_number"] = snapshot.TurnNumber,
            ["phase"] = snapshot.Phase,
            ["active_player_id"] = snapshot.ActivePlayerId,
            ["priority_player_id"] = snapshot.PriorityPlayerId,
            ["players"] = players,
            ["board"] = BuildBoard(snapshot.Players.Select(player => player.PlayerId)),
            ["visibility_policy"] = new JsonObject
            {
                ["model"] = "minimal_visibility_projection_v0",
                ["deck"] = "count_only",
                ["own_hand"] = "owner_visible",
                ["opponent_hand"] = "count_only",
                ["discard"] = "public",
                ["board"] = "public",
            },
            ["legal_action_summary"] = new JsonObject
            {
                ["state_version"] = snapshot.StateVersion,
                ["action_count"] = viewerActions.Actions.Length,
                ["enabled_count"] = viewerActions.Actions.Count(action => action.Enabled),
                ["disabled_count"] = viewerActions.Actions.Count(action => !action.Enabled),
                ["action_types"] = StringArray(actionTypes),
            },
            ["event_log_summary"] = new JsonObject
            {
                ["event_count"] = visibleEvents.Length,
                ["last_event_type"] = lastEvent?.EventType,
                ["last_event_sequence"] = lastEvent?.EventSequence,
            },
            ["diagnostics_summary"] = new JsonObject
            {
                ["invariant_errors"] = invariantErrorCount,
                ["blocking_errors"] = invariantDiagnostics.Count(item => item.Blocking),
                ["warnings"] = invariantDiagnostics.Count(item => item.Severity == "warning"),
                ["hand_deck_invariants_ok"] = invariantErrorCount == 0,
                ["draw_preconditions_ok"] = snapshot.Players.All(player => player.Deck.Count > 0),
            },
            ["metadata"] = new JsonObject
            {
                ["rules_scope"] = "minimal_draw_end_turn_smoke",
                ["hidden_information_model"] = "minimal_visibility_projection_v0",
                ["player_visible_snapshot_model"] = "stable_minimal_v2",
                ["debug_snapshot_source"] = false,
                ["card_instance_model"] = "minimal_registry_v0",
                ["board_model"] = "minimal-public-domain-board-v0",
                ["card_id_overlap_guard"] = false,
            },
        };
    }

    public static JsonObject BuildLegacyRequest(ActionRequest request) => new()
    {
        ["request_id"] = request.RequestId,
        ["match_id"] = request.MatchId,
        ["player_id"] = request.PlayerId,
        ["action_id"] = request.ActionId,
        ["action_type"] = request.ActionType,
        ["expected_state_version"] = request.ExpectedStateVersion,
        ["payload"] = JsonNode.Parse(request.Payload.GetRawText()),
    };

    public static JsonObject BuildLegacyResponse(ActionResponse response, bool invariantsOk)
    {
        var events = new JsonArray();
        foreach (var item in response.Events)
        {
            events.Add(BuildResponseEvent(item, response.Accepted));
        }

        var diagnostics = new JsonArray();
        foreach (var diagnostic in response.Diagnostics)
        {
            diagnostics.Add(BuildLegacyDiagnostic(diagnostic));
        }

        return new JsonObject
        {
            ["schema_version"] = "minimal-action-response-v0",
            ["contract_type"] = "action_response",
            ["response_type"] = "minimal_action_response",
            ["match_id"] = response.MatchId,
            ["request_id"] = response.RequestId,
            ["player_id"] = response.PlayerId,
            ["action_id"] = response.ActionId,
            ["action_type"] = response.ActionType,
            ["accepted"] = response.Accepted,
            ["success"] = response.Accepted,
            ["reason"] = response.Reason,
            ["state_version_before"] = response.StateVersionBefore,
            ["state_version_after"] = response.StateVersionAfter,
            ["new_event_count"] = response.Events.Length,
            ["new_event_sequences"] = IntArray(response.Events.Select(item => item.EventSequence)),
            ["events"] = events,
            ["event_count"] = response.Events.Length,
            ["diagnostics"] = diagnostics,
            ["diagnostics_summary"] = new JsonObject
            {
                ["count"] = response.Diagnostics.Length,
                ["blocking_errors"] = response.Diagnostics.Count(item => item.Severity == "error"),
                ["warnings"] = response.Diagnostics.Count(item => item.Severity == "warning"),
            },
            ["invariants_ok"] = invariantsOk,
            ["metadata"] = new JsonObject
            {
                ["rules_scope"] = "minimal_end_turn_smoke",
            },
        };
    }

    public static JsonArray CanonicalEvents(IEnumerable<EngineEvent> source)
    {
        var events = new JsonArray();
        foreach (var item in source)
        {
            events.Add(BuildCanonicalEvent(item));
        }

        return events;
    }

    private static JsonObject BuildResponseEvent(EngineEvent item, bool applied) => new()
    {
        ["schema_version"] = "minimal-engine-event-v0",
        ["contract_type"] = "engine_event",
        ["event_type"] = item.EventType,
        ["event_sequence"] = item.EventSequence,
        ["event_index"] = item.EventSequence - 1,
        ["state_version"] = item.StateVersion,
        ["turn_number"] = item.TurnNumber,
        ["player_id"] = item.ActorPlayerId,
        ["action_type"] = item.CauseActionType,
        ["payload"] = BuildLegacyEventPayload(item, canonical: false, applied),
    };

    private static JsonObject BuildCanonicalEvent(EngineEvent item) => new()
    {
        ["schema_version"] = "minimal-engine-event-v0",
        ["contract_type"] = "engine_event",
        ["event_type"] = item.EventType,
        ["event_sequence"] = item.EventSequence,
        ["event_index"] = item.EventSequence - 1,
        ["state_version"] = item.StateVersion,
        ["turn_number"] = item.TurnNumber,
        ["player_id"] = item.ActorPlayerId,
        ["action_type"] = item.CauseActionType,
        ["payload"] = BuildLegacyEventPayload(
            item,
            canonical: true,
            applied: item.EventSequence > 0 && item.StateVersion > 0),
        ["semantic_metadata"] = new JsonObject(),
    };

    private static JsonObject BuildLegacyEventPayload(EngineEvent item, bool canonical, bool applied)
    {
        JsonObject payload;
        if (item.EventType == "zone_move")
        {
            var source = item.Payload;
            payload = new JsonObject
            {
                ["schema_version"] = "minimal-zone-move-record-v0",
                ["contract_type"] = "zone_move",
                ["event_type"] = "zone_move",
                ["event_sequence"] = item.EventSequence,
                ["state_version"] = item.StateVersion,
                ["source_action_id"] = ReadString(source, "source_action_id"),
                ["source_action_type"] = ReadString(source, "source_action_type"),
                ["card_instance_id"] = ReadString(source, "card_instance_id"),
                ["card_id"] = ReadString(source, "card_id"),
                ["owner_player_id"] = ReadString(source, "owner_player_id"),
                ["controller_player_id"] = ReadString(source, "controller_player_id"),
                ["from_zone"] = ReadString(source, "from_zone"),
                ["to_zone"] = ReadString(source, "to_zone"),
                ["from_zone_index"] = ReadInt(source, "from_zone_index"),
                ["to_zone_index"] = ReadInt(source, "to_zone_index"),
                ["visibility_before"] = ReadString(source, "visibility_before"),
                ["visibility_after"] = ReadString(source, "visibility_after"),
            };
            payload[canonical ? "semantic_metadata" : "metadata"] = new JsonObject
            {
                ["zone_operation"] = "draw_card",
                ["semantic_event_type"] = "card_drawn",
                ["applied"] = applied,
            };
        }
        else if (item.EventType == "turn_transition")
        {
            var source = item.Payload;
            payload = new JsonObject
            {
                ["schema_version"] = "minimal-turn-transition-record-v0",
                ["contract_type"] = "turn_transition",
                ["event_type"] = "turn_transition",
                ["event_sequence"] = item.EventSequence,
                ["state_version"] = item.StateVersion,
                ["source_action_id"] = ReadString(source, "source_action_id"),
                ["source_action_type"] = ReadString(source, "source_action_type"),
                ["previous_active_player_id"] = ReadString(source, "previous_active_player_id"),
                ["next_active_player_id"] = ReadString(source, "next_active_player_id"),
                ["previous_priority_player_id"] = ReadString(source, "previous_priority_player_id"),
                ["next_priority_player_id"] = ReadString(source, "next_priority_player_id"),
                ["turn_number_before"] = ReadInt(source, "turn_number_before"),
                ["turn_number_after"] = ReadInt(source, "turn_number_after"),
                ["phase_before"] = ReadString(source, "phase_before"),
                ["phase_after"] = ReadString(source, "phase_after"),
            };
            payload[canonical ? "semantic_metadata" : "metadata"] = new JsonObject
            {
                ["turn_model"] = "minimal_alternating_players",
                ["semantic_event_type"] = "end_turn_resolved",
                ["applied"] = applied,
            };
        }
        else
        {
            throw new InvalidOperationException($"Unsupported fixture event type: {item.EventType}");
        }

        return payload;
    }

    private static JsonObject BuildLegacyDiagnostic(EngineDiagnostic diagnostic)
    {
        var result = new JsonObject
        {
            ["code"] = diagnostic.Code,
            ["severity"] = diagnostic.Severity,
            ["category"] = diagnostic.Category,
        };
        if (diagnostic.Details.TryGetProperty("expected_state_version", out var expected))
        {
            result["expected_state_version"] = expected.GetInt32();
        }

        if (diagnostic.Details.TryGetProperty("current_state_version", out var current))
        {
            result["current_state_version"] = current.GetInt32();
        }

        result["retry_policy"] = diagnostic.RetryPolicy;
        return result;
    }

    private static JsonObject BuildCanonicalCardInstance(DebugCardInstanceSnapshot card) => new()
    {
        ["schema_version"] = "minimal-card-instance-record-v1",
        ["contract_type"] = "card_instance_record",
        ["card_instance_id"] = card.CardInstanceId,
        ["card_id"] = card.CardId,
        ["owner_player_id"] = card.OwnerPlayerId,
        ["controller_player_id"] = card.ControllerPlayerId,
        ["zone"] = card.Zone,
        ["zone_index"] = card.ZoneIndex,
        ["visibility"] = card.Visibility,
        ["created_sequence"] = card.CreatedSequence,
        ["zone_sequence"] = card.ZoneSequence,
        ["activity_state"] = card.ActivityState,
        ["semantic_metadata"] = new JsonObject
        {
            ["creation_reason"] = "initial_match_setup",
            ["initial_zone"] = card.InitialZone,
        },
    };

    private static JsonObject BuildPlayerProjection(PlayerSnapshotEntry player)
    {
        var isViewer = string.Equals(player.Relation, "self", StringComparison.Ordinal);
        return new JsonObject
        {
            ["player_id"] = player.PlayerId,
            ["relation"] = player.Relation,
            ["is_viewer"] = isViewer,
            ["deck_count"] = player.Deck.Count,
            ["hand_count"] = player.Hand.Count,
            ["discard_count"] = player.Discard.Count,
            ["zones"] = new JsonObject
            {
                ["deck"] = BuildZoneProjection(player.Deck),
                ["hand"] = BuildZoneProjection(player.Hand),
                ["discard"] = BuildZoneProjection(player.Discard),
            },
        };
    }

    private static JsonObject BuildZoneProjection(ZoneSnapshot zone)
    {
        var objects = new JsonArray();
        foreach (var card in zone.Objects)
        {
            objects.Add(BuildObjectReference(card));
        }

        return new JsonObject
        {
            ["zone"] = zone.Zone,
            ["count"] = zone.Count,
            ["visibility_mode"] = zone.VisibilityMode,
            ["redacted"] = zone.Redacted,
            ["objects"] = objects,
            ["metadata"] = new JsonObject
            {
                ["ordered"] = !zone.Redacted,
            },
        };
    }

    private static JsonObject BuildObjectReference(CardReference card) => new()
    {
        ["schema_version"] = "minimal-object-reference-v0",
        ["contract_type"] = "object_reference",
        ["object_type"] = "card_instance",
        ["object_id"] = card.CardInstanceId,
        ["card_instance_id"] = card.CardInstanceId,
        ["card_id"] = card.CardId,
        ["zone"] = card.Zone,
        ["zone_sequence"] = card.ZoneSequence,
        ["controller_player_id"] = card.ControllerPlayerId,
        ["visibility"] = card.Visibility,
        ["metadata"] = new JsonObject
        {
            ["reference_scope"] = "minimal_card_instance_helper",
        },
    };

    private static JsonObject BuildTopology(string playerId)
    {
        var currents = new JsonArray();
        var positions = new JsonArray();
        for (var currentIndex = 1; currentIndex <= 6; currentIndex++)
        {
            var currentId = CurrentId(playerId, currentIndex);
            foreach (var positionType in new[] { "horizon", "zenith", "seal" })
            {
                positions.Add(new JsonObject
                {
                    ["schema_version"] = "minimal-domain-position-v0",
                    ["contract_type"] = "domain_position_reference",
                    ["position_id"] = PositionId(playerId, currentIndex, positionType),
                    ["player_id"] = playerId,
                    ["area"] = positionType == "seal" ? "seal_layer" : "domain",
                    ["current_index"] = currentIndex,
                    ["position_type"] = positionType,
                    ["row"] = positionType == "seal" ? null : positionType,
                    ["linked_current_id"] = currentId,
                    ["visibility"] = "public",
                    ["semantic_metadata"] = new JsonObject
                    {
                        ["topology_model"] = "base_game_six_current_v0",
                        ["current_count"] = 6,
                        ["static_topology"] = true,
                        ["occupancy_model"] = "not_implemented",
                    },
                });
            }

            currents.Add(new JsonObject
            {
                ["current_id"] = currentId,
                ["current_index"] = currentIndex,
                ["horizon_position_id"] = PositionId(playerId, currentIndex, "horizon"),
                ["zenith_position_id"] = PositionId(playerId, currentIndex, "zenith"),
                ["seal_position_id"] = PositionId(playerId, currentIndex, "seal"),
                ["semantic_metadata"] = new JsonObject
                {
                    ["positionally_linked_seal"] = true,
                    ["ordered"] = true,
                },
            });
        }

        return new JsonObject
        {
            ["schema_version"] = "minimal-player-domain-topology-v0",
            ["contract_type"] = "player_domain_topology",
            ["player_id"] = playerId,
            ["current_count"] = 6,
            ["row_count"] = 2,
            ["rows"] = StringArray(["horizon", "zenith"]),
            ["currents"] = currents,
            ["positions"] = positions,
            ["semantic_metadata"] = new JsonObject
            {
                ["topology_model"] = "base_game_six_current_v0",
                ["static_topology"] = true,
                ["domain_scope"] = "combat_field_structure",
                ["full_play_area_model"] = false,
                ["occupancy_model"] = "not_implemented",
                ["four_current_variant_active"] = false,
            },
        };
    }

    private static JsonObject BuildOccupancy(string playerId)
    {
        var slots = new JsonArray();
        for (var currentIndex = 1; currentIndex <= 6; currentIndex++)
        {
            foreach (var positionType in new[] { "horizon", "zenith" })
            {
                slots.Add(new JsonObject
                {
                    ["schema_version"] = "minimal-domain-position-occupancy-v0",
                    ["contract_type"] = "domain_position_occupancy",
                    ["position_id"] = PositionId(playerId, currentIndex, positionType),
                    ["player_id"] = playerId,
                    ["current_index"] = currentIndex,
                    ["position_type"] = positionType,
                    ["row"] = positionType,
                    ["occupancy_state"] = "empty",
                    ["occupant_object_type"] = null,
                    ["occupant_card_instance_id"] = null,
                    ["visibility"] = "public",
                    ["semantic_metadata"] = new JsonObject
                    {
                        ["occupancy_model"] = "single_card_instance_per_domain_position_v0",
                        ["capacity"] = 1,
                        ["topology_model"] = "base_game_six_current_v0",
                        ["mutation_api"] = "not_implemented",
                        ["gameplay_integration"] = "not_implemented",
                        ["seal_position_supported"] = false,
                    },
                });
            }
        }

        return new JsonObject
        {
            ["schema_version"] = "minimal-player-domain-occupancy-v0",
            ["contract_type"] = "player_domain_occupancy",
            ["player_id"] = playerId,
            ["topology_schema_version"] = "minimal-player-domain-topology-v0",
            ["topology_model"] = "base_game_six_current_v0",
            ["occupancy_model"] = "single_card_instance_per_domain_position_v0",
            ["slot_count"] = 12,
            ["slots"] = slots,
            ["semantic_metadata"] = new JsonObject
            {
                ["static_topology_reference"] = true,
                ["slot_capacity"] = 1,
                ["seal_state_model"] = "not_implemented",
                ["mutation_api"] = "not_implemented",
                ["play_card_integration"] = "not_implemented",
                ["match_state_integration"] = "not_implemented",
                ["four_current_variant_active"] = false,
            },
        };
    }

    private static JsonObject BuildBoard(IEnumerable<string> playerIds)
    {
        var players = new JsonArray();
        foreach (var playerId in playerIds.OrderBy(playerId => playerId, StringComparer.Ordinal))
        {
            var currents = new JsonArray();
            for (var currentIndex = 1; currentIndex <= 6; currentIndex++)
            {
                currents.Add(new JsonObject
                {
                    ["current_id"] = CurrentId(playerId, currentIndex),
                    ["current_index"] = currentIndex,
                    ["horizon"] = BuildBoardSlot(playerId, currentIndex, "horizon"),
                    ["zenith"] = BuildBoardSlot(playerId, currentIndex, "zenith"),
                    ["seal_position"] = new JsonObject
                    {
                        ["position_id"] = PositionId(playerId, currentIndex, "seal"),
                        ["player_id"] = playerId,
                        ["current_index"] = currentIndex,
                        ["position_type"] = "seal",
                        ["visibility"] = "public",
                        ["state_model"] = "not_implemented",
                    },
                    ["metadata"] = new JsonObject
                    {
                        ["ordered"] = true,
                        ["positionally_linked_seal"] = true,
                    },
                });
            }

            players.Add(new JsonObject
            {
                ["player_id"] = playerId,
                ["current_count"] = 6,
                ["occupied_slot_count"] = 0,
                ["empty_slot_count"] = 12,
                ["currents"] = currents,
                ["metadata"] = new JsonObject
                {
                    ["visibility"] = "public",
                    ["domain_slot_count"] = 12,
                    ["seal_position_count"] = 6,
                },
            });
        }

        return new JsonObject
        {
            ["schema_version"] = "minimal-player-visible-domain-board-v0",
            ["contract_type"] = "player_visible_domain_board",
            ["board_model"] = "minimal-public-domain-board-v0",
            ["visibility_mode"] = "public",
            ["current_count"] = 6,
            ["players"] = players,
            ["metadata"] = new JsonObject
            {
                ["topology_model"] = "base_game_six_current_v0",
                ["occupancy_model"] = "single_card_instance_per_domain_position_v0",
                ["object_reference_model"] = "minimal-object-reference-v0",
                ["seal_state_model"] = "not_implemented",
                ["gameplay_mutation_model"] = "not_implemented",
                ["public_information_only"] = true,
            },
        };
    }

    private static JsonObject BuildBoardSlot(string playerId, int currentIndex, string positionType) => new()
    {
        ["position_id"] = PositionId(playerId, currentIndex, positionType),
        ["player_id"] = playerId,
        ["current_index"] = currentIndex,
        ["position_type"] = positionType,
        ["row"] = positionType,
        ["occupancy_state"] = "empty",
        ["occupied"] = false,
        ["occupant"] = null,
        ["visibility"] = "public",
        ["metadata"] = new JsonObject
        {
            ["capacity"] = 1,
            ["occupancy_model"] = "single_card_instance_per_domain_position_v0",
        },
    };

    private static string ReadString(System.Text.Json.JsonElement source, string propertyName) =>
        source.GetProperty(propertyName).GetString()
        ?? throw new InvalidOperationException($"Event payload string is missing: {propertyName}");

    private static int ReadInt(System.Text.Json.JsonElement source, string propertyName) =>
        source.GetProperty(propertyName).GetInt32();

    private static JsonArray StringArray(IEnumerable<string> values)
    {
        var result = new JsonArray();
        foreach (var value in values)
        {
            result.Add(value);
        }

        return result;
    }

    private static JsonArray IntArray(IEnumerable<int> values)
    {
        var result = new JsonArray();
        foreach (var value in values)
        {
            result.Add(value);
        }

        return result;
    }

    private static string CurrentId(string playerId, int currentIndex) =>
        $"domain_{playerId}_current_{currentIndex:00}";

    private static string PositionId(string playerId, int currentIndex, string positionType) =>
        $"{CurrentId(playerId, currentIndex)}_{positionType}";
}
