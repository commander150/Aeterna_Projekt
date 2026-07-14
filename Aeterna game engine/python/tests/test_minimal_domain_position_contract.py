import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
DOMAIN_POSITION_PATH = ENGINE_DIR / "domain_position.py"
MATCH_STATE_PATH = AI_VS_AI_DIR / "match_state.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _error_codes(result):
    return {error["code"] for error in result["errors"]}


def _contains_key(value, key):
    if isinstance(value, dict):
        return key in value or any(_contains_key(nested, key) for nested in value.values())
    if isinstance(value, list):
        return any(_contains_key(nested, key) for nested in value)
    return False


class TestMinimalDomainPositionContract(unittest.TestCase):
    def setUp(self):
        self.domain_position = _load_module("domain_position", DOMAIN_POSITION_PATH)

    def test_a_position_ids_are_stable_and_reject_invalid_inputs(self):
        # A1-A4: deterministic, padded, player-scoped, type-scoped IDs.
        first = self.domain_position.create_domain_position_id("P1", 1, "horizon")
        self.assertEqual(first, "domain_P1_current_01_horizon")
        self.assertEqual(
            first,
            self.domain_position.create_domain_position_id("P1", 1, "horizon"),
        )
        self.assertEqual(
            self.domain_position.create_domain_position_id("P1", 6, "seal"),
            "domain_P1_current_06_seal",
        )
        self.assertNotEqual(
            first,
            self.domain_position.create_domain_position_id("P2", 1, "horizon"),
        )
        type_ids = {
            self.domain_position.create_domain_position_id("P1", 1, position_type)
            for position_type in self.domain_position.DOMAIN_POSITION_TYPES
        }
        self.assertEqual(len(type_ids), 3)

        # A5-A9: invalid identity inputs fail in a controlled way.
        invalid_inputs = (
            ("P1", 0, "horizon"),
            ("P1", 7, "horizon"),
            ("P1", True, "horizon"),
            ("P1", 1, "depth"),
            ("", 1, "horizon"),
        )
        for arguments in invalid_inputs:
            with self.subTest(arguments=arguments):
                with self.assertRaises(self.domain_position.DomainPositionError):
                    self.domain_position.create_domain_position_id(*arguments)

    def test_b_position_reference_contract_and_validation(self):
        records = {
            position_type: self.domain_position.create_domain_position_reference(
                "P1", 2, position_type
            )
            for position_type in self.domain_position.DOMAIN_POSITION_TYPES
        }

        # B10-B19: all three references follow the static public contract.
        for position_type, record in records.items():
            with self.subTest(position_type=position_type):
                expected_area = "seal_layer" if position_type == "seal" else "domain"
                expected_row = None if position_type == "seal" else position_type
                self.assertEqual(record["schema_version"], "minimal-domain-position-v0")
                self.assertEqual(record["contract_type"], "domain_position_reference")
                self.assertEqual(record["area"], expected_area)
                self.assertEqual(record["row"], expected_row)
                self.assertEqual(record["linked_current_id"], "domain_P1_current_02")
                self.assertEqual(record["visibility"], "public")
                self.assertEqual(record["metadata"]["occupancy_model"], "not_implemented")
                self.assertEqual(json.loads(json.dumps(record, ensure_ascii=False)), record)
                self.assertEqual(
                    self.domain_position.validate_domain_position_reference(record),
                    {"valid": True, "errors": []},
                )

        # B20-B24: identity and topology inconsistencies are diagnosed.
        invalid_mutations = (
            ("POSITION_ID_MISMATCH", "position_id", "wrong-position"),
            ("AREA_INVALID", "area", "wrong-area"),
            ("ROW_INVALID", "row", "zenith"),
            ("LINKED_CURRENT_ID_MISMATCH", "linked_current_id", "wrong-current"),
            ("CURRENT_INDEX_INVALID", "current_index", 0),
        )
        for expected_code, field_name, value in invalid_mutations:
            with self.subTest(expected_code=expected_code):
                invalid = copy.deepcopy(records["horizon"])
                invalid[field_name] = value
                result = self.domain_position.validate_domain_position_reference(invalid)
                self.assertFalse(result["valid"])
                self.assertIn(expected_code, _error_codes(result))

        # B25: ordinary malformed input returns structured diagnostics.
        result = self.domain_position.validate_domain_position_reference(None)
        self.assertFalse(result["valid"])
        self.assertIn("RECORD_NOT_DICT", _error_codes(result))
        json.dumps(result, ensure_ascii=False)

    def test_c_player_topology_shape_links_and_identity(self):
        topology = self.domain_position.create_player_domain_topology("P1")
        currents = topology["currents"]
        positions = topology["positions"]

        # C26-C35: canonical six-current, two-row, eighteen-position shape.
        self.assertEqual(topology["schema_version"], "minimal-player-domain-topology-v0")
        self.assertEqual(topology["contract_type"], "player_domain_topology")
        self.assertEqual(topology["current_count"], 6)
        self.assertEqual(topology["row_count"], 2)
        self.assertEqual(topology["rows"], ["horizon", "zenith"])
        self.assertEqual(len(currents), 6)
        self.assertEqual(len(positions), 18)
        for position_type in self.domain_position.DOMAIN_POSITION_TYPES:
            self.assertEqual(
                sum(position["position_type"] == position_type for position in positions),
                6,
            )
        self.assertEqual([current["current_index"] for current in currents], list(range(1, 7)))

        # C36-C39: stable IDs and links cover current 1 through current 6.
        current_ids = [current["current_id"] for current in currents]
        position_ids = [position["position_id"] for position in positions]
        self.assertEqual(len(current_ids), len(set(current_ids)))
        self.assertEqual(len(position_ids), len(set(position_ids)))
        position_by_id = {position["position_id"]: position for position in positions}
        for current in currents:
            for position_type in self.domain_position.DOMAIN_POSITION_TYPES:
                position_id = current["%s_position_id" % position_type]
                self.assertIn(position_id, position_by_id)
                linked_position = position_by_id[position_id]
                self.assertEqual(linked_position["current_index"], current["current_index"])
                self.assertEqual(linked_position["linked_current_id"], current["current_id"])
        self.assertEqual(
            [position["position_type"] for position in positions[:3]],
            ["horizon", "zenith", "seal"],
        )
        self.assertTrue(all(position["current_index"] == 1 for position in positions[:3]))
        self.assertTrue(all(position["current_index"] == 6 for position in positions[-3:]))

        # C40-C42: players are disjoint and the complete result validates/serializes.
        p2_topology = self.domain_position.create_player_domain_topology("P2")
        p2_position_ids = {position["position_id"] for position in p2_topology["positions"]}
        self.assertTrue(set(position_ids).isdisjoint(p2_position_ids))
        self.assertEqual(
            self.domain_position.validate_player_domain_topology(topology),
            {"valid": True, "errors": []},
        )
        self.assertEqual(json.loads(json.dumps(topology, ensure_ascii=False)), topology)

    def test_d_topology_is_static_and_does_not_mutate_match_state(self):
        topology = self.domain_position.create_player_domain_topology("P1")

        # D43-D49: the contract contains no runtime object or gameplay state.
        forbidden_keys = (
            "card_instance_id",
            "card_id",
            "occupant",
            "objects",
            "attackability",
            "targetability",
            "seal_state",
        )
        for key in forbidden_keys:
            with self.subTest(key=key):
                self.assertFalse(_contains_key(topology, key))

        # D50: constructing/validating topology cannot mutate MatchState.
        match_state = _load_module("match_state", MATCH_STATE_PATH)
        state = match_state.MatchState(
            match_id="DOMAIN-HELPER-ISOLATION-001",
            turn_number=1,
            active_player_id="P1",
            players=[
                match_state.PlayerState("P1", "DECK-A", ["ci_P1_0001"]),
                match_state.PlayerState("P2", "DECK-B", ["ci_P2_0001"]),
            ],
            phase="minimal_main",
        )
        before = copy.deepcopy(state)
        self.domain_position.create_player_domain_topology("P2")
        self.domain_position.validate_player_domain_topology(topology)
        self.assertEqual(state, before)

    def test_e_topology_calls_do_not_share_mutable_state(self):
        first = self.domain_position.create_player_domain_topology("P1")
        second = self.domain_position.create_player_domain_topology("P1")

        # E51-E54: list and nested metadata identities are independent.
        self.assertIsNot(first["currents"], second["currents"])
        self.assertIsNot(first["positions"], second["positions"])
        self.assertIsNot(first["metadata"], second["metadata"])
        self.assertIsNot(first["positions"][0]["metadata"], second["positions"][0]["metadata"])
        first["rows"].append("mutated")
        first["currents"][0]["metadata"]["ordered"] = False
        first["positions"][0]["metadata"]["source"] = "mutated"
        self.assertEqual(second["rows"], ["horizon", "zenith"])
        self.assertTrue(second["currents"][0]["metadata"]["ordered"])
        self.assertEqual(second["positions"][0]["metadata"]["source"], "python.engine.domain_position")

    def test_f_topology_validator_reports_required_negative_cases(self):
        base = self.domain_position.create_player_domain_topology("P1")

        five_currents = copy.deepcopy(base)
        five_currents["currents"].pop()

        seven_currents = copy.deepcopy(base)
        seventh = copy.deepcopy(seven_currents["currents"][-1])
        seventh["current_id"] = "domain_P1_current_07"
        seventh["current_index"] = 7
        seven_currents["currents"].append(seventh)

        missing_seal = copy.deepcopy(base)
        missing_seal["positions"] = [
            position
            for position in missing_seal["positions"]
            if not (position["current_index"] == 1 and position["position_type"] == "seal")
        ]

        duplicate_position = copy.deepcopy(base)
        duplicate_position["positions"][1]["position_id"] = duplicate_position["positions"][0][
            "position_id"
        ]

        wrong_player = copy.deepcopy(base)
        wrong_player["positions"][0]["player_id"] = "P2"

        bad_link = copy.deepcopy(base)
        bad_link["currents"][0]["horizon_position_id"] = bad_link["currents"][1][
            "horizon_position_id"
        ]

        four_current = copy.deepcopy(base)
        four_current["metadata"]["four_current_variant_active"] = True

        occupied = copy.deepcopy(base)
        occupied["occupancy"] = {"domain_P1_current_01_horizon": "ci_P1_0001"}

        # F55-F62: each malformed topology is invalid with a useful code.
        cases = (
            (five_currents, "CURRENTS_INVALID"),
            (seven_currents, "CURRENTS_INVALID"),
            (missing_seal, "POSITIONS_INVALID"),
            (duplicate_position, "POSITION_ID_DUPLICATE"),
            (wrong_player, "POSITION_PLAYER_MISMATCH"),
            (bad_link, "CURRENT_POSITION_LINK_INVALID"),
            (four_current, "METADATA_INVALID"),
            (occupied, "UNEXPECTED_RUNTIME_STATE_FIELD"),
        )
        for invalid, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                result = self.domain_position.validate_player_domain_topology(invalid)
                self.assertFalse(result["valid"])
                self.assertIn(expected_code, _error_codes(result))
                json.dumps(result, ensure_ascii=False)

        # F63: non-dict input is reported, not raised.
        result = self.domain_position.validate_player_domain_topology([])
        self.assertFalse(result["valid"])
        self.assertIn("TOPOLOGY_NOT_DICT", _error_codes(result))
        json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
