import unittest
from types import SimpleNamespace

from backend.facade import (
    create_match,
    drop_match,
    get_match_result,
    get_snapshot,
    list_matches,
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
