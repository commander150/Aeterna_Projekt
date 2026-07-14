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

CARD_INSTANCE_PATH = ENGINE_DIR / "card_instance.py"
BOARD_PATH = ENGINE_DIR / "domain_board_projection.py"
PLACEMENT_PATH = ENGINE_DIR / "entity_domain_placement.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
ENVIRONMENT_PATH = ENGINE_DIR / "minimal_engine_environment.py"
PLAYER_SNAPSHOT_PATH = ENGINE_DIR / "player_visible_snapshot.py"
KERNEL_PATH = AI_VS_AI_DIR / "rules_kernel.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"
INVARIANTS_PATH = AI_VS_AI_DIR / "state_invariants.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_PYTHON_DIR), str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestMinimalCardInstanceActivityState(unittest.TestCase):
    def setUp(self):
        self.card_instance = _load_module("card_instance", CARD_INSTANCE_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.board = _load_module("domain_board_projection", BOARD_PATH)
        self.placement = _load_module("entity_domain_placement", PLACEMENT_PATH)
        self.player_snapshot = _load_module("player_visible_snapshot", PLAYER_SNAPSHOT_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.environment_module = _load_module("minimal_engine_environment", ENVIRONMENT_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        self.deck_id_a, self.deck_id_b = sorted(self.runtime_package.decks_by_id)[:2]

    def test_a_builder_and_schema_v1_contract(self):
        metadata = {"source": "activity_state_test"}
        default_record = self._record("deck", metadata=metadata)
        active_record = self._record("domain", activity_state="active")
        exhausted_record = self._record("domain", activity_state="exhausted")

        # A1-A5: v1 always carries one of the explicit canonical values.
        self.assertEqual(default_record["schema_version"], "minimal-card-instance-record-v1")
        self.assertIn("activity_state", default_record)
        self.assertIsNone(default_record["activity_state"])
        self.assertEqual(active_record["activity_state"], "active")
        self.assertEqual(exhausted_record["activity_state"], "exhausted")

        # A6-A7: metadata remains detached and the complete record round-trips.
        default_record["metadata"]["source"] = "changed"
        self.assertEqual(metadata, {"source": "activity_state_test"})
        self.assertEqual(json.loads(json.dumps(exhausted_record, ensure_ascii=False)), exhausted_record)

    def test_b_record_validator_enforces_activity_and_zone_rules(self):
        valid_cases = (
            ("deck", None),
            ("hand", None),
            ("discard", None),
            ("domain", "active"),
            ("domain", "exhausted"),
        )
        for zone, activity_state in valid_cases:
            with self.subTest(zone=zone, activity_state=activity_state):
                self.assertTrue(
                    self.card_instance.validate_card_instance_record(
                        self._record(zone, activity_state=activity_state)
                    )["valid"]
                )

        invalid_zone_cases = (
            ("deck", "active"),
            ("hand", "exhausted"),
            ("discard", "active"),
            ("domain", None),
        )
        for zone, activity_state in invalid_zone_cases:
            with self.subTest(zone=zone, activity_state=activity_state):
                result = self.card_instance.validate_card_instance_record(
                    self._record(zone, activity_state=activity_state)
                )
                self.assertFalse(result["valid"])
                self.assertIn("ACTIVITY_STATE_ZONE_MISMATCH", _codes(result["errors"]))

        for activity_state in ("ready", True, 1, ["active"], {"value": "active"}):
            with self.subTest(activity_state=activity_state):
                result = self.card_instance.validate_card_instance_record(
                    self._record("deck", activity_state=activity_state)
                )
                self.assertFalse(result["valid"])
                self.assertIn("ACTIVITY_STATE_INVALID", _codes(result["errors"]))

        missing_activity = self._record("deck")
        missing_activity.pop("activity_state")
        missing_result = self.card_instance.validate_card_instance_record(missing_activity)
        self.assertFalse(missing_result["valid"])
        self.assertIn("FIELD_MISSING", _codes(missing_result["errors"]))

        old_schema = self._record("deck")
        old_schema["schema_version"] = "minimal-card-instance-record-v0"
        old_result = self.card_instance.validate_card_instance_record(old_schema)
        self.assertFalse(old_result["valid"])
        self.assertIn("SCHEMA_VERSION_INVALID", _codes(old_result["errors"]))

        non_dict_result = self.card_instance.validate_card_instance_record(None)
        self.assertFalse(non_dict_result["valid"])
        self.assertIn("RECORD_NOT_DICT", _codes(non_dict_result["errors"]))
        json.dumps(non_dict_result, ensure_ascii=False)

    def test_c_initial_production_state_uses_null_activity_deterministically(self):
        first = self._create_state("ACTIVITY-INITIAL-DETERMINISTIC-001")
        second = self._create_state("ACTIVITY-INITIAL-DETERMINISTIC-001")
        activity_states = [record["activity_state"] for record in first.card_instances.values()]

        # C24-C28: all production setup records are canonical deck records.
        self.assertTrue(activity_states)
        self.assertTrue(all(value is None for value in activity_states))
        self.assertNotIn("active", activity_states)
        self.assertNotIn("exhausted", activity_states)
        self.assertEqual(self.invariants.validate_state_invariants(first, self.runtime_package), [])
        self.assertEqual(first.card_instances, second.card_instances)
        self.assertEqual(
            [player.deck_card_instance_ids for player in first.players],
            [player.deck_card_instance_ids for player in second.players],
        )

    def test_d_draw_preserves_null_activity_and_existing_contracts(self):
        session = self._create_session("ACTIVITY-DRAW-001")
        player = session.state.get_player("P1")
        drawn_id = player.deck_card_instance_ids[0]
        before = self._activity_map(session.state)

        self.assertIsNone(before[drawn_id])
        response = self._step(session, "draw_card")
        after = self._activity_map(session.state)

        # D29-D34: draw changes the zone, not the activity or existing contracts.
        self.assertIn(drawn_id, player.hand_card_instance_ids)
        self.assertIsNone(after[drawn_id])
        self.assertEqual(
            {key: value for key, value in before.items() if key != drawn_id},
            {key: value for key, value in after.items() if key != drawn_id},
        )
        event = response["events"][0]
        self.assertEqual(event["schema_version"], "minimal-engine-event-v0")
        self.assertEqual(event["contract_type"], "engine_event")
        self.assertEqual(event["event_type"], "zone_move")
        self.assertEqual(response["schema_version"], "minimal-action-response-v0")
        self.assertEqual(response["contract_type"], "action_response")
        self.assertFalse(_contains_key(event, "activity_state"))
        self.assertEqual(self.invariants.validate_state_invariants(session.state, self.runtime_package), [])

    def test_e_end_turn_does_not_change_or_restore_activity(self):
        session = self._create_session("ACTIVITY-END-TURN-001")
        exhausted_id = self._bind_domain_instance(
            session.state,
            occupancy_player_id="P1",
            activity_state="exhausted",
        )
        before = self._activity_map(session.state)

        response = self._step(session, "end_turn")
        after = self._activity_map(session.state)

        # E35-E39: end_turn remains only a typed turn transition.
        self.assertEqual(after, before)
        self.assertEqual(after[exhausted_id], "exhausted")
        event = response["events"][0]
        self.assertFalse(_contains_key(event, "activity_state"))
        self.assertEqual(event["schema_version"], "minimal-engine-event-v0")
        self.assertEqual(event["contract_type"], "engine_event")
        self.assertEqual(event["event_type"], "turn_transition")
        self.assertEqual(event["payload"]["schema_version"], "minimal-turn-transition-record-v0")
        self.assertEqual(event["payload"]["contract_type"], "turn_transition")
        self.assertEqual(self.invariants.validate_state_invariants(session.state, self.runtime_package), [])

    def test_f_active_domain_occupant_is_structurally_valid(self):
        state = self._create_state("ACTIVITY-DOMAIN-ACTIVE-001")
        occupant_id = self._bind_domain_instance(state, "P1", "active")
        errors = self.invariants.validate_state_invariants(state, self.runtime_package)
        occupancy = state.get_domain_occupancy("P1")

        # F40-F44: active is canonical and remains internal to the registry.
        self.assertEqual(errors, [])
        self.assertEqual(occupancy["slots"][0]["occupant_card_instance_id"], occupant_id)
        self.assertEqual(state.card_instances[occupant_id]["activity_state"], "active")
        board = self.board.create_player_visible_domain_board(state)
        self.assertEqual(board["schema_version"], "minimal-player-visible-domain-board-v0")
        references = _object_references(board)
        self.assertTrue(any(reference.get("card_instance_id") == occupant_id for reference in references))
        self.assertTrue(all("activity_state" not in reference for reference in references))

        source_id = self._find_instance(state, "entity", "P1", excluded_ids={occupant_id})
        self._put_instance_in_hand(state, source_id, "P1")
        self.assertIsNone(state.card_instances[source_id]["activity_state"])
        options = self.placement.list_structural_entity_domain_placement_options(
            state,
            self.runtime_package,
            "P1",
            source_id,
        )
        self.assertTrue(self.placement.validate_entity_domain_placement_options(options)["valid"])
        self.assertEqual(options["schema_version"], "minimal-entity-domain-placement-options-v0")
        self.assertNotIn("activity_state", options["source_card"])
        self.assertIn("entry_state", options["unchecked_requirements"])
        self.assertNotIn("position_id", state.card_instances[occupant_id])

    def test_g_exhausted_domain_occupant_remains_valid_and_occupied(self):
        state = self._create_state("ACTIVITY-DOMAIN-EXHAUSTED-001")
        occupant_id = self._bind_domain_instance(state, "P1", "exhausted")

        # G45-G49: exhausted is valid and does not imply removal from Domain.
        self.assertEqual(state.card_instances[occupant_id]["activity_state"], "exhausted")
        occupancy = state.get_domain_occupancy("P1")
        self.assertEqual(occupancy["slots"][0]["occupant_card_instance_id"], occupant_id)
        board = self.board.create_player_visible_domain_board(state)
        self.assertTrue(any(
            reference.get("card_instance_id") == occupant_id
            for reference in _object_references(board)
        ))
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])
        self.assertEqual(
            state.domain_occupancies["P1"]["slots"][0]["occupancy_state"],
            "occupied",
        )

    def test_h_invalid_activity_state_reports_authoritative_diagnostics(self):
        domain_null = self._create_state("ACTIVITY-INVALID-DOMAIN-NULL-001")
        self._bind_domain_instance(domain_null, "P1", None)
        null_codes = _codes(self.invariants.validate_state_invariants(domain_null, self.runtime_package))
        self.assertIn("CARD_INSTANCE_ACTIVITY_ZONE_MISMATCH", null_codes)
        self.assertIn("DOMAIN_OCCUPANT_ACTIVITY_STATE_INVALID", null_codes)

        domain_unknown = self._create_state("ACTIVITY-INVALID-DOMAIN-UNKNOWN-001")
        self._bind_domain_instance(domain_unknown, "P1", "ready")
        unknown_codes = _codes(self.invariants.validate_state_invariants(domain_unknown, self.runtime_package))
        self.assertIn("CARD_INSTANCE_ACTIVITY_STATE_INVALID", unknown_codes)
        self.assertIn("DOMAIN_OCCUPANT_ACTIVITY_STATE_INVALID", unknown_codes)

        occupied_deck = self._create_state("ACTIVITY-INVALID-OCCUPIED-DECK-001")
        deck_id = occupied_deck.get_player("P1").deck_card_instance_ids[0]
        self._set_slot_occupied(occupied_deck, "P1", 0, deck_id)
        deck_codes = _codes(self.invariants.validate_state_invariants(occupied_deck, self.runtime_package))
        self.assertIn("DOMAIN_OCCUPANT_ZONE_MISMATCH", deck_codes)

        active_hand = self._create_state("ACTIVITY-INVALID-ACTIVE-HAND-001")
        active_id = active_hand.get_player("P1").deck_card_instance_ids[0]
        self._put_instance_in_hand(active_hand, active_id, "P1")
        active_hand.card_instances[active_id]["activity_state"] = "active"
        hand_codes = _codes(self.invariants.validate_state_invariants(active_hand, self.runtime_package))
        self.assertIn("CARD_INSTANCE_ACTIVITY_ZONE_MISMATCH", hand_codes)

        overlap = self._create_state("ACTIVITY-INVALID-MULTIPLE-ZONES-001")
        overlap_id = self._bind_domain_instance(overlap, "P1", "active")
        overlap.get_player("P1").hand_card_instance_ids.append(overlap_id)
        overlap_codes = _codes(self.invariants.validate_state_invariants(overlap, self.runtime_package))
        self.assertIn("CARD_INSTANCE_MULTIPLE_ZONES", overlap_codes)

    def test_i_activity_is_independent_from_owner_and_controller(self):
        own = self._create_state("ACTIVITY-AUTHORITY-OWN-001")
        own_id = self._bind_domain_instance(own, "P1", "active")
        self.assertEqual(own.card_instances[own_id]["owner_player_id"], "P1")
        self.assertEqual(own.card_instances[own_id]["controller_player_id"], "P1")
        self.assertEqual(self.invariants.validate_state_invariants(own, self.runtime_package), [])

        controlled = self._create_state("ACTIVITY-AUTHORITY-CONTROLLED-001")
        controlled_id = self._bind_domain_instance(
            controlled,
            occupancy_player_id="P1",
            activity_state="active",
            source_player_id="P2",
            controller_player_id="P1",
        )
        self.assertEqual(controlled.card_instances[controlled_id]["owner_player_id"], "P2")
        self.assertEqual(controlled.card_instances[controlled_id]["controller_player_id"], "P1")
        self.assertEqual(self.invariants.validate_state_invariants(controlled, self.runtime_package), [])

        mismatch = self._create_state("ACTIVITY-AUTHORITY-MISMATCH-001")
        mismatch_id = self._bind_domain_instance(
            mismatch,
            occupancy_player_id="P1",
            activity_state="active",
            source_player_id="P2",
            controller_player_id="P2",
        )
        mismatch_codes = _codes(self.invariants.validate_state_invariants(mismatch, self.runtime_package))
        self.assertIn("DOMAIN_OCCUPANT_CONTROLLER_MISMATCH", mismatch_codes)
        mismatch.card_instances[mismatch_id]["activity_state"] = "exhausted"
        exhausted_codes = _codes(self.invariants.validate_state_invariants(mismatch, self.runtime_package))
        self.assertIn("DOMAIN_OCCUPANT_CONTROLLER_MISMATCH", exhausted_codes)

    def test_j_deep_copy_and_existing_contract_regressions(self):
        session = self._create_session("ACTIVITY-DEEP-COPY-001")
        occupant_id = self._bind_domain_instance(session.state, "P1", "active")

        # J59-J60: state lookups and board projections remain detached copies.
        occupancy_copy = session.state.get_domain_occupancy("P1")
        occupancy_copy["slots"][0]["occupancy_state"] = "empty"
        self.assertEqual(
            session.state.domain_occupancies["P1"]["slots"][0]["occupancy_state"],
            "occupied",
        )
        board = self.board.create_player_visible_domain_board(session.state)
        reference = next(
            item for item in _object_references(board) if item.get("card_instance_id") == occupant_id
        )
        reference["card_id"] = "MUTATED-PROJECTION"
        self.assertNotEqual(session.state.card_instances[occupant_id]["card_id"], "MUTATED-PROJECTION")

        # J61-J65: player, trajectory, legal action, bot, and placement schemas stay stable.
        player_snapshot = session.get_player_snapshot("P1")
        self.assertTrue(self.player_snapshot.validate_player_visible_snapshot(player_snapshot)["valid"])
        self.assertEqual(player_snapshot["schema_version"], "engine-player-visible-snapshot-v2")
        self.assertFalse(_contains_key(player_snapshot, "activity_state"))

        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)
        episode = environment.run_episode(max_steps=4, match_id="ACTIVITY-TRAJECTORY-001")
        self.assertTrue(episode["trajectory_validation"]["valid"])
        self.assertEqual(episode["schema_version"], "minimal-ai-vs-ai-episode-v1")

        action_space = environment.get_action_space()
        self.assertEqual([action["action_type"] for action in action_space["actions"]], ["end_turn", "draw_card"])
        bot = self.environment_module.DeterministicMinimalBotPolicy()
        self.assertEqual(bot.ACTION_PRIORITY, ("draw_card", "end_turn"))
        self.assertEqual(bot.choose_action(environment.get_observation())["action_type"], "draw_card")

        source_id = self._find_instance(session.state, "entity", "P1", excluded_ids={occupant_id})
        self._put_instance_in_hand(session.state, source_id, "P1")
        options = self.placement.list_structural_entity_domain_placement_options(
            session.state,
            self.runtime_package,
            "P1",
            source_id,
        )
        self.assertEqual(options["schema_version"], "minimal-entity-domain-placement-options-v0")
        self.assertFalse(_contains_key(options, "activity_state"))

    def test_k_no_forbidden_gameplay_system_was_added(self):
        state = self._create_state("ACTIVITY-FORBIDDEN-SCOPE-001")
        sample_record = next(iter(state.card_instances.values()))

        # K66-K71: no future zone, resource, payment, or entry restriction state exists.
        self.assertTrue(all(record["zone"] != "wellspring" for record in state.card_instances.values()))
        self.assertTrue(all(not hasattr(player, "wellspring_card_instance_ids") for player in state.players))
        forbidden_fields = {
            "aura",
            "aura_type",
            "magnitude",
            "payment_state",
            "summoning_sick",
            "summoning_sickness",
            "entry_turn",
        }
        self.assertTrue(forbidden_fields.isdisjoint(sample_record))

        # K72: the contract module exposes no activity mutation operation.
        for helper_name in ("set_active", "set_exhausted", "exhaust_card", "restore_card"):
            self.assertFalse(hasattr(self.card_instance, helper_name))

        # K73-K75: action and event vocabularies are unchanged and play_card is absent.
        session = self._create_session("ACTIVITY-FORBIDDEN-ACTIONS-001")
        self.assertEqual(
            {action["action_type"] for action in session.list_legal_actions()},
            {"draw_card", "end_turn"},
        )
        draw_response = self._step(session, "draw_card")
        end_turn_response = self._step(session, "end_turn")
        self.assertEqual(
            [draw_response["events"][0]["event_type"], end_turn_response["events"][0]["event_type"]],
            ["zone_move", "turn_transition"],
        )
        self.assertFalse(_contains_key(draw_response["events"], "activity_state"))
        self.assertFalse(_contains_key(end_turn_response["events"], "activity_state"))
        self.assertNotIn("play_card", {action["action_type"] for action in session.list_legal_actions()})

    def _record(self, zone, activity_state=None, metadata=None):
        return self.card_instance.create_card_instance_record(
            card_instance_id="ci_P1_0001",
            card_id="IGN-HAM-001",
            owner_player_id="P1",
            controller_player_id="P1",
            zone=zone,
            zone_index=None if zone == "domain" else 0,
            visibility="public" if zone == "domain" else "owner_only",
            created_sequence=1,
            zone_sequence=1,
            metadata=metadata or {"source": "activity_state_test"},
            activity_state=activity_state,
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

    def _step(self, session, action_type):
        action = next(
            action
            for action in session.list_legal_actions()
            if action["action_type"] == action_type and action["enabled"] is True
        )
        response = session.step(session.build_action_request(action))
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        return response

    def _bind_domain_instance(
        self,
        state,
        occupancy_player_id,
        activity_state,
        slot_index=0,
        source_player_id=None,
        controller_player_id=None,
    ):
        source_player = state.get_player(source_player_id or occupancy_player_id)
        card_instance_id = source_player.deck_card_instance_ids[0]
        self._remove_instance_from_list_zones(state, card_instance_id)
        record = state.card_instances[card_instance_id]
        record["zone"] = "domain"
        record["zone_index"] = None
        record["visibility"] = "public"
        record["controller_player_id"] = controller_player_id or occupancy_player_id
        record["activity_state"] = activity_state
        record["zone_sequence"] += 1
        self._set_slot_occupied(state, occupancy_player_id, slot_index, card_instance_id)
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

    def _put_instance_in_hand(self, state, card_instance_id, player_id):
        self._remove_instance_from_list_zones(state, card_instance_id)
        player = state.get_player(player_id)
        player.hand_card_instance_ids.append(card_instance_id)
        record = state.card_instances[card_instance_id]
        record["zone"] = "hand"
        record["zone_index"] = len(player.hand_card_instance_ids) - 1
        record["visibility"] = "owner_only"
        record["controller_player_id"] = player_id
        record["activity_state"] = None
        record["zone_sequence"] += 1

    def _find_instance(self, state, canonical_type, owner_player_id, excluded_ids=None):
        excluded_ids = set(excluded_ids or [])
        for card_instance_id in sorted(state.card_instances):
            record = state.card_instances[card_instance_id]
            if card_instance_id in excluded_ids or record.get("owner_player_id") != owner_player_id:
                continue
            card = self.runtime_package.get_card(record["card_id"])
            if self._canonical_card_type(card) == canonical_type:
                return card_instance_id
        self.fail("No %s card instance found for %s." % (canonical_type, owner_player_id))

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

    @staticmethod
    def _activity_map(state):
        return {
            card_instance_id: record.get("activity_state")
            for card_instance_id, record in sorted(state.card_instances.items())
        }


def _codes(value):
    return {
        item.get("code")
        for item in _walk_dicts(value)
        if isinstance(item.get("code"), str)
    }


def _object_references(value):
    return [
        item
        for item in _walk_dicts(value)
        if item.get("contract_type") == "object_reference"
    ]


def _contains_key(value, target_key):
    if isinstance(value, dict):
        return target_key in value or any(_contains_key(item, target_key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, target_key) for item in value)
    return False


def _walk_dicts(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _walk_dicts(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_dicts(item)


if __name__ == "__main__":
    unittest.main()
