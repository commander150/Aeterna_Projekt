using System.Text.Json.Nodes;

namespace Aeterna.RuntimeCandidate;

internal static class RuntimeProjection
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

    public static JsonObject BuildCanonicalState(RuntimeState state)
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
        foreach (var card in state.CardInstances.Values
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

        var events = new JsonArray();
        foreach (var runtimeEvent in state.Events)
        {
            events.Add(runtimeEvent.CanonicalEvent.DeepClone());
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
            ["priority_player_id"] = state.ActivePlayerId,
            ["priority_model"] = "minimal_priority_model_v1",
            ["players"] = players,
            ["card_instances"] = cardInstances,
            ["domain_topologies"] = topologyEntries,
            ["domain_occupancies"] = occupancyEntries,
            ["event_log"] = events,
            ["semantic_metadata"] = new JsonObject(),
        };
    }

    public static JsonObject BuildActionSpace(
        RuntimeState state,
        string playerId,
        IReadOnlyList<LegalAction> actions)
    {
        var actionRecords = new JsonArray();
        foreach (var action in actions)
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
            ["priority_player_id"] = state.ActivePlayerId,
            ["player_id"] = playerId,
            ["actions"] = actionRecords,
            ["enabled_action_count"] = actions.Count(action => action.Enabled),
            ["disabled_action_count"] = actions.Count(action => !action.Enabled),
            ["metadata"] = new JsonObject
            {
                ["rules_scope"] = "minimal_end_turn_smoke",
            },
        };
    }

    public static JsonObject BuildCheckpoint(
        RuntimeState state,
        string checkpointId,
        string playerId,
        IReadOnlyList<LegalAction> actions)
    {
        var canonicalState = BuildCanonicalState(state);
        var orderingActions = new JsonArray();
        foreach (var action in actions)
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
            ["player_id"] = playerId,
            ["action_space"] = BuildActionSpace(state, playerId, actions),
            ["canonical_action_ordering"] = new JsonObject
            {
                ["profile"] = "canonical_legal_action_ordering_v1",
                ["keys"] = StringArray(["order_rank", "action_type", "action_id"]),
                ["actions"] = orderingActions,
            },
            ["state_unchanged"] = true,
            ["state_sha256"] = CanonicalJson.Sha256(CanonicalJson.Serialize(canonicalState)),
        };
    }

    public static JsonObject BuildPlayerSnapshot(
        RuntimeState state,
        string viewerPlayerId,
        IReadOnlyList<LegalAction> viewerActions)
    {
        var players = new JsonArray();
        foreach (var player in state.Players)
        {
            players.Add(BuildPlayerProjection(state, player, viewerPlayerId));
        }

        var actionTypes = viewerActions
            .Select(action => action.ActionType)
            .Distinct(StringComparer.Ordinal)
            .OrderBy(value => value, StringComparer.Ordinal);
        var lastEvent = state.Events.LastOrDefault()?.CanonicalEvent;
        return new JsonObject
        {
            ["schema_version"] = "engine-player-visible-snapshot-v2",
            ["contract_type"] = "engine_player_visible_snapshot",
            ["snapshot_type"] = "player_visible_snapshot",
            ["visibility_mode"] = "player",
            ["player_id"] = viewerPlayerId,
            ["match_id"] = state.MatchId,
            ["state_version"] = state.StateVersion,
            ["turn"] = state.TurnNumber,
            ["turn_number"] = state.TurnNumber,
            ["phase"] = state.Phase,
            ["active_player_id"] = state.ActivePlayerId,
            ["priority_player_id"] = state.ActivePlayerId,
            ["players"] = players,
            ["board"] = BuildBoard(state),
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
                ["state_version"] = state.StateVersion,
                ["action_count"] = viewerActions.Count,
                ["enabled_count"] = viewerActions.Count(action => action.Enabled),
                ["disabled_count"] = viewerActions.Count(action => !action.Enabled),
                ["action_types"] = StringArray(actionTypes),
            },
            ["event_log_summary"] = new JsonObject
            {
                ["event_count"] = state.Events.Count,
                ["last_event_type"] = lastEvent?["event_type"]?.GetValue<string>(),
                ["last_event_sequence"] = lastEvent?["event_sequence"]?.GetValue<int>(),
            },
            ["diagnostics_summary"] = new JsonObject
            {
                ["invariant_errors"] = 0,
                ["blocking_errors"] = 0,
                ["warnings"] = 0,
                ["hand_deck_invariants_ok"] = true,
                ["draw_preconditions_ok"] = state.Players.All(player => player.DeckCardInstanceIds.Count > 0),
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

    private static JsonObject BuildCanonicalCardInstance(CardInstanceState card) => new()
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
        ["activity_state"] = null,
        ["semantic_metadata"] = new JsonObject
        {
            ["creation_reason"] = "initial_match_setup",
            ["initial_zone"] = card.InitialZone,
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

    private static JsonObject BuildPlayerProjection(
        RuntimeState state,
        PlayerRuntimeState player,
        string viewerPlayerId)
    {
        var isViewer = string.Equals(player.PlayerId, viewerPlayerId, StringComparison.Ordinal);
        return new JsonObject
        {
            ["player_id"] = player.PlayerId,
            ["relation"] = isViewer ? "self" : "opponent",
            ["is_viewer"] = isViewer,
            ["deck_count"] = player.DeckCardInstanceIds.Count,
            ["hand_count"] = player.HandCardInstanceIds.Count,
            ["discard_count"] = player.DiscardCardInstanceIds.Count,
            ["zones"] = new JsonObject
            {
                ["deck"] = BuildZoneProjection(state, "deck", player.DeckCardInstanceIds, "count_only"),
                ["hand"] = BuildZoneProjection(
                    state,
                    "hand",
                    player.HandCardInstanceIds,
                    isViewer ? "owner_visible" : "count_only"),
                ["discard"] = BuildZoneProjection(state, "discard", player.DiscardCardInstanceIds, "public"),
            },
        };
    }

    private static JsonObject BuildZoneProjection(
        RuntimeState state,
        string zone,
        IReadOnlyList<string> cardInstanceIds,
        string visibilityMode)
    {
        var visible = visibilityMode is "owner_visible" or "public";
        var objects = new JsonArray();
        if (visible)
        {
            foreach (var cardInstanceId in cardInstanceIds)
            {
                objects.Add(BuildObjectReference(state.GetCardInstance(cardInstanceId)));
            }
        }

        return new JsonObject
        {
            ["zone"] = zone,
            ["count"] = cardInstanceIds.Count,
            ["visibility_mode"] = visibilityMode,
            ["redacted"] = !visible,
            ["objects"] = objects,
            ["metadata"] = new JsonObject
            {
                ["ordered"] = visible,
            },
        };
    }

    private static JsonObject BuildObjectReference(CardInstanceState card) => new()
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

    private static JsonObject BuildBoard(RuntimeState state)
    {
        var players = new JsonArray();
        foreach (var player in state.Players.OrderBy(player => player.PlayerId, StringComparer.Ordinal))
        {
            var currents = new JsonArray();
            for (var currentIndex = 1; currentIndex <= 6; currentIndex++)
            {
                currents.Add(new JsonObject
                {
                    ["current_id"] = CurrentId(player.PlayerId, currentIndex),
                    ["current_index"] = currentIndex,
                    ["horizon"] = BuildBoardSlot(player.PlayerId, currentIndex, "horizon"),
                    ["zenith"] = BuildBoardSlot(player.PlayerId, currentIndex, "zenith"),
                    ["seal_position"] = new JsonObject
                    {
                        ["position_id"] = PositionId(player.PlayerId, currentIndex, "seal"),
                        ["player_id"] = player.PlayerId,
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
                ["player_id"] = player.PlayerId,
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

    private static JsonArray StringArray(IEnumerable<string> values)
    {
        var array = new JsonArray();
        foreach (var value in values)
        {
            array.Add(value);
        }

        return array;
    }

    private static string CurrentId(string playerId, int currentIndex) =>
        $"domain_{playerId}_current_{currentIndex:00}";

    private static string PositionId(string playerId, int currentIndex, string positionType) =>
        $"{CurrentId(playerId, currentIndex)}_{positionType}";
}
