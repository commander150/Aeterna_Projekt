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


class TestMinimalMatchStateDomainTopology(unittest.TestCase):
    def setUp(self):
        self.match_state = _load_module("match_state", MATCH_STATE_PATH)
        self.domain_position = _load_module("domain_position", DOMAIN_POSITION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.player_snapshot = _load_module("player_visible_snapshot", PLAYER_SNAPSHOT_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.environment_module = _load_module("minimal_engine_environment", ENVIRONMENT_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        self.deck_id_a, self.deck_id_b = _pick_two_decks(self.runtime_package)

    def test_a_initial_match_contains_two_valid_disjoint_topologies(self):
        state = self._create_state("DOMAIN-SETUP-001")

        # A1-A7: the canonical registry contains one valid topology per player.
        self.assertTrue(hasattr(state, "domain_topologies"))
        self.assertIsInstance(state.domain_topologies, dict)
        self.assertEqual(set(state.domain_topologies), {"P1", "P2"})
        self.assertIn("P1", state.domain_topologies)
        self.assertIn("P2", state.domain_topologies)
        self.assertEqual(state.domain_topologies["P1"]["player_id"], "P1")
        self.assertEqual(state.domain_topologies["P2"]["player_id"], "P2")
        for topology in state.domain_topologies.values():
            self.assertTrue(self.domain_position.validate_player_domain_topology(topology)["valid"])

        # A8-A13: shape, global identity, serialization, and state invariants are stable.
        for topology in state.domain_topologies.values():
            self.assertEqual(len(topology["currents"]), 6)
            self.assertEqual(len(topology["positions"]), 18)
        p1_position_ids = _ids(state.domain_topologies["P1"], "positions", "position_id")
        p2_position_ids = _ids(state.domain_topologies["P2"], "positions", "position_id")
        p1_current_ids = _ids(state.domain_topologies["P1"], "currents", "current_id")
        p2_current_ids = _ids(state.domain_topologies["P2"], "currents", "current_id")
        self.assertTrue(p1_position_ids.isdisjoint(p2_position_ids))
        self.assertTrue(p1_current_ids.isdisjoint(p2_current_ids))
        json.dumps(state.domain_topologies, ensure_ascii=False)
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_b_lookup_returns_deep_copies_and_controlled_errors(self):
        state = self._create_state("DOMAIN-LOOKUP-001")

        # B14-B19: lookup is player-scoped, controlled, and does not expose state references.
        p1 = state.get_domain_topology("P1")
        p2 = state.get_domain_topology("P2")
        self.assertEqual(p1["player_id"], "P1")
        self.assertEqual(p2["player_id"], "P2")
        with self.assertRaisesRegex(self.match_state.MatchStateError, "Unknown player_id"):
            state.get_domain_topology("P3")
        state.domain_topologies.pop("P1")
        with self.assertRaisesRegex(self.match_state.MatchStateError, "Missing Domain topology"):
            state.get_domain_topology("P1")

        state = self._create_state("DOMAIN-LOOKUP-COPY-001")
        lookup = state.get_domain_topology("P1")
        lookup["rows"].append("mutated")
        lookup["positions"][0]["metadata"]["source"] = "mutated"
        self.assertEqual(state.domain_topologies["P1"]["rows"], ["horizon", "zenith"])
        self.assertEqual(
            state.domain_topologies["P1"]["positions"][0]["metadata"]["source"],
            "python.engine.domain_position",
        )

    def test_c_draw_and_end_turn_leave_topology_unchanged(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(
            deck_id_a=self.deck_id_a,
            deck_id_b=self.deck_id_b,
            match_id="DOMAIN-RUNTIME-STABILITY-001",
        )
        initial_topologies = copy.deepcopy(state.domain_topologies)

        # C20-C23: draw and both turn directions leave topology byte-for-byte unchanged.
        responses = [
            self._submit_action(session, "draw_card"),
            self._submit_action(session, "end_turn"),
            self._submit_action(session, "end_turn"),
            self._submit_action(session, "draw_card"),
            self._submit_action(session, "draw_card"),
        ]
        self.assertEqual(state.domain_topologies, initial_topologies)
        self.assertEqual(state.domain_topologies["P1"], initial_topologies["P1"])
        self.assertEqual(state.domain_topologies["P2"], initial_topologies["P2"])
        self.assertEqual(len(state.players[0].hand_card_instance_ids), 3)

        # C24-C27: topology creates no event and transition sequencing is unchanged.
        self.assertEqual(
            [event["event_type"] for event in state.event_log],
            ["zone_move", "turn_transition", "turn_transition", "zone_move", "zone_move"],
        )
        self.assertEqual([response["state_version_after"] for response in responses], [1, 2, 3, 4, 5])
        self.assertEqual([event["event_sequence"] for event in state.event_log], [1, 2, 3, 4, 5])
        self.assertEqual(session.get_diagnostics(), [])

    def test_d_snapshots_observations_and_trajectory_do_not_export_topology(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(
            deck_id_a=self.deck_id_a,
            deck_id_b=self.deck_id_b,
            match_id="DOMAIN-PROJECTION-BOUNDARY-001",
        )
        player_snapshot = session.get_player_snapshot("P1")
        debug_snapshot = session.get_debug_snapshot()
        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)
        observation = environment.reset(
            match_id="DOMAIN-OBSERVATION-BOUNDARY-001",
            deck_id_a=self.deck_id_a,
            deck_id_b=self.deck_id_b,
        )
        episode = environment.run_episode(max_steps=2, match_id="DOMAIN-TRAJECTORY-BOUNDARY-001")

        # D28-D32: no full topology or position IDs cross current projection boundaries.
        self.assertFalse(_contains_key(player_snapshot, "domain_topologies"))
        self.assertFalse(_contains_key(player_snapshot, "position_id"))
        self.assertFalse(_contains_contract_type(observation, "player_domain_topology"))
        self.assertFalse(_contains_key(episode["trajectory"], "domain_topologies"))
        self.assertFalse(_contains_contract_type(debug_snapshot, "player_domain_topology"))

        # D33-D34: existing player-snapshot and trajectory contracts remain valid.
        self.assertTrue(self.player_snapshot.validate_player_visible_snapshot(player_snapshot)["valid"])
        self.assertTrue(episode["trajectory_validation"]["valid"])

    def test_e_domain_topology_invariants_report_all_required_failures(self):
        # E35: absent and invalid containers have explicit diagnostics.
        missing_container = self._create_state("DOMAIN-INVARIANT-MISSING-CONTAINER")
        del missing_container.domain_topologies
        self.assertInvariantCode(missing_container, "DOMAIN_TOPOLOGIES_MISSING")
        invalid_container = self._create_state("DOMAIN-INVARIANT-INVALID-CONTAINER")
        invalid_container.domain_topologies = []
        self.assertInvariantCode(invalid_container, "DOMAIN_TOPOLOGIES_INVALID")

        # E36-E39: player-set, ownership, and contract failures remain distinguishable.
        missing_p2 = self._create_state("DOMAIN-INVARIANT-MISSING-P2")
        missing_p2.domain_topologies.pop("P2")
        self.assertInvariantCode(missing_p2, "DOMAIN_TOPOLOGY_MISSING")
        extra_p3 = self._create_state("DOMAIN-INVARIANT-EXTRA-P3")
        extra_p3.domain_topologies["P3"] = self.domain_position.create_player_domain_topology("P3")
        self.assertInvariantCode(extra_p3, "DOMAIN_TOPOLOGY_UNEXPECTED")
        wrong_player = self._create_state("DOMAIN-INVARIANT-WRONG-PLAYER")
        wrong_player.domain_topologies["P1"]["player_id"] = "P2"
        self.assertInvariantCode(wrong_player, "DOMAIN_TOPOLOGY_PLAYER_MISMATCH")
        invalid_contract = self._create_state("DOMAIN-INVARIANT-CONTRACT")
        invalid_contract.domain_topologies["P1"]["contract_type"] = "wrong_contract"
        self.assertInvariantCode(invalid_contract, "DOMAIN_TOPOLOGY_RECORD_INVALID")

        # E40-E41: position/current IDs are globally unique across player topologies.
        position_collision = self._create_state("DOMAIN-INVARIANT-POSITION-COLLISION")
        position_collision.domain_topologies["P2"]["positions"][0]["position_id"] = (
            position_collision.domain_topologies["P1"]["positions"][0]["position_id"]
        )
        self.assertInvariantCode(position_collision, "DOMAIN_POSITION_ID_COLLISION")
        current_collision = self._create_state("DOMAIN-INVARIANT-CURRENT-COLLISION")
        current_collision.domain_topologies["P2"]["currents"][0]["current_id"] = (
            current_collision.domain_topologies["P1"]["currents"][0]["current_id"]
        )
        self.assertInvariantCode(current_collision, "DOMAIN_CURRENT_ID_COLLISION")

        # E42-E44: occupancy and card data cannot leak into static topology.
        for field_name, field_value in (
            ("occupancy", {}),
            ("card_instance_id", "ci_P1_0001"),
            ("card_id", "IGN-HAM-001"),
        ):
            with self.subTest(field_name=field_name):
                leaked = self._create_state("DOMAIN-INVARIANT-LEAK-%s" % field_name)
                leaked.domain_topologies["P1"]["positions"][0][field_name] = field_value
                self.assertInvariantCode(leaked, "DOMAIN_RUNTIME_STATE_LEAK")

    def test_f_topologies_are_deeply_independent(self):
        state = self._create_state("DOMAIN-INDEPENDENCE-001")
        p1 = state.domain_topologies["P1"]
        p2 = state.domain_topologies["P2"]

        # F45-F46: players do not share nested mutable topology structures.
        self.assertIsNot(p1["positions"], p2["positions"])
        self.assertIsNot(p1["currents"], p2["currents"])
        self.assertIsNot(p1["positions"][0]["metadata"], p2["positions"][0]["metadata"])

        # F47-F48: separately created matches do not share topology references.
        other = self._create_state("DOMAIN-INDEPENDENCE-002")
        self.assertIsNot(state.domain_topologies, other.domain_topologies)
        self.assertIsNot(state.domain_topologies["P1"]["positions"], other.domain_topologies["P1"]["positions"])
        state.domain_topologies["P1"]["rows"].append("mutated")
        self.assertEqual(other.domain_topologies["P1"]["rows"], ["horizon", "zenith"])

    def test_g_topology_setup_is_deterministic_and_six_current_only(self):
        first = self._create_state("DOMAIN-DETERMINISM-001")
        second = self._create_state("DOMAIN-DETERMINISM-001")
        different_match = self._create_state("DOMAIN-DETERMINISM-OTHER-MATCH")

        # G49-G52: match ID does not affect the active base-game topology model.
        self.assertEqual(first.domain_topologies, second.domain_topologies)
        self.assertEqual(
            _all_position_ids(first.domain_topologies),
            _all_position_ids(different_match.domain_topologies),
        )
        for topology in first.domain_topologies.values():
            self.assertEqual(topology["current_count"], 6)
            self.assertEqual(topology["metadata"]["topology_model"], "base_game_six_current_v0")
            self.assertFalse(topology["metadata"]["four_current_variant_active"])

    def _create_state(self, match_id):
        return self.kernel.create_initial_match_state(
            self.runtime_package,
            self.deck_id_a,
            self.deck_id_b,
            match_id=match_id,
        )

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

    def assertInvariantCode(self, state, code):
        errors = self.invariants.validate_state_invariants(state, self.runtime_package)
        self.assertIn(code, _error_codes(errors))
        json.dumps(errors, ensure_ascii=False)


def _ids(topology, collection_name, id_field):
    return {record[id_field] for record in topology[collection_name]}


def _all_position_ids(topologies):
    return {
        player_id: sorted(_ids(topology, "positions", "position_id"))
        for player_id, topology in topologies.items()
    }


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
