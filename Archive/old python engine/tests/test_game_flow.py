import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from engine.actions import ActionLibrary
from engine.card import CsataEgyseg
from engine.game import AeternaSzimulacio
from engine.targeting import TargetingEngine


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

    def test_dispatch_damage_events_emits_canonical_combat_damage_taken(self):
        sim = object.__new__(AeternaSzimulacio)
        source = make_unit("Tamado")
        target = make_unit("Vedett")
        owner = make_player("Owner")
        seen = []

        with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            AeternaSzimulacio._dispatch_damage_events(
                sim,
                source,
                owner,
                target,
                {"damage": 2, "combat": True},
            )

        self.assertIn("on_damage_taken", seen)
        self.assertIn("on_combat_damage_taken", seen)

    def test_feltor_pecset_emits_on_seal_break(self):
        sim = object.__new__(AeternaSzimulacio)
        defender = make_player("Defender")
        seal = make_card("Pecset", card_type="Pecset", magnitude=1, aura=0)
        defender.pecsetek = [seal]
        seen = []

        with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            broken, _ = AeternaSzimulacio._feltor_pecset(sim, defender, False, "Teszt")

        self.assertTrue(broken)
        self.assertIn("on_seal_break", seen)

    def test_move_target_to_horizont_emits_canonical_move_trigger(self):
        owner = make_player("Owner")
        target = make_unit("Hatso", exhausted=False)
        target.owner = owner
        owner.zenit[0] = target
        seen = []

        with patch("engine.actions.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            moved = ActionLibrary.move_target_to_horizont(owner, "zenit", 0, "Teszt", exhausted=True)

        self.assertTrue(moved)
        self.assertIn("on_move_zenit_to_horizont", seen)
        self.assertIs(owner.horizont[0], target)

    def test_kor_futtatasa_emits_canonical_turn_adapters(self):
        sim = object.__new__(AeternaSzimulacio)
        sim.kor = 1

        def _player(name):
            return SimpleNamespace(
                nev=name,
                kell_tamadnia_kovetkezo_korben=False,
                horizont=[None] * 6,
                uj_kor_inditasa=lambda: None,
                huzas=lambda: None,
                osforras_bovites=lambda: None,
                kor_vegi_heal=lambda: None,
            )

        sim.p1 = _player("P1")
        sim.p2 = _player("P2")
        sim.state = SimpleNamespace(kor=1)
        sim.phase_runner = SimpleNamespace(run_play_phase=lambda akt: None)
        sim.combat_resolver = SimpleNamespace(resolve_attack_phase=lambda akt, ell: None)

        seen = []
        with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            result = AeternaSzimulacio.kor_futtatasa(sim)

        self.assertIsNone(result)
        self.assertIn("on_start_of_turn", seen)
        self.assertIn("on_next_own_awakening", seen)

    def test_alkalmaz_kartya_hatast_emits_enemy_spell_or_ritual_played(self):
        sim = object.__new__(AeternaSzimulacio)
        caster = make_player("Caster")
        defender = make_player("Defender")
        spell = make_card("Villam", card_type="Ige", magnitude=1, aura=1)
        sim.p1 = caster
        sim.p2 = defender
        seen = []

        with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            with patch("engine.game.EffectEngine.trigger_on_play", return_value=None):
                result = AeternaSzimulacio._alkalmaz_kartya_hatast(sim, spell, caster, defender)

        self.assertIsNone(result)
        self.assertIn("on_enemy_spell_or_ritual_played", seen)

    def test_kijatszas_fazis_emits_enemy_zenit_summon(self):
        sim = object.__new__(AeternaSzimulacio)
        unit_card = make_card("Zenit Entitas", card_type="Entitas", magnitude=1, aura=1)
        caster = SimpleNamespace(
            nev="Caster",
            kez=[unit_card],
            horizont=[None] * 6,
            zenit=[None] * 6,
            osforras=[{"lap": make_card("Forras"), "hasznalt": False}],
            megidezett_entitasok_ebben_a_korben=0,
            elerheto_aura=lambda: 1,
            effektiv_aura_koltseg=lambda lap: 1,
            fizet=lambda lap: True,
        )
        defender = make_player("Defender")
        sim.p1 = caster
        sim.p2 = defender
        sim._resolve_summon_traps = Mock(return_value=False)
        sim._alkalmaz_kartya_hatast = Mock(return_value=None)
        seen = []

        with patch("engine.game.random.choice", return_value=unit_card):
            with patch("engine.game.random.random", return_value=0.95):
                with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
                    result = AeternaSzimulacio.kijatszas_fazis(sim, caster)

        self.assertIsNone(result)
        self.assertIn("on_enemy_zenit_summon", seen)
        self.assertIsNotNone(caster.zenit[0])

    def test_summon_card_to_zenit_uses_shared_dispatch_path(self):
        owner = make_player("Owner")
        card = make_card("Hatso Erkezo", card_type="Entitas")
        seen = []

        with patch("engine.actions.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            unit = ActionLibrary.summon_card_to_zenit(owner, card, lane_index=2, reason="Teszt", exhausted=True)

        self.assertIsNotNone(unit)
        self.assertIs(owner.zenit[2], unit)
        self.assertIn("on_summon", seen)
        self.assertNotIn("on_entity_enters_horizont", seen)

    def test_kijatszas_fazis_horizont_summon_uses_shared_horizont_path(self):
        sim = object.__new__(AeternaSzimulacio)
        unit_card = make_card("Horizont Entitas", card_type="Entitas", magnitude=1, aura=1)
        caster = SimpleNamespace(
            nev="Caster",
            kez=[unit_card],
            horizont=[None] * 6,
            zenit=[None] * 6,
            osforras=[{"lap": make_card("Forras"), "hasznalt": False}],
            megidezett_entitasok_ebben_a_korben=0,
            elerheto_aura=lambda: 1,
            effektiv_aura_koltseg=lambda lap: 1,
            fizet=lambda lap: True,
        )
        defender = make_player("Defender")
        sim.p1 = caster
        sim.p2 = defender
        sim._resolve_summon_traps = Mock(return_value=False)
        sim._alkalmaz_kartya_hatast = Mock(return_value=None)
        seen = []

        with patch("engine.game.random.choice", return_value=unit_card):
            with patch("engine.game.random.random", return_value=0.2):
                with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
                    result = AeternaSzimulacio.kijatszas_fazis(sim, caster)

        self.assertIsNone(result)
        self.assertIn("on_entity_enters_horizont", seen)
        self.assertIn("on_enemy_summon", seen)
        self.assertIsNotNone(caster.horizont[0])

    def test_resolve_spell_cast_traps_emits_on_trap_triggered(self):
        sim = object.__new__(AeternaSzimulacio)
        caster = make_player("Caster")
        defender = make_player("Defender")
        defender.hasznalt_jelek_ebben_a_korben = 0
        trap = make_card("Teszt Jel", card_type="Jel")
        spell = make_card("Villam", card_type="Ige")
        defender.zenit[0] = trap
        seen = []

        with patch("engine.game.resolve_spell_cast_trap", return_value={"consume_trap": True}):
            with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
                result = AeternaSzimulacio._resolve_spell_cast_traps(sim, spell, caster, defender)

        self.assertTrue(result["consume_trap"])
        self.assertIn("on_trap_triggered", seen)

    def test_resolve_summon_traps_emits_on_trap_triggered_and_consumes_trap(self):
        sim = object.__new__(AeternaSzimulacio)
        owner = make_player("Owner")
        opponent = make_player("Opponent")
        opponent.hasznalt_jelek_ebben_a_korben = 0
        summoned = make_unit("Erkezo")
        trap = make_card("Teszt Summon Trap", card_type="Jel")
        opponent.zenit[0] = trap
        seen = []

        with patch("engine.game.resolve_card_handler", return_value={"consume_trap": True, "destroy_summoned": False}):
            with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
                resolved = AeternaSzimulacio._resolve_summon_traps(sim, summoned, owner, opponent)

        self.assertTrue(resolved)
        self.assertIn("on_trap_triggered", seen)
        self.assertIsNone(opponent.zenit[0])
        self.assertEqual(opponent.temeto[-1].nev, "Teszt Summon Trap")

    def test_harc_fazis_emits_on_attack_hits_for_seal_hit(self):
        sim = object.__new__(AeternaSzimulacio)
        sim.kor = 1
        sim._feltor_pecset = lambda vedo, burst=False, *args, **kwargs: (True, burst)
        sim._ellenoriz_gyoztest = lambda: None
        sim._jelol_harc_overflowot = lambda tamado, vedo: (None, None)
        sim._elpusztit_egyseget = lambda *args, **kwargs: False

        attacker_player = make_player("Attacker")
        defender_player = make_player("Defender")
        attacker = make_unit("Tamado", atk=3, hp=3, exhausted=False)
        attacker.owner = attacker_player
        attacker_player.horizont[0] = attacker
        defender_player.pecsetek = [make_card("Pecset", card_type="Pecset")]
        seen = []

        with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            AeternaSzimulacio.harc_fazis(sim, attacker_player, defender_player)

        self.assertIn("on_attack_hits", seen)

    def test_harc_fazis_emits_on_attack_hits_for_blocker_hit(self):
        sim = object.__new__(AeternaSzimulacio)
        sim.kor = 1
        sim._feltor_pecset = lambda vedo, burst=False, *args, **kwargs: (True, burst)
        sim._ellenoriz_gyoztest = lambda: None
        sim._jelol_harc_overflowot = lambda tamado, vedo: (None, None)
        sim._elpusztit_egyseget = lambda *args, **kwargs: False

        attacker_player = make_player("Attacker")
        defender_player = make_player("Defender")
        attacker = make_unit("Tamado", atk=3, hp=4, exhausted=False)
        blocker = make_unit("Blokkolo", atk=1, hp=5, exhausted=False)
        attacker.owner = attacker_player
        blocker.owner = defender_player
        attacker_player.horizont[0] = attacker
        defender_player.horizont[0] = blocker
        seen = []

        with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            AeternaSzimulacio.harc_fazis(sim, attacker_player, defender_player)

        self.assertIn("on_attack_hits", seen)

    def test_heal_unit_emits_on_heal(self):
        owner = make_player("Owner")
        target = make_unit("Serult", hp=5)
        target.owner = owner
        target.akt_hp = 2
        seen = []

        with patch("engine.actions.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            healed = ActionLibrary.heal_unit(target, 2, "Teszt", owner=owner, source=target)

        self.assertEqual(healed, 2)
        self.assertIn("on_heal", seen)

    def test_return_target_to_hand_emits_on_bounce(self):
        owner = make_player("Owner")
        target = make_unit("Visszatero")
        target.owner = owner
        owner.horizont[0] = target
        seen = []

        with patch("engine.actions.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            returned = ActionLibrary.return_target_to_hand(owner, "horizont", 0, "Teszt")

        self.assertTrue(returned)
        self.assertIn("on_bounce", seen)

    def test_move_target_to_zenit_swap_emits_on_position_swap(self):
        owner = make_player("Owner")
        front = make_unit("Front", exhausted=False)
        back = make_unit("Back", exhausted=False)
        front.owner = owner
        back.owner = owner
        owner.horizont[0] = front
        owner.zenit[0] = back
        seen = []

        with patch("engine.actions.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            moved = ActionLibrary.move_target_to_zenit(owner, "horizont", 0, "Teszt")

        self.assertTrue(moved)
        self.assertIn("on_position_swap", seen)

    def test_summon_card_to_horizont_emits_on_entity_enters_horizont(self):
        owner = make_player("Owner")
        card = make_card("Erkezo", card_type="Entitas")
        seen = []

        with patch("engine.actions.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            unit = ActionLibrary.summon_card_to_horizont(owner, card, lane_index=1, reason="Teszt", exhausted=False)

        self.assertIsNotNone(unit)
        self.assertIn("on_entity_enters_horizont", seen)

    def test_destroy_unit_emits_on_destroy(self):
        from engine.effects import EffectEngine

        owner = make_player("Owner")
        enemy = make_player("Enemy")
        target = make_unit("Aldozat", hp=2)
        target.owner = owner
        owner.horizont[0] = target
        seen = []

        with patch("engine.effects.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            destroyed = EffectEngine.destroy_unit(owner, "horizont", 0, enemy, "Teszt")

        self.assertTrue(destroyed)
        self.assertIn("on_destroy", seen)

    def test_discard_from_hand_emits_on_discard(self):
        owner = make_player("Owner")
        owner.kez = [make_card("Eldobott Lap", card_type="Ige")]
        seen = []

        with patch("engine.actions.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            discarded = ActionLibrary.discard_from_hand(owner, 0, "Teszt")

        self.assertTrue(discarded)
        self.assertIn("on_discard", seen)

    def test_move_target_to_source_emits_on_source_placement(self):
        owner = make_player("Owner")
        owner.temeto = [make_card("Forrasba Kerulo", card_type="Ige")]
        seen = []

        with patch("engine.actions.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            moved = ActionLibrary.move_target_to_source(owner, "temeto", 0, "Teszt")

        self.assertTrue(moved)
        self.assertIn("on_source_placement", seen)

    def test_grant_keyword_emits_on_gain_keyword(self):
        owner = make_player("Owner")
        target = make_unit("Cel")
        target.owner = owner
        seen = []

        with patch("engine.actions.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            granted = ActionLibrary.grant_keyword(target, "taunt", temporary=True, owner=owner, source=target)

        self.assertTrue(granted)
        self.assertIn("on_gain_keyword", seen)

    def test_return_to_hand_respects_untargetable_enforcement(self):
        owner = make_player("Owner")
        target = make_unit("Vedett")
        target.owner = owner
        owner.horizont[0] = target
        ActionLibrary.grant_untargetable(target, "Teszt", owner=owner, source=target)

        returned = ActionLibrary.return_target_to_hand(owner, "horizont", 0, "Teszt")

        self.assertFalse(returned)
        self.assertIs(owner.horizont[0], target)

    def test_position_lock_blocks_move_to_horizont(self):
        owner = make_player("Owner")
        target = make_unit("Hatso")
        target.owner = owner
        target.position_lock_awakenings = 1
        owner.zenit[0] = target

        moved = ActionLibrary.move_target_to_horizont(owner, "zenit", 0, "Teszt", exhausted=True)

        self.assertFalse(moved)
        self.assertIs(owner.zenit[0], target)
        self.assertIsNone(owner.horizont[0])

    def test_locked_summon_ability_does_not_apply_priority_effect(self):
        from cards.priority_handlers import on_summon_priority

        owner = make_player("Owner")
        enemy = make_player("Enemy")
        unit = make_unit("Lopakodo Felcser-Dron")
        unit.owner = owner
        unit.abilities_locked_until_turn_end = True

        on_summon_priority(SimpleNamespace(source=unit, owner=owner, target=enemy, payload={}))

        self.assertFalse(TargetingEngine.target_state(unit).spell_negate)

    def test_feltor_pecset_emits_on_source_placement_when_guardianship_moves_to_source(self):
        sim = object.__new__(AeternaSzimulacio)
        defender = make_player("Defender")
        seal = make_card("Pecset", card_type="PecsĂ©t", magnitude=3, aura=0)
        defender.pecsetek = [seal]
        seen = []

        with patch("engine.game.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            broken, _ = AeternaSzimulacio._feltor_pecset(sim, defender, False, "Teszt")

        self.assertTrue(broken)
        self.assertIn("on_source_placement", seen)

    def test_explicit_seal_break_helper_emits_on_seal_break(self):
        from engine.effects import EffectEngine

        caster = make_player("Caster")
        defender = make_player("Defender")
        defender.pecsetek = [make_card("Pecset", card_type="PecsĂ©t", magnitude=1, aura=0)]
        seen = []

        with patch("engine.effects.trigger_engine.dispatch", side_effect=lambda event_name, **kwargs: seen.append(event_name)):
            resolved = EffectEngine._deal_direct_seal_damage("Teszt", 1, caster, defender, "Structured")

        self.assertTrue(resolved)
        self.assertIn("on_seal_break", seen)


if __name__ == "__main__":
    unittest.main()
