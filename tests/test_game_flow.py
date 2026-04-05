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
        kez=[],
        horizont=[None] * 6,
        zenit=[None] * 6,
        osforras=[],
        temeto=[],
        pecsetek=[],
        hasznalt_jelek_ebben_a_korben=2,
        kell_tamadnia_kovetkezo_korben=False,
        overflow_vereseg=False,
        overflow_gyoztes_nev=None,
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

    def test_folyekony_pancel_halves_combat_damage_on_horizon(self):
        sim = object.__new__(AeternaSzimulacio)
        sim.kor = 1
        sim._feltor_pecset = lambda vedo, burst=False, *args, **kwargs: (True, burst)
        sim._ellenoriz_gyoztest = lambda: None
        sim._jelol_harc_overflowot = lambda tamado, vedo: (None, None)
        sim._elpusztit_egyseget = lambda *args, **kwargs: False

        attacker_player = make_player("Attacker")
        defender_player = make_player("Defender")
        attacker = make_unit("Tamado", atk=4, hp=5, kingdom="Ignis", exhausted=False)
        defender = make_unit("Vedett", atk=1, hp=5, kingdom="Aqua", exhausted=False)
        attacker.owner = attacker_player
        defender.owner = defender_player
        defender.half_damage_on_horizon_until_turn_end = True
        attacker_player.horizont[0] = attacker
        defender_player.horizont[0] = defender

        with patch("engine.game.trigger_engine.dispatch", Mock(return_value=None)):
            AeternaSzimulacio.harc_fazis(sim, attacker_player, defender_player)

        self.assertEqual(defender.akt_hp, 3)

    def test_langolo_visszavagas_surviving_attacker_continues_combat(self):
        sim = object.__new__(AeternaSzimulacio)
        sim.kor = 1
        sim._feltor_pecset = lambda vedo, burst=False, *args, **kwargs: (True, burst)
        sim._ellenoriz_gyoztest = lambda: None
        sim._jelol_harc_overflowot = lambda tamado, vedo: (None, None)
        sim._elpusztit_egyseget = AeternaSzimulacio._elpusztit_egyseget.__get__(sim, AeternaSzimulacio)

        attacker_player = make_player("Attacker")
        defender_player = make_player("Defender")
        defender_player.hasznalt_jelek_ebben_a_korben = 0

        attacker = make_unit("Tamado", atk=4, hp=6, kingdom="Ignis", exhausted=False)
        defender = make_unit("Vedett", atk=0, hp=5, kingdom="Ignis", exhausted=False)
        trap = make_card("Lángoló Visszavágás", card_type="Jel", magnitude=1, aura=1)
        trap.kepesseg = "Aktivalas: amikor az ellenfel megtamadja az egyik Entitasodat a Horizonton. Hatas: a tamado Entitas azonnal kap 4 sebzest a harc elott."

        attacker.owner = attacker_player
        defender.owner = defender_player
        attacker_player.horizont[0] = attacker
        defender_player.horizont[0] = defender
        defender_player.zenit[0] = trap

        with patch("engine.game.trigger_engine.dispatch", Mock(return_value=SimpleNamespace(cancelled=False))):
            AeternaSzimulacio.harc_fazis(sim, attacker_player, defender_player)

        self.assertEqual(attacker.akt_hp, 2)
        self.assertEqual(defender.akt_hp, 1)
        self.assertIsNone(defender_player.zenit[0])
        self.assertEqual(defender_player.hasznalt_jelek_ebben_a_korben, 1)

    def test_tuzes_megtorlas_triggers_from_real_combat_when_attacker_dies_to_block(self):
        sim = object.__new__(AeternaSzimulacio)
        sim.kor = 1
        sim._feltor_pecset = lambda vedo, burst=False, *args, **kwargs: (True, burst)
        sim._ellenoriz_gyoztest = lambda: None
        sim._jelol_harc_overflowot = lambda tamado, vedo: (None, None)
        sim._elpusztit_egyseget = AeternaSzimulacio._elpusztit_egyseget.__get__(sim, AeternaSzimulacio)

        attacker_player = make_player("Attacker")
        defender_player = make_player("Defender")
        attacker_player.hasznalt_jelek_ebben_a_korben = 0
        defender_player.hasznalt_jelek_ebben_a_korben = 0

        attacker = make_unit("Elesett Tamado", atk=4, hp=1, kingdom="Ignis", exhausted=False)
        blocker = make_unit("Blokkolo", atk=2, hp=5, kingdom="Aqua", exhausted=False)
        trap = make_card("Tuzes Megtorlas", card_type="Jel", magnitude=1, aura=1)
        trap.kepesseg = "Aktivalas: amikor egy sajat, tamado Entitasodat az ellenfel elpusztitja Blokkolas soran. Hatas: a megsemmisult Entitasod ATK-janak felet azonnal megkapja az ellenfel blokkolja mogotti Pecset."

        attacker.owner = attacker_player
        blocker.owner = defender_player
        attacker_player.horizont[0] = attacker
        attacker_player.zenit[0] = trap
        defender_player.horizont[0] = blocker
        sim.p1 = attacker_player
        sim.p2 = defender_player
        defender_player.pecsetek = [
            make_card("Pecset 1", card_type="Pecsét"),
            make_card("Pecset 2", card_type="Pecsét"),
            make_card("Pecset 3", card_type="Pecsét"),
        ]

        AeternaSzimulacio.harc_fazis(sim, attacker_player, defender_player)

        self.assertIsNone(attacker_player.horizont[0])
        self.assertIsNone(attacker_player.zenit[0])
        self.assertEqual(len(defender_player.pecsetek), 1)

    def test_perzselo_csapas_bonus_applies_during_combat_and_cleans_up_afterward(self):
        from cards.resolver import resolve_card_handler

        sim = object.__new__(AeternaSzimulacio)
        sim.kor = 1
        sim._feltor_pecset = lambda vedo, burst=False, *args, **kwargs: (True, burst)
        sim._ellenoriz_gyoztest = lambda: None
        sim._jelol_harc_overflowot = lambda tamado, vedo: (None, None)
        sim._elpusztit_egyseget = AeternaSzimulacio._elpusztit_egyseget.__get__(sim, AeternaSzimulacio)

        attacker_player = make_player("Attacker")
        defender_player = make_player("Defender")
        attacker_player.hasznalt_jelek_ebben_a_korben = 0
        defender_player.hasznalt_jelek_ebben_a_korben = 0

        attacker = make_unit("Buffolt Tamado", atk=2, hp=5, kingdom="Ignis", exhausted=False)
        blocker = make_unit("Blokkolo", atk=0, hp=5, kingdom="Aqua", exhausted=False)
        spell = make_card("Perzselo Csapas", card_type="Ige", magnitude=1, aura=1)

        attacker.owner = attacker_player
        blocker.owner = defender_player
        attacker_player.horizont[0] = attacker
        defender_player.horizont[0] = blocker
        sim.p1 = attacker_player
        sim.p2 = defender_player

        result = resolve_card_handler(spell, category="on_play", jatekos=attacker_player, ellenfel=defender_player)
        self.assertTrue(result["resolved"])
        self.assertEqual(attacker.akt_tamadas, 5)

        AeternaSzimulacio.harc_fazis(sim, attacker_player, defender_player)

        self.assertIsNone(defender_player.horizont[0])
        self.assertEqual(attacker.akt_tamadas, 2)
        self.assertEqual(getattr(attacker, "temp_atk_bonus_until_combat_end", 0), 0)

    def test_tuzgyuru_retribution_damages_attacker_and_cleans_up_on_turn_end(self):
        from cards.resolver import resolve_card_handler
        from cards.priority_handlers import on_turn_end_priority

        sim = object.__new__(AeternaSzimulacio)
        sim.kor = 1
        sim._feltor_pecset = lambda vedo, burst=False, *args, **kwargs: (True, burst)
        sim._ellenoriz_gyoztest = lambda: None
        sim._jelol_harc_overflowot = lambda tamado, vedo: (None, None)
        sim._elpusztit_egyseget = AeternaSzimulacio._elpusztit_egyseget.__get__(sim, AeternaSzimulacio)

        attacker_player = make_player("Attacker")
        defender_player = make_player("Defender")
        attacker = make_unit("Tamado", atk=3, hp=4, kingdom="Aqua", exhausted=False)
        defender = make_unit("Vedett", atk=1, hp=5, kingdom="Ignis", exhausted=False)
        spell = make_card("Tuzgyuru", card_type="Ige", magnitude=1, aura=1)

        attacker.owner = attacker_player
        defender.owner = defender_player
        attacker_player.horizont[0] = attacker
        defender_player.horizont[0] = defender
        sim.p1 = attacker_player
        sim.p2 = defender_player

        result = resolve_card_handler(spell, category="on_play", jatekos=defender_player, ellenfel=attacker_player)
        self.assertTrue(result["resolved"])
        self.assertEqual(getattr(defender, "retaliate_on_attacked_damage_until_turn_end", 0), 2)

        AeternaSzimulacio.harc_fazis(sim, attacker_player, defender_player)

        self.assertEqual(attacker.akt_hp, 1)
        self.assertEqual(defender.akt_hp, 2)

        on_turn_end_priority(SimpleNamespace(owner=defender_player))
        self.assertEqual(getattr(defender, "retaliate_on_attacked_damage_until_turn_end", 0), 0)
        self.assertNotIn("aegis", getattr(defender, "temp_granted_keywords", set()))


if __name__ == "__main__":
    unittest.main()
