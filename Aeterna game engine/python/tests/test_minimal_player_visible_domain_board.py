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
BOARD_PATH = ENGINE_DIR / "domain_board_projection.py"
ENVIRONMENT_PATH = ENGINE_DIR / "minimal_engine_environment.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
SNAPSHOT_PATH = ENGINE_DIR / "player_visible_snapshot.py"
TRAJECTORY_PATH = ENGINE_DIR / "episode_trajectory.py"
INVARIANTS_PATH = AI_VS_AI_DIR / "state_invariants.py"
KERNEL_PATH = AI_VS_AI_DIR / "rules_kernel.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_PYTHON_DIR), str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestMinimalPlayerVisibleDomainBoard(unittest.TestCase):
    def setUp(self):
        self.board_module = _load_module("domain_board_projection", BOARD_PATH)
        self.snapshot_module = _load_module("player_visible_snapshot", SNAPSHOT_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.environment_module = _load_module("minimal_engine_environment", ENVIRONMENT_PATH)
        self.trajectory_module = _load_module("episode_trajectory", TRAJECTORY_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        self.deck_id_a, self.deck_id_b = _pick_two_decks(self.runtime_package)

    def test_a_initial_empty_board_contract(self):
        board = self._initial_board("BOARD-INITIAL-001")

        # A1-A5: canonical public board envelope and exactly two players.
        self.assertEqual(board["schema_version"], "minimal-player-visible-domain-board-v0")
        self.assertEqual(board["contract_type"], "player_visible_domain_board")
        self.assertEqual(board["board_model"], "minimal-public-domain-board-v0")
        self.assertEqual(board["visibility_mode"], "public")
        self.assertEqual(len(board["players"]), 2)

        # A6-A12: six currents, twelve empty slots, and six static seals per player.
        for player in board["players"]:
            self.assertEqual(len(player["currents"]), 6)
            self.assertEqual(player["empty_slot_count"], 12)
            self.assertEqual(player["occupied_slot_count"], 0)
            self.assertEqual([current["current_index"] for current in player["currents"]], list(range(1, 7)))
            self.assertTrue(all("horizon" in current and "zenith" in current for current in player["currents"]))
            self.assertTrue(all("seal_position" in current for current in player["currents"]))
            self.assertTrue(all(slot["occupant"] is None for slot in _slots(player)))

        # A13-A14: JSON-compatible and contract-valid.
        json.dumps(board, ensure_ascii=False)
        self.assertTrue(self.board_module.validate_player_visible_domain_board(board)["valid"])

    def test_b_structure_is_deterministic_and_player_scoped(self):
        first = self._initial_board("BOARD-DETERMINISM-001")
        second = self._initial_board("BOARD-DETERMINISM-001")
        other_match = self._initial_board("BOARD-DETERMINISM-OTHER")

        # B15-B20: player/current order and static identifiers are deterministic.
        self.assertEqual([player["player_id"] for player in first["players"]], ["P1", "P2"])
        for player in first["players"]:
            self.assertEqual([current["current_index"] for current in player["currents"]], list(range(1, 7)))
        self.assertTrue(_position_ids(_board_player(first, "P1")).isdisjoint(_position_ids(_board_player(first, "P2"))))
        for player in first["players"]:
            for current in player["currents"]:
                prefix = "domain_%s_current_%02d" % (player["player_id"], current["current_index"])
                self.assertEqual(current["current_id"], prefix)
                self.assertEqual(current["horizon"]["position_id"], prefix + "_horizon")
                self.assertEqual(current["zenith"]["position_id"], prefix + "_zenith")
                self.assertEqual(current["seal_position"]["position_id"], prefix + "_seal")
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertEqual(_all_position_ids(first), _all_position_ids(other_match))

    def test_c_synthetic_occupied_horizon_uses_canonical_object_reference(self):
        state = self._create_state("BOARD-OCCUPIED-HORIZON-001")
        card_instance_id = self._bind_domain_instance(state, "P1", slot_index=0)
        record = deepcopy(state.card_instances[card_instance_id])
        board = self.board_module.create_player_visible_domain_board(state)
        player = _board_player(board, "P1")
        slot = player["currents"][0]["horizon"]

        # C21-C34: occupied horizon projects one canonical public ObjectReference.
        self.assertTrue(slot["occupied"])
        self.assertEqual(slot["occupancy_state"], "occupied")
        self.assertIs(slot["occupied"], True)
        self.assertEqual(slot["occupant"]["contract_type"], "object_reference")
        self.assertEqual(slot["occupant"]["object_type"], "card_instance")
        self.assertEqual(slot["occupant"]["object_id"], card_instance_id)
        self.assertEqual(slot["occupant"]["card_id"], record["card_id"])
        self.assertEqual(slot["occupant"]["zone"], "domain")
        self.assertEqual(slot["occupant"]["visibility"], "public")
        self.assertEqual(slot["occupant"]["controller_player_id"], "P1")
        self.assertEqual(slot["occupant"]["zone_sequence"], record["zone_sequence"])
        self.assertEqual(player["occupied_slot_count"], 1)
        self.assertEqual(player["empty_slot_count"], 11)
        self.assertTrue(self.board_module.validate_player_visible_domain_board(board)["valid"])

    def test_d_zenith_multiple_occupants_and_duplicate_guard(self):
        state = self._create_state("BOARD-OCCUPIED-MULTIPLE-001")
        first_id = self._bind_domain_instance(state, "P1", slot_index=1)
        second_id = self._bind_domain_instance(state, "P1", slot_index=2)
        board = self.board_module.create_player_visible_domain_board(state)
        player = _board_player(board, "P1")

        # D35-D38: zenith and a second distinct slot can be occupied independently.
        self.assertEqual(player["currents"][0]["zenith"]["occupant"]["card_instance_id"], first_id)
        self.assertEqual(
            {slot["occupant"]["card_instance_id"] for slot in _slots(player) if slot["occupied"]},
            {first_id, second_id},
        )
        self.assertEqual(player["occupied_slot_count"], 2)
        self.assertTrue(all(slot["occupant"] is None for slot in _slots(player) if not slot["occupied"]))

        # D39: a duplicated projected occupant is rejected board-wide.
        duplicate = deepcopy(board)
        occupied_slots = [slot for slot in _slots(_board_player(duplicate, "P1")) if slot["occupied"]]
        occupied_slots[1]["occupant"] = deepcopy(occupied_slots[0]["occupant"])
        result = self.board_module.validate_player_visible_domain_board(duplicate)
        self.assertIn("OCCUPANT_INSTANCE_DUPLICATE", _error_codes(result))

    def test_e_controller_is_authoritative_for_domain_projection(self):
        # E40: ordinary owner/controller P1 is valid.
        own_state = self._create_state("BOARD-CONTROLLER-OWN-001")
        self._bind_domain_instance(own_state, "P1", source_player_id="P1")
        self.assertTrue(self.board_module.validate_player_visible_domain_board(
            self.board_module.create_player_visible_domain_board(own_state)
        )["valid"])

        # E41: owner P2/controller P1 is valid and public in P1's Domain.
        controlled_state = self._create_state("BOARD-CONTROLLER-CONTROLLED-001")
        controlled_id = self._bind_domain_instance(
            controlled_state, "P1", source_player_id="P2", controller_player_id="P1"
        )
        board = self.board_module.create_player_visible_domain_board(controlled_state)
        occupant = _board_player(board, "P1")["currents"][0]["horizon"]["occupant"]
        self.assertEqual(controlled_state.card_instances[controlled_id]["owner_player_id"], "P2")
        self.assertEqual(occupant["controller_player_id"], "P1")

        # E42-E43: wrong and unknown controllers are rejected before projection.
        for controller in ("P2", "P3"):
            with self.subTest(controller=controller):
                invalid = self._create_state("BOARD-CONTROLLER-INVALID-%s" % controller)
                self._bind_domain_instance(
                    invalid,
                    "P1",
                    controller_player_id=controller,
                    validate_state=False,
                )
                with self.assertRaises(self.board_module.DomainBoardProjectionError):
                    self.board_module.create_player_visible_domain_board(invalid)

    def test_f_seal_is_only_a_static_public_reference(self):
        board = self._initial_board("BOARD-SEAL-001")
        seal = _board_player(board, "P1")["currents"][0]["seal_position"]

        # F44-F49: seal identity is present while all runtime seal state remains absent.
        self.assertEqual(seal["position_type"], "seal")
        self.assertEqual(seal["state_model"], "not_implemented")
        self.assertNotIn("occupancy_state", seal)
        self.assertNotIn("occupant", seal)
        self.assertNotIn("card_instance_id", seal)
        self.assertFalse(any(key in seal for key in ("hp", "broken", "broken_state")))

    def test_g_invalid_state_never_produces_a_partial_board(self):
        cases = []
        missing_topology = self._create_state("BOARD-INVALID-MISSING-TOPOLOGY")
        missing_topology.domain_topologies.pop("P1")
        cases.append(missing_topology)  # G50
        missing_occupancy = self._create_state("BOARD-INVALID-MISSING-OCCUPANCY")
        missing_occupancy.domain_occupancies.pop("P1")
        cases.append(missing_occupancy)  # G51
        invalid_occupancy = self._create_state("BOARD-INVALID-OCCUPANCY")
        invalid_occupancy.domain_occupancies["P1"]["slots"].pop()
        cases.append(invalid_occupancy)  # G52
        unknown = self._create_state("BOARD-INVALID-UNKNOWN-OCCUPANT")
        self._set_slot_occupied(unknown, "P1", 0, "ci_UNKNOWN_9999")
        cases.append(unknown)  # G53
        wrong_zone = self._create_state("BOARD-INVALID-ZONE")
        wrong_zone_id = self._bind_domain_instance(wrong_zone, "P1")
        wrong_zone.card_instances[wrong_zone_id]["zone"] = "hand"
        cases.append(wrong_zone)  # G54
        hidden = self._create_state("BOARD-INVALID-VISIBILITY")
        hidden_id = self._bind_domain_instance(hidden, "P1")
        hidden.card_instances[hidden_id]["visibility"] = "owner_only"
        cases.append(hidden)  # G55
        controller = self._create_state("BOARD-INVALID-CONTROLLER")
        self._bind_domain_instance(
            controller,
            "P1",
            controller_player_id="P2",
            validate_state=False,
        )
        cases.append(controller)  # G56

        # G50-G57: every invalid state raises the controlled error; no partial dict escapes.
        for state in cases:
            with self.subTest(match_id=state.match_id):
                with self.assertRaises(self.board_module.DomainBoardProjectionError) as context:
                    self.board_module.create_player_visible_domain_board(state)
                self.assertTrue(context.exception.errors)

    def test_h_board_validator_negative_contract_cases(self):
        valid = self._initial_board("BOARD-VALIDATOR-001")
        cases = []
        cases.append(("BOARD_NOT_DICT", None))  # H58
        missing_player = deepcopy(valid)
        missing_player["players"].pop()
        cases.append(("PLAYERS_INVALID", missing_player))  # H59
        duplicate_player = deepcopy(valid)
        duplicate_player["players"][1]["player_id"] = "P1"
        cases.append(("PLAYER_ID_DUPLICATE", duplicate_player))  # H60
        five_currents = deepcopy(valid)
        five_currents["players"][0]["currents"].pop()
        cases.append(("CURRENT_COUNT_INVALID", five_currents))  # H61
        seven_currents = deepcopy(valid)
        seven_currents["players"][0]["currents"].append(deepcopy(seven_currents["players"][0]["currents"][0]))
        cases.append(("CURRENT_COUNT_INVALID", seven_currents))  # H62
        missing_horizon = deepcopy(valid)
        missing_horizon["players"][0]["currents"][0].pop("horizon")
        cases.append(("SLOT_PROJECTION_INVALID", missing_horizon))  # H63
        missing_zenith = deepcopy(valid)
        missing_zenith["players"][0]["currents"][0].pop("zenith")
        cases.append(("SLOT_PROJECTION_INVALID", missing_zenith))  # H64
        bad_seal = deepcopy(valid)
        bad_seal["players"][0]["currents"][0]["seal_position"]["occupant"] = {}
        cases.append(("SEAL_PROJECTION_INVALID", bad_seal))  # H65
        empty_with_occupant = deepcopy(valid)
        empty_with_occupant["players"][0]["currents"][0]["horizon"]["occupant"] = {}
        cases.append(("SLOT_OCCUPANCY_MISMATCH", empty_with_occupant))  # H66

        occupied_state = self._create_state("BOARD-VALIDATOR-OCCUPIED")
        self._bind_domain_instance(occupied_state, "P1")
        occupied_board = self.board_module.create_player_visible_domain_board(occupied_state)
        occupied_null = deepcopy(occupied_board)
        occupied_null["players"][0]["currents"][0]["horizon"]["occupant"] = None
        cases.append(("SLOT_OCCUPANCY_MISMATCH", occupied_null))  # H67
        wrong_zone = deepcopy(occupied_board)
        wrong_zone["players"][0]["currents"][0]["horizon"]["occupant"]["zone"] = "hand"
        cases.append(("OBJECT_REFERENCE_ZONE_INVALID", wrong_zone))  # H68
        wrong_controller = deepcopy(occupied_board)
        wrong_controller["players"][0]["currents"][0]["horizon"]["occupant"]["controller_player_id"] = "P2"
        cases.append(("OBJECT_REFERENCE_CONTROLLER_MISMATCH", wrong_controller))  # H69
        duplicate_occupant = deepcopy(occupied_board)
        first_slot = duplicate_occupant["players"][0]["currents"][0]["horizon"]
        second_slot = duplicate_occupant["players"][0]["currents"][0]["zenith"]
        second_slot.update({"occupancy_state": "occupied", "occupied": True, "occupant": deepcopy(first_slot["occupant"])})
        duplicate_occupant["players"][0]["occupied_slot_count"] = 2
        duplicate_occupant["players"][0]["empty_slot_count"] = 10
        cases.append(("OCCUPANT_INSTANCE_DUPLICATE", duplicate_occupant))  # H70

        for expected_code, invalid in cases:
            with self.subTest(expected_code=expected_code):
                result = self.board_module.validate_player_visible_domain_board(invalid)
                self.assertFalse(result["valid"], result)
                self.assertIn(expected_code, _error_codes(result), result)
                json.dumps(result, ensure_ascii=False)

    def test_i_player_snapshot_v2_preserves_hidden_information_policy(self):
        session = self._create_session("BOARD-SNAPSHOT-V2-001")
        self._submit_action(session, "draw_card")
        p1_snapshot = session.get_player_snapshot("P1")
        p2_snapshot = session.get_player_snapshot("P2")

        # I71-I76: v2 embeds one validated viewer-independent public board.
        self.assertEqual(p1_snapshot["schema_version"], "engine-player-visible-snapshot-v2")
        self.assertIn("board", p1_snapshot)
        self.assertEqual(p1_snapshot["metadata"]["board_model"], "minimal-public-domain-board-v0")
        self.assertEqual(p1_snapshot["visibility_policy"]["board"], "public")
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(p1_snapshot)["valid"])
        self.assertEqual(p1_snapshot["board"], p2_snapshot["board"])

        # I77-I82: hand/deck redaction remains unchanged; internal contracts do not leak.
        self.assertEqual(_snapshot_player(p1_snapshot, "P1")["zones"]["hand"]["visibility_mode"], "owner_visible")
        self.assertEqual(_snapshot_player(p2_snapshot, "P1")["zones"]["hand"]["objects"], [])
        self.assertTrue(all(player["zones"]["deck"]["visibility_mode"] == "count_only" for player in p1_snapshot["players"]))
        self.assertFalse(_contains_key(p1_snapshot, "card_instances"))
        self.assertFalse(_contains_contract_type(p1_snapshot, "player_domain_occupancy"))
        self.assertFalse(_contains_contract_type(p1_snapshot, "player_domain_topology"))

    def test_j_environment_and_trajectory_use_only_the_canonical_public_board(self):
        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)
        initial = environment.reset(
            match_id="BOARD-ENVIRONMENT-001",
            deck_id_a=self.deck_id_a,
            deck_id_b=self.deck_id_b,
        )
        initial_board = deepcopy(initial["player_snapshot"]["board"])

        # J83-J87: canonical v2 observation starts empty; draw/end_turn do not mutate board.
        self.assertEqual(initial["player_snapshot"]["schema_version"], "engine-player-visible-snapshot-v2")
        self.assertEqual(sum(player["occupied_slot_count"] for player in initial_board["players"]), 0)
        draw = _enabled_action(environment.get_action_space(), "draw_card")
        draw_response = environment.step(environment.session.build_action_request(draw))
        after_draw = environment.get_observation()
        self.assertEqual(after_draw["player_snapshot"]["board"], initial_board)
        end_turn = _enabled_action(environment.get_action_space(), "end_turn")
        environment.step(environment.session.build_action_request(end_turn))
        after_end = environment.get_observation()
        self.assertEqual(after_end["player_snapshot"]["board"], initial_board)
        self.assertTrue(draw_response["accepted"])

        # J88-J91: trajectory remains valid, contains only snapshot board, and is deterministic.
        first_episode = self.environment_module.MinimalEngineEnvironment(self.runtime_package).run_episode(
            max_steps=4, match_id="BOARD-EPISODE-DETERMINISM-001"
        )
        second_episode = self.environment_module.MinimalEngineEnvironment(self.runtime_package).run_episode(
            max_steps=4, match_id="BOARD-EPISODE-DETERMINISM-001"
        )
        self.assertTrue(first_episode["trajectory_validation"]["valid"])
        self.assertTrue(all(
            step["observation_before"]["player_snapshot"]["board"]["visibility_mode"] == "public"
            for step in first_episode["trajectory"]
        ))
        self.assertFalse(_contains_key(first_episode["trajectory"], "domain_occupancies"))
        self.assertEqual(
            json.dumps(first_episode, ensure_ascii=False, sort_keys=True),
            json.dumps(second_episode, ensure_ascii=False, sort_keys=True),
        )

    def test_k_projection_is_deeply_detached_from_state_and_other_snapshots(self):
        session = self._create_session("BOARD-DEEP-COPY-001")
        card_instance_id = self._bind_domain_instance(session.state, "P1")
        registry_before = deepcopy(session.state.card_instances[card_instance_id])
        occupancy_before = deepcopy(session.state.domain_occupancies)
        topology_before = deepcopy(session.state.domain_topologies)
        p1_snapshot = session.get_player_snapshot("P1")
        p2_snapshot = session.get_player_snapshot("P2")
        board = p1_snapshot["board"]
        occupied_slot = _board_player(board, "P1")["currents"][0]["horizon"]

        # K92-K94: mutating projected occupant, slot, or current list cannot mutate authority.
        occupied_slot["occupant"]["card_id"] = "MUTATED"
        self.assertEqual(session.state.card_instances[card_instance_id], registry_before)
        occupied_slot["occupancy_state"] = "empty"
        self.assertEqual(session.state.domain_occupancies, occupancy_before)
        _board_player(board, "P1")["currents"].pop()
        self.assertEqual(session.state.domain_topologies, topology_before)

        # K95-K97: snapshots and nested metadata are independent and rebuild canonically.
        self.assertEqual(len(_board_player(p2_snapshot["board"], "P1")["currents"]), 6)
        fresh = session.get_player_snapshot("P1")
        self.assertEqual(
            _board_player(fresh["board"], "P1")["currents"][0]["horizon"]["occupant"]["card_id"],
            registry_before["card_id"],
        )
        self.assertIsNot(
            _board_player(fresh["board"], "P1")["currents"][0]["horizon"]["metadata"],
            _board_player(p2_snapshot["board"], "P1")["currents"][0]["horizon"]["metadata"],
        )

    def test_l_board_excludes_runtime_and_gameplay_internal_data(self):
        state = self._create_state("BOARD-FORBIDDEN-DATA-001")
        self._bind_domain_instance(state, "P1")
        board = self.board_module.create_player_visible_domain_board(state)
        serialized = json.dumps(board, ensure_ascii=False).lower()

        # L98-L108: board exports only the public projection boundary.
        for forbidden_key in ("deck_card_instance_ids", "hand_card_instance_ids", "discard_card_instance_ids"):
            self.assertFalse(_contains_key(board, forbidden_key), forbidden_key)
        self.assertFalse(_contains_contract_type(board, "card_instance_record"))
        self.assertFalse(_contains_key(board, "match_state"))
        self.assertFalse(_contains_key(board, "event_log"))
        self.assertFalse(_contains_key(board, "legal_actions"))
        self.assertNotIn("attackability", serialized)
        self.assertNotIn("targetability", serialized)
        self.assertNotIn("play_card", serialized)
        self.assertFalse(_contains_key(board, "seal_state"))
        self.assertFalse(_contains_key(board, "occupant_card_instance_id"))

    def test_snapshot_validator_preserves_nested_board_errors_and_player_set_mismatch(self):
        session = self._create_session("BOARD-SNAPSHOT-VALIDATOR-001")
        snapshot = session.get_player_snapshot("P1")
        invalid_board = deepcopy(snapshot)
        invalid_board["board"]["players"][0]["currents"][0]["horizon"]["visibility"] = "hidden"
        result = self.snapshot_module.validate_player_visible_snapshot(invalid_board)
        self.assertIn("BOARD_PROJECTION_INVALID", _error_codes(result))
        parent = next(error for error in result["errors"] if error["code"] == "BOARD_PROJECTION_INVALID")
        self.assertIn("VISIBILITY_INVALID", _collect_diagnostic_codes(parent["board_errors"]))

        mismatch = deepcopy(snapshot)
        mismatch["board"]["players"][1]["player_id"] = "PX"
        result = self.snapshot_module.validate_player_visible_snapshot(mismatch)
        self.assertIn("BOARD_PLAYER_SET_MISMATCH", _error_codes(result))

    def test_synthetic_public_board_is_identical_for_both_viewers(self):
        session = self._create_session("BOARD-SYNTHETIC-VIEWERS-001")
        self._submit_action(session, "draw_card")
        card_instance_id = self._bind_domain_instance(session.state, "P1", source_player_id="P2")
        p1 = session.get_player_snapshot("P1")
        p2 = session.get_player_snapshot("P2")

        self.assertEqual(p1["board"], p2["board"])
        occupant = _board_player(p1["board"], "P1")["currents"][0]["horizon"]["occupant"]
        self.assertEqual(occupant["card_instance_id"], card_instance_id)
        self.assertEqual(occupant["visibility"], "public")
        self.assertEqual(_snapshot_player(p2, "P1")["zones"]["hand"]["objects"], [])
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(p1)["valid"])
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(p2)["valid"])

    def _initial_board(self, match_id):
        return self.board_module.create_player_visible_domain_board(self._create_state(match_id))

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
        action = _enabled_action(session.get_action_space(), action_type)
        response = session.step(session.build_action_request(action))
        self.assertTrue(response["accepted"])
        return response

    def _bind_domain_instance(
        self,
        state,
        occupancy_player_id,
        slot_index=0,
        source_player_id=None,
        controller_player_id=None,
        validate_state=True,
    ):
        source_player = state.get_player(source_player_id or occupancy_player_id)
        card_instance_id = source_player.deck_card_instance_ids[0]
        self._remove_instance_from_list_zones(state, card_instance_id)
        record = state.card_instances[card_instance_id]
        record["zone"] = "domain"
        record["zone_index"] = None
        record["visibility"] = "public"
        record["controller_player_id"] = controller_player_id or occupancy_player_id
        record["activity_state"] = "active"
        record["zone_sequence"] += 1
        self._set_slot_occupied(state, occupancy_player_id, slot_index, card_instance_id)
        if validate_state:
            self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])
        return card_instance_id

    @staticmethod
    def _set_slot_occupied(state, player_id, slot_index, card_instance_id):
        slot = state.domain_occupancies[player_id]["slots"][slot_index]
        slot["occupancy_state"] = "occupied"
        slot["occupant_object_type"] = "card_instance"
        slot["occupant_card_instance_id"] = card_instance_id

    @staticmethod
    def _remove_instance_from_list_zones(state, card_instance_id):
        for player in state.players:
            for zone_name in ("deck", "hand", "discard"):
                zone = getattr(player, "%s_card_instance_ids" % zone_name)
                while card_instance_id in zone:
                    zone.remove(card_instance_id)
                for zone_index, remaining_id in enumerate(zone):
                    record = state.card_instances[remaining_id]
                    record["zone"] = zone_name
                    record["zone_index"] = zone_index


