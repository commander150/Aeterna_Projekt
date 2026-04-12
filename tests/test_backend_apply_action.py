import unittest
from types import SimpleNamespace

from backend.facade import apply_action, create_match, drop_match, get_legal_actions


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
        self.assertEqual(result["result"]["advanced_via"], "kor_futtatasa")
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

    def test_apply_action_does_not_execute_play_entity_yet(self):
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

        legal_actions = get_legal_actions(match_id, "p1")
        play_entity = next((item for item in legal_actions if item["action_type"] == "play_entity"), None)
        if play_entity is None:
            self.skipTest("A teszt deck/kez allapotban nem volt egyszeru play_entity akcio.")

        result = apply_action(match_id, "p1", play_entity)

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "action_type_not_executable_yet")
