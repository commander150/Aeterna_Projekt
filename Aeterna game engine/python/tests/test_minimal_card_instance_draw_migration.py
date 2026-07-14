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
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"
INVARIANTS_PATH = AI_VS_AI_DIR / "state_invariants.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestMinimalCardInstanceDrawMigration(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_initial_setup_builds_deterministic_authoritative_registry(self):
        session = self._create_session("ENGINE-INSTANCE-SETUP-TEST-001")
        state = session.state
        all_zone_ids = _all_zone_instance_ids(state)
        p1_ids = set(state.get_player("P1").deck_card_instance_ids)
        p2_ids = set(state.get_player("P2").deck_card_instance_ids)

        self.assertIsInstance(state.card_instances, dict)
        self.assertEqual(len(all_zone_ids), len(state.card_instances))
        self.assertEqual(len(all_zone_ids), len(set(all_zone_ids)))
        self.assertTrue(p1_ids.isdisjoint(p2_ids))

        for player in state.players:
            expected_card_ids = _expanded_runtime_card_ids(self.runtime_package.get_deck(player.deck_id))
            actual_card_ids = []
            for zone_index, card_instance_id in enumerate(player.deck_card_instance_ids):
                self.assertIn(card_instance_id, state.card_instances)
                record = state.get_card_instance(card_instance_id)
                actual_card_ids.append(record["card_id"])
                self.assertIn(record["card_id"], self.runtime_package.cards_by_id)
                self.assertEqual(record["card_instance_id"], card_instance_id)
                self.assertEqual(record["owner_player_id"], player.player_id)
                self.assertEqual(record["controller_player_id"], player.player_id)
                self.assertEqual(record["zone"], "deck")
                self.assertEqual(record["zone_index"], zone_index)
                self.assertEqual(record["visibility"], "owner_only")
                self.assertEqual(record["created_sequence"], zone_index + 1)
                self.assertEqual(record["zone_sequence"], 1)
                self.assertEqual(record["metadata"]["source"], "initial_deck_setup")
                self.assertEqual(record["metadata"]["authority"], "rules_kernel")
            self.assertEqual(actual_card_ids, expected_card_ids)

        second_session = self.session_module.MinimalEngineSession(self.runtime_package)
        second_state = second_session.create_match(
            deck_id_a=session.deck_id_a,
            deck_id_b=session.deck_id_b,
            match_id="ENGINE-INSTANCE-SETUP-TEST-002",
        )
        self.assertEqual(
            [player.deck_card_instance_ids for player in state.players],
            [player.deck_card_instance_ids for player in second_state.players],
        )
        self.assertEqual(state.card_instances, second_state.card_instances)
        self.assertEqual(session.get_diagnostics(), [])
        with self.assertRaisesRegex(Exception, "Unknown card_instance_id"):
            state.get_card_instance("ci_UNKNOWN_0001")

    def test_duplicate_card_ids_remain_distinct_and_drawable(self):
        session = self._create_session("ENGINE-INSTANCE-DUPLICATE-CARD-TEST-001")
        state = session.state
        player = state.get_player("P1")
        first_instance_id, second_instance_id = player.deck_card_instance_ids[:2]
        first_card_id = state.get_card_id(first_instance_id)

        self.assertNotEqual(first_instance_id, second_instance_id)
        self.assertEqual(first_card_id, state.get_card_id(second_instance_id))
        self.assertEqual(session.get_draw_precondition("P1")["reason"], "ok")
        self.assertTrue(_find_action(session, "draw_card")["enabled"])

        first_response = _draw(session)
        second_response = _draw(session)

        self.assertTrue(first_response["accepted"])
        self.assertTrue(second_response["accepted"])
        self.assertEqual(first_response["events"][0]["payload"]["card_instance_id"], first_instance_id)
        self.assertEqual(second_response["events"][0]["payload"]["card_instance_id"], second_instance_id)
        self.assertEqual(first_response["events"][0]["payload"]["card_id"], first_card_id)
        self.assertEqual(second_response["events"][0]["payload"]["card_id"], first_card_id)
        self.assertEqual(player.hand_card_instance_ids[:2], [first_instance_id, second_instance_id])
        self.assertEqual(session.get_diagnostics(), [])

    def test_draw_moves_one_instance_and_updates_registry_and_event(self):
        session = self._create_session("ENGINE-INSTANCE-DRAW-TEST-001")
        state = session.state
        player = state.get_player("P1")
        initial_deck = list(player.deck_card_instance_ids)
        initial_hand = list(player.hand_card_instance_ids)
        drawn_instance_id = initial_deck[0]
        initial_record = deepcopy(state.get_card_instance(drawn_instance_id))

        response = _draw(session)

        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(player.deck_card_instance_ids, initial_deck[1:])
        self.assertEqual(player.hand_card_instance_ids, initial_hand + [drawn_instance_id])
        record = state.get_card_instance(drawn_instance_id)
        self.assertEqual(record["card_instance_id"], drawn_instance_id)
        self.assertEqual(record["card_id"], initial_record["card_id"])
        self.assertEqual(record["zone"], "hand")
        self.assertEqual(record["zone_index"], len(initial_hand))
        self.assertEqual(record["visibility"], "owner_only")
        self.assertEqual(record["zone_sequence"], initial_record["zone_sequence"] + 1)

        for zone_index, card_instance_id in enumerate(player.deck_card_instance_ids):
            remaining_record = state.get_card_instance(card_instance_id)
            self.assertEqual(remaining_record["zone"], "deck")
            self.assertEqual(remaining_record["zone_index"], zone_index)

        event = response["events"][0]
        payload = event["payload"]
        self.assertEqual(event["event_index"], 0)
        self.assertEqual(event["event_sequence"], 1)
        self.assertEqual(event["contract_type"], "engine_event")
        self.assertEqual(event["event_type"], "zone_move")
        self.assertEqual(event["player_id"], "P1")
        self.assertEqual(event["action_type"], "draw_card")
        self.assertEqual(payload["card_instance_id"], drawn_instance_id)
        self.assertEqual(payload["card_id"], initial_record["card_id"])
        self.assertEqual(payload["from_zone"], "deck")
        self.assertEqual(payload["from_zone_index"], 0)
        self.assertEqual(payload["to_zone"], "hand")
        self.assertEqual(payload["to_zone_index"], len(initial_hand))
        self.assertEqual(payload["metadata"]["semantic_event_type"], "card_drawn")
        self.assertEqual(event["turn_number"], 1)
        self.assertEqual(event["state_version"], 1)
        self.assertEqual(state.state_version, 1)
        self.assertEqual(response["new_event_sequences"], [1])
        self.assertEqual(session.get_diagnostics(), [])

    def test_instance_invariants_report_registry_and_zone_failures(self):
        cases = (
            ("CARD_INSTANCE_MULTIPLE_ZONES", self._put_same_instance_in_two_zones),
            ("PLAYER_ZONE_INSTANCE_UNKNOWN", self._put_unknown_instance_in_zone),
            ("CARD_INSTANCE_ZONE_MISMATCH", self._mismatch_registry_zone),
            ("CARD_INSTANCE_ZONE_INDEX_MISMATCH", self._mismatch_registry_zone_index),
            ("CARD_INSTANCE_ORPHANED", self._orphan_registry_instance),
            ("CARD_INSTANCE_CARD_UNKNOWN", self._set_unknown_runtime_card),
        )
        for expected_code, mutate in cases:
            with self.subTest(expected_code=expected_code):
                session = self._create_session("ENGINE-INSTANCE-INVARIANT-%s" % expected_code)
                mutate(session.state)
                errors = self.invariants.validate_state_invariants(session.state, self.runtime_package)
                self.assertIn(expected_code, [error["code"] for error in errors])
                self.assertFalse(session.get_debug_snapshot()["diagnostics_summary"]["hand_deck_invariants_ok"])

    def test_snapshots_expose_only_visible_instance_ids_and_counts(self):
        session = self._create_session("ENGINE-INSTANCE-SNAPSHOT-TEST-001")
        state = session.state
        p1 = state.get_player("P1")
        p2 = state.get_player("P2")
        initial_p1_deck_count = len(p1.deck_card_instance_ids)
        initial_registry_count = len(state.card_instances)

        initial_player_snapshot = session.get_player_snapshot("P1")
        initial_debug_snapshot = session.get_debug_snapshot()
        _draw(session)
        player_snapshot = session.get_player_snapshot("P1")
        debug_snapshot = session.get_debug_snapshot()
        debug_export = session.export_debug_session_state()

        for value in (initial_player_snapshot, initial_debug_snapshot, player_snapshot, debug_snapshot, debug_export):
            json.dumps(value, ensure_ascii=False)

        serialized_player_snapshot = json.dumps(player_snapshot, ensure_ascii=False)
        self.assertTrue(
            all(card_instance_id not in serialized_player_snapshot for card_instance_id in p2.deck_card_instance_ids)
        )
        self.assertTrue(
            all(card_instance_id not in serialized_player_snapshot for card_instance_id in p1.deck_card_instance_ids)
        )
        drawn_instance_id = p1.hand_card_instance_ids[0]
        self.assertIn(drawn_instance_id, serialized_player_snapshot)
        self.assertEqual(player_snapshot["players"][0]["deck_count"], initial_p1_deck_count - 1)
        self.assertEqual(player_snapshot["players"][0]["hand_count"], 1)
        self.assertEqual(player_snapshot["players"][0]["discard_count"], 0)
        self.assertEqual(player_snapshot["metadata"]["card_instance_model"], "minimal_registry_v0")
        self.assertFalse(player_snapshot["metadata"]["card_id_overlap_guard"])
        self.assertEqual(debug_snapshot["card_instance_count"], initial_registry_count)
        self.assertEqual(debug_snapshot["metadata"]["card_instance_model"], "minimal_registry_v0")
        self.assertFalse(debug_snapshot["metadata"]["card_id_overlap_guard"])
        self.assertEqual(debug_export["debug_snapshot"]["card_instance_count"], initial_registry_count)

    def _create_session(self, match_id):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id=match_id)
        return session

    @staticmethod
    def _put_same_instance_in_two_zones(state):
        player = state.get_player("P1")
        player.hand_card_instance_ids.append(player.deck_card_instance_ids[0])

    @staticmethod
    def _put_unknown_instance_in_zone(state):
        state.get_player("P1").hand_card_instance_ids.append("ci_P1_UNKNOWN")

    @staticmethod
    def _mismatch_registry_zone(state):
        card_instance_id = state.get_player("P1").deck_card_instance_ids[0]
        state.get_card_instance(card_instance_id)["zone"] = "hand"

    @staticmethod
    def _mismatch_registry_zone_index(state):
        card_instance_id = state.get_player("P1").deck_card_instance_ids[0]
        state.get_card_instance(card_instance_id)["zone_index"] = 99

    @staticmethod
    def _orphan_registry_instance(state):
        state.get_player("P1").deck_card_instance_ids.pop(0)

    @staticmethod
    def _set_unknown_runtime_card(state):
        card_instance_id = state.get_player("P1").deck_card_instance_ids[0]
        state.get_card_instance(card_instance_id)["card_id"] = "UNKNOWN-RUNTIME-CARD"


def _all_zone_instance_ids(state):
    instance_ids = []
    for player in state.players:
        instance_ids.extend(player.deck_card_instance_ids)
        instance_ids.extend(player.hand_card_instance_ids)
        instance_ids.extend(player.discard_card_instance_ids)
    return instance_ids


def _expanded_runtime_card_ids(deck):
    card_ids = []
    for entry in deck.get("card_entries", []) or []:
        card_ids.extend([entry.get("card_id")] * int(entry.get("count") or 0))
    return card_ids


def _find_action(session, action_type):
    return next(action for action in session.get_action_space()["actions"] if action["action_type"] == action_type)


def _draw(session):
    return session.step(session.build_action_request(_find_action(session, "draw_card")))


if __name__ == "__main__":
    unittest.main()
