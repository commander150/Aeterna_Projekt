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
        osforras=[],
        temeto=[],
        horizont=[None] * 6,
        zenit=[None] * 6,
        pecsetek=[],
        hasznalt_jelek_ebben_a_korben=0,
        kovetkezo_jel_kedvezmeny=0,
        kovetkezo_gepezet_kedvezmeny=0,
        megidezett_entitasok_ebben_a_korben=0,
        kovetkezo_kor_ideiglenes_aura=0,
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

    def test_alvilagi_kapcsolatok_puts_lowest_trap_to_zenit(self):
        ritual = make_card("Alvilági Kapcsolatok", card_type="Rituálé")
        owner = make_player()
        owner.pakli = [
            make_card("Drága Jel", card_type="Jel", magnitude=4, aura=4),
            make_card("Olcsó Jel", card_type="Jel", magnitude=1, aura=1),
        ]

        result = resolve_card_handler(ritual, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(owner.zenit[0].nev, "Olcsó Jel")

    def test_kereskedelmi_embargo_marks_second_summon_for_destruction(self):
        trap = make_card("Kereskedelmi Embargó", card_type="Jel")
        defender = make_player("Defender")
        attacker_owner = make_player("Attacker")
        attacker_owner.megidezett_entitasok_ebben_a_korben = 2
        summoned = CsataEgyseg(make_card("Második Idézés", magnitude=5))

        result = resolve_card_handler(
            trap,
            category="summon_trap",
            vedo=defender,
            tamado=attacker_owner,
            summoned_unit=summoned,
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["destroy_summoned"])

    def test_hamis_arany_drains_remaining_aura_after_spell(self):
        trap = make_card("Hamis Arany", card_type="Jel")
        defender = make_player("Defender")
        attacker = make_player("Caster")
        attacker.osforras = [{"lap": make_card("Forrás"), "hasznalt": False} for _ in range(3)]
        spell = make_card("Varázslat", card_type="Ige")

        result = resolve_card_handler(
            trap,
            category="trap",
            varazslat=spell,
            jatekos=defender,
            ellenfel=attacker,
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(all(source["hasznalt"] for source in attacker.osforras))


if __name__ == "__main__":
    unittest.main()
