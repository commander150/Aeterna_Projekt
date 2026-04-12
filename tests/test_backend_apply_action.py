import unittest
from types import SimpleNamespace

from backend.facade import _MATCH_REGISTRY, apply_action, create_match, drop_match, get_legal_actions, get_snapshot


def make_card(name, realm="Ignis", card_type="Entitas", aura=1, magnitude=1):
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
        spell_e="ige" in lower_type,
        reakcio_e=False,
    )


def make_card_pool():
    cards = []
    for index in range(10):
        cards.append(make_card(f"Ignis Lap {index}", realm="Ignis", card_type="Entitas"))
        cards.append(make_card(f"Aqua Lap {index}", realm="Aqua", card_type="Entitas"))
    return cards


class TestBackendApplyAction(unittest.TestCase):
    def _prepare_simple_play_entity_state(self, match_id, card):
        game = _MATCH_REGISTRY[match_id]["game"]
        player = game.p1
        player.kez = [card]
        player.temeto = []
        player.horizont = [None] * 6
        player.zenit = [None] * 6
        player.osforras = [{"lap": make_card("Forras"), "hasznalt": False}]
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

    def _prepare_simple_play_trap_state(self, match_id, card):
        game, player = self._prepare_simple_play_entity_state(match_id, card)
        player.horizont = [None] * 6
        player.zenit = [None] * 6
        return game, player

    def test_apply_action_executes_valid_end_turn_and_returns_snapshot(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
                "random_seed": 19,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        result = apply_action(match_id, "p1", {"action_type": "end_turn", "player": "Jatekos_1"})

        self.assertTrue(result["ok"])
        self.assertIsNone(result["reason"])
        self.assertEqual(result["action"]["action_type"], "end_turn")
        self.assertEqual(result["result"]["executed_action_type"], "end_turn")
        self.assertEqual(result["result"]["status"], "executed")
        self.assertIsNone(result["result"]["card_name"])
        self.assertIsNone(result["result"]["zone"])
        self.assertIsNone(result["result"]["lane"])
        self.assertEqual(result["result"]["details"]["advanced_via"], "kor_futtatasa")
        self.assertIsInstance(result["events"], list)
        self.assertGreaterEqual(len(result["events"]), 2)
        self.assertEqual(result["events"][0]["type"], "action_executed")
        self.assertEqual(result["events"][1]["type"], "turn_advanced")
        self.assertIsInstance(result["snapshot"], dict)
        self.assertEqual(result["snapshot"]["active_player"], "Jatekos_1")
        self.assertEqual(result["snapshot"]["phase"], "play")
        self.assertGreaterEqual(result["snapshot"]["turn"], 2)

    def test_apply_action_rejects_invalid_request(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        result = apply_action(match_id, "p1", {"action_type": "cast_spell", "player": "Jatekos_1"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "unsupported_action_type")
        self.assertIsNone(result["result"])
        self.assertEqual(result["events"], [])
        self.assertIsInstance(result["snapshot"], dict)

    def test_apply_action_handles_unknown_match_and_player(self):
        no_match = apply_action("nincs", "p1", {"action_type": "end_turn", "player": "Jatekos_1"})
        self.assertFalse(no_match["ok"])
        self.assertEqual(no_match["reason"], "unknown_match_id")

        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        wrong_player = apply_action(match_id, "rossz", {"action_type": "end_turn", "player": "Jatekos_1"})
        self.assertFalse(wrong_player["ok"])
        self.assertEqual(wrong_player["reason"], "unknown_player_id")

    def test_apply_action_executes_simple_play_entity_and_updates_snapshot(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
                "random_seed": 23,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        harcos = make_card("Backend Harcos", card_type="Entitas", aura=1, magnitude=1)
        _, player = self._prepare_simple_play_entity_state(match_id, harcos)

        legal_actions = get_legal_actions(match_id, "p1")
        play_entity = next(
            (
                item for item in legal_actions
                if item["action_type"] == "play_entity"
                and item["card_name"] == "Backend Harcos"
                and item["zone"] == "horizont"
                and item["lane"] == 0
            ),
            None,
        )
        self.assertIsNotNone(play_entity)

        result = apply_action(match_id, "p1", play_entity)

        self.assertTrue(result["ok"])
        self.assertIsNone(result["reason"])
        self.assertEqual(result["result"]["executed_action_type"], "play_entity")
        self.assertEqual(result["result"]["status"], "executed")
        self.assertEqual(result["result"]["card_name"], "Backend Harcos")
        self.assertEqual(result["result"]["zone"], "horizont")
        self.assertEqual(result["result"]["lane"], 0)
        self.assertTrue(result["result"]["details"]["survived_on_board"])
        self.assertIsInstance(result["events"], list)
        self.assertEqual([event["type"] for event in result["events"][:3]], ["action_executed", "entity_played", "board_changed"])
        self.assertEqual(result["events"][1]["card_name"], "Backend Harcos")
        self.assertEqual(result["events"][1]["zone"], "horizont")
        self.assertEqual(result["events"][1]["lane"], 0)
        self.assertEqual(player.kez, [])
        self.assertIsNotNone(player.horizont[0])

        snapshot = get_snapshot(match_id)
        self.assertEqual(snapshot["p1"]["hand_size"], 0)
        self.assertEqual(snapshot["p1"]["horizont"][0]["card"]["name"], "Backend Harcos")

    def test_apply_action_rejects_play_entity_for_occupied_slot(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        game, _ = self._prepare_simple_play_entity_state(match_id, make_card("Backend Harcos", card_type="Entitas", aura=1, magnitude=1))
        game.p1.horizont[0] = SimpleNamespace(lap=make_card("Foglalo", card_type="Entitas"), akt_tamadas=1, akt_hp=1, kimerult=False)

        result = apply_action(
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

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "not_in_legal_actions")
        self.assertIn("action", result)
        self.assertIn("result", result)
        self.assertIn("events", result)
        self.assertIsNone(result["result"])
        self.assertEqual(result["events"], [])
        self.assertIsInstance(result["snapshot"], dict)

    def test_apply_action_rejects_non_entity_card_for_play_entity(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        self._prepare_simple_play_entity_state(match_id, make_card("Nem Harcos", card_type="Jel", aura=1, magnitude=1))

        result = apply_action(
            match_id,
            "p1",
            {
                "action_type": "play_entity",
                "player": "Jatekos_1",
                "card_name": "Nem Harcos",
                "zone": "horizont",
                "lane": 0,
            },
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "not_in_legal_actions")
        self.assertIn("action", result)
        self.assertIn("events", result)
        self.assertIsNone(result["result"])
        self.assertEqual(result["events"], [])
        self.assertIsInstance(result["snapshot"], dict)

    def test_apply_action_executes_simple_play_trap_and_updates_snapshot(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
                "random_seed": 29,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        trap = make_card("Backend Jel", card_type="Jel", aura=1, magnitude=1)
        _, player = self._prepare_simple_play_trap_state(match_id, trap)

        legal_actions = get_legal_actions(match_id, "p1")
        play_trap = next(
            (
                item for item in legal_actions
                if item["action_type"] == "play_trap"
                and item["card_name"] == "Backend Jel"
                and item["zone"] == "zenit"
                and item["lane"] == 0
            ),
            None,
        )
        self.assertIsNotNone(play_trap)

        result = apply_action(match_id, "p1", play_trap)

        self.assertTrue(result["ok"])
        self.assertIsNone(result["reason"])
        self.assertEqual(result["result"]["executed_action_type"], "play_trap")
        self.assertEqual(result["result"]["status"], "executed")
        self.assertEqual(result["result"]["card_name"], "Backend Jel")
        self.assertEqual(result["result"]["zone"], "zenit")
        self.assertEqual(result["result"]["lane"], 0)
        self.assertTrue(result["result"]["details"]["trap_on_board"])
        self.assertEqual([event["type"] for event in result["events"][:3]], ["action_executed", "trap_played", "board_changed"])
        self.assertEqual(result["events"][1]["card_name"], "Backend Jel")
        self.assertEqual(result["events"][1]["zone"], "zenit")
        self.assertEqual(result["events"][1]["lane"], 0)
        self.assertEqual(player.kez, [])
        self.assertEqual(getattr(player.zenit[0], "nev", None), "Backend Jel")

        snapshot = get_snapshot(match_id)
        self.assertEqual(snapshot["p1"]["hand_size"], 0)
        self.assertTrue(snapshot["p1"]["zenit"][0]["face_down"])
        self.assertEqual(snapshot["p1"]["zenit"][0]["card"]["name"], "Backend Jel")

    def test_apply_action_rejects_non_trap_card_for_play_trap(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        self._prepare_simple_play_trap_state(match_id, make_card("Nem Jel", card_type="Entitas", aura=1, magnitude=1))

        result = apply_action(
            match_id,
            "p1",
            {
                "action_type": "play_trap",
                "player": "Jatekos_1",
                "card_name": "Nem Jel",
                "zone": "zenit",
                "lane": 0,
            },
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "not_in_legal_actions")
        self.assertIsNone(result["result"])
        self.assertEqual(result["events"], [])
        self.assertIsInstance(result["snapshot"], dict)

    def test_apply_action_rejects_play_trap_for_invalid_zone(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        self._prepare_simple_play_trap_state(match_id, make_card("Backend Jel", card_type="Jel", aura=1, magnitude=1))

        result = apply_action(
            match_id,
            "p1",
            {
                "action_type": "play_trap",
                "player": "Jatekos_1",
                "card_name": "Backend Jel",
                "zone": "horizont",
                "lane": 0,
            },
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "not_in_legal_actions")
        self.assertIsNone(result["result"])
        self.assertEqual(result["events"], [])
        self.assertIsInstance(result["snapshot"], dict)

    def test_apply_action_rejects_play_trap_when_trap_limit_is_full(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        _, player = self._prepare_simple_play_trap_state(match_id, make_card("Backend Jel", card_type="Jel", aura=1, magnitude=1))
        player.zenit[0] = make_card("Jel 1", card_type="Jel", aura=1, magnitude=1)
        player.zenit[1] = make_card("Jel 2", card_type="Jel", aura=1, magnitude=1)

        result = apply_action(
            match_id,
            "p1",
            {
                "action_type": "play_trap",
                "player": "Jatekos_1",
                "card_name": "Backend Jel",
                "zone": "zenit",
                "lane": 2,
            },
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "not_in_legal_actions")
        self.assertIsNone(result["result"])
        self.assertEqual(result["events"], [])
        self.assertIsInstance(result["snapshot"], dict)

    def test_apply_action_keeps_consistent_error_shape_for_unknown_match(self):
        result = apply_action("nincs", "p1", {"action_type": "end_turn", "player": "Jatekos_1"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "unknown_match_id")
        self.assertIn("action", result)
        self.assertIn("result", result)
        self.assertIn("events", result)
        self.assertIn("snapshot", result)
        self.assertIsNone(result["action"])
        self.assertIsNone(result["result"])
        self.assertEqual(result["events"], [])
        self.assertIsNone(result["snapshot"])
