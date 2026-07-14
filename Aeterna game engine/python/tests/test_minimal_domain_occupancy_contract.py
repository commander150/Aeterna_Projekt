import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
DOMAIN_OCCUPANCY_PATH = ENGINE_DIR / "domain_occupancy.py"
DOMAIN_POSITION_PATH = ENGINE_DIR / "domain_position.py"


def _load_module(module_name, path):
    engine_dir = str(ENGINE_DIR)
    if engine_dir not in sys.path:
        sys.path.insert(0, engine_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _error_codes(result):
    return {error.get("code") for error in result.get("errors", [])}


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


class TestMinimalDomainOccupancyContract(unittest.TestCase):
    def setUp(self):
        self.domain_position = _load_module("domain_position", DOMAIN_POSITION_PATH)
        self.occupancy = _load_module("domain_occupancy", DOMAIN_OCCUPANCY_PATH)
        self.p1_topology = self.domain_position.create_player_domain_topology("P1")

    def test_a_empty_position_occupancy_contract(self):
        horizon_reference = self._position("P1", 1, "horizon")
        zenith_reference = self._position("P1", 1, "zenith")
        seal_reference = self._position("P1", 1, "seal")
        horizon = self.occupancy.create_empty_domain_position_occupancy(horizon_reference)
        zenith = self.occupancy.create_empty_domain_position_occupancy(zenith_reference)

        # A1-A3: only canonical horizon/zenith references can create slots.
        self.assertEqual(horizon["position_type"], "horizon")
        self.assertEqual(horizon["row"], "horizon")
        self.assertEqual(zenith["position_type"], "zenith")
        self.assertEqual(zenith["row"], "zenith")
        with self.assertRaises(self.occupancy.DomainOccupancyError):
            self.occupancy.create_empty_domain_position_occupancy(seal_reference)

        # A4-A11: canonical empty values, metadata, JSON, and validation.
        self.assertEqual(horizon["occupancy_state"], "empty")
        self.assertIsNone(horizon["occupant_object_type"])
        self.assertIsNone(horizon["occupant_card_instance_id"])
        self.assertEqual(horizon["visibility"], "public")
        self.assertEqual(horizon["metadata"]["capacity"], 1)
        self.assertEqual(horizon["metadata"]["mutation_api"], "not_implemented")
        self.assertEqual(json.loads(json.dumps(horizon, ensure_ascii=False)), horizon)
        self.assertEqual(
            self.occupancy.validate_domain_position_occupancy(horizon),
            {"valid": True, "errors": []},
        )

    def test_b_position_occupancy_negative_cases_are_structured(self):
        base = self._empty_slot("P1", 1, "horizon")

        # B12-B17: position identity, index, row, type, and seal errors.
        cases = []
        invalid = copy.deepcopy(base)
        invalid["position_id"] = "wrong-position"
        cases.append((invalid, "POSITION_ID_MISMATCH"))
        invalid = copy.deepcopy(base)
        invalid["current_index"] = 0
        cases.append((invalid, "CURRENT_INDEX_INVALID"))
        invalid = copy.deepcopy(base)
        invalid["current_index"] = True
        cases.append((invalid, "CURRENT_INDEX_INVALID"))
        invalid = copy.deepcopy(base)
        invalid["row"] = "zenith"
        cases.append((invalid, "ROW_INVALID"))
        invalid = copy.deepcopy(base)
        invalid["position_type"] = "depth"
        cases.append((invalid, "POSITION_TYPE_INVALID"))
        invalid = copy.deepcopy(base)
        invalid["position_type"] = "seal"
        invalid["row"] = None
        invalid["position_id"] = self.domain_position.create_domain_position_id("P1", 1, "seal")
        cases.append((invalid, "SEAL_POSITION_NOT_SUPPORTED"))

        # B18-B20: empty/occupied identity consistency and object type.
        invalid = copy.deepcopy(base)
        invalid["occupant_card_instance_id"] = "ci_P1_0001"
        cases.append((invalid, "EMPTY_OCCUPANCY_HAS_OCCUPANT"))
        invalid = copy.deepcopy(base)
        invalid["occupancy_state"] = "occupied"
        cases.append((invalid, "OCCUPIED_OCCUPANCY_MISSING_OCCUPANT"))
        invalid = self._occupied(base, "ci_P1_0001")
        invalid["occupant_object_type"] = "card_definition"
        cases.append((invalid, "OCCUPANT_OBJECT_TYPE_INVALID"))

        for invalid, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                result = self.occupancy.validate_domain_position_occupancy(invalid)
                self.assertFalse(result["valid"])
                self.assertIn(expected_code, _error_codes(result))
                json.dumps(result, ensure_ascii=False)

        # B21-B22: ordinary malformed input never raises unexpectedly.
        result = self.occupancy.validate_domain_position_occupancy(None)
        self.assertFalse(result["valid"])
        self.assertIn("RECORD_NOT_DICT", _error_codes(result))
        result = self.occupancy.validate_domain_position_occupancy({})
        self.assertFalse(result["valid"])
        self.assertIn("FIELD_MISSING", _error_codes(result))
        json.dumps(result, ensure_ascii=False)

    def test_c_synthetic_occupied_record_is_structurally_valid(self):
        topology_before = copy.deepcopy(self.p1_topology)
        registry = {"ci_P1_9999": {"unrelated": True}}
        registry_before = copy.deepcopy(registry)
        occupied = self._occupied(self._empty_slot("P1", 2, "horizon"), "ci_UNKNOWN_9999")

        # C23-C28: occupied form uses only instance identity and no runtime lookup.
        result = self.occupancy.validate_domain_position_occupancy(occupied)
        self.assertTrue(result["valid"])
        self.assertEqual(occupied["occupant_object_type"], "card_instance")
        self.assertEqual(occupied["occupant_card_instance_id"], "ci_UNKNOWN_9999")
        self.assertFalse(_contains_key(occupied, "card_id"))
        self.assertEqual(result["errors"], [])
        self.assertEqual(registry, registry_before)
        self.assertEqual(self.p1_topology, topology_before)

    def test_d_empty_player_occupancy_has_twelve_ordered_slots(self):
        occupancy = self.occupancy.create_empty_player_domain_occupancy(self.p1_topology)
        slots = occupancy["slots"]

        # D29-D38: canonical player contract covers six currents and two rows.
        self.assertEqual(occupancy["contract_type"], "player_domain_occupancy")
        self.assertEqual(occupancy["player_id"], "P1")
        self.assertEqual(occupancy["topology_schema_version"], self.p1_topology["schema_version"])
        self.assertEqual(occupancy["slot_count"], 12)
        self.assertEqual(len(slots), 12)
        self.assertEqual(sum(slot["position_type"] == "horizon" for slot in slots), 6)
        self.assertEqual(sum(slot["position_type"] == "zenith" for slot in slots), 6)
        self.assertEqual(sum(slot["position_type"] == "seal" for slot in slots), 0)
        self.assertEqual(sorted({slot["current_index"] for slot in slots}), list(range(1, 7)))
        for current_index in range(1, 7):
            current_slots = [slot for slot in slots if slot["current_index"] == current_index]
            self.assertEqual(
                [slot["position_type"] for slot in current_slots],
                ["horizon", "zenith"],
            )

        # D39-D43: all slots start empty in deterministic JSON-compatible order.
        self.assertTrue(all(slot["occupancy_state"] == "empty" for slot in slots))
        self.assertTrue(all(slot["occupant_card_instance_id"] is None for slot in slots))
        self.assertEqual(
            [(slot["current_index"], slot["position_type"]) for slot in slots],
            [
                (current_index, position_type)
                for current_index in range(1, 7)
                for position_type in ("horizon", "zenith")
            ],
        )
        shuffled_topology = copy.deepcopy(self.p1_topology)
        shuffled_topology["positions"].reverse()
        shuffled_slots = self.occupancy.create_empty_player_domain_occupancy(
            shuffled_topology
        )["slots"]
        self.assertEqual(
            [slot["position_id"] for slot in shuffled_slots],
            [slot["position_id"] for slot in slots],
        )
        self.assertTrue(
            self.occupancy.validate_player_domain_occupancy(occupancy, self.p1_topology)["valid"]
        )
        self.assertEqual(json.loads(json.dumps(occupancy, ensure_ascii=False)), occupancy)

    def test_e_player_occupancy_tracks_topology_position_set(self):
        occupancy = self.occupancy.create_empty_player_domain_occupancy(self.p1_topology)
        occupancy_ids = {slot["position_id"] for slot in occupancy["slots"]}
        domain_ids = {
            position["position_id"]
            for position in self.p1_topology["positions"]
            if position["position_type"] in ("horizon", "zenith")
        }
        seal_ids = {
            position["position_id"]
            for position in self.p1_topology["positions"]
            if position["position_type"] == "seal"
        }

        # E44-E46: only topology horizon/zenith IDs appear and players remain disjoint.
        self.assertEqual(occupancy_ids, domain_ids)
        self.assertTrue(occupancy_ids.isdisjoint(seal_ids))
        p2_topology = self.domain_position.create_player_domain_topology("P2")
        p2_occupancy = self.occupancy.create_empty_player_domain_occupancy(p2_topology)
        self.assertTrue(
            occupancy_ids.isdisjoint({slot["position_id"] for slot in p2_occupancy["slots"]})
        )

        # E47-E52: ownership, missing/extra slots, seals, and topology links are guarded.
        wrong_player = copy.deepcopy(occupancy)
        wrong_player["player_id"] = "P2"
        self.assertPlayerError(wrong_player, self.p1_topology, "PLAYER_ID_MISMATCH")

        missing_horizon = copy.deepcopy(occupancy)
        missing_horizon["slots"] = missing_horizon["slots"][1:]
        self.assertPlayerError(missing_horizon, self.p1_topology, "POSITION_SET_MISMATCH")
        missing_zenith = copy.deepcopy(occupancy)
        missing_zenith["slots"].pop(1)
        self.assertPlayerError(missing_zenith, self.p1_topology, "POSITION_SET_MISMATCH")

        extra_seal = copy.deepcopy(occupancy)
        seal_slot = copy.deepcopy(extra_seal["slots"][0])
        seal_slot.update(
            {
                "position_id": next(iter(seal_ids)),
                "position_type": "seal",
                "row": None,
            }
        )
        extra_seal["slots"].append(seal_slot)
        self.assertPlayerError(extra_seal, self.p1_topology, "SEAL_SLOT_UNEXPECTED")

        extra_unknown = copy.deepcopy(occupancy)
        unknown_slot = copy.deepcopy(extra_unknown["slots"][0])
        unknown_slot["position_id"] = "domain_P1_current_99_horizon"
        extra_unknown["slots"].append(unknown_slot)
        self.assertPlayerError(extra_unknown, self.p1_topology, "POSITION_SET_MISMATCH")

        wrong_link = copy.deepcopy(occupancy)
        wrong_link["slots"][0]["current_index"] = 2
        self.assertPlayerError(wrong_link, self.p1_topology, "SLOT_CURRENT_MISMATCH")

    def test_f_occupant_instance_identity_is_unique_per_player(self):
        occupancy = self.occupancy.create_empty_player_domain_occupancy(self.p1_topology)

        # F53: one non-null card instance cannot occupy two slots.
        duplicate = copy.deepcopy(occupancy)
        duplicate["slots"][0] = self._occupied(duplicate["slots"][0], "ci_P1_0001")
        duplicate["slots"][1] = self._occupied(duplicate["slots"][1], "ci_P1_0001")
        self.assertPlayerError(duplicate, self.p1_topology, "OCCUPANT_INSTANCE_DUPLICATE")

        # F54-F55: distinct identities and repeated nulls are structurally valid.
        distinct = copy.deepcopy(occupancy)
        distinct["slots"][0] = self._occupied(distinct["slots"][0], "ci_P1_0001")
        distinct["slots"][1] = self._occupied(distinct["slots"][1], "ci_P1_0002")
        self.assertTrue(
            self.occupancy.validate_player_domain_occupancy(distinct, self.p1_topology)["valid"]
        )
        self.assertTrue(
            self.occupancy.validate_player_domain_occupancy(occupancy, self.p1_topology)["valid"]
        )

    def test_g_lookup_returns_detached_supported_slots(self):
        occupancy = self.occupancy.create_empty_player_domain_occupancy(self.p1_topology)
        horizon_id = self._position("P1", 1, "horizon")["position_id"]
        zenith_id = self._position("P1", 1, "zenith")["position_id"]
        seal_id = self._position("P1", 1, "seal")["position_id"]

        # G56-G60: supported slots resolve; unknown/seal IDs fail; results are copies.
        horizon = self.occupancy.get_domain_position_occupancy(occupancy, horizon_id)
        zenith = self.occupancy.get_domain_position_occupancy(occupancy, zenith_id)
        self.assertEqual(horizon["position_type"], "horizon")
        self.assertEqual(zenith["position_type"], "zenith")
        with self.assertRaises(self.occupancy.DomainOccupancyError):
            self.occupancy.get_domain_position_occupancy(occupancy, "unknown-position")
        with self.assertRaises(self.occupancy.DomainOccupancyError):
            self.occupancy.get_domain_position_occupancy(occupancy, seal_id)
        self.assertIsNot(horizon, occupancy["slots"][0])

    def test_h_outputs_and_lookups_are_deeply_independent(self):
        topology = self.domain_position.create_player_domain_topology("P1")
        first = self.occupancy.create_empty_player_domain_occupancy(topology)
        second = self.occupancy.create_empty_player_domain_occupancy(topology)

        # H61-H65: calls, slots, topology input, and lookup results share no mutable state.
        self.assertIsNot(first["slots"], second["slots"])
        self.assertIsNot(first["slots"][0]["metadata"], first["slots"][1]["metadata"])
        self.assertIsNot(first["slots"][0]["metadata"], second["slots"][0]["metadata"])
        first["slots"][0]["metadata"]["source"] = "mutated"
        self.assertEqual(second["slots"][0]["metadata"]["source"], "python.engine.domain_occupancy")
        built_position_id = second["slots"][0]["position_id"]
        topology["positions"][0]["position_id"] = "mutated-topology-position"
        self.assertEqual(second["slots"][0]["position_id"], built_position_id)
        lookup = self.occupancy.get_domain_position_occupancy(second, built_position_id)
        lookup["metadata"]["source"] = "mutated-lookup"
        self.assertEqual(second["slots"][0]["metadata"]["source"], "python.engine.domain_occupancy")

    def test_i_output_excludes_runtime_and_gameplay_payloads(self):
        occupancy = self.occupancy.create_empty_player_domain_occupancy(self.p1_topology)

        # I66-I75: canonical output contains no definition, runtime, event, or gameplay payload.
        forbidden_keys = (
            "card_id",
            "card_instance",
            "card_instances",
            "object_reference",
            "topology",
            "match_state",
            "events",
            "event_log",
            "action",
            "actions",
            "legal_actions",
            "seal_state",
            "attackability",
            "targetability",
            "play_card",
        )
        for key in forbidden_keys:
            with self.subTest(key=key):
                self.assertFalse(_contains_key(occupancy, key))
        self.assertFalse(_contains_contract_type(occupancy, "card_instance_record"))
        self.assertFalse(_contains_contract_type(occupancy, "object_reference"))

        leaked_slot = copy.deepcopy(occupancy["slots"][0])
        leaked_slot["card_id"] = "IGN-HAM-001"
        self.assertIn(
            "UNEXPECTED_GAMEPLAY_FIELD",
            _error_codes(self.occupancy.validate_domain_position_occupancy(leaked_slot)),
        )
        leaked_player = copy.deepcopy(occupancy)
        leaked_player["event_log"] = []
        self.assertPlayerError(leaked_player, self.p1_topology, "UNEXPECTED_RUNTIME_STATE_FIELD")

    def test_additional_container_topology_and_metadata_guards(self):
        occupancy = self.occupancy.create_empty_player_domain_occupancy(self.p1_topology)
        result = self.occupancy.validate_player_domain_occupancy(None, self.p1_topology)
        self.assertIn("OCCUPANCY_NOT_DICT", _error_codes(result))

        invalid_topology = copy.deepcopy(self.p1_topology)
        invalid_topology["contract_type"] = "wrong_contract"
        result = self.occupancy.validate_player_domain_occupancy(occupancy, invalid_topology)
        self.assertIn("TOPOLOGY_INVALID", _error_codes(result))
        with self.assertRaises(self.occupancy.DomainOccupancyError):
            self.occupancy.create_empty_player_domain_occupancy(invalid_topology)

        invalid_metadata = copy.deepcopy(occupancy)
        invalid_metadata["metadata"]["slot_capacity"] = True
        self.assertPlayerError(invalid_metadata, self.p1_topology, "METADATA_INVALID")

        malformed_slot = copy.deepcopy(occupancy)
        malformed_slot["slots"][0]["current_index"] = []
        self.assertPlayerError(malformed_slot, self.p1_topology, "SLOT_RECORD_INVALID")

    def _position(self, player_id, current_index, position_type):
        return self.domain_position.create_domain_position_reference(
            player_id, current_index, position_type
        )

    def _empty_slot(self, player_id, current_index, position_type):
        return self.occupancy.create_empty_domain_position_occupancy(
            self._position(player_id, current_index, position_type)
        )

    @staticmethod
    def _occupied(slot, card_instance_id):
        occupied = copy.deepcopy(slot)
        occupied["occupancy_state"] = "occupied"
        occupied["occupant_object_type"] = "card_instance"
        occupied["occupant_card_instance_id"] = card_instance_id
        return occupied

    def assertPlayerError(self, occupancy, topology, code):
        result = self.occupancy.validate_player_domain_occupancy(occupancy, topology)
        self.assertFalse(result["valid"])
        self.assertIn(code, _error_codes(result))
        json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
