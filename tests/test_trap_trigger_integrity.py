import unittest
from types import SimpleNamespace

from cards.resolver import can_activate_trap, resolve_lethal_trap
from engine.card import CsataEgyseg


def make_card(name, card_type="Entitas", atk=1, hp=1, magnitude=1, aura=1):
    return SimpleNamespace(
        nev=name,
        kartyatipus=card_type,
        kepesseg="",
        birodalom="Terra",
        klan="",
        faj="",
        kaszt="",
        magnitudo=magnitude,
        aura_koltseg=aura,
        tamadas=atk,
        eletero=hp,
        egyseg_e="Entitas" in card_type,
        jel_e="Jel" in card_type,
        reakcio_e=False,
    )


def make_player(name="P1"):
    return SimpleNamespace(
        nev=name,
        birodalom="Terra",
        pakli=[],
        kez=[],
        osforras=[],
        temeto=[],
        horizont=[None] * 6,
        zenit=[None] * 6,
        pecsetek=[],
        hasznalt_jelek_ebben_a_korben=0,
    )


class TestTrapTriggerIntegrity(unittest.TestCase):
    def test_fa_oleles_does_not_activate_as_generic_combat_trap(self):
        trap = make_card("Fa-ölelés", card_type="Jel")
        attacker = CsataEgyseg(make_card("Tamado", atk=4, hp=4))
        attacker_owner = make_player("Attacker")
        defender = make_player("Defender")

        self.assertFalse(
            can_activate_trap(
                trap,
                tamado_egyseg=attacker,
                tamado=attacker_owner,
                vedo=defender,
            )
        )

    def test_fa_oleles_lethal_trap_moves_unit_to_zenit_and_prevents_death(self):
        owner = make_player("Owner")
        attacker = CsataEgyseg(make_card("Tamado", atk=4, hp=4))
        unit = CsataEgyseg(make_card("Vedett", atk=2, hp=2))
        owner.horizont[0] = unit
        owner.zenit[0] = make_card("Fa-ölelés", card_type="Jel")

        result = resolve_lethal_trap(
            owner=owner,
            unit=unit,
            attacker=attacker,
            zone_name="horizont",
            index=0,
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["prevented_death"])
        self.assertTrue(result["stop_attack"])
        self.assertIsNone(owner.horizont[0])
        self.assertIs(owner.zenit[0], unit)
        self.assertEqual(unit.akt_hp, 1)


if __name__ == "__main__":
    unittest.main()
