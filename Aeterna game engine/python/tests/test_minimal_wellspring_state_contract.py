import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from dataclasses import fields
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"

CARD_INSTANCE_PATH = ENGINE_DIR / "card_instance.py"
WELLSPRING_PATH = ENGINE_DIR / "wellspring_state.py"
BOARD_PATH = ENGINE_DIR / "domain_board_projection.py"
PLACEMENT_PATH = ENGINE_DIR / "entity_domain_placement.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
ENVIRONMENT_PATH = ENGINE_DIR / "minimal_engine_environment.py"
MATCH_STATE_PATH = AI_VS_AI_DIR / "match_state.py"
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


class TestMinimalWellspringStateContract(unittest.TestCase):
    def setUp(self):
        self.card_instance = _load_module("card_instance", CARD_INSTANCE_PATH)
        self.wellspring = _load_module("wellspring_state", WELLSPRING_PATH)
        self.match_state = _load_module("match_state", MATCH_STATE_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.board = _load_module("domain_board_projection", BOARD_PATH)
        self.placement = _load_module("entity_domain_placement", PLACEMENT_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.environment_module = _load_module("minimal_engine_environment", ENVIRONMENT_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        self.deck_id_a, self.deck_id_b = sorted(self.runtime_package.decks_by_id)[:2]

    def test_a_card_instance_wellspring_zone_support(self):
        active = self._card_record("wellspring", "active", zone_index=0)
        exhausted = self._card_record("wellspring", "exhausted", zone_index=3)

        # A1-A3: card instance schema remains v1 and accepts both activity states.
        self.assertEqual(active["schema_version"], "minimal-card-instance-record-v1")
        self.assertTrue(self.card_instance.validate_card_instance_record(active)["valid"])
        self.assertTrue(self.card_instance.validate_card_instance_record(exhausted)["valid"])

        # A4-A5: null and unknown activity values are rejected.
        null_result = self.card_instance.validate_card_instance_record(
            self._card_record("wellspring", None, zone_index=0)
        )
        unknown_result = self.card_instance.validate_card_instance_record(
            self._card_record("wellspring", "ready", zone_index=0)
        )
        self.assertIn("ACTIVITY_STATE_ZONE_MISMATCH", _codes(null_result))
        self.assertIn("ACTIVITY_STATE_INVALID", _codes(unknown_result))

        # A6-A10: Wellspring index and hidden visibility rules are explicit.
        self.assertTrue(self.card_instance.validate_card_instance_record(active)["valid"])
        self.assertTrue(self.card_instance.validate_card_instance_record(exhausted)["valid"])
        for invalid_index in (-1, True):
            result = self.card_instance.validate_card_instance_record(
                self._card_record("wellspring", "active", zone_index=invalid_index)
            )
            self.assertIn("ZONE_INDEX_INVALID", _codes(result))
        visibility_result = self.card_instance.validate_card_instance_record(
            self._card_record("wellspring", "active", zone_index=0, visibility="public")
        )
        self.assertIn("ZONE_VISIBILITY_MISMATCH", _codes(visibility_result))
        self.assertEqual(
            self.card_instance.CANONICAL_HIDDEN_VISIBILITY,
            "owner_only",
        )

        # A11-A12: previous list-zone and Domain activity rules remain unchanged.
        for zone in ("deck", "hand", "discard"):
            with self.subTest(zone=zone):
                self.assertTrue(
                    self.card_instance.validate_card_instance_record(
                        self._card_record(zone, None, zone_index=0)
                    )["valid"]
                )
        self.assertTrue(
            self.card_instance.validate_card_instance_record(
                self._card_record("domain", "active", zone_index=None, visibility="public")
            )["valid"]
        )
        self.assertFalse(
            self.card_instance.validate_card_instance_record(
                self._card_record("domain", None, zone_index=None, visibility="public")
            )["valid"]
        )

    def test_b_empty_wellspring_state_contract(self):
        state = self.wellspring.create_empty_player_wellspring_state("P1")

        # B13-B23: empty state has the complete isolated contract and metadata.
        self.assertEqual(state["schema_version"], "minimal-player-wellspring-state-v0")
        self.assertEqual(state["contract_type"], "player_wellspring_state")
        self.assertEqual(state["player_id"], "P1")
        self.assertEqual(state["zone"], "wellspring")
        self.assertEqual(state["visibility_mode"], "owner_only")
        self.assertEqual(state["wellspring_card_instance_ids"], [])
        self.assertEqual(state["card_count"], 0)
        self.assertTrue(state["metadata"]["cards_face_down"])
        self.assertEqual(state["metadata"]["typed_aura_model"], "not_implemented")
        self.assertEqual(state["metadata"]["payment_model"], "not_implemented")
        self.assertEqual(json.loads(json.dumps(state, ensure_ascii=False)), state)
        self.assertTrue(self.wellspring.validate_player_wellspring_state(state, {})["valid"])

    def test_c_non_empty_wellspring_state_contract(self):
        ids, registry = self._registry(
            ("active", "exhausted", "active"),
            owner_player_ids=("P1", "P2", "P1"),
        )
        input_ids = list(ids)
        state = self.wellspring.create_player_wellspring_state("P1", input_ids, registry)

        # C24-C30: active/exhausted membership preserves stable order and authority.
        self.assertEqual(state["wellspring_card_instance_ids"][0], ids[0])
        self.assertEqual(state["wellspring_card_instance_ids"][1], ids[1])
        self.assertEqual(state["wellspring_card_instance_ids"], ids)
        self.assertEqual(state["card_count"], 3)
        self.assertTrue(all(registry[card_id]["zone_index"] == index for index, card_id in enumerate(ids)))
        self.assertTrue(all(registry[card_id]["controller_player_id"] == "P1" for card_id in ids))
        self.assertEqual(registry[ids[1]]["owner_player_id"], "P2")
        self.assertNotEqual(
            registry[ids[1]]["owner_player_id"],
            registry[ids[1]]["controller_player_id"],
        )

        # C31-C33: state contains IDs only and validates against the registry.
        self.assertFalse(_contains_key(state, "card_ids"))
        self.assertFalse(_contains_key(state, "card_id"))
        self.assertFalse(_contains_value(state, "card_instance_record"))
        self.assertTrue(self.wellspring.validate_player_wellspring_state(state, registry)["valid"])

    def test_d_builder_rejects_invalid_state_input_without_partial_output(self):
        ids, registry = self._registry(("active",))

        # D34-D42: each invalid registry relationship raises a controlled error.
        cases = []
        cases.append((["ci_UNKNOWN_9999"], registry))
        cases.append(([ids[0], ids[0]], registry))

        deck_registry = deepcopy(registry)
        deck_registry[ids[0]].update(zone="deck", zone_index=0, activity_state=None)
        cases.append((ids, deck_registry))
        hand_registry = deepcopy(registry)
        hand_registry[ids[0]].update(zone="hand", zone_index=0, activity_state=None)
        cases.append((ids, hand_registry))
        domain_registry = deepcopy(registry)
        domain_registry[ids[0]].update(zone="domain", zone_index=None, visibility="public")
        cases.append((ids, domain_registry))
        index_registry = deepcopy(registry)
        index_registry[ids[0]]["zone_index"] = 2
        cases.append((ids, index_registry))
        controller_registry = deepcopy(registry)
        controller_registry[ids[0]]["controller_player_id"] = "P2"
        cases.append((ids, controller_registry))
        null_registry = deepcopy(registry)
        null_registry[ids[0]]["activity_state"] = None
        cases.append((ids, null_registry))
        visibility_registry = deepcopy(registry)
        visibility_registry[ids[0]]["visibility"] = "public"
        cases.append((ids, visibility_registry))

        for case_ids, case_registry in cases:
            with self.subTest(case_ids=case_ids, registry=case_registry):
                with self.assertRaises(self.wellspring.WellspringStateError) as context:
                    self.wellspring.create_player_wellspring_state("P1", case_ids, case_registry)
                self.assertTrue(context.exception.errors)

        # D43: failure returns no partial state object.
        partial = None
        try:
            partial = self.wellspring.create_player_wellspring_state("P1", ids, visibility_registry)
        except self.wellspring.WellspringStateError:
            pass
        self.assertIsNone(partial)

        with self.assertRaises(self.wellspring.WellspringStateError) as registry_error:
            self.wellspring.create_player_wellspring_state("P1", [], None)
        self.assertIn("INSTANCE_RECORD_INVALID", _codes({"errors": registry_error.exception.errors}))

    def test_e_state_validator_negative_cases(self):
        ids, registry = self._registry(("active", "exhausted"))
        valid = self.wellspring.create_player_wellspring_state("P1", ids, registry)

        # E44-E49: malformed envelope and ID-list state produce structured errors.
        self.assertIn("WELLSPRING_NOT_DICT", _codes(self.wellspring.validate_player_wellspring_state(None)))
        mutations = (
            ("CONTRACT_TYPE_INVALID", lambda value: value.update(contract_type="wrong")),
            ("PLAYER_ID_INVALID", lambda value: value.update(player_id="")),
            ("ZONE_INVALID", lambda value: value.update(zone="deck")),
            (
                "INSTANCE_ID_DUPLICATE",
                lambda value: value.update(
                    wellspring_card_instance_ids=[ids[0], ids[0]],
                    card_count=2,
                ),
            ),
            ("CARD_COUNT_MISMATCH", lambda value: value.update(card_count=99)),
        )
        for expected_code, mutation in mutations:
            invalid = deepcopy(valid)
            mutation(invalid)
            self.assertIn(expected_code, _codes(self.wellspring.validate_player_wellspring_state(invalid)))

        # E50-E54: optional registry cross-validation reports exact relationship failures.
        unknown = deepcopy(valid)
        unknown["wellspring_card_instance_ids"] = ["ci_UNKNOWN_9999"]
        unknown["card_count"] = 1
        self.assertIn("INSTANCE_UNKNOWN", _codes(self.wellspring.validate_player_wellspring_state(unknown, registry)))

        registry_cases = (
            ("INSTANCE_ZONE_MISMATCH", "zone", "deck"),
            ("INSTANCE_ZONE_INDEX_MISMATCH", "zone_index", 9),
            ("INSTANCE_CONTROLLER_MISMATCH", "controller_player_id", "P2"),
            ("INSTANCE_ACTIVITY_INVALID", "activity_state", None),
        )
        for expected_code, field_name, value in registry_cases:
            invalid_registry = deepcopy(registry)
            invalid_registry[ids[0]][field_name] = value
            self.assertIn(
                expected_code,
                _codes(self.wellspring.validate_player_wellspring_state(valid, invalid_registry)),
            )

        # E55-E56: typed Aura and payment cannot be promoted through metadata.
        typed = deepcopy(valid)
        typed["metadata"]["typed_aura_model"] = "implemented"
        payment = deepcopy(valid)
        payment["metadata"]["payment_model"] = "implemented"
        self.assertIn("UNSUPPORTED_RESOURCE_LAYER_INCLUDED", _codes(
            self.wellspring.validate_player_wellspring_state(typed)
        ))
        self.assertIn("UNSUPPORTED_RESOURCE_LAYER_INCLUDED", _codes(
            self.wellspring.validate_player_wellspring_state(payment)
        ))

    def test_f_empty_resource_summary(self):
        state = self.wellspring.create_empty_player_wellspring_state("P1")
        summary = self.wellspring.create_wellspring_resource_summary(state, {})

        # F57-F64: empty resources are computed as zero and remain JSON compatible.
        self.assertEqual(summary["wellspring_card_count"], 0)
        self.assertEqual(summary["magnitude"], 0)
        self.assertEqual(summary["active_source_count"], 0)
        self.assertEqual(summary["exhausted_source_count"], 0)
        self.assertEqual(summary["available_aura"], 0)
        self.assertIsNone(summary["typed_aura"])
        self.assertTrue(self.wellspring.validate_wellspring_resource_summary(summary)["valid"])
        self.assertEqual(json.loads(json.dumps(summary, ensure_ascii=False)), summary)
        with self.assertRaises(self.wellspring.WellspringStateError):
            self.wellspring.create_wellspring_resource_summary(state, None)

    def test_g_active_and_exhausted_resource_calculation(self):
        cases = (
            (("active",), (1, 1, 1, 0)),
            (("exhausted",), (1, 0, 0, 1)),
            (("active", "exhausted"), (2, 1, 1, 1)),
            (("active", "active", "active"), (3, 3, 3, 0)),
            (("exhausted", "exhausted", "exhausted"), (3, 0, 0, 3)),
        )
        summaries = {}
        for activity_states, expected in cases:
            with self.subTest(activity_states=activity_states):
                summary = self._summary(activity_states)
                summaries[activity_states] = summary
                magnitude, aura, active_count, exhausted_count = expected
                self.assertEqual(summary["magnitude"], magnitude)
                self.assertEqual(summary["available_aura"], aura)
                self.assertEqual(summary["active_source_count"], active_count)
                self.assertEqual(summary["exhausted_source_count"], exhausted_count)

        # G65-G71: exhaustion changes Aura, never Magnitude or membership.
        self.assertEqual(summaries[("active",)]["magnitude"], 1)
        self.assertEqual(summaries[("active",)]["available_aura"], 1)
        self.assertEqual(summaries[("exhausted",)]["magnitude"], 1)
        self.assertEqual(summaries[("exhausted",)]["available_aura"], 0)
        mixed = summaries[("active", "exhausted")]
        self.assertEqual((mixed["magnitude"], mixed["available_aura"]), (2, 1))
        self.assertEqual(summaries[("active", "active", "active")]["available_aura"], 3)
        self.assertEqual(summaries[("exhausted", "exhausted", "exhausted")]["magnitude"], 3)
        self.assertTrue(all(
            summary["active_source_count"] + summary["exhausted_source_count"]
            == summary["wellspring_card_count"]
            for summary in summaries.values()
        ))

    def test_h_resource_summary_validator_negative_cases(self):
        valid = self._summary(("active", "exhausted"))

        # H72-H82: all arithmetic and unsupported resource layers are guarded.
        cases = (
            ("MAGNITUDE_MISMATCH", lambda value: value.update(magnitude=9)),
            ("AVAILABLE_AURA_MISMATCH", lambda value: value.update(available_aura=9)),
            ("ACTIVITY_COUNT_MISMATCH", lambda value: value.update(exhausted_source_count=9)),
            ("COUNT_INVALID", lambda value: value.update(active_source_count=-1)),
            ("COUNT_INVALID", lambda value: value.update(wellspring_card_count=True)),
            ("TYPED_AURA_NOT_SUPPORTED", lambda value: value.update(typed_aura={"ignis": 1})),
            (
                "UNSUPPORTED_RESOURCE_LAYER_INCLUDED",
                lambda value: value["metadata"].update(resonance_included=True),
            ),
            (
                "UNSUPPORTED_RESOURCE_LAYER_INCLUDED",
                lambda value: value["metadata"].update(temporary_aura_included=True),
            ),
            (
                "UNSUPPORTED_RESOURCE_LAYER_INCLUDED",
                lambda value: value["metadata"].update(aura_burn_included=True),
            ),
            (
                "UNSUPPORTED_RESOURCE_LAYER_INCLUDED",
                lambda value: value["metadata"].update(magnitude_overrides_included=True),
            ),
            (
                "UNSUPPORTED_RESOURCE_LAYER_INCLUDED",
                lambda value: value["metadata"].update(payment_legality="implemented"),
            ),
        )
        for expected_code, mutation in cases:
            invalid = deepcopy(valid)
            mutation(invalid)
            result = self.wellspring.validate_wellspring_resource_summary(invalid)
            self.assertFalse(result["valid"])
            self.assertIn(expected_code, _codes(result))

    def test_i_lookup_and_deep_copy_boundaries(self):
        ids, registry = self._registry(("active", "exhausted"))
        input_ids = list(ids)
        registry_before = deepcopy(registry)
        first = self.wellspring.create_player_wellspring_state("P1", input_ids, registry)
        second = self.wellspring.create_player_wellspring_state("P1", input_ids, registry)

        # I83-I90: lists, metadata, and registry relationships remain detached.
        lookup = self.wellspring.get_wellspring_card_instance_ids(first)
        self.assertEqual(lookup, ids)
        self.assertIsNot(lookup, first["wellspring_card_instance_ids"])
        lookup.append("ci_MUTATED_9999")
        self.assertEqual(first["wellspring_card_instance_ids"], ids)
        self.assertEqual(input_ids, ids)
        self.assertIsNot(first["wellspring_card_instance_ids"], input_ids)
        self.assertIsNot(first["wellspring_card_instance_ids"], second["wellspring_card_instance_ids"])
        self.assertIsNot(first["metadata"], second["metadata"])
        first["metadata"]["source"] = "mutated"
        self.assertEqual(second["metadata"]["source"], "python.engine.wellspring_state")
        registry[ids[0]]["activity_state"] = "exhausted"
        self.assertEqual(first["wellspring_card_instance_ids"], ids)
        self.assertEqual(registry_before[ids[0]]["activity_state"], "active")

        # I91: summary output is detached from both inputs.
        summary = self.wellspring.create_wellspring_resource_summary(second, registry_before)
        state_before = deepcopy(second)
        registry_snapshot = deepcopy(registry_before)
        summary["available_aura"] = 999
        self.assertEqual(second, state_before)
        self.assertEqual(registry_before, registry_snapshot)

    def test_j_deterministic_contract_serialization(self):
        ids = ["ci_W_0002", "ci_W_0001"]
        _, registry_p1 = self._registry(("active", "exhausted"), ids=ids, controller_player_id="P1")
        _, registry_p2 = self._registry(("active", "exhausted"), ids=ids, controller_player_id="P2")
        first = self.wellspring.create_player_wellspring_state("P1", ids, registry_p1)
        second = self.wellspring.create_player_wellspring_state("P1", ids, registry_p1)

        # J92-J96: input order and repeated state/summary output are deterministic.
        self.assertEqual(_json(first), _json(second))
        self.assertEqual(first["wellspring_card_instance_ids"], ids)
        first_summary = self.wellspring.create_wellspring_resource_summary(first, registry_p1)
        second_summary = self.wellspring.create_wellspring_resource_summary(second, registry_p1)
        self.assertEqual(_json(first_summary), _json(second_summary))
        p2 = self.wellspring.create_player_wellspring_state("P2", ids, registry_p2)
        p1_without_player = deepcopy(first)
        p2_without_player = deepcopy(p2)
        p1_without_player.pop("player_id")
        p2_without_player.pop("player_id")
        self.assertEqual(p1_without_player, p2_without_player)
        self.assertTrue(all(_json(first) == _json(
            self.wellspring.create_player_wellspring_state("P1", ids, registry_p1)
        ) for _ in range(3)))

    def test_k_production_runtime_remains_unintegrated(self):
        player_fields = [field.name for field in fields(self.match_state.PlayerState)]
        match_fields = [field.name for field in fields(self.match_state.MatchState)]

        # K97-K99: PlayerState, MatchState, and initial production setup are unchanged.
        self.assertEqual(
            player_fields,
            [
                "player_id",
                "deck_id",
                "deck_card_instance_ids",
                "hand_card_instance_ids",
                "discard_card_instance_ids",
            ],
        )
        self.assertEqual(
            match_fields,
            [
                "match_id",
                "turn_number",
                "active_player_id",
                "players",
                "phase",
                "card_instances",
                "domain_topologies",
                "domain_occupancies",
                "state_version",
                "event_log",
            ],
        )
        session = self._create_session("WELLSPRING-PRODUCTION-UNCHANGED-001")
        self.assertTrue(all(not hasattr(player, "wellspring_card_instance_ids") for player in session.state.players))
        self.assertTrue(all(record["zone"] != "wellspring" for record in session.state.card_instances.values()))

        # K100-K103: legal actions, draw, end_turn, and event vocabulary are unchanged.
        self.assertEqual(
            [action["action_type"] for action in session.list_legal_actions()],
            ["end_turn", "draw_card"],
        )
        draw_response = self._step(session, "draw_card")
        end_response = self._step(session, "end_turn")
        self.assertEqual(draw_response["events"][0]["event_type"], "zone_move")
        self.assertEqual(end_response["events"][0]["event_type"], "turn_transition")
        self.assertEqual([event["event_type"] for event in session.state.event_log], ["zone_move", "turn_transition"])

        # K104-K108: player-facing, board, trajectory, placement, and bot contracts stay stable.
        snapshot = session.get_player_snapshot("P2")
        self.assertEqual(snapshot["schema_version"], "engine-player-visible-snapshot-v2")
        self.assertFalse(_contains_key(snapshot, "wellspring_card_instance_ids"))
        board = self.board.create_player_visible_domain_board(session.state)
        self.assertEqual(board["schema_version"], "minimal-player-visible-domain-board-v0")
        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)
        episode = environment.run_episode(max_steps=2, match_id="WELLSPRING-TRAJECTORY-UNCHANGED-001")
        self.assertEqual(episode["schema_version"], "minimal-ai-vs-ai-episode-v1")
        self.assertTrue(episode["trajectory_validation"]["valid"])

        placement_state = self._create_state("WELLSPRING-PLACEMENT-UNCHANGED-001")
        source_id = self._find_entity_instance(placement_state, "P1")
        self._put_instance_in_hand(placement_state, source_id, "P1")
        options = self.placement.list_structural_entity_domain_placement_options(
            placement_state,
            self.runtime_package,
            "P1",
            source_id,
        )
        self.assertEqual(options["schema_version"], "minimal-entity-domain-placement-options-v0")
        bot = self.environment_module.DeterministicMinimalBotPolicy()
        self.assertEqual(bot.ACTION_PRIORITY, ("draw_card", "end_turn"))

    def test_l_no_forbidden_runtime_systems(self):
        state = self.wellspring.create_empty_player_wellspring_state("P1")
        summary = self.wellspring.create_wellspring_resource_summary(state, {})

        # L109-L112: no Inflow transition, payment, or Magnitude preflight exists.
        for helper_name in (
            "inflow",
            "apply_inflow",
            "move_hand_to_wellspring",
            "pay_aura",
            "validate_payment",
            "preflight_magnitude",
        ):
            self.assertFalse(hasattr(self.wellspring, helper_name))
            self.assertFalse(hasattr(self.kernel, helper_name))
        self.assertEqual(state["metadata"]["inflow_action_integration"], "not_implemented")
        self.assertEqual(state["metadata"]["payment_model"], "not_implemented")

        # L113-L118: unsupported resource layers are explicit null/false values.
        self.assertIsNone(summary["typed_aura"])
        self.assertFalse(summary["metadata"]["resonance_included"])
        self.assertFalse(summary["metadata"]["temporary_aura_included"])
        self.assertFalse(summary["metadata"]["aura_burn_included"])
        self.assertFalse(summary["metadata"]["magnitude_overrides_included"])
        self.assertFalse(_contains_key(summary, "providence"))
        self.assertFalse(_contains_key(summary, "rooting"))

        # L119-L122: no activity mutator, play_card, action, or event was added.
        for helper_name in (
            "add_card",
            "remove_card",
            "exhaust_card",
            "restore_card",
            "set_active",
            "set_exhausted",
        ):
            self.assertFalse(hasattr(self.wellspring, helper_name))
            self.assertFalse(hasattr(self.card_instance, helper_name))
        session = self._create_session("WELLSPRING-FORBIDDEN-RUNTIME-001")
        action_types = {action["action_type"] for action in session.list_legal_actions()}
        self.assertNotIn("play_card", action_types)
        self.assertEqual(action_types, {"draw_card", "end_turn"})
        self.assertEqual(session.state.event_log, [])

    def _card_record(
        self,
        zone,
        activity_state,
        zone_index,
        visibility="owner_only",
        card_instance_id="ci_W_0001",
        owner_player_id="P1",
        controller_player_id="P1",
    ):
        return self.card_instance.create_card_instance_record(
            card_instance_id=card_instance_id,
            card_id="IGN-HAM-001",
            owner_player_id=owner_player_id,
            controller_player_id=controller_player_id,
            zone=zone,
            zone_index=zone_index,
            visibility=visibility,
            created_sequence=1,
            zone_sequence=1,
            metadata={"source": "wellspring_contract_test"},
            activity_state=activity_state,
        )

    def _registry(
        self,
        activity_states,
        owner_player_ids=None,
        ids=None,
        controller_player_id="P1",
    ):
        ids = list(ids or ["ci_W_%04d" % (index + 1) for index in range(len(activity_states))])
        owner_player_ids = list(owner_player_ids or [controller_player_id] * len(ids))
        registry = {
            card_instance_id: self._card_record(
                "wellspring",
                activity_state,
                zone_index=index,
                card_instance_id=card_instance_id,
                owner_player_id=owner_player_ids[index],
                controller_player_id=controller_player_id,
            )
            for index, (card_instance_id, activity_state) in enumerate(zip(ids, activity_states))
        }
        return ids, registry

    def _summary(self, activity_states):
        ids, registry = self._registry(activity_states)
        state = self.wellspring.create_player_wellspring_state("P1", ids, registry)
        return self.wellspring.create_wellspring_resource_summary(state, registry)

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

    def _find_entity_instance(self, state, player_id):
        for card_instance_id in sorted(state.card_instances):
            record = state.card_instances[card_instance_id]
            if record.get("owner_player_id") != player_id:
                continue
            card = self.runtime_package.get_card(record["card_id"])
            if self._canonical_card_type(card) == "entity":
                return card_instance_id
        self.fail("No Entity card instance found for %s." % player_id)

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
    def _put_instance_in_hand(state, card_instance_id, player_id):
        for player in state.players:
            for zone_name in ("deck", "hand", "discard"):
                zone = getattr(player, "%s_card_instance_ids" % zone_name)
                while card_instance_id in zone:
                    zone.remove(card_instance_id)
                for zone_index, remaining_id in enumerate(zone):
                    state.card_instances[remaining_id]["zone"] = zone_name
                    state.card_instances[remaining_id]["zone_index"] = zone_index
        player = state.get_player(player_id)
        player.hand_card_instance_ids.append(card_instance_id)
        record = state.card_instances[card_instance_id]
        record.update(
            zone="hand",
            zone_index=len(player.hand_card_instance_ids) - 1,
            visibility="owner_only",
            controller_player_id=player_id,
            activity_state=None,
        )
        record["zone_sequence"] += 1


def _codes(value):
    return {
        item.get("code")
        for item in _walk_dicts(value)
        if isinstance(item.get("code"), str)
    }


def _contains_key(value, target_key):
    if isinstance(value, dict):
        return target_key in value or any(_contains_key(item, target_key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, target_key) for item in value)
    return False


def _contains_value(value, target_value):
    if isinstance(value, dict):
        return any(_contains_value(item, target_value) for item in value.values())
    if isinstance(value, list):
        return any(_contains_value(item, target_value) for item in value)
    return value == target_value


def _walk_dicts(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _walk_dicts(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_dicts(item)


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
