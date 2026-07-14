import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
PLACEMENT_PATH = ENGINE_DIR / "entity_domain_placement.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
TRAJECTORY_PATH = ENGINE_DIR / "episode_trajectory.py"
KERNEL_PATH = AI_VS_AI_DIR / "rules_kernel.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"
INVARIANTS_PATH = AI_VS_AI_DIR / "state_invariants.py"
BOT_POLICY_PATH = AI_VS_AI_DIR / "bot_policy.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_PYTHON_DIR), str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestMinimalEntityDomainPlacementOptions(unittest.TestCase):
    def setUp(self):
        self.placement = _load_module("entity_domain_placement", PLACEMENT_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.trajectory = _load_module("episode_trajectory", TRAJECTORY_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.bot_policy = _load_module("bot_policy", BOT_POLICY_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        self.deck_id_a, self.deck_id_b = sorted(self.runtime_package.decks_by_id)[:2]

    def test_a_runtime_card_type_resolution_uses_exact_canonical_lookup(self):
        entity_definitions = [
            card
            for card in self.runtime_package.cards_by_id.values()
            if self._canonical_card_type(card) == self.placement.ENTITY_CANONICAL_CARD_TYPE
        ]
        non_entity_definitions = [
            card
            for card in self.runtime_package.cards_by_id.values()
            if self._canonical_card_type(card) != self.placement.ENTITY_CANONICAL_CARD_TYPE
        ]

        # A1-A3: the production schema is card_type and contains both kinds.
        self.assertEqual(self.placement.RUNTIME_CARD_TYPE_FIELD, "card_type")
        self.assertTrue(entity_definitions)
        self.assertTrue(non_entity_definitions)

        # A4: both raw "Entitás" and canonical "entity" resolve exactly to entity.
        state = self._create_state("PLACEMENT-CARD-TYPE-EXACT-001")
        source_id = self._find_instance(state, "entity", owner_player_id="P1")
        self._put_instance_in_hand(state, source_id, "P1")
        canonical_package = deepcopy(self.runtime_package)
        canonical_package.cards_by_id[state.card_instances[source_id]["card_id"]]["card_type"] = "entity"
        result = self._list(state, source_id, runtime_package=canonical_package)
        self.assertEqual(result["source_card_type"], "entity")
        self.assertTrue(result["source_eligible"])

        # A5: an Entity-looking display name cannot override a non-Entity card_type.
        state = self._create_state("PLACEMENT-CARD-TYPE-DISPLAY-001")
        source_id = self._find_instance(state, "incantation", owner_player_id="P1")
        self._put_instance_in_hand(state, source_id, "P1")
        display_package = deepcopy(self.runtime_package)
        card_id = state.card_instances[source_id]["card_id"]
        display_package.cards_by_id[card_id]["name_hu"] = "Entitásnak látszó név"
        result = self._list(state, source_id, runtime_package=display_package)
        self.assertFalse(result["source_eligible"])
        self.assertEqual(result["reason"], "source_card_type_not_entity")

        # A6: a missing definition is a controlled builder error.
        missing_package = deepcopy(self.runtime_package)
        missing_package.cards_by_id.pop(card_id)
        with self.assertRaises(self.placement.EntityDomainPlacementError) as context:
            self._list(state, source_id, runtime_package=missing_package)
        self.assertIn("RUNTIME_CARD_DEFINITION_MISSING", _exception_error_codes(context.exception))

    def test_b_eligible_entity_source_contract(self):
        state, source_id, result = self._eligible_result("PLACEMENT-ELIGIBLE-001")

        # B7-B14: a controlled hand Entity produces a valid source envelope.
        self.assertTrue(result["source_eligible"])
        self.assertIsInstance(result["source_card"], dict)
        self.assertEqual(result["source_card"]["zone"], "hand")
        self.assertEqual(result["source_card"]["controller_player_id"], "P1")
        self.assertEqual(result["source_card_type"], "entity")
        self.assertIsNone(result["reason"])
        self.assertEqual(result["target_player_id"], "P1")
        self.assertTrue(self.placement.validate_entity_domain_placement_options(result)["valid"])
        self.assertEqual(result["source_card"]["object_id"], source_id)
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_c_empty_domain_returns_twelve_deterministic_own_targets(self):
        _, _, result = self._eligible_result("PLACEMENT-EMPTY-001")
        options = result["options"]

        # C15-C17: exactly one horizon and zenith option per current.
        self.assertEqual(len(options), 12)
        self.assertEqual(sorted({option["target_current_index"] for option in options}), list(range(1, 7)))
        self.assertTrue(all(
            {option["target_position_type"] for option in options if option["target_current_index"] == index}
            == {"horizon", "zenith"}
            for index in range(1, 7)
        ))

        # C18-C21: an empty Domain exposes twelve available options and no reasons.
        self.assertTrue(all(option["structurally_available"] for option in options))
        self.assertTrue(all(option["unavailable_reason"] is None for option in options))
        self.assertEqual(result["structurally_available_count"], 12)
        self.assertEqual(result["structurally_unavailable_count"], 0)

        # C22-C26: order/identity are stable, unique, own-player, and exclude seals.
        self.assertEqual(
            [(option["target_current_index"], option["target_position_type"]) for option in options],
            [(index, row) for index in range(1, 7) for row in ("horizon", "zenith")],
        )
        self.assertEqual(len({option["option_id"] for option in options}), 12)
        self.assertEqual(len({option["target_position_id"] for option in options}), 12)
        self.assertFalse(any(option["target_position_type"] == "seal" for option in options))
        self.assertTrue(all(option["target_player_id"] == "P1" for option in options))

    def test_d_occupied_positions_remain_disabled_options_without_leaks(self):
        state, source_id, _ = self._eligible_result("PLACEMENT-OCCUPIED-001")
        first_occupant = self._occupy_slot(state, "P1", 0, excluded_ids={source_id})
        one_occupied = self._list(state, source_id)
        horizon = one_occupied["options"][0]

        # D27-D31: occupied horizon remains visible with 11/1 counts.
        self.assertEqual(horizon["target_position_type"], "horizon")
        self.assertFalse(horizon["structurally_available"])
        self.assertEqual(horizon["unavailable_reason"], "position_occupied")
        self.assertEqual(one_occupied["structurally_available_count"], 11)
        self.assertEqual(one_occupied["structurally_unavailable_count"], 1)

        second_occupant = self._occupy_slot(
            state,
            "P1",
            1,
            excluded_ids={source_id, first_occupant},
        )
        two_occupied = self._list(state, source_id)
        zenith = two_occupied["options"][1]

        # D32-D35: occupied zenith gives 10/2, leaks no occupant, and is retained.
        self.assertEqual(
            (zenith["target_position_type"], zenith["structurally_available"], zenith["unavailable_reason"]),
            ("zenith", False, "position_occupied"),
        )
        self.assertEqual(
            (
                two_occupied["structurally_available_count"],
                two_occupied["structurally_unavailable_count"],
            ),
            (10, 2),
        )
        self.assertFalse(_contains_value(two_occupied, first_occupant))
        self.assertFalse(_contains_value(two_occupied, second_occupant))
        self.assertEqual(len(two_occupied["options"]), 12)
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_e_ineligible_sources_return_empty_valid_contracts(self):
        # E36-E39: a hand non-Entity is a valid ineligible result with zero counts.
        state = self._create_state("PLACEMENT-INELIGIBLE-TYPE-001")
        non_entity_id = self._find_instance(state, "incantation", owner_player_id="P1")
        self._put_instance_in_hand(state, non_entity_id, "P1")
        non_entity = self._list(state, non_entity_id)
        self.assertFalse(non_entity["source_eligible"])
        self.assertEqual(non_entity["reason"], "source_card_type_not_entity")
        self.assertEqual(non_entity["options"], [])
        self.assertEqual(
            (
                non_entity["target_option_count"],
                non_entity["structurally_available_count"],
                non_entity["structurally_unavailable_count"],
            ),
            (0, 0, 0),
        )

        # E40: an instance controlled by P2 is ineligible for a P1 query.
        state = self._create_state("PLACEMENT-INELIGIBLE-CONTROLLER-001")
        p2_entity_id = self._find_instance(state, "entity", owner_player_id="P2")
        controller_result = self._list(state, p2_entity_id)
        self.assertEqual(controller_result["reason"], "source_not_controlled_by_player")

        # E41: an ordinary deck instance is not a hand source.
        state = self._create_state("PLACEMENT-INELIGIBLE-ZONE-001")
        deck_entity_id = self._find_instance(state, "entity", owner_player_id="P1")
        self.assertEqual(self._list(state, deck_entity_id)["reason"], "source_zone_not_hand")

        # E42: record says hand, but absence from the hand list is ineligible.
        state = self._create_state("PLACEMENT-INELIGIBLE-HAND-LIST-001")
        missing_list_id = self._find_instance(state, "entity", owner_player_id="P1")
        self._put_instance_in_hand(state, missing_list_id, "P1")
        state.get_player("P1").hand_card_instance_ids.remove(missing_list_id)
        self.assertEqual(self._list(state, missing_list_id)["reason"], "source_not_in_player_hand")

        # E43: hand membership cannot override a non-hand instance record.
        state = self._create_state("PLACEMENT-INELIGIBLE-RECORD-ZONE-001")
        wrong_zone_id = self._find_instance(state, "entity", owner_player_id="P1")
        self._put_instance_in_hand(state, wrong_zone_id, "P1")
        state.card_instances[wrong_zone_id]["zone"] = "deck"
        self.assertEqual(self._list(state, wrong_zone_id)["reason"], "source_zone_not_hand")

        # E44: owner P2/controller P1 in P1's hand remains eligible.
        state = self._create_state("PLACEMENT-CONTROLLED-OWNER-DIFFERS-001")
        controlled_id = self._find_instance(state, "entity", owner_player_id="P2")
        self._put_instance_in_hand(state, controlled_id, "P1", controller_player_id="P1")
        controlled = self._list(state, controlled_id)
        self.assertEqual(state.card_instances[controlled_id]["owner_player_id"], "P2")
        self.assertTrue(controlled["source_eligible"])
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_f_invalid_query_or_state_raises_controlled_builder_error(self):
        state, source_id, _ = self._eligible_result("PLACEMENT-INVALID-BASE-001")

        # F45-F46: unknown player and source are controlled errors.
        with self.assertRaises(self.placement.EntityDomainPlacementError) as player_error:
            self._list(state, source_id, player_id="P3")
        self.assertIn("PLAYER_UNKNOWN", _exception_error_codes(player_error.exception))
        with self.assertRaises(self.placement.EntityDomainPlacementError) as source_error:
            self._list(state, "ci_UNKNOWN_9999")
        self.assertIn("CARD_INSTANCE_UNKNOWN", _exception_error_codes(source_error.exception))

        # F47: missing occupancy fails before any partial contract can escape.
        missing_occupancy = deepcopy(state)
        missing_occupancy.domain_occupancies.pop("P1")
        with self.assertRaises(self.placement.EntityDomainPlacementError) as occupancy_error:
            self._list(missing_occupancy, source_id)
        self.assertIn("DOMAIN_OCCUPANCY_MISSING", _exception_error_codes(occupancy_error.exception))

        # F48: invalid topology is rejected through the canonical topology validator.
        invalid_topology = deepcopy(state)
        invalid_topology.domain_topologies["P1"]["current_count"] = 5
        with self.assertRaises(self.placement.EntityDomainPlacementError) as topology_error:
            self._list(invalid_topology, source_id)
        self.assertTrue(topology_error.exception.errors)

        # F49: unrelated MatchState invariant failures are never hidden.
        invalid_state = deepcopy(state)
        invalid_state.active_player_id = "P3"
        with self.assertRaises(self.placement.EntityDomainPlacementError) as invariant_error:
            self._list(invalid_state, source_id)
        self.assertIn("ACTIVE_PLAYER_UNKNOWN", _exception_error_codes(invariant_error.exception))

        # F50: source card definition must exist in the supplied runtime package.
        missing_package = deepcopy(self.runtime_package)
        missing_package.cards_by_id.pop(state.card_instances[source_id]["card_id"])
        with self.assertRaises(self.placement.EntityDomainPlacementError) as runtime_error:
            self._list(state, source_id, runtime_package=missing_package)
        self.assertIn("RUNTIME_CARD_DEFINITION_MISSING", _exception_error_codes(runtime_error.exception))

        # F51: all failures are exceptions, never partial options dicts.
        self.assertTrue(all(
            isinstance(error.exception, self.placement.EntityDomainPlacementError)
            for error in (player_error, source_error, occupancy_error, topology_error, invariant_error, runtime_error)
        ))

    def test_g_single_option_validator_contract(self):
        empty = self._valid_option("empty")
        occupied = self._valid_option("occupied")

        # G52-G53: canonical empty and occupied options validate.
        self.assertTrue(self.placement.validate_entity_domain_placement_option(empty)["valid"])
        self.assertTrue(self.placement.validate_entity_domain_placement_option(occupied)["valid"])

        cases = []
        invalid = deepcopy(empty); invalid["source_zone"] = "deck"
        cases.append(("SOURCE_ZONE_INVALID", invalid))  # G54
        invalid = deepcopy(empty); invalid["target_player_id"] = "P2"
        cases.append(("TARGET_PLAYER_MISMATCH", invalid))  # G55
        invalid = deepcopy(empty); invalid["target_current_index"] = 0
        cases.append(("CURRENT_INDEX_INVALID", invalid))  # G56
        invalid = deepcopy(empty); invalid["target_current_index"] = 7
        cases.append(("CURRENT_INDEX_INVALID", invalid))  # G57
        invalid = deepcopy(empty); invalid["target_current_index"] = True
        cases.append(("CURRENT_INDEX_INVALID", invalid))  # G58
        invalid = deepcopy(empty); invalid["target_position_type"] = "seal"; invalid["target_row"] = "seal"
        cases.append(("TARGET_POSITION_TYPE_INVALID", invalid))  # G59
        invalid = deepcopy(empty); invalid["target_row"] = "zenith"
        cases.append(("TARGET_ROW_INVALID", invalid))  # G60
        invalid = deepcopy(empty); invalid["target_position_id"] = "domain_P1_current_99_horizon"
        cases.append(("TARGET_POSITION_ID_MISMATCH", invalid))  # G61
        invalid = deepcopy(empty); invalid["structurally_available"] = False
        cases.append(("STRUCTURAL_AVAILABILITY_INVALID", invalid))  # G62
        invalid = deepcopy(occupied); invalid["structurally_available"] = True
        cases.append(("STRUCTURAL_AVAILABILITY_INVALID", invalid))  # G63
        invalid = deepcopy(occupied); invalid["unavailable_reason"] = "wrong"
        cases.append(("UNAVAILABLE_REASON_INVALID", invalid))  # G64
        invalid = deepcopy(empty); invalid["option_id"] = "wrong"
        cases.append(("OPTION_ID_MISMATCH", invalid))  # G65
        cases.append(("OPTION_NOT_DICT", None))  # G66

        for expected_code, invalid in cases:
            with self.subTest(expected_code=expected_code):
                result = self.placement.validate_entity_domain_placement_option(invalid)
                self.assertFalse(result["valid"], result)
                self.assertIn(expected_code, _error_codes(result), result)
                json.dumps(result, ensure_ascii=False)

    def test_h_options_validator_contract(self):
        _, _, eligible = self._eligible_result("PLACEMENT-OPTIONS-VALIDATOR-001")
        _, _, ineligible = self._non_entity_result("PLACEMENT-OPTIONS-INELIGIBLE-001")

        # H67-H68: builder-produced eligible and ineligible envelopes validate.
        self.assertTrue(self.placement.validate_entity_domain_placement_options(eligible)["valid"])
        self.assertTrue(self.placement.validate_entity_domain_placement_options(ineligible)["valid"])

        cases = []
        invalid = deepcopy(eligible); invalid["options"].pop(); _sync_counts(invalid)
        cases.append(("TARGET_OPTION_COUNT_INVALID", invalid))  # H69
        invalid = deepcopy(eligible); invalid["options"][1]["option_id"] = invalid["options"][0]["option_id"]
        cases.append(("OPTION_ID_DUPLICATE", invalid))  # H70
        invalid = deepcopy(eligible)
        invalid["options"][1]["target_position_id"] = invalid["options"][0][
            "target_position_id"
        ]
        cases.append(("TARGET_POSITION_ID_DUPLICATE", invalid))  # H71
        invalid = deepcopy(eligible)
        invalid["options"] = [
            option
            for option in invalid["options"]
            if option["target_current_index"] != 6
        ]
        _sync_counts(invalid)
        cases.append(("TARGET_POSITION_SET_INVALID", invalid))  # H72
        invalid = deepcopy(eligible)
        extra = deepcopy(invalid["options"][0])
        extra["target_position_type"] = "seal"
        extra["target_row"] = "seal"
        extra["target_position_id"] = "domain_P1_current_01_seal"
        extra["option_id"] = "place_%s_to_%s" % (
            extra["source_card_instance_id"],
            extra["target_position_id"],
        )
        invalid["options"].append(extra)
        _sync_counts(invalid)
        cases.append(("TARGET_POSITION_SET_INVALID", invalid))  # H73
        invalid = deepcopy(eligible)
        option = invalid["options"][0]
        option["player_id"] = "P2"
        option["target_player_id"] = "P2"
        option["target_position_id"] = "domain_P2_current_01_horizon"
        option["option_id"] = "place_%s_to_%s" % (
            option["source_card_instance_id"],
            option["target_position_id"],
        )
        cases.append(("OPTION_RECORD_INVALID", invalid))  # H74
        invalid = deepcopy(eligible); invalid["structurally_available_count"] = 11
        cases.append(("COUNT_MISMATCH", invalid))  # H75
        invalid = deepcopy(eligible); invalid["source_card_type"] = "incantation"
        cases.append(("SOURCE_CARD_TYPE_INVALID", invalid))  # H76
        invalid = deepcopy(ineligible); invalid["reason"] = None
        cases.append(("SOURCE_REASON_INVALID", invalid))  # H77
        invalid = deepcopy(ineligible); invalid["options"] = [deepcopy(eligible["options"][0])]; _sync_counts(invalid)
        cases.append(("OPTIONS_INVALID", invalid))  # H78
        invalid = deepcopy(eligible); invalid.pop("unchecked_requirements")
        cases.append(("UNCHECKED_REQUIREMENTS_INVALID", invalid))  # H79
        invalid = deepcopy(eligible); invalid["metadata"]["full_play_legality"] = True
        cases.append(("METADATA_INVALID", invalid))  # H80
        invalid = deepcopy(eligible); invalid["legal"] = True
        cases.append(("FULL_LEGALITY_CLAIM_INVALID", invalid))  # H81

        for expected_code, invalid in cases:
            with self.subTest(expected_code=expected_code):
                result = self.placement.validate_entity_domain_placement_options(invalid)
                self.assertFalse(result["valid"], result)
                self.assertIn(expected_code, _error_codes(result), result)
                json.dumps(result, ensure_ascii=False)

    def test_i_builder_is_detached_and_deterministic(self):
        state, source_id, first = self._eligible_result("PLACEMENT-DEEPCOPY-001")
        topology_before = deepcopy(state.domain_topologies)
        occupancy_before = deepcopy(state.domain_occupancies)
        registry_before = deepcopy(state.card_instances)

        # I82-I84: mutating returned structures cannot affect authoritative state.
        first["options"][0]["target_position_id"] = "mutated"
        self.assertEqual(state.domain_topologies, topology_before)
        first["options"][0]["target_occupancy_state"] = "occupied"
        self.assertEqual(state.domain_occupancies, occupancy_before)
        first["source_card"]["zone"] = "deck"
        self.assertEqual(state.card_instances, registry_before)

        second = self._list(state, source_id)
        third = self._list(state, source_id)

        # I85-I87: calls and option metadata are detached; identical input is identical JSON.
        self.assertIsNot(second["options"], third["options"])
        self.assertIsNot(second["options"][0]["metadata"], second["options"][1]["metadata"])
        self.assertEqual(_json(second), _json(third))

        # I88-I89: match_id is the only match-specific field and never enters option IDs.
        other_state, other_source_id, other = self._eligible_result("PLACEMENT-DEEPCOPY-OTHER")
        self.assertEqual(source_id, other_source_id)
        second_without_match = deepcopy(second); second_without_match.pop("match_id")
        other_without_match = deepcopy(other); other_without_match.pop("match_id")
        self.assertEqual(second_without_match, other_without_match)
        self.assertTrue(all("PLACEMENT-DEEPCOPY" not in option["option_id"] for option in other["options"]))

    def test_j_helper_has_no_runtime_action_or_snapshot_integration(self):
        state, source_id, _ = self._eligible_result("PLACEMENT-NO-INTEGRATION-001")
        legal_before = deepcopy(self.kernel.list_legal_actions(state))
        priorities_before = dict(self.bot_policy.ACTION_PRIORITIES)
        state_before = deepcopy(state)
        result = self._list(state, source_id)
        legal_after = self.kernel.list_legal_actions(state)

        # J90-J94: legal actions, action space, bot policy, draw, and end_turn remain unchanged.
        self.assertEqual(legal_after, legal_before)
        self.assertNotIn("entity_domain_placement", {action["action_type"] for action in legal_after})
        self.assertEqual(self.bot_policy.ACTION_PRIORITIES, priorities_before)
        self.assertEqual([action["action_type"] for action in legal_after], ["end_turn", "draw_card"])
        self.assertTrue(all(action["enabled"] for action in legal_after))

        # J95-J98: querying changes no version, events, occupancy, or hand.
        self.assertEqual(state.state_version, state_before.state_version)
        self.assertEqual(state.event_log, state_before.event_log)
        self.assertEqual(state.domain_occupancies, state_before.domain_occupancies)
        self.assertEqual(
            state.get_player("P1").hand_card_instance_ids,
            state_before.get_player("P1").hand_card_instance_ids,
        )

        # J99-J100: snapshot and trajectory schemas remain untouched and absent from output.
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(
            deck_id_a=self.deck_id_a,
            deck_id_b=self.deck_id_b,
            match_id="PLACEMENT-SNAPSHOT-UNCHANGED-001",
        )
        session_source = self._find_instance(session.state, "entity", owner_player_id="P1")
        self._put_instance_in_hand(session.state, session_source, "P1")
        snapshot_before = session.get_player_snapshot("P1")
        self.placement.list_structural_entity_domain_placement_options(
            session.state, self.runtime_package, "P1", session_source
        )
        snapshot_after = session.get_player_snapshot("P1")
        self.assertEqual(snapshot_before["schema_version"], "engine-player-visible-snapshot-v2")
        self.assertEqual(snapshot_after, snapshot_before)
        self.assertEqual(self.trajectory.EPISODE_STEP_SCHEMA_VERSION, "minimal-episode-step-v0")
        self.assertFalse(_contains_key(result, "trajectory"))

    def test_k_output_excludes_forbidden_data_and_full_legality_claims(self):
        _, _, result = self._eligible_result("PLACEMENT-FORBIDDEN-DATA-001")

        # K101-K104: no complete runtime, instance, topology, or occupancy record leaks.
        self.assertFalse(any(_contains_key(result, key) for key in ("name_hu", "structured_ability", "aura_cost")))
        self.assertFalse(any(_contains_key(result, key) for key in ("owner_player_id", "created_sequence")))
        self.assertFalse(any(_contains_key(result, key) for key in ("currents", "positions", "current_count")))
        self.assertFalse(any(_contains_key(result, key) for key in ("slots", "occupant_card_instance_id", "occupant")))

        # K105-K109: no request/response/event/payment/timing result is emitted.
        self.assertFalse(_contains_key(result, "action_request"))
        self.assertFalse(_contains_key(result, "action_response"))
        self.assertFalse(any(_contains_key(result, key) for key in ("event", "events", "event_log")))
        self.assertFalse(any(_contains_key(result, key) for key in ("payment_result", "payment_valid")))
        self.assertFalse(any(_contains_key(result, key) for key in ("timing_result", "timing_valid")))

        # K110-K111: the contract denies full legality and implements no play_card action.
        self.assertFalse(result["metadata"]["full_play_legality"])
        self.assertFalse(any(
            isinstance(value, dict) and value.get("legal") is True
            for value in _walk_values(result)
        ))
        self.assertEqual(result["metadata"]["play_card_integration"], "not_implemented")
        self.assertFalse(any(option.get("action_type") == "play_card" for option in result["options"]))

    def _create_state(self, match_id):
        return self.kernel.create_initial_match_state(
            self.runtime_package,
            self.deck_id_a,
            self.deck_id_b,
            match_id=match_id,
        )

    def _list(self, state, source_id, player_id="P1", runtime_package=None):
        return self.placement.list_structural_entity_domain_placement_options(
            state,
            runtime_package or self.runtime_package,
            player_id,
            source_id,
        )

    def _eligible_result(self, match_id):
        state = self._create_state(match_id)
        source_id = self._find_instance(state, "entity", owner_player_id="P1")
        self._put_instance_in_hand(state, source_id, "P1")
        return state, source_id, self._list(state, source_id)

    def _non_entity_result(self, match_id):
        state = self._create_state(match_id)
        source_id = self._find_instance(state, "incantation", owner_player_id="P1")
        self._put_instance_in_hand(state, source_id, "P1")
        return state, source_id, self._list(state, source_id)

    def _canonical_card_type(self, card_definition):
        raw_value = card_definition["card_type"]
        values = {
            lookup["canonical_value"]
            for lookup in self.runtime_package.lookups
            if lookup.get("lookup_group") == "card_type"
            and lookup.get("status") == "active"
            and lookup.get("value") == raw_value
        }
        self.assertEqual(len(values), 1, (raw_value, values))
        return next(iter(values))

    def _find_instance(self, state, canonical_type, owner_player_id=None, excluded_ids=None):
        excluded_ids = set(excluded_ids or [])
        for card_instance_id in sorted(state.card_instances):
            record = state.card_instances[card_instance_id]
            if card_instance_id in excluded_ids:
                continue
            if owner_player_id is not None and record.get("owner_player_id") != owner_player_id:
                continue
            card = self.runtime_package.get_card(record["card_id"])
            if self._canonical_card_type(card) == canonical_type:
                return card_instance_id
        self.fail("No %s card instance found." % canonical_type)

    def _put_instance_in_hand(self, state, card_instance_id, player_id, controller_player_id=None):
        self._remove_instance_from_list_zones(state, card_instance_id)
        player = state.get_player(player_id)
        player.hand_card_instance_ids.append(card_instance_id)
        record = state.card_instances[card_instance_id]
        record["zone"] = "hand"
        record["zone_index"] = len(player.hand_card_instance_ids) - 1
        record["visibility"] = "owner_only"
        record["controller_player_id"] = controller_player_id or player_id
        record["zone_sequence"] += 1

    def _occupy_slot(self, state, player_id, slot_index, excluded_ids=None):
        occupant_id = next(
            card_instance_id
            for card_instance_id in sorted(state.card_instances)
            if card_instance_id not in set(excluded_ids or [])
            and state.card_instances[card_instance_id]["zone"] in ("deck", "hand", "discard")
        )
        self._remove_instance_from_list_zones(state, occupant_id)
        record = state.card_instances[occupant_id]
        record["zone"] = "domain"
        record["zone_index"] = None
        record["visibility"] = "public"
        record["controller_player_id"] = player_id
        record["zone_sequence"] += 1
        slot = state.domain_occupancies[player_id]["slots"][slot_index]
        slot["occupancy_state"] = "occupied"
        slot["occupant_object_type"] = "card_instance"
        slot["occupant_card_instance_id"] = occupant_id
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])
        return occupant_id

    @staticmethod
    def _remove_instance_from_list_zones(state, card_instance_id):
        for player in state.players:
            for zone_name in ("deck", "hand", "discard"):
                zone = getattr(player, "%s_card_instance_ids" % zone_name)
                while card_instance_id in zone:
                    zone.remove(card_instance_id)
                for zone_index, remaining_id in enumerate(zone):
                    state.card_instances[remaining_id]["zone"] = zone_name
                    state.card_instances[remaining_id]["zone_index"] = zone_index

    def _valid_option(self, occupancy_state):
        position_id = "domain_P1_current_01_horizon"
        return self.placement.create_entity_domain_placement_option(
            player_id="P1",
            source_card_instance_id="ci_P1_0001",
            target_player_id="P1",
            target_position_id=position_id,
            target_current_index=1,
            target_position_type="horizon",
            target_occupancy_state=occupancy_state,
        )


def _sync_counts(record):
    options = record["options"]
    record["target_option_count"] = len(options)
    record["structurally_available_count"] = sum(
        option.get("structurally_available") is True for option in options
    )
    record["structurally_unavailable_count"] = sum(
        option.get("structurally_available") is False for option in options
    )


def _error_codes(result):
    return {error.get("code") for error in result.get("errors", [])}


def _exception_error_codes(exception):
    return {error.get("code") for error in getattr(exception, "errors", [])}


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _contains_key(value, target_key):
    if isinstance(value, dict):
        return target_key in value or any(_contains_key(nested, target_key) for nested in value.values())
    if isinstance(value, list):
        return any(_contains_key(nested, target_key) for nested in value)
    return False


def _contains_value(value, target_value):
    if value == target_value:
        return True
    if isinstance(value, dict):
        return any(_contains_value(nested, target_value) for nested in value.values())
    if isinstance(value, list):
        return any(_contains_value(nested, target_value) for nested in value)
    return False


def _walk_values(value):
    yield value
    if isinstance(value, dict):
        for nested in value.values():
            yield from _walk_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_values(nested)


if __name__ == "__main__":
    unittest.main()
