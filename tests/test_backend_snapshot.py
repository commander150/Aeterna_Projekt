import unittest
from types import SimpleNamespace

from backend.snapshot import (
    export_card_ref,
    export_match_snapshot,
    export_player_state,
    export_unit_state,
)
from engine.card import CsataEgyseg


def make_card(name, card_type="Entitas", magnitude=1, aura=1):
    lower_type = card_type.lower()
    return SimpleNamespace(
        nev=name,
        kartyatipus=card_type,
        birodalom="Ignis",
        klan="Hamvaskezu",
        magnitudo=magnitude,
        aura_koltseg=aura,
        tamadas=3,
        eletero=4,
        egyseg_e="entitas" in lower_type,
        jel_e="jel" in lower_type,
        sik_e="sik" in lower_type,
        spell_e="ige" in lower_type,
    )


def make_unit(name, atk=3, hp=4, exhausted=False):
    card = make_card(name, card_type="Entitas")
    card.tamadas = atk
    card.eletero = hp
    unit = CsataEgyseg(card)
    unit.kimerult = exhausted
    return unit


def make_player(name="P1", realm="Ignis"):
    return SimpleNamespace(
        nev=name,
        birodalom=realm,
        pakli=[],
        kez=[],
        temeto=[],
        pecsetek=[],
        osforras=[],
        horizont=[None] * 6,
        zenit=[None] * 6,
        overflow_vereseg=False,
    )


class TestBackendSnapshot(unittest.TestCase):
    def test_export_card_ref_returns_frontend_friendly_fields(self):
        card = make_card("Parazs", card_type="Ige", magnitude=2, aura=3)

        snapshot = export_card_ref(card)

        self.assertEqual(snapshot["name"], "Parazs")
        self.assertEqual(snapshot["card_type"], "Ige")
        self.assertEqual(snapshot["realm"], "Ignis")
        self.assertEqual(snapshot["clan"], "Hamvaskezu")
        self.assertEqual(snapshot["magnitude"], 2)
        self.assertEqual(snapshot["aura_cost"], 3)
        self.assertTrue(snapshot["is_spell"])

    def test_export_unit_state_includes_position_and_combat_state(self):
        unit = make_unit("Tamado", atk=5, hp=6, exhausted=True)

        snapshot = export_unit_state(unit, zone_name="horizont", lane_index=2)

        self.assertEqual(snapshot["kind"], "entity")
        self.assertEqual(snapshot["zone"], "horizont")
        self.assertEqual(snapshot["lane"], 2)
        self.assertEqual(snapshot["current_attack"], 5)
        self.assertEqual(snapshot["current_hp"], 6)
        self.assertTrue(snapshot["exhausted"])
        self.assertFalse(snapshot["active"])
        self.assertEqual(snapshot["card"]["name"], "Tamado")

    def test_export_player_state_includes_zone_snapshots_and_hand_refs(self):
        player = make_player("Jatekos_1", realm="Ignis")
        player.pakli = [make_card("Pakli Lap 1"), make_card("Pakli Lap 2")]
        player.kez = [make_card("Kez Lap", card_type="Ige")]
        player.temeto = [make_card("Temeto Lap")]
        player.pecsetek = [make_card("Pecset 1"), make_card("Pecset 2")]
        player.osforras = [{"lap": make_card("Forras Lap"), "hasznalt": False}]
        player.horizont[0] = make_unit("Horizont Egyseg", atk=2, hp=3)
        player.zenit[1] = make_card("Titkos Jel", card_type="Jel")

        snapshot = export_player_state(player)

        self.assertEqual(snapshot["name"], "Jatekos_1")
        self.assertEqual(snapshot["realm"], "Ignis")
        self.assertEqual(snapshot["deck_size"], 2)
        self.assertEqual(snapshot["hand_size"], 1)
        self.assertEqual(snapshot["graveyard_size"], 1)
        self.assertEqual(snapshot["seal_count"], 2)
        self.assertEqual(snapshot["source_count"], 1)
        self.assertEqual(snapshot["hand_cards"][0]["name"], "Kez Lap")
        self.assertEqual(snapshot["source_cards"][0]["name"], "Forras Lap")
        self.assertEqual(snapshot["horizont"][0]["kind"], "entity")
        self.assertEqual(snapshot["horizont"][0]["card"]["name"], "Horizont Egyseg")
        self.assertEqual(snapshot["zenit"][1]["kind"], "card")
        self.assertTrue(snapshot["zenit"][1]["face_down"])
        self.assertTrue(snapshot["zenit"][1]["hidden"])

    def test_export_match_snapshot_includes_players_and_result_metadata(self):
        p1 = make_player("Jatekos_1", realm="Ignis")
        p2 = make_player("Jatekos_2", realm="Aqua")
        p2.overflow_vereseg = True
        game = SimpleNamespace(
            kor=7,
            p1=p1,
            p2=p2,
            log_metrics={"spells_cast": 3, "seal_breaks": 1},
            state=SimpleNamespace(active_player=p1),
        )

        snapshot = export_match_snapshot(game)

        self.assertEqual(snapshot["turn"], 7)
        self.assertEqual(snapshot["active_player"], "Jatekos_1")
        self.assertTrue(snapshot["match_finished"])
        self.assertEqual(snapshot["winner"], "Jatekos_1")
        self.assertEqual(snapshot["victory_reason"], "overflow")
        self.assertEqual(snapshot["p1"]["realm"], "Ignis")
        self.assertEqual(snapshot["p2"]["realm"], "Aqua")
        self.assertEqual(snapshot["log_metrics"]["spells_cast"], 3)
