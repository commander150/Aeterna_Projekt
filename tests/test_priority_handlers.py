import unittest
from types import SimpleNamespace

from cards.resolver import can_activate_trap, resolve_card_handler
from engine.card import CsataEgyseg


def make_card(name, card_type="Entitás", text="", realm="Aether", magnitude=1, aura=1, atk=1, hp=1):
    return SimpleNamespace(
        nev=name,
        kartyatipus=card_type,
        kepesseg=text,
        birodalom=realm,
        klan="",
        faj="",
        kaszt="",
        magnitudo=magnitude,
        aura_koltseg=aura,
        tamadas=atk,
        eletero=hp,
        egyseg_e="Entitás" in card_type,
        jel_e="Jel" in card_type,
        reakcio_e=False,
    )


def make_player(name="P1", realm="Aether"):
    return SimpleNamespace(
        nev=name,
        birodalom=realm,
        pakli=[],
        kez=[],
        temeto=[],
        horizont=[None] * 6,
        zenit=[None] * 6,
        pecsetek=[],
        hasznalt_jelek_ebben_a_korben=0,
        kovetkezo_jel_kedvezmeny=0,
    )


class TestPriorityHandlers(unittest.TestCase):
    def test_felderito_bagoly_handles_opponent_topdeck(self):
        bagoly = make_card("Felderítő Bagoly", text="[DOMÍNIUM] Riadó (Clarion): Nézd meg...")
        owner = make_player("P1")
        opponent = make_player("P2")
        opponent.pakli = [
            make_card("Gyenge lap", aura=1, magnitude=1),
            make_card("Erős lap", aura=4, magnitude=4, atk=4, hp=4),
        ]

        result = resolve_card_handler(bagoly, category="on_play", jatekos=owner, ellenfel=opponent)

        self.assertTrue(result["resolved"])
        self.assertEqual(opponent.pakli[0].nev, "Erős lap")

    def test_csapdaallito_adds_next_trap_discount(self):
        csapdaallito = make_card("Csapdaállító", text="[DOMÍNIUM] Riadó (Clarion): ...")
        owner = make_player()

        result = resolve_card_handler(csapdaallito, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(owner.kovetkezo_jel_kedvezmeny, 1)

    def test_csapda_a_fustben_consumes_on_big_summon(self):
        trap = make_card("Csapda a Füstben", card_type="Jel", text="Aktiválás: ...")
        summoned = CsataEgyseg(make_card("Nagy Entitás", magnitude=4, atk=4, hp=4))
        owner = make_player("Attacker")
        defender = make_player("Defender")

        result = resolve_card_handler(
            trap,
            category="summon_trap",
            vedo=defender,
            tamado=owner,
            summoned_unit=summoned,
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["consume_trap"])
        self.assertTrue(summoned.kimerult)

    def test_varatlan_erosites_only_activates_on_open_seal_attack(self):
        trap = make_card("Váratlan Erősítés", card_type="Jel", text="Aktiválás: ...")
        attacker_owner = make_player("Attacker")
        defender = make_player("Defender")
        defender.pecsetek = [make_card("Pecsét", card_type="Pecsét")]
        attacker = CsataEgyseg(make_card("Támadó", atk=3, hp=2))
        attacker.kimerult = False
        attacker_owner.horizont[2] = attacker

        self.assertTrue(can_activate_trap(trap, tamado_egyseg=attacker, tamado=attacker_owner, vedo=defender))

        result = resolve_card_handler(
            trap,
            category="trap",
            tamado_egyseg=attacker,
            tamado=attacker_owner,
            vedo=defender,
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["stop_attack"])


if __name__ == "__main__":
    unittest.main()
