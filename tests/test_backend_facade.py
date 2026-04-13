import unittest
from types import SimpleNamespace

from backend.facade import (
    apply_action,
    create_match,
    drop_match,
    get_event_log,
    get_match_result,
    get_snapshot,
    list_matches,
    run_ai_step,
)


def make_card(name, realm, card_type="Entitas", magnitude=1, aura=1):
    lower_type = card_type.lower()
    return SimpleNamespace(
        nev=name,
        kartyatipus=card_type,
        kepesseg="",
        birodalom=realm,
        klan="Teszt Klan",
        faj="Teszt Faj",
        kaszt="Teszt Kaszt",
        magnitudo=magnitude,
        aura_koltseg=aura,
        tamadas=2 if "entitas" in lower_type else 0,
        eletero=3 if "entitas" in lower_type else 0,
        egyseg_e="entitas" in lower_type,
        jel_e="jel" in lower_type,
        sik_e="sik" in lower_type,
        spell_e="ige" in lower_type,
        reakcio_e=False,
    )


def make_card_pool():
    cards = []
    for index in range(10):
        cards.append(make_card(f"Ignis Lap {index}", "Ignis", "Entitas"))
        cards.append(make_card(f"Aqua Lap {index}", "Aqua", "Entitas"))
    return cards


class TestBackendFacade(unittest.TestCase):
    def _prepare_simple_play_entity_state(self, match_id, card):
        from backend.facade import _MATCH_REGISTRY

        game = _MATCH_REGISTRY[match_id]["game"]
        player = game.p1
        player.kez = [card]
        player.temeto = []
        player.horizont = [None] * 6
        player.zenit = [None] * 6
        player.osforras = [{"lap": make_card("Forras", "Ignis"), "hasznalt": False}]
        player.rezonancia_aura = 0
        player.kovetkezo_jel_kedvezmeny = 0
        player.kovetkezo_gepezet_kedvezmeny = 0
        player.kovetkezo_entitas_kedvezmeny = 0
        game.state.active_player = player
        game.state.phase = "play"
        game.state.match_finished = False
        game.state.winner = None
        game.state.victory_reason = None
        return game, player

    def test_create_match_registers_match_and_snapshot_is_available(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
                "random_seed": 7,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        snapshot = get_snapshot(match_id)

        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot["p1"]["realm"], "Ignis")
        self.assertEqual(snapshot["p2"]["realm"], "Aqua")
        self.assertIn(match_id, [item["match_id"] for item in list_matches()])

    def test_get_match_result_returns_running_state_for_new_match(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        result = get_match_result(match_id)

        self.assertEqual(result["match_id"], match_id)
        self.assertFalse(result["finished"])
        self.assertIsNone(result["winner"])
        self.assertGreaterEqual(result["turn"], 1)

    def test_drop_match_removes_registry_entry(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )

        removed = drop_match(match_id)

        self.assertTrue(removed)
        self.assertIsNone(get_snapshot(match_id))
        self.assertIsNone(get_match_result(match_id))

    def test_drop_unknown_match_id_is_safe(self):
        self.assertFalse(drop_match("ismeretlen"))

    def test_unknown_match_id_returns_none(self):
        self.assertIsNone(get_snapshot("nincs-ilyen"))
        self.assertIsNone(get_match_result("nincs-ilyen"))

    def test_new_match_has_empty_event_log(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        event_log = get_event_log(match_id)

        self.assertEqual(event_log["events"], [])
        self.assertEqual(event_log["next_index"], 0)
        self.assertIsNone(event_log["reason"])

    def test_end_turn_events_are_buffered_per_match(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
                "random_seed": 7,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        response = apply_action(match_id, "p1", {"action_type": "end_turn", "player": "Jatekos_1"})
        event_log = get_event_log(match_id)

        self.assertTrue(response["ok"])
        self.assertGreaterEqual(len(response["events"]), 2)
        self.assertEqual(len(event_log["events"]), len(response["events"]))
        self.assertEqual(event_log["events"][0]["index"], 0)
        self.assertEqual(event_log["next_index"], len(event_log["events"]))

    def test_play_entity_events_are_buffered_and_since_index_filters(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        self._prepare_simple_play_entity_state(match_id, make_card("Backend Harcos", "Ignis", "Entitas"))
        baseline = get_event_log(match_id)
        baseline_index = baseline["next_index"]

        response = apply_action(
            match_id,
            "p1",
            {
                "action_type": "play_entity",
                "player": "Jatekos_1",
                "card_name": "Backend Harcos",
                "zone": "horizont",
                "lane": 0,
            },
        )
        event_log = get_event_log(match_id, since_index=baseline_index)

        self.assertTrue(response["ok"])
        self.assertEqual([event["type"] for event in event_log["events"][:3]], ["action_executed", "entity_played", "board_changed"])
        self.assertEqual(event_log["events"][0]["index"], baseline_index)
        self.assertEqual(event_log["next_index"], baseline_index + len(event_log["events"]))

    def test_unknown_match_event_log_is_consistent(self):
        event_log = get_event_log("nincs")

        self.assertEqual(event_log["events"], [])
        self.assertEqual(event_log["next_index"], 0)
        self.assertEqual(event_log["reason"], "unknown_match_id")

    def test_run_ai_step_uses_supported_legal_action_and_returns_snapshot(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        self._prepare_simple_play_entity_state(match_id, make_card("AI Harcos", "Ignis", "Entitas"))

        result = run_ai_step(match_id, "p1")

        self.assertTrue(result["ok"])
        self.assertEqual(result["player"], "Jatekos_1")
        self.assertEqual(result["action"]["action_type"], "play_entity")
        self.assertEqual(result["action"]["card_name"], "AI Harcos")
        self.assertEqual(result["response"]["result"]["executed_action_type"], "play_entity")
        self.assertIsInstance(result["snapshot"], dict)
