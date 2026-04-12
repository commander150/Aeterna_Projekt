import unittest
from types import SimpleNamespace

from backend.facade import create_match, drop_match, get_legal_actions
from backend.legal_actions import get_legal_actions_for_player


def make_card(name, realm="Ignis", card_type="Entitas", aura=1, magnitude=1):
    lower_type = card_type.lower()
    return SimpleNamespace(
        nev=name,
        kartyatipus=card_type,
        birodalom=realm,
        klan="Teszt Klan",
        magnitudo=magnitude,
        aura_koltseg=aura,
        egyseg_e="entitas" in lower_type,
        jel_e="jel" in lower_type,
        spell_e="ige" in lower_type,
    )


def make_player(name="Jatekos_1", realm="Ignis"):
    return SimpleNamespace(
        nev=name,
        birodalom=realm,
        kez=[],
        horizont=[None] * 6,
        zenit=[None] * 6,
        osforras=[],
        elerheto_aura=lambda: 0,
        effektiv_aura_koltseg=lambda lap: getattr(lap, "aura_koltseg", 0),
    )


def make_card_pool():
    cards = []
    for index in range(10):
        cards.append(make_card(f"Ignis Lap {index}", realm="Ignis", card_type="Entitas"))
        cards.append(make_card(f"Aqua Lap {index}", realm="Aqua", card_type="Entitas"))
    return cards


class TestBackendLegalActions(unittest.TestCase):
    def test_legal_actions_returns_end_turn_when_no_simple_play_exists(self):
        player = make_player()

        actions = get_legal_actions_for_player(SimpleNamespace(), player)

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["action_type"], "end_turn")

    def test_legal_actions_detect_simple_entity_and_trap_plays(self):
        player = make_player()
        player.osforras = [{"lap": make_card("Forras"), "hasznalt": False}]
        player.elerheto_aura = lambda: 1
        player.kez = [
            make_card("Harcos", card_type="Entitas", aura=1, magnitude=1),
            make_card("Csapda", card_type="Jel", aura=1, magnitude=1),
            make_card("Tul Draga", card_type="Entitas", aura=3, magnitude=1),
        ]

        actions = get_legal_actions_for_player(SimpleNamespace(), player)

        action_types = {(item["action_type"], item.get("card_name"), item.get("zone")) for item in actions}
        self.assertIn(("end_turn", None, None), action_types)
        self.assertIn(("play_entity", "Harcos", "horizont"), action_types)
        self.assertIn(("play_entity", "Harcos", "zenit"), action_types)
        self.assertIn(("play_trap", "Csapda", "zenit"), action_types)
        self.assertNotIn(("play_entity", "Tul Draga", "horizont"), action_types)

    def test_trap_play_is_omitted_when_trap_limit_is_already_full(self):
        player = make_player()
        player.osforras = [{"lap": make_card("Forras"), "hasznalt": False}]
        player.elerheto_aura = lambda: 1
        player.kez = [make_card("Uj Jel", card_type="Jel", aura=1, magnitude=1)]
        player.zenit[0] = make_card("Meglevo Jel 1", card_type="Jel")
        player.zenit[1] = make_card("Meglevo Jel 2", card_type="Jel")

        actions = get_legal_actions_for_player(SimpleNamespace(), player)

        self.assertEqual([item["action_type"] for item in actions], ["end_turn"])

    def test_facade_get_legal_actions_returns_actions_for_known_match_and_player(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
                "random_seed": 11,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        actions = get_legal_actions(match_id, "p1")

        self.assertIsInstance(actions, list)
        self.assertGreaterEqual(len(actions), 1)
        self.assertEqual(actions[0]["action_type"], "end_turn")

    def test_facade_get_legal_actions_handles_unknown_match_or_player(self):
        self.assertIsNone(get_legal_actions("nincs", "p1"))

        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        self.assertIsNone(get_legal_actions(match_id, "rossz-jatekos"))
