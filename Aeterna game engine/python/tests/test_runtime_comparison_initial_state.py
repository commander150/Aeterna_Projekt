import importlib.util
import json
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
FIXTURE_DIR = (
    ENGINE_PYTHON_DIR.parent
    / "runtime_comparison"
    / "fixtures"
    / "minimal_draw_end_turn_v1"
)
RUNTIME_PACKAGE_DIR = FIXTURE_DIR / "runtime_package"
FIXTURE_PATH = FIXTURE_DIR / "fixture.json"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"
KERNEL_PATH = AI_VS_AI_DIR / "rules_kernel.py"
INVARIANTS_PATH = AI_VS_AI_DIR / "state_invariants.py"
MINIMAL_ENGINE_PATH = ENGINE_DIR / "minimal_engine.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"

EXPECTED_CARD_IDS = (
    "FIXTURE-CARD-P1-001",
    "FIXTURE-CARD-P1-002",
    "FIXTURE-CARD-P1-003",
    "FIXTURE-CARD-P2-001",
    "FIXTURE-CARD-P2-002",
    "FIXTURE-CARD-P2-003",
)
EXPECTED_DECK_ORDERS = {
    "FIXTURE-DECK-PLAYER-1": list(EXPECTED_CARD_IDS[:3]),
    "FIXTURE-DECK-PLAYER-2": list(EXPECTED_CARD_IDS[3:]),
}
REQUIRED_PACKAGE_FILES = {
    "manifest.json",
    "cards.jsonl",
    "decks.jsonl",
    "lookups.json",
}


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_PYTHON_DIR), str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestRuntimeComparisonInitialState(unittest.TestCase):
    def setUp(self):
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.minimal_engine = _load_module("minimal_engine", MINIMAL_ENGINE_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.runtime_package = self.reader.load_runtime_package(RUNTIME_PACKAGE_DIR)

    def test_comparison_runtime_package_is_minimal_valid_and_stable(self):
        package_files = {path.name for path in RUNTIME_PACKAGE_DIR.iterdir() if path.is_file()}
        self.assertEqual(package_files, REQUIRED_PACKAGE_FILES)

        summary = self.runtime_package.count_summary()
        self.assertEqual(summary["cards_count"], 6)
        self.assertEqual(summary["decks_count"], 2)
        self.assertEqual(summary["lookup_records_count"], 2)
        self.assertEqual(summary["deck_reference_error_count"], 0)
        self.assertEqual(tuple(self.runtime_package.cards_by_id), EXPECTED_CARD_IDS)
        self.assertTrue(all(card_id.startswith("FIXTURE-CARD-") for card_id in EXPECTED_CARD_IDS))

        deck_card_sets = []
        for deck_id, expected_order in EXPECTED_DECK_ORDERS.items():
            deck = self.runtime_package.get_deck(deck_id)
            actual_order = _expanded_card_ids(deck)
            self.assertEqual(deck["card_count"], 3)
            self.assertEqual(actual_order, expected_order)
            deck_card_sets.append(set(actual_order))
        self.assertTrue(deck_card_sets[0].isdisjoint(deck_card_sets[1]))

        manifest = self.runtime_package.manifest
        self.assertEqual(
            [entry["path"] for entry in manifest["files"]],
            ["manifest.json", "cards.jsonl", "decks.jsonl", "lookups.json"],
        )
        for source in manifest.get("source_files", []):
            source_path = source.get("path", "")
            self.assertFalse(Path(source_path).is_absolute())
            self.assertFalse(_looks_like_windows_absolute_path(source_path))

        package_payloads = [
            json.loads((RUNTIME_PACKAGE_DIR / "manifest.json").read_text(encoding="utf-8")),
            json.loads((RUNTIME_PACKAGE_DIR / "lookups.json").read_text(encoding="utf-8")),
        ]
        package_payloads.extend(_read_jsonl(RUNTIME_PACKAGE_DIR / "cards.jsonl"))
        package_payloads.extend(_read_jsonl(RUNTIME_PACKAGE_DIR / "decks.jsonl"))
        for payload in package_payloads:
            self.assertFalse(_contains_key(payload, {"created_at", "generated_at", "timestamp"}))
            self.assertFalse(_contains_absolute_path(payload))

        self.assertEqual(self.fixture["schema_version"], "aeterna-runtime-comparison-fixture-v1")
        self.assertEqual(self.fixture["runtime_package_ref"], "runtime_package")
        self.assertEqual(self.fixture["starting_hand_size"], 1)
        self.assertNotIn("expected_artifacts", self.fixture)

    def test_canonical_comparison_initial_state_uses_direct_final_zone_setup(self):
        session, state = self._create_comparison_session()

        self.assertEqual(state.match_id, self.fixture["match_id"])
        self.assertEqual([player.player_id for player in state.players], ["player_1", "player_2"])
        self.assertEqual(state.active_player_id, "player_1")
        self.assertEqual(state.state_version, 0)
        self.assertEqual(state.turn_number, 1)
        self.assertEqual(state.phase, "main")
        self.assertEqual(state.event_log, [])
        self.assertEqual(session.get_event_log(), [])

        self.assertEqual(set(state.domain_topologies), {"player_1", "player_2"})
        self.assertEqual(set(state.domain_occupancies), {"player_1", "player_2"})
        for player_id in self.fixture["player_ids"]:
            topology = state.domain_topologies[player_id]
            occupancy = state.domain_occupancies[player_id]
            self.assertEqual(topology["current_count"], 6)
            self.assertEqual(len(topology["currents"]), 6)
            self.assertEqual(len(occupancy["slots"]), 12)
            self.assertTrue(all(slot["occupancy_state"] == "empty" for slot in occupancy["slots"]))
            self.assertTrue(all(slot["occupant_card_instance_id"] is None for slot in occupancy["slots"]))

        all_zone_instance_ids = []
        for player_setup in self.fixture["player_setup"]:
            player_id = player_setup["player_id"]
            player = state.get_player(player_id)
            expected_card_ids = EXPECTED_DECK_ORDERS[player_setup["deck_id"]]
            self.assertEqual(player.deck_id, player_setup["deck_id"])
            self.assertEqual(len(player.hand_card_instance_ids), 1)
            self.assertEqual(len(player.deck_card_instance_ids), 2)
            self.assertEqual(player.discard_card_instance_ids, [])

            ordered_instance_ids = player.hand_card_instance_ids + player.deck_card_instance_ids
            all_zone_instance_ids.extend(ordered_instance_ids)
            self.assertEqual(
                [state.get_card_id(card_instance_id) for card_instance_id in ordered_instance_ids],
                expected_card_ids,
            )
            for sequence, card_instance_id in enumerate(ordered_instance_ids, start=1):
                record = state.get_card_instance(card_instance_id)
                expected_zone = "hand" if sequence == 1 else "deck"
                expected_zone_index = 0 if sequence == 1 else sequence - 2
                self.assertEqual(card_instance_id, "ci_%s_%04d" % (player_id, sequence))
                self.assertEqual(record["created_sequence"], sequence)
                self.assertEqual(record["zone_sequence"], 1)
                self.assertEqual(record["zone"], expected_zone)
                self.assertEqual(record["zone_index"], expected_zone_index)
                self.assertEqual(record["owner_player_id"], player_id)
                self.assertEqual(record["controller_player_id"], player_id)
                self.assertIsNone(record["activity_state"])
                self.assertEqual(record["visibility"], "owner_only")
                self.assertEqual(
                    record["metadata"],
                    {
                        "creation_reason": "initial_match_setup",
                        "initial_zone": expected_zone,
                    },
                )

        self.assertEqual(set(all_zone_instance_ids), set(state.card_instances))
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_custom_player_order_controls_inactive_player_and_turn_wrap(self):
        session, state = self._create_comparison_session()

        first_response = _submit_enabled_action(session, "end_turn")
        self.assertTrue(first_response["accepted"])
        self.assertEqual(state.active_player_id, "player_2")
        self.assertEqual(state.turn_number, 1)

        second_response = _submit_enabled_action(session, "end_turn")
        self.assertTrue(second_response["accepted"])
        self.assertEqual(state.active_player_id, "player_1")
        self.assertEqual(state.turn_number, 2)
        self.assertEqual(
            [event["player_id"] for event in state.event_log],
            ["player_1", "player_2"],
        )
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_default_setup_remains_p1_p2_with_empty_starting_hands(self):
        deck_id_a, deck_id_b = self.fixture["deck_ids"]
        state = self.minimal_engine.create_match(
            self.runtime_package,
            deck_id_a,
            deck_id_b,
            match_id="RUNTIME-COMPARISON-DEFAULT-COMPATIBILITY",
        )

        self.assertEqual([player.player_id for player in state.players], ["P1", "P2"])
        self.assertEqual(state.active_player_id, "P1")
        self.assertTrue(all(player.hand_card_instance_ids == [] for player in state.players))
        self.assertTrue(all(len(player.deck_card_instance_ids) == 3 for player in state.players))
        self.assertEqual(state.state_version, 0)
        self.assertEqual(state.event_log, [])
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_invalid_setup_parameters_fail_before_exposing_partial_state(self):
        invalid_cases = (
            ({"player_ids": ("player_1", "player_1")}, "distinct"),
            ({"player_ids": ("player_1",)}, "exactly two"),
            ({"player_ids": ("player_1", "")}, "non-empty string"),
            ({"player_ids": ("player_1", None)}, "non-empty string"),
            ({"starting_hand_size": -1}, "non-negative integer"),
            ({"starting_hand_size": True}, "non-negative integer"),
            ({"starting_hand_size": 4}, "exceeds deck size"),
        )
        for overrides, expected_message in invalid_cases:
            with self.subTest(overrides=overrides):
                session = self.session_module.MinimalEngineSession(self.runtime_package)
                kwargs = {
                    "deck_id_a": self.fixture["deck_ids"][0],
                    "deck_id_b": self.fixture["deck_ids"][1],
                    "match_id": self.fixture["match_id"],
                    "player_ids": tuple(self.fixture["player_ids"]),
                    "starting_hand_size": self.fixture["starting_hand_size"],
                }
                kwargs.update(overrides)
                with self.assertRaisesRegex(self.kernel.RulesKernelError, expected_message):
                    session.create_match(**kwargs)
                self.assertIsNone(session.state)
                self.assertIsNone(session.deck_id_a)
                self.assertIsNone(session.deck_id_b)
                self.assertEqual(session.get_action_response_history(), [])

    def _create_comparison_session(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(
            deck_id_a=self.fixture["deck_ids"][0],
            deck_id_b=self.fixture["deck_ids"][1],
            match_id=self.fixture["match_id"],
            player_ids=tuple(self.fixture["player_ids"]),
            starting_hand_size=self.fixture["starting_hand_size"],
        )
        return session, state


def _expanded_card_ids(deck):
    card_ids = []
    for entry in deck.get("card_entries", []) or []:
        card_ids.extend([entry.get("card_id")] * int(entry.get("count") or 0))
    return card_ids


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _contains_key(value, keys):
    if isinstance(value, dict):
        return any(key in keys for key in value) or any(
            _contains_key(nested, keys) for nested in value.values()
        )
    if isinstance(value, list):
        return any(_contains_key(nested, keys) for nested in value)
    return False


def _contains_absolute_path(value):
    if isinstance(value, dict):
        return any(_contains_absolute_path(nested) for nested in value.values())
    if isinstance(value, list):
        return any(_contains_absolute_path(nested) for nested in value)
    if isinstance(value, str):
        return Path(value).is_absolute() or _looks_like_windows_absolute_path(value)
    return False


def _looks_like_windows_absolute_path(value):
    return len(value) >= 3 and value[0].isalpha() and value[1] == ":" and value[2] in {"/", "\\"}


def _submit_enabled_action(session, action_type):
    action = next(
        action
        for action in session.list_legal_actions()
        if action["action_type"] == action_type and action["enabled"] is True
    )
    return session.step(session.build_action_request(action))


if __name__ == "__main__":
    unittest.main()