def _board_player(board, player_id):
    return next(player for player in board["players"] if player["player_id"] == player_id)


def _snapshot_player(snapshot, player_id):
    return next(player for player in snapshot["players"] if player["player_id"] == player_id)


def _slots(player):
    return [slot for current in player["currents"] for slot in (current["horizon"], current["zenith"])]


def _position_ids(player):
    return {
        position["position_id"]
        for current in player["currents"]
        for position in (current["horizon"], current["zenith"], current["seal_position"])
    }


def _all_position_ids(board):
    return {player["player_id"]: sorted(_position_ids(player)) for player in board["players"]}


def _enabled_action(action_space, action_type):
    return next(
        action
        for action in action_space["actions"]
        if action["action_type"] == action_type and action["enabled"] is True
    )


def _contains_key(value, key):
    if isinstance(value, dict):
        return key in value or any(_contains_key(nested, key) for nested in value.values())
    if isinstance(value, list):
        return any(_contains_key(nested, key) for nested in value)
    return False


def _contains_contract_type(value, contract_type):
    if isinstance(value, dict):
        return value.get("contract_type") == contract_type or any(
            _contains_contract_type(nested, contract_type) for nested in value.values()
        )
    if isinstance(value, list):
        return any(_contains_contract_type(nested, contract_type) for nested in value)
    return False


def _error_codes(result):
    return {error.get("code") for error in result.get("errors", [])}


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
