import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
DOMAIN_POSITION_PATH = ENGINE_DIR / "domain_position.py"
DOMAIN_OCCUPANCY_PATH = ENGINE_DIR / "domain_occupancy.py"
ENVIRONMENT_PATH = ENGINE_DIR / "minimal_engine_environment.py"
PLAYER_SNAPSHOT_PATH = ENGINE_DIR / "player_visible_snapshot.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
INVARIANTS_PATH = AI_VS_AI_DIR / "state_invariants.py"
KERNEL_PATH = AI_VS_AI_DIR / "rules_kernel.py"
MATCH_STATE_PATH = AI_VS_AI_DIR / "match_state.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _error_codes(errors):
    return {error.get("code") for error in errors}


def _contains_key(value, key):
    if isinstance(value, dict):
        return key in value or any(_contains_key(nested, key) for nested in value.values())
    if isinstance(value, list):
        return any(_contains_key(nested, key) for nested in value)
    return False


def _contains_contract_type(value, contract_type):
    if isinstance(value, dict):
        if value.get("contract_type") == contract_type:
            return True
        return any(_contains_contract_type(nested, contract_type) for nested in value.values())
    if isinstance(value, list):
        return any(_contains_contract_type(nested, contract_type) for nested in value)
    return False


class TestMinimalMatchStateDomainOccupancy(unittest.TestCase):
    def setUp(self):
        self.match_state = _load_module("match_state", MATCH_STATE_PATH)
        self.domain_position = _load_module("domain_position", DOMAIN_POSITION_PATH)
        self.domain_occupancy = _load_module("domain_occupancy", DOMAIN_OCCUPANCY_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.player_snapshot = _load_module("player_visible_snapshot", PLAYER_SNAPSHOT_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.environment_module = _load_module("minimal_engine_environment", ENVIRONMENT_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        self.deck_id_a, self.deck_id_b = _pick_two_decks(self.runtime_package)

    def test_a_production_initial_setup_has_two_empty_valid_occupancies(self):
        state = self._create_state("DOMAIN-OCCUPANCY-SETUP-001")

        # A1-A7: production setup owns one canonical occupancy per player/topology.
        self.assertTrue(hasattr(state, "domain_occupancies"))
        self.assertIsInstance(state.domain_occupancies, dict)
        self.assertEqual(set(state.domain_occupancies), {"P1", "P2"})
        self.assertIn("P1", state.domain_occupancies)
        self.assertIn("P2", state.domain_occupancies)
        self.assertEqual(state.domain_occupancies["P1"]["player_id"], "P1")
        self.assertEqual(state.domain_occupancies["P2"]["player_id"], "P2")
        for player_id in ("P1", "P2"):
            validation = self.domain_occupancy.validate_player_domain_occupancy(
                state.domain_occupancies[player_id],
                state.domain_topologies[player_id],
            )
            self.assertTrue(validation["valid"], validation)

        # A8-A14: both players start with twelve empty non-seal slots and no Domain instance.
        for occupancy in state.domain_occupancies.values():
            self.assertEqual(len(occupancy["slots"]), 12)
            self.assertTrue(all(slot["occupancy_state"] == "empty" for slot in occupancy["slots"]))
            self.assertTrue(
                all(slot["occupant_card_instance_id"] is None for slot in occupancy["slots"])
            )
            self.assertFalse(any(slot["position_type"] == "seal" for slot in occupancy["slots"]))
        self.assertFalse(any(record["zone"] == "domain" for record in state.card_instances.values()))
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])
        json.dumps(state.domain_occupancies, ensure_ascii=False)

    def test_b_lookup_is_controlled_and_deeply_detached(self):
        state = self._create_state("DOMAIN-OCCUPANCY-LOOKUP-001")

        # B15-B18: both player lookups work and invalid/missing records fail controllably.
        self.assertEqual(state.get_domain_occupancy("P1")["player_id"], "P1")
        self.assertEqual(state.get_domain_occupancy("P2")["player_id"], "P2")
        with self.assertRaisesRegex(self.match_state.MatchStateError, "Unknown player_id"):
            state.get_domain_occupancy("P3")
        state.domain_occupancies.pop("P1")
        with self.assertRaisesRegex(self.match_state.MatchStateError, "Missing Domain occupancy"):
            state.get_domain_occupancy("P1")
        state = self._create_state("DOMAIN-OCCUPANCY-LOOKUP-NULL-001")
        state.domain_occupancies["P1"] = None
        with self.assertRaisesRegex(self.match_state.MatchStateError, "Missing Domain occupancy"):
            state.get_domain_occupancy("P1")

        # B19-B21: top-level, slot, and nested metadata are not authoritative references.
        state = self._create_state("DOMAIN-OCCUPANCY-LOOKUP-COPY-001")
        lookup = state.get_domain_occupancy("P1")
        self.assertIsNot(lookup, state.domain_occupancies["P1"])
        lookup["slots"][0]["occupancy_state"] = "occupied"
        lookup["slots"][0]["metadata"]["source"] = "mutated"
        self.assertEqual(state.domain_occupancies["P1"]["slots"][0]["occupancy_state"], "empty")
        self.assertEqual(
            state.domain_occupancies["P1"]["slots"][0]["metadata"]["source"],
            "python.engine.domain_occupancy",
        )

    def test_c_draw_and_end_turn_leave_occupancies_unchanged(self):
        session = self._create_session("DOMAIN-OCCUPANCY-RUNTIME-STABILITY-001")
        state = session.state
        before = copy.deepcopy(state.domain_occupancies)
        p1_slots = state.domain_occupancies["P1"]["slots"]
        p2_slots = state.domain_occupancies["P2"]["slots"]
        p1_metadata = state.domain_occupancies["P1"]["slots"][0]["metadata"]

        # C22-C26: the existing P1/P2 draw and end-turn flow never mutates occupancy.
        responses = [
            self._submit_action(session, "draw_card"),
            self._submit_action(session, "end_turn"),
            self._submit_action(session, "draw_card"),
            self._submit_action(session, "end_turn"),
        ]
        self.assertEqual(state.domain_occupancies, before)
        self.assertEqual(state.domain_occupancies["P1"], before["P1"])
        self.assertEqual(state.domain_occupancies["P2"], before["P2"])
        self.assertEqual(state.domain_occupancies, before)
        self.assertEqual(state.domain_occupancies["P1"]["slots"][0]["metadata"], before["P1"]["slots"][0]["metadata"])

        # C27-C31: no occupancy event/regeneration occurs; existing typed events and versions remain stable.
        self.assertEqual(
            [event["event_type"] for event in state.event_log],
            ["zone_move", "turn_transition", "zone_move", "turn_transition"],
        )
        self.assertIs(state.domain_occupancies["P1"]["slots"], p1_slots)
        self.assertIs(state.domain_occupancies["P2"]["slots"], p2_slots)
        self.assertIs(state.domain_occupancies["P1"]["slots"][0]["metadata"], p1_metadata)
        self.assertEqual([response["state_version_after"] for response in responses], [1, 2, 3, 4])
        self.assertEqual(session.get_diagnostics(), [])

    def test_d_valid_synthetic_occupied_state_is_bidirectionally_consistent(self):
        state = self._create_state("DOMAIN-OCCUPANCY-SYNTHETIC-VALID-001")
        topology_before = copy.deepcopy(state.domain_topologies)

        # D32-D41: one test-only occupied horizon binding has canonical registry values.
        first_id = self._make_synthetic_domain_binding(state, "P1", slot_index=0)
        first_slot = state.domain_occupancies["P1"]["slots"][0]
        first_record = state.card_instances[first_id]
        self.assertEqual(first_slot["occupancy_state"], "occupied")
        self.assertIn(first_id, state.card_instances)
        self.assertNotIn(first_id, self._all_list_zone_ids(state))
        self.assertEqual(first_record["zone"], "domain")
        self.assertIsNone(first_record["zone_index"])
        self.assertEqual(first_record["visibility"], "public")
        self.assertEqual(first_record["controller_player_id"], "P1")
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])
        self.assertEqual(state.domain_topologies, topology_before)
        self.assertTrue(
            self.domain_occupancy.validate_player_domain_occupancy(
                state.domain_occupancies["P1"], state.domain_topologies["P1"]
            )["valid"]
        )

        # D42: a different instance may occupy a different P1 slot.
        second_id = self._make_synthetic_domain_binding(state, "P1", slot_index=1)
        self.assertNotEqual(first_id, second_id)
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_e_domain_binding_uses_controller_not_owner(self):
        # E43: ordinary owner/controller P1 binding is valid.
        own_state = self._create_state("DOMAIN-OCCUPANCY-OWNER-CONTROLLER-001")
        own_id = self._make_synthetic_domain_binding(own_state, "P1", source_player_id="P1")
        self.assertEqual(own_state.card_instances[own_id]["owner_player_id"], "P1")
        self.assertEqual(self.invariants.validate_state_invariants(own_state, self.runtime_package), [])

        # E44: owner P2 with controller P1 is valid in P1 Domain.
        controlled_state = self._create_state("DOMAIN-OCCUPANCY-CONTROLLED-001")
        controlled_id = self._make_synthetic_domain_binding(
            controlled_state,
            "P1",
            source_player_id="P2",
            controller_player_id="P1",
        )
        self.assertEqual(controlled_state.card_instances[controlled_id]["owner_player_id"], "P2")
        self.assertEqual(controlled_state.card_instances[controlled_id]["controller_player_id"], "P1")
        self.assertEqual(self.invariants.validate_state_invariants(controlled_state, self.runtime_package), [])

        # E45-E46: wrong or unknown controller is rejected.
        wrong_controller = self._create_state("DOMAIN-OCCUPANCY-WRONG-CONTROLLER")
        self._make_synthetic_domain_binding(
            wrong_controller, "P1", controller_player_id="P2"
        )
        self.assertInvariantCode(wrong_controller, "DOMAIN_OCCUPANT_CONTROLLER_MISMATCH")
        unknown_controller = self._create_state("DOMAIN-OCCUPANCY-UNKNOWN-CONTROLLER")
        self._make_synthetic_domain_binding(
            unknown_controller, "P1", controller_player_id="P3"
        )
        self.assertInvariantCode(unknown_controller, "DOMAIN_OCCUPANT_CONTROLLER_UNKNOWN")

    def test_f_invalid_occupants_report_structured_diagnostics(self):
        # F47: unknown occupant identity is visible at MatchState level.
        unknown = self._create_state("DOMAIN-OCCUPANCY-UNKNOWN-INSTANCE")
        self._set_slot_occupied(unknown, "P1", 0, "ci_UNKNOWN_9999")
        self.assertInvariantCode(unknown, "DOMAIN_OCCUPANT_INSTANCE_UNKNOWN")

        # F48-F49: malformed occupied slot identity remains in nested contract diagnostics.
        missing_id = self._create_state("DOMAIN-OCCUPANCY-MISSING-ID")
        self._set_slot_occupied(missing_id, "P1", 0, None)
        self.assertNestedOccupancyCode(missing_id, "OCCUPIED_OCCUPANCY_MISSING_OCCUPANT")
        wrong_type = self._create_state("DOMAIN-OCCUPANCY-WRONG-TYPE")
        self._set_slot_occupied(wrong_type, "P1", 0, "ci_UNKNOWN_9999", "card_definition")
        self.assertNestedOccupancyCode(wrong_type, "OCCUPANT_OBJECT_TYPE_INVALID")

        # F50-F52: Domain registry zone, index, and visibility are explicit invariants.
        wrong_zone = self._create_state("DOMAIN-OCCUPANCY-WRONG-ZONE")
        wrong_zone_id = self._make_synthetic_domain_binding(wrong_zone, "P1")
        wrong_zone.card_instances[wrong_zone_id]["zone"] = "deck"
        self.assertInvariantCode(wrong_zone, "DOMAIN_OCCUPANT_ZONE_MISMATCH")
        wrong_index = self._create_state("DOMAIN-OCCUPANCY-WRONG-INDEX")
        wrong_index_id = self._make_synthetic_domain_binding(wrong_index, "P1")
        wrong_index.card_instances[wrong_index_id]["zone_index"] = 0
        self.assertInvariantCode(wrong_index, "DOMAIN_OCCUPANT_ZONE_INDEX_INVALID")
        wrong_visibility = self._create_state("DOMAIN-OCCUPANCY-WRONG-VISIBILITY")
        wrong_visibility_id = self._make_synthetic_domain_binding(wrong_visibility, "P1")
        wrong_visibility.card_instances[wrong_visibility_id]["visibility"] = "owner_only"
        self.assertInvariantCode(wrong_visibility, "DOMAIN_OCCUPANT_VISIBILITY_INVALID")

        # F53: seal positions cannot leak into occupied Domain slots.
        seal_state = self._create_state("DOMAIN-OCCUPANCY-SEAL-LEAK")
        self._make_synthetic_domain_binding(seal_state, "P1")
        seal_reference = next(
            position
            for position in seal_state.domain_topologies["P1"]["positions"]
            if position["position_type"] == "seal"
        )
        seal_state.domain_occupancies["P1"]["slots"][0].update(
            {
                "position_id": seal_reference["position_id"],
                "current_index": seal_reference["current_index"],
                "position_type": "seal",
                "row": None,
            }
        )
        self.assertInvariantCode(seal_state, "DOMAIN_OCCUPANT_SEAL_POSITION_INVALID")

    def test_g_authoritative_zone_membership_includes_domain_slots(self):
        # G54-G56: deck, hand, or discard plus Domain is a multiple-zone violation.
        for zone_name in ("deck", "hand", "discard"):
            with self.subTest(zone_name=zone_name):
                state = self._create_state("DOMAIN-OCCUPANCY-LIST-OVERLAP-%s" % zone_name)
                card_instance_id = self._put_instance_in_list_zone(state, "P1", zone_name)
                self._bind_without_list_removal(state, "P1", 0, card_instance_id)
                self.assertInvariantCode(state, "CARD_INSTANCE_MULTIPLE_ZONES")

        # G57-G58: duplicate occupancy is global across slots and players.
        duplicate_p1 = self._create_state("DOMAIN-OCCUPANCY-DUPLICATE-P1")
        duplicate_id = self._make_synthetic_domain_binding(duplicate_p1, "P1", slot_index=0)
        self._set_slot_occupied(duplicate_p1, "P1", 1, duplicate_id)
        self.assertInvariantCode(duplicate_p1, "DOMAIN_OCCUPANT_INSTANCE_DUPLICATE")
        duplicate_players = self._create_state("DOMAIN-OCCUPANCY-DUPLICATE-PLAYERS")
        cross_id = self._make_synthetic_domain_binding(duplicate_players, "P1", slot_index=0)
        self._set_slot_occupied(duplicate_players, "P2", 0, cross_id)
        self.assertInvariantCode(duplicate_players, "DOMAIN_OCCUPANT_INSTANCE_DUPLICATE")

        # G59-G60: existing list/list overlap remains invalid; repeated null occupants remain valid.
        list_overlap = self._create_state("DOMAIN-OCCUPANCY-LIST-LIST-OVERLAP")
        list_id = list_overlap.get_player("P1").deck_card_instance_ids[0]
        list_overlap.get_player("P1").hand_card_instance_ids.append(list_id)
        self.assertInvariantCode(list_overlap, "CARD_INSTANCE_MULTIPLE_ZONES")
        empty_state = self._create_state("DOMAIN-OCCUPANCY-EMPTY-NULLS")
        self.assertEqual(self.invariants.validate_state_invariants(empty_state, self.runtime_package), [])

    def test_h_registry_and_occupancy_relationship_is_bidirectional(self):
        # H61: occupied slot requires a registry record.
        missing_record = self._create_state("DOMAIN-OCCUPANCY-MISSING-RECORD")
        missing_id = missing_record.get_player("P1").deck_card_instance_ids[0]
        self._remove_instance_from_lists(missing_record, missing_id)
        missing_record.card_instances.pop(missing_id)
        self._set_slot_occupied(missing_record, "P1", 0, missing_id)
        self.assertInvariantCode(missing_record, "DOMAIN_OCCUPANT_INSTANCE_UNKNOWN")

        # H62-H63: a Domain-zoned registry record requires one occupied slot.
        unbound = self._create_state("DOMAIN-OCCUPANCY-UNBOUND-RECORD")
        unbound_id = unbound.get_player("P1").deck_card_instance_ids[0]
        self._make_unbound_domain_record(unbound, unbound_id, "P1")
        self.assertInvariantCode(unbound, "DOMAIN_CARD_INSTANCE_UNBOUND")
        self.assertInvariantCode(unbound, "CARD_INSTANCE_ORPHANED")

        # H64-H65: non-Domain occupant is rejected; correct two-way binding is valid.
        non_domain = self._create_state("DOMAIN-OCCUPANCY-NON-DOMAIN-RECORD")
        non_domain_id = self._make_synthetic_domain_binding(non_domain, "P1")
        non_domain.card_instances[non_domain_id]["zone"] = "hand"
        self.assertInvariantCode(non_domain, "DOMAIN_OCCUPANT_ZONE_MISMATCH")
        valid = self._create_state("DOMAIN-OCCUPANCY-BIDIRECTIONAL-VALID")
        valid_id = self._make_synthetic_domain_binding(valid, "P1")
        self.assertEqual(self.invariants.validate_state_invariants(valid, self.runtime_package), [])

        # H66-H67: position identity is authoritative only in occupancy, never the instance record.
        slot = valid.domain_occupancies["P1"]["slots"][0]
        self.assertTrue(slot["position_id"])
        self.assertNotIn("position_id", valid.card_instances[valid_id])

    def test_i_occupancy_container_invariants_preserve_nested_errors(self):
        # I68: absent and non-dict containers have dedicated diagnostics.
        missing_container = self._create_state("DOMAIN-OCCUPANCY-MISSING-CONTAINER")
        del missing_container.domain_occupancies
        self.assertInvariantCode(missing_container, "DOMAIN_OCCUPANCIES_MISSING")
        invalid_container = self._create_state("DOMAIN-OCCUPANCY-INVALID-CONTAINER")
        invalid_container.domain_occupancies = []
        self.assertInvariantCode(invalid_container, "DOMAIN_OCCUPANCIES_INVALID")
        empty_container = self._create_state("DOMAIN-OCCUPANCY-EMPTY-CONTAINER")
        empty_container.domain_occupancies = {}
        self.assertInvariantCode(empty_container, "DOMAIN_OCCUPANCY_MISSING")
        invalid_record = self._create_state("DOMAIN-OCCUPANCY-INVALID-RECORD")
        invalid_record.domain_occupancies["P1"] = None
        self.assertInvariantCode(invalid_record, "DOMAIN_OCCUPANCY_RECORD_INVALID")

        # I69-I72: player set, registry key, and topology relation are guarded.
        missing_p2 = self._create_state("DOMAIN-OCCUPANCY-MISSING-P2")
        missing_p2.domain_occupancies.pop("P2")
        self.assertInvariantCode(missing_p2, "DOMAIN_OCCUPANCY_MISSING")
        extra_p3 = self._create_state("DOMAIN-OCCUPANCY-EXTRA-P3")
        p3_topology = self.domain_position.create_player_domain_topology("P3")
        extra_p3.domain_occupancies["P3"] = (
            self.domain_occupancy.create_empty_player_domain_occupancy(p3_topology)
        )
        self.assertInvariantCode(extra_p3, "DOMAIN_OCCUPANCY_UNEXPECTED")
        wrong_player = self._create_state("DOMAIN-OCCUPANCY-WRONG-PLAYER")
        wrong_player.domain_occupancies["P1"]["player_id"] = "P2"
        self.assertInvariantCode(wrong_player, "DOMAIN_OCCUPANCY_PLAYER_MISMATCH")
        wrong_topology = self._create_state("DOMAIN-OCCUPANCY-WRONG-TOPOLOGY")
        wrong_topology.domain_occupancies["P1"]["topology_schema_version"] = "wrong"
        self.assertInvariantCode(wrong_topology, "DOMAIN_OCCUPANCY_TOPOLOGY_MISMATCH")

        # I73-I75: slot set/seal failures remain nested in the parent diagnostic.
        missing_slot = self._create_state("DOMAIN-OCCUPANCY-MISSING-SLOT")
        missing_slot.domain_occupancies["P1"]["slots"].pop()
        self.assertInvariantCode(missing_slot, "DOMAIN_OCCUPANCY_RECORD_INVALID")
        seal_slot = self._create_state("DOMAIN-OCCUPANCY-EXTRA-SEAL")
        extra = copy.deepcopy(seal_slot.domain_occupancies["P1"]["slots"][0])
        seal_reference = next(
            position
            for position in seal_slot.domain_topologies["P1"]["positions"]
            if position["position_type"] == "seal"
        )
        extra.update(
            {
                "position_id": seal_reference["position_id"],
                "current_index": seal_reference["current_index"],
                "position_type": "seal",
                "row": None,
            }
        )
        seal_slot.domain_occupancies["P1"]["slots"].append(extra)
        self.assertNestedOccupancyCode(seal_slot, "SEAL_SLOT_UNEXPECTED")
        self.assertNestedOccupancyCode(missing_slot, "POSITION_SET_MISMATCH")

    def test_j_current_snapshots_and_trajectory_do_not_export_occupancy(self):
        session = self._create_session("DOMAIN-OCCUPANCY-PROJECTION-001")
        player_snapshot = session.get_player_snapshot("P1")
        debug_snapshot = session.get_debug_snapshot()
        action = next(action for action in session.list_legal_actions() if action["action_type"] == "end_turn")
        action_response = session.step(session.build_action_request(action))

        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)
        observation = environment.reset(
            match_id="DOMAIN-OCCUPANCY-OBSERVATION-001",
            deck_id_a=self.deck_id_a,
            deck_id_b=self.deck_id_b,
        )
        episode = environment.run_episode(max_steps=2, match_id="DOMAIN-OCCUPANCY-TRAJECTORY-001")

        # J76-J82: no occupancy state, occupant ID, or Domain position crosses current projections.
        self.assertFalse(_contains_key(player_snapshot, "domain_occupancies"))
        self.assertFalse(_contains_key(player_snapshot, "occupant_card_instance_id"))
        serialized_snapshot = json.dumps(player_snapshot, ensure_ascii=False)
        for slot in session.state.domain_occupancies["P1"]["slots"]:
            self.assertNotIn(slot["position_id"], serialized_snapshot)
        self.assertFalse(_contains_contract_type(observation, "player_domain_occupancy"))
        self.assertFalse(_contains_contract_type(action_response, "player_domain_occupancy"))
        self.assertFalse(_contains_key(episode["trajectory"], "domain_occupancies"))
        self.assertFalse(_contains_contract_type(debug_snapshot, "player_domain_occupancy"))

        # J83-J84: existing projection and trajectory contracts remain valid.
        self.assertTrue(self.player_snapshot.validate_player_visible_snapshot(player_snapshot)["valid"])
        self.assertTrue(episode["trajectory_validation"]["valid"])

    def test_k_occupancies_are_deeply_independent(self):
        state = self._create_state("DOMAIN-OCCUPANCY-INDEPENDENCE-001")
        p1 = state.domain_occupancies["P1"]
        p2 = state.domain_occupancies["P2"]

        # K85-K86: player containers and nested metadata are independent.
        self.assertIsNot(p1["slots"], p2["slots"])
        self.assertIsNot(p1["slots"][0]["metadata"], p2["slots"][0]["metadata"])

        # K87-K89: matches do not share occupancy, and topology is not embedded/shared.
        other = self._create_state("DOMAIN-OCCUPANCY-INDEPENDENCE-002")
        self.assertIsNot(state.domain_occupancies, other.domain_occupancies)
        self.assertIsNot(state.domain_occupancies["P1"]["slots"], other.domain_occupancies["P1"]["slots"])
        state.domain_occupancies["P1"]["slots"][0]["metadata"]["source"] = "mutated"
        self.assertEqual(
            other.domain_occupancies["P1"]["slots"][0]["metadata"]["source"],
            "python.engine.domain_occupancy",
        )
        self.assertIsNot(
            state.domain_occupancies["P1"]["slots"][0],
            state.domain_topologies["P1"]["positions"][0],
        )

        # K90: public lookup remains detached from authoritative state.
        lookup = other.get_domain_occupancy("P1")
        lookup["slots"][0]["metadata"]["source"] = "lookup-mutated"
        self.assertEqual(
            other.domain_occupancies["P1"]["slots"][0]["metadata"]["source"],
            "python.engine.domain_occupancy",
        )

    def test_l_setup_is_deterministic_and_six_current_only(self):
        first = self._create_state("DOMAIN-OCCUPANCY-DETERMINISM-001")
        second = self._create_state("DOMAIN-OCCUPANCY-DETERMINISM-001")
        different_match = self._create_state("DOMAIN-OCCUPANCY-DETERMINISM-OTHER")

        # L91-L95: setup is deterministic, player-scoped, empty, and six-current only.
        self.assertEqual(first.domain_occupancies, second.domain_occupancies)
        self.assertEqual(
            _occupancy_position_ids(first.domain_occupancies),
            _occupancy_position_ids(different_match.domain_occupancies),
        )
        self.assertTrue(
            set(slot["position_id"] for slot in first.domain_occupancies["P1"]["slots"]).isdisjoint(
                slot["position_id"] for slot in first.domain_occupancies["P2"]["slots"]
            )
        )
        self.assertTrue(
            all(
                len(occupancy["slots"]) == 12
                and all(slot["occupancy_state"] == "empty" for slot in occupancy["slots"])
                for occupancy in first.domain_occupancies.values()
            )
        )
        self.assertTrue(
            all(
                occupancy["metadata"]["four_current_variant_active"] is False
                for occupancy in first.domain_occupancies.values()
            )
        )

    def _create_state(self, match_id):
        return self.kernel.create_initial_match_state(
            self.runtime_package,
            self.deck_id_a,
            self.deck_id_b,
            match_id=match_id,
        )

    def _create_session(self, match_id):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(
            deck_id_a=self.deck_id_a,
            deck_id_b=self.deck_id_b,
            match_id=match_id,
        )
        return session

    def _submit_action(self, session, action_type):
        action = next(
            action
            for action in session.list_legal_actions()
            if action["action_type"] == action_type and action["enabled"] is True
        )
        response = session.step(session.build_action_request(action))
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        return response

    def _make_synthetic_domain_binding(
        self,
        state,
        occupancy_player_id,
        slot_index=0,
        source_player_id=None,
        controller_player_id=None,
    ):
        source_player_id = source_player_id or occupancy_player_id
        source_player = state.get_player(source_player_id)
        card_instance_id = source_player.deck_card_instance_ids[0]
        self._remove_instance_from_lists(state, card_instance_id)
        record = state.card_instances[card_instance_id]
        record["zone"] = "domain"
        record["zone_index"] = None
        record["visibility"] = "public"
        record["controller_player_id"] = controller_player_id or occupancy_player_id
        record["zone_sequence"] += 1
        self._set_slot_occupied(state, occupancy_player_id, slot_index, card_instance_id)
        return card_instance_id

    def _make_unbound_domain_record(self, state, card_instance_id, controller_player_id):
        self._remove_instance_from_lists(state, card_instance_id)
        record = state.card_instances[card_instance_id]
        record["zone"] = "domain"
        record["zone_index"] = None
        record["visibility"] = "public"
        record["controller_player_id"] = controller_player_id
        record["zone_sequence"] += 1

    def _bind_without_list_removal(self, state, player_id, slot_index, card_instance_id):
        record = state.card_instances[card_instance_id]
        record["zone"] = "domain"
        record["zone_index"] = None
        record["visibility"] = "public"
        record["controller_player_id"] = player_id
        record["zone_sequence"] += 1
        self._set_slot_occupied(state, player_id, slot_index, card_instance_id)

    @staticmethod
    def _set_slot_occupied(
        state,
        player_id,
        slot_index,
        card_instance_id,
        occupant_object_type="card_instance",
    ):
        slot = state.domain_occupancies[player_id]["slots"][slot_index]
        slot["occupancy_state"] = "occupied"
        slot["occupant_object_type"] = occupant_object_type
        slot["occupant_card_instance_id"] = card_instance_id

    def _put_instance_in_list_zone(self, state, player_id, zone_name):
        player = state.get_player(player_id)
        card_instance_id = player.deck_card_instance_ids[0]
        if zone_name != "deck":
            player.deck_card_instance_ids.remove(card_instance_id)
            target = getattr(player, "%s_card_instance_ids" % zone_name)
            target.append(card_instance_id)
            self._reindex_player_zones(state)
        return card_instance_id

    def _remove_instance_from_lists(self, state, card_instance_id):
        for player in state.players:
            for field_name in (
                "deck_card_instance_ids",
                "hand_card_instance_ids",
                "discard_card_instance_ids",
            ):
                zone = getattr(player, field_name)
                while card_instance_id in zone:
                    zone.remove(card_instance_id)
        self._reindex_player_zones(state)

    @staticmethod
    def _reindex_player_zones(state):
        for player in state.players:
            for zone_name in ("deck", "hand", "discard"):
                zone = getattr(player, "%s_card_instance_ids" % zone_name)
                for zone_index, card_instance_id in enumerate(zone):
                    record = state.card_instances[card_instance_id]
                    record["zone"] = zone_name
                    record["zone_index"] = zone_index

    @staticmethod
    def _all_list_zone_ids(state):
        card_instance_ids = []
        for player in state.players:
            card_instance_ids.extend(player.deck_card_instance_ids)
            card_instance_ids.extend(player.hand_card_instance_ids)
            card_instance_ids.extend(player.discard_card_instance_ids)
        return card_instance_ids

    def assertInvariantCode(self, state, code):
        errors = self.invariants.validate_state_invariants(state, self.runtime_package)
        self.assertIn(code, _error_codes(errors), errors)
        json.dumps(errors, ensure_ascii=False)

    def assertNestedOccupancyCode(self, state, code):
        errors = self.invariants.validate_state_invariants(state, self.runtime_package)
        parent_errors = [
            error for error in errors if error.get("code") == "DOMAIN_OCCUPANCY_RECORD_INVALID"
        ]
        nested_codes = _collect_diagnostic_codes(parent_errors)
        self.assertIn(code, nested_codes, errors)
        json.dumps(errors, ensure_ascii=False)


def _occupancy_position_ids(occupancies):
    return {
        player_id: [slot["position_id"] for slot in occupancy["slots"]]
        for player_id, occupancy in occupancies.items()
    }


def _collect_diagnostic_codes(value):
    codes = set()
    if isinstance(value, dict):
        if isinstance(value.get("code"), str):
            codes.add(value["code"])
        for nested in value.values():
            codes.update(_collect_diagnostic_codes(nested))
    elif isinstance(value, list):
        for nested in value:
            codes.update(_collect_diagnostic_codes(nested))
    return codes


def _pick_two_decks(runtime_package):
    preferred = ["DECK-IGN-HAM-TEST-001", "DECK-IGN-LAN-TEST-001"]
    available = sorted(runtime_package.decks_by_id)
    selected = [deck_id for deck_id in preferred if deck_id in runtime_package.decks_by_id]
    if len(selected) >= 2:
        return selected[0], selected[1]
    for deck_id in available:
        if deck_id not in selected:
            selected.append(deck_id)
        if len(selected) == 2:
            return selected[0], selected[1]
    raise AssertionError("The runtime package must contain at least two decks.")


if __name__ == "__main__":
    unittest.main()
