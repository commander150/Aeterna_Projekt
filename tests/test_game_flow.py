import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from engine.card import CsataEgyseg
from engine.game import AeternaSzimulacio


def make_card(name, card_type="Entitas", magnitude=1, aura=1):
    return SimpleNamespace(
        nev=name,
        kartyatipus=card_type,
        kepesseg="",
        birodalom="Aether",
        klan="",
        faj="",
        kaszt="",
        magnitudo=magnitude,
        aura_koltseg=aura,
        tamadas=1,
        eletero=1,
        egyseg_e="Entitas" in card_type,
        jel_e="Jel" in card_type,
        reakcio_e=False,
    )


def make_unit(name, *, atk=1, hp=1, kingdom="Aether", exhausted=False):
    card = make_card(name, magnitude=1, aura=1)
    card.birodalom = kingdom
    card.tamadas = atk
    card.eletero = hp
    unit = CsataEgyseg(card)
    unit.kimerult = exhausted
    return unit


def make_player(name):
    return SimpleNamespace(
        nev=name,
        horizont=[None] * 6,
        zenit=[None] * 6,
        temeto=[],
        pecsetek=[],
        hasznalt_jelek_ebben_a_korben=2,
        kell_tamadnia_kovetkezo_korben=False,
        jelol_overflow_vereseget=lambda gyoztes_nev: None,
    )


class TestGameFlow(unittest.TestCase):
    def test_kijatszas_fazis_skips_spell_effect_when_spell_trap_cancels(self):
        sim = object.__new__(AeternaSzimulacio)
        spell = make_card("Villam", card_type="Ige", magnitude=1, aura=1)
        caster = SimpleNamespace(
            nev="Caster",
            kez=[spell],
            osforras=[{"lap": make_card("Forras"), "hasznalt": False}],
            temeto=[],
            elerheto_aura=lambda: 1,
            effektiv_aura_koltseg=lambda lap: 1,
            fizet=lambda lap: True,
        )
        defender = SimpleNamespace(nev="Defender")
        sim.p1 = caster
        sim.p2 = defender
        sim._alkalmaz_kartya_hatast = Mock(return_value=None)
        sim._resolve_spell_cast_traps = Mock(return_value={"consume_trap": True, "cancelled_spell": True})

        result = AeternaSzimulacio.kijatszas_fazis(sim, caster)

        self.assertIsNone(result)
        sim._resolve_spell_cast_traps.assert_called_once_with(spell, caster, defender)
        sim._alkalmaz_kartya_hatast.assert_not_called()
        self.assertIn(spell, caster.temeto)
        self.assertNotIn(spell, caster.kez)

    def test_vulkani_golem_cannot_attack_without_two_other_active_ignis_units(self):
        sim = object.__new__(AeternaSzimulacio)
        sim.kor = 1
        sim._feltor_pecset = lambda vedo, burst=False, *args, **kwargs: (True, burst)
        sim._ellenoriz_gyoztest = lambda: None
        sim._jelol_harc_overflowot = lambda tamado, vedo: (None, None)
        sim._elpusztit_egyseget = lambda *args, **kwargs: False

        attacker_player = make_player("Attacker")
        defender_player = make_player("Defender")
        golem = make_unit("Vulkáni Gólem", atk=4, hp=6, kingdom="Ignis", exhausted=False)
        ally = make_unit("Ignis Tars", atk=2, hp=2, kingdom="Ignis", exhausted=False)
        golem.owner = attacker_player
        ally.owner = attacker_player
        attacker_player.horizont[0] = golem
        attacker_player.horizont[1] = ally

        with patch("engine.game.trigger_engine.dispatch", Mock(return_value=None)):
            AeternaSzimulacio.harc_fazis(sim, attacker_player, defender_player)

        self.assertFalse(golem.kimerult)

    def test_vulkani_golem_can_attack_with_two_other_active_ignis_units(self):
        sim = object.__new__(AeternaSzimulacio)
        sim.kor = 1
        sim._feltor_pecset = lambda vedo, burst=False, *args, **kwargs: (True, burst)
        sim._ellenoriz_gyoztest = lambda: None
        sim._jelol_harc_overflowot = lambda tamado, vedo: (None, None)
        sim._elpusztit_egyseget = lambda *args, **kwargs: False

        attacker_player = make_player("Attacker")
        defender_player = make_player("Defender")
        golem = make_unit("Vulkáni Gólem", atk=4, hp=6, kingdom="Ignis", exhausted=False)
        ally1 = make_unit("Ignis Tars 1", atk=2, hp=2, kingdom="Ignis", exhausted=False)
        ally2 = make_unit("Ignis Tars 2", atk=2, hp=2, kingdom="Ignis", exhausted=False)
        golem.owner = attacker_player
        ally1.owner = attacker_player
        ally2.owner = attacker_player
        attacker_player.horizont[0] = golem
        attacker_player.horizont[1] = ally1
        attacker_player.horizont[2] = ally2

        with patch("engine.game.trigger_engine.dispatch", Mock(return_value=None)):
            AeternaSzimulacio.harc_fazis(sim, attacker_player, defender_player)

        self.assertTrue(golem.kimerult)


if __name__ == "__main__":
    unittest.main()
