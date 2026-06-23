import unittest
from types import SimpleNamespace

from backend.action_request import (
    action_request_to_key,
    normalize_action_request,
    validate_action_request,
)
from backend.facade import create_match, drop_match, get_legal_actions, validate_action


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


class TestBackendActionRequest(unittest.TestCase):
    def test_normalize_action_request_stabilizes_fields(self):
        normalized = normalize_action_request(
            {
                "action_type": "play_entity",
                "player": "Jatekos_1",
                "card_name": "Harcos",
                "zone": "horizont",
                "lane": "2",
                "extra": "ignored",
            }
        )

        self.assertEqual(
            normalized,
            {
                "action_type": "play_entity",
                "player": "Jatekos_1",
                "card_name": "Harcos",
                "zone": "horizont",
                "lane": 2,
            },
        )

    def test_validate_end_turn_request(self):
        player = make_player()
        game = SimpleNamespace(
            state=SimpleNamespace(active_player=player, phase="play", match_finished=False)
        )

        result = validate_action_request(
            game,
            player,
            {"action_type": "end_turn", "player": "Jatekos_1"},
        )

        self.assertTrue(result["valid"])
        self.assertIsNone(result["reason"])
        self.assertEqual(action_request_to_key(result["normalized"]), ("end_turn", "Jatekos_1", None, None, None))

    def test_validate_simple_play_entity_request(self):
        player = make_player()
        player.osforras = [{"lap": make_card("Forras"), "hasznalt": False}]
        player.elerheto_aura = lambda: 1
        player.kez = [make_card("Harcos", card_type="Entitas", aura=1, magnitude=1)]
        game = SimpleNamespace(
            state=SimpleNamespace(active_player=player, phase="play", match_finished=False)
        )

        result = validate_action_request(
            game,
            player,
            {
                "action_type": "play_entity",
                "player": "Jatekos_1",
                "card_name": "Harcos",
                "zone": "horizont",
                "lane": 0,
            },
        )

        self.assertTrue(result["valid"])

    def test_validate_rejects_unknown_type_and_missing_fields(self):
        player = make_player()
        game = SimpleNamespace(
            state=SimpleNamespace(active_player=player, phase="play", match_finished=False)
        )

        invalid_type = validate_action_request(
            game,
            player,
            {"action_type": "cast_spell", "player": "Jatekos_1"},
        )
        missing_fields = validate_action_request(
            game,
            player,
            {"action_type": "play_trap", "player": "Jatekos_1"},
        )

        self.assertFalse(invalid_type["valid"])
        self.assertEqual(invalid_type["reason"], "unsupported_action_type")
        self.assertFalse(missing_fields["valid"])
        self.assertTrue(missing_fields["reason"].startswith("missing_required_fields:"))

    def test_facade_validate_action_uses_match_and_player_context(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
                "random_seed": 17,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        legal_actions = get_legal_actions(match_id, "p1")
        valid_result = validate_action(match_id, "p1", legal_actions[0])
        unknown_match = validate_action("nincs", "p1", {"action_type": "end_turn", "player": "Jatekos_1"})
        unknown_player = validate_action(match_id, "rossz", {"action_type": "end_turn", "player": "Jatekos_1"})

        self.assertTrue(valid_result["valid"])
        self.assertEqual(unknown_match["reason"], "unknown_match_id")
        self.assertEqual(unknown_player["reason"], "unknown_player_id")
