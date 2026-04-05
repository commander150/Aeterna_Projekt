import unittest
from types import SimpleNamespace

from cards.resolver import can_activate_trap, resolve_card_handler, resolve_spell_redirect
from engine.card import CsataEgyseg
from engine.effects import EffectEngine
from engine.effect_diagnostics_v2 import install_effect_diagnostics
from engine.game import AeternaSzimulacio
from engine.triggers import trigger_engine


def make_card(name, card_type="EntitĂˇs", text="", realm="Aether", magnitude=1, aura=1, atk=1, hp=1):
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
        egyseg_e="EntitĂˇs" in card_type,
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
        kovetkezo_entitas_kedvezmeny=0,
        tomegtermeles_gyara_aktiv=False,
        tomegtermeles_gyara_triggerelt_ebben_a_korben=False,
        tukrozodo_remeny_aktiv=False,
        megtorlo_feny_aktiv=False,
        martirok_vedelme_aktiv=False,
        vamszedo_pont_figyelo=None,
        ideiglenes_aura_ebben_a_korben=0,
        rezonancia_aura=0,
        ad_ideiglenes_aurat=lambda mennyiseg, forras="": mennyiseg,
        huzas=lambda extra=False, trigger_watch=True: True,
    )


class TestPriorityHandlers(unittest.TestCase):
    def test_felderito_bagoly_handles_opponent_topdeck(self):
        bagoly = make_card("FelderĂ­tĹ‘ Bagoly", text="[DOMĂŤNIUM] RiadĂł (Clarion): NĂ©zd meg...")
        owner = make_player("P1")
        opponent = make_player("P2")
        opponent.pakli = [
            make_card("Gyenge lap", aura=1, magnitude=1),
            make_card("ErĹ‘s lap", aura=4, magnitude=4, atk=4, hp=4),
        ]

        result = resolve_card_handler(bagoly, category="on_play", jatekos=owner, ellenfel=opponent)

        self.assertTrue(result["resolved"])
        self.assertEqual(opponent.pakli[0].nev, "ErĹ‘s lap")

    def test_csapdaallito_adds_next_trap_discount(self):
        csapdaallito = make_card("CsapdaĂˇllĂ­tĂł", text="[DOMĂŤNIUM] RiadĂł (Clarion): ...")
        owner = make_player()

        result = resolve_card_handler(csapdaallito, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(owner.kovetkezo_jel_kedvezmeny, 1)

    def test_csapda_a_fustben_consumes_on_big_summon(self):
        trap = make_card("Csapda a FĂĽstben", card_type="Jel", text="AktivĂˇlĂˇs: ...")
        summoned = CsataEgyseg(make_card("Nagy EntitĂˇs", magnitude=4, atk=4, hp=4))
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
        trap = make_card("VĂˇratlan ErĹ‘sĂ­tĂ©s", card_type="Jel", text="AktivĂˇlĂˇs: ...")
        attacker_owner = make_player("Attacker")
        defender = make_player("Defender")
        defender.pecsetek = [make_card("PecsĂ©t", card_type="PecsĂ©t")]
        attacker = CsataEgyseg(make_card("TĂˇmadĂł", atk=3, hp=2))
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
        ritual = make_card("AlvilĂˇgi Kapcsolatok", card_type="RituĂˇlĂ©")
        owner = make_player()
        owner.pakli = [
            make_card("DrĂˇga Jel", card_type="Jel", magnitude=4, aura=4),
            make_card("OlcsĂł Jel", card_type="Jel", magnitude=1, aura=1),
        ]

        result = resolve_card_handler(ritual, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(owner.zenit[0].nev, "OlcsĂł Jel")

    def test_kereskedelmi_embargo_marks_second_summon_for_destruction(self):
        trap = make_card("Kereskedelmi EmbargĂł", card_type="Jel")
        defender = make_player("Defender")
        attacker_owner = make_player("Attacker")
        attacker_owner.megidezett_entitasok_ebben_a_korben = 2
        summoned = CsataEgyseg(make_card("MĂˇsodik IdĂ©zĂ©s", magnitude=5))

        result = resolve_card_handler(
            trap,
            category="summon_trap",
            vedo=defender,
            tamado=attacker_owner,
            summoned_unit=summoned,
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["destroy_summoned"])

    def test_viharos_ellencsapas_reactivates_exhausted_unit_on_big_enemy_summon(self):
        trap = make_card("Viharos Ellencsapas", card_type="Jel")
        defender = make_player("Defender")
        attacker_owner = make_player("Attacker")
        summoned = CsataEgyseg(make_card("Nagy Entitas", magnitude=4, atk=4, hp=4))
        exhausted = CsataEgyseg(make_card("Faradt Vedo", atk=2, hp=3))
        exhausted.kimerult = True
        defender.horizont[0] = exhausted

        result = resolve_card_handler(
            trap,
            category="summon_trap",
            vedo=defender,
            tamado=attacker_owner,
            summoned_unit=summoned,
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["consume_trap"])
        self.assertFalse(exhausted.kimerult)
        self.assertEqual(exhausted.akt_tamadas, 4)

    def test_viharos_ellencsapas_does_not_activate_as_generic_combat_trap(self):
        trap = make_card("Viharos Ellencsapas", card_type="Jel")

        self.assertFalse(can_activate_trap(trap))

    def test_vegzetes_lepes_only_on_seal_attack_and_redirects_attacker_damage(self):
        trap = make_card("Vegzetes Lepes", card_type="Jel")
        attacker_owner = make_player("Attacker")
        defender = make_player("Defender")
        attacker = CsataEgyseg(make_card("Tamado", atk=4, hp=4))
        other_enemy = CsataEgyseg(make_card("Masik", atk=1, hp=4))
        aldozat = CsataEgyseg(make_card("Aldozat", atk=1, hp=2))
        attacker_owner.horizont[0] = attacker
        attacker_owner.horizont[1] = other_enemy
        defender.horizont[0] = aldozat

        self.assertFalse(can_activate_trap(trap, tamado_egyseg=attacker, tamado=attacker_owner, vedo=defender))
        self.assertTrue(
            can_activate_trap(
                trap,
                tamado_egyseg=attacker,
                tamado=attacker_owner,
                vedo=defender,
                target_kind="seal",
            )
        )

        result = resolve_card_handler(
            trap,
            category="trap",
            tamado_egyseg=attacker,
            tamado=attacker_owner,
            vedo=defender,
            target_kind="seal",
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["stop_attack"])
        self.assertTrue(result["consume_trap"])
        self.assertIsNone(defender.horizont[0])
        self.assertEqual(defender.temeto[-1].nev, "Aldozat")
        self.assertIsNone(attacker_owner.horizont[1])

    def test_vegzetes_lepes_partial_when_no_other_enemy_target_exists(self):
        trap = make_card("Vegzetes Lepes", card_type="Jel")
        attacker_owner = make_player("Attacker")
        defender = make_player("Defender")
        attacker = CsataEgyseg(make_card("Tamado", atk=4, hp=4))
        aldozat = CsataEgyseg(make_card("Aldozat", atk=1, hp=2))
        attacker_owner.horizont[0] = attacker
        defender.horizont[0] = aldozat

        self.assertFalse(
            can_activate_trap(
                trap,
                tamado_egyseg=attacker,
                tamado=attacker_owner,
                vedo=defender,
                target_kind="seal",
            )
        )

        result = resolve_card_handler(
            trap,
            category="trap",
            tamado_egyseg=attacker,
            tamado=attacker_owner,
            vedo=defender,
            target_kind="seal",
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["partial"])
        self.assertTrue(result["stop_attack"])
        self.assertTrue(result["consume_trap"])
        self.assertIsNone(defender.horizont[0])

    def test_hamis_arany_drains_remaining_aura_after_spell(self):
        trap = make_card("Hamis Arany", card_type="Jel")
        defender = make_player("Defender")
        attacker = make_player("Caster")
        attacker.osforras = [{"lap": make_card("ForrĂˇs"), "hasznalt": False} for _ in range(3)]
        spell = make_card("VarĂˇzslat", card_type="Ige")

        result = resolve_card_handler(
            trap,
            category="trap",
            varazslat=spell,
            jatekos=defender,
            ellenfel=attacker,
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(all(source["hasznalt"] for source in attacker.osforras))

    def test_tuzeso_hits_all_enemy_horizon_units(self):
        spell = make_card("Tuzeso", card_type="Ige")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(make_card("ElsĹ‘", atk=1, hp=2))
        enemy.horizont[1] = CsataEgyseg(make_card("MĂˇsodik", atk=1, hp=3))

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[0])
        self.assertEqual(enemy.horizont[1].akt_hp, 1)

    def test_langnyelvek_tanca_hits_two_different_enemy_units(self):
        spell = make_card("Langnyelvek Tanca", card_type="Ige")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(make_card("Elso", atk=1, hp=2))
        enemy.zenit[0] = CsataEgyseg(make_card("Masodik", atk=1, hp=3))

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[0])
        self.assertEqual(enemy.zenit[0].akt_hp, 1)

    def test_langnyelvek_tanca_returns_partial_with_one_enemy_unit(self):
        spell = make_card("Langnyelvek Tanca", card_type="Ige")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(make_card("Elso", atk=1, hp=3))

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertTrue(result["partial"])
        self.assertEqual(enemy.horizont[0].akt_hp, 1)

    def test_fenykard_csapas_kill_buffs_ally(self):
        spell = make_card("Fenykard Csapas", card_type="Ige")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        owner.horizont[0] = CsataEgyseg(make_card("Szovetseg", atk=2, hp=2))
        enemy.horizont[0] = CsataEgyseg(make_card("Celpont", atk=1, hp=2))

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[0])
        self.assertEqual(owner.horizont[0].bonus_max_hp, 1)
        self.assertEqual(owner.horizont[0].akt_hp, 3)

    def test_apaly_es_dagaly_zero_empty_horizon_draws_zero(self):
        spell = make_card("Apaly es Dagaly", card_type="Rituale")
        owner = make_player("Caster")
        for i in range(6):
            owner.horizont[i] = CsataEgyseg(make_card(f"E{i}", atk=1, hp=1))
        huzasok = {"db": 0}
        owner.huzas = lambda extra=False, trigger_watch=True: huzasok.__setitem__("db", huzasok["db"] + 1) or True

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(huzasok["db"], 0)

    def test_apaly_es_dagaly_draws_for_one_or_two_empty_slots(self):
        spell = make_card("Apaly es Dagaly", card_type="Rituale")
        owner = make_player("Caster")
        owner.horizont[0] = CsataEgyseg(make_card("E0", atk=1, hp=1))
        owner.horizont[1] = CsataEgyseg(make_card("E1", atk=1, hp=1))
        owner.horizont[2] = CsataEgyseg(make_card("E2", atk=1, hp=1))
        owner.horizont[3] = CsataEgyseg(make_card("E3", atk=1, hp=1))
        huzasok = {"db": 0}
        owner.huzas = lambda extra=False, trigger_watch=True: huzasok.__setitem__("db", huzasok["db"] + 1) or True

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(huzasok["db"], 2)

    def test_apaly_es_dagaly_caps_at_three_draws(self):
        spell = make_card("Apaly es Dagaly", card_type="Rituale")
        owner = make_player("Caster")
        owner.horizont[0] = CsataEgyseg(make_card("E0", atk=1, hp=1))
        owner.horizont[1] = CsataEgyseg(make_card("E1", atk=1, hp=1))
        huzasok = {"db": 0}
        owner.huzas = lambda extra=False, trigger_watch=True: huzasok.__setitem__("db", huzasok["db"] + 1) or True

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(huzasok["db"], 3)

    def test_koborlo_lelek_puts_top_deck_card_into_graveyard(self):
        unit = make_card("Koborlo Lelek", text="[DOMINIUM] Clarion ...", atk=1, hp=2)
        owner = make_player("Caster")
        owner.pakli = [make_card("Also"), make_card("Felso")]

        result = resolve_card_handler(unit, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(owner.temeto[-1].nev, "Felso")
        self.assertEqual(owner.pakli[-1].nev, "Also")

    def test_koborlo_lelek_clarion_path_uses_effect_engine_on_summon(self):
        unit = make_card("Koborlo Lelek", text="[DOMINIUM] Clarion ...", atk=1, hp=2)
        owner = make_player("Caster")
        owner.pakli = [make_card("Felso")]
        enemy = make_player("Enemy")
        owner.overflow_vereseg = False
        owner.overflow_gyoztes_nev = None
        enemy.overflow_vereseg = False
        enemy.overflow_gyoztes_nev = None
        game = object.__new__(AeternaSzimulacio)
        game.p1 = owner
        game.p2 = enemy
        install_effect_diagnostics()

        result = game._alkalmaz_kartya_hatast(unit, owner, enemy)

        self.assertIsNone(result)
        self.assertEqual(owner.temeto[-1].nev, "Felso")
        self.assertEqual(len(owner.pakli), 0)

    def test_koborlo_lelek_handles_empty_deck_safely(self):
        unit = make_card("Koborlo Lelek", text="[DOMINIUM] Clarion ...", atk=1, hp=2)
        owner = make_player("Caster")
        owner.pakli = []

        result = resolve_card_handler(unit, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertTrue(result["partial"])
        self.assertEqual(owner.temeto, [])

    def test_vadon_szeme_ijasz_damages_exhausted_enemy_on_clarion(self):
        unit = make_card("Vadon Szeme Ijasz", text="[DOMINIUM] Clarion: 2 damage to exhausted enemy", atk=2, hp=2)
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        exhausted = CsataEgyseg(make_card("Faradt", atk=2, hp=2))
        exhausted.kimerult = True
        active = CsataEgyseg(make_card("Aktiv", atk=2, hp=3))
        active.kimerult = False
        enemy.horizont[0] = exhausted
        enemy.horizont[1] = active

        result = resolve_card_handler(unit, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[0])
        self.assertIsNotNone(enemy.horizont[1])

    def test_vadon_szeme_ijasz_handles_missing_exhausted_target(self):
        unit = make_card("Vadon Szeme Ijasz", text="[DOMINIUM] Clarion: 2 damage to exhausted enemy", atk=2, hp=2)
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        active = CsataEgyseg(make_card("Aktiv", atk=2, hp=3))
        active.kimerult = False
        enemy.horizont[0] = active

        result = resolve_card_handler(unit, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertTrue(result["partial"])
        self.assertIs(enemy.horizont[0], active)

    def test_vakito_szikra_exhausts_active_enemy_horizon_unit(self):
        spell = make_card("Vakito Szikra", card_type="Ige")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        active = CsataEgyseg(make_card("Aktiv", atk=2, hp=2))
        active.kimerult = False
        exhausted = CsataEgyseg(make_card("Faradt", atk=1, hp=3))
        exhausted.kimerult = True
        enemy.horizont[0] = active
        enemy.horizont[1] = exhausted

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertTrue(enemy.horizont[0].kimerult)
        self.assertTrue(enemy.horizont[1].kimerult)

    def test_visszahivas_az_uressegbol_summons_active_unit(self):
        spell = make_card("VisszahĂ­vĂˇs az ĂśressĂ©gbĹ‘l", card_type="Ige")
        owner = make_player("Caster")
        owner.temeto.append(make_card("Elesett EntitĂˇs", atk=2, hp=2))

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertIsNotNone(owner.horizont[0])
        self.assertFalse(owner.horizont[0].kimerult)

    def test_univerzalis_csere_discards_two_and_draws_four(self):
        spell = make_card("UniverzĂˇlis Csere", card_type="Ige")
        owner = make_player("Caster")
        owner.kez = [make_card("A"), make_card("B"), make_card("C")]
        huzasok = {"db": 0}
        owner.huzas = lambda extra=False: huzasok.__setitem__("db", huzasok["db"] + 1) or True

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(len(owner.temeto), 2)
        self.assertEqual(huzasok["db"], 4)

    def test_lathatatlan_fal_returns_direct_attacker_to_hand(self):
        trap = make_card("LĂˇthatatlan Fal", card_type="Jel")
        attacker_owner = make_player("Attacker")
        defender = make_player("Defender")
        attacker = CsataEgyseg(make_card("TĂˇmadĂł", atk=3, hp=2))
        attacker.kimerult = False
        attacker_owner.horizont[0] = attacker

        result = resolve_card_handler(
            trap,
            category="trap",
            tamado_egyseg=attacker,
            tamado=attacker_owner,
            vedo=defender,
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["stop_attack"])
        self.assertIsNone(attacker_owner.horizont[0])
        self.assertEqual(attacker_owner.kez[0].nev, "TĂˇmadĂł")

    def test_onfelaldozo_esku_only_on_seal_attack_and_kills_highest_hp_ally(self):
        trap = make_card("Onfelaldozo Esku", card_type="Jel")
        attacker_owner = make_player("Attacker")
        defender = make_player("Defender")
        attacker = CsataEgyseg(make_card("Tamado", atk=4, hp=3))
        weak = CsataEgyseg(make_card("Gyenge", atk=1, hp=2))
        strong = CsataEgyseg(make_card("Vedelmezo", atk=2, hp=5))
        attacker_owner.horizont[0] = attacker
        defender.horizont[0] = weak
        defender.horizont[1] = strong

        self.assertFalse(can_activate_trap(trap, tamado_egyseg=attacker, tamado=attacker_owner, vedo=defender))
        self.assertTrue(
            can_activate_trap(
                trap,
                tamado_egyseg=attacker,
                tamado=attacker_owner,
                vedo=defender,
                target_kind="seal",
            )
        )

        result = resolve_card_handler(
            trap,
            category="trap",
            tamado_egyseg=attacker,
            tamado=attacker_owner,
            vedo=defender,
            target_kind="seal",
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["stop_attack"])
        self.assertIsNone(defender.horizont[1])
        self.assertEqual(defender.temeto[-1].nev, "Vedelmezo")

    def test_meglepetesszeru_ellenakcio_activates_on_attack_and_can_kill_attacker(self):
        trap = make_card("Meglepetesszeru Ellenakcio", card_type="Jel")
        attacker_owner = make_player("Attacker")
        defender = make_player("Defender")
        attacker = CsataEgyseg(make_card("Tamado", atk=3, hp=2))
        ally = CsataEgyseg(make_card("Vedelmezo", atk=2, hp=4))
        attacker_owner.horizont[0] = attacker
        defender.horizont[0] = ally

        self.assertTrue(can_activate_trap(trap, tamado_egyseg=attacker, tamado=attacker_owner, vedo=defender))

        result = resolve_card_handler(
            trap,
            category="trap",
            tamado_egyseg=attacker,
            tamado=attacker_owner,
            vedo=defender,
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["consume_trap"])
        self.assertTrue(result["stop_attack"])
        self.assertIsNone(attacker_owner.horizont[0])
        self.assertEqual(attacker_owner.temeto[-1].nev, "Tamado")
        self.assertEqual(ally.akt_hp, 1)

    def test_meglepetesszeru_ellenakcio_requires_own_unit(self):
        trap = make_card("Meglepetesszeru Ellenakcio", card_type="Jel")
        attacker_owner = make_player("Attacker")
        defender = make_player("Defender")
        attacker = CsataEgyseg(make_card("Tamado", atk=3, hp=4))
        attacker_owner.horizont[0] = attacker

        self.assertFalse(can_activate_trap(trap, tamado_egyseg=attacker, tamado=attacker_owner, vedo=defender))

    def test_gyar_felugyelo_summons_token(self):
        unit = make_card("GyĂˇr-FelĂĽgyelĹ‘")
        owner = make_player("Caster")

        result = resolve_card_handler(unit, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertIsNotNone(owner.horizont[0])
        self.assertEqual(owner.horizont[0].lap.nev, "Gepezet Token")

    def test_kod_alak_cancels_spell_when_targeted(self):
        owner = make_player("Caster")
        unit = CsataEgyseg(make_card("KĂ¶d-Alak", atk=1, hp=1))
        unit.owner = owner
        owner.horizont[0] = unit

        context = trigger_engine.dispatch(
            "on_spell_targeted",
            source="Teszt Ige",
            owner=make_player("Enemy"),
            target=unit,
            payload={"zone": "horizont", "index": 0, "target_owner": owner},
        )

        self.assertTrue(context.cancelled)
        self.assertIsNone(owner.horizont[0])
        self.assertEqual(owner.kez[0].nev, "KĂ¶d-Alak")


    def test_tulhevult_kazan_never_activates_as_generic_combat_trap(self):
        trap = make_card("TĂşlhevĂĽlt KazĂˇn", card_type="Jel")

        self.assertFalse(can_activate_trap(trap))

    def test_martirok_vedelme_does_not_activate_as_generic_combat_trap_but_returns_on_death(self):
        trap = make_card("Martirok Vedelme", card_type="Jel")
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        unit = CsataEgyseg(make_card("Vedett", atk=2, hp=3))
        owner.horizont[1] = unit
        owner.zenit[0] = trap

        self.assertFalse(can_activate_trap(trap, tamado_egyseg=unit, tamado=enemy, vedo=owner))

        destroyed = EffectEngine.destroy_unit(owner, "horizont", 1, enemy, "teszt")

        self.assertTrue(destroyed)
        self.assertIsNone(owner.horizont[1])
        self.assertIsNotNone(owner.zenit[1])
        self.assertEqual(owner.zenit[1].lap.nev, "Vedett")
        self.assertEqual(owner.zenit[1].akt_hp, 1)
        self.assertIn("aegis", getattr(owner.zenit[1], "granted_keywords", set()))
        self.assertEqual(owner.temeto[-1].nev, "Martirok Vedelme")

    def test_megtorlo_feny_does_not_activate_as_generic_combat_trap(self):
        trap = make_card("Megtorlo Feny", card_type="Jel")
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

    def test_megtorlo_feny_trap_consumes_on_damage_taken_and_reflects_half_damage(self):
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        trap = make_card("Megtorlo Feny", card_type="Jel")
        defender = CsataEgyseg(make_card("Vedett", atk=2, hp=5))
        attacker = CsataEgyseg(make_card("Tamado", atk=4, hp=4))
        defender.owner = owner
        attacker.owner = enemy
        owner.horizont[0] = defender
        owner.zenit[0] = trap
        enemy.horizont[0] = attacker

        trigger_engine.dispatch(
            "on_damage_taken",
            source=attacker,
            owner=enemy,
            target=defender,
            payload={
                "damage": 3,
                "zone": "horizont",
                "target_owner": owner,
                "source_zone": "horizont",
                "source_index": 0,
                "combat": True,
            },
        )

        self.assertIsNone(owner.zenit[0])
        self.assertEqual(owner.temeto[-1].nev, "Megtorlo Feny")
        self.assertEqual(attacker.akt_hp, 2)

    def test_vakito_fust_sets_enemy_horizon_attack_to_zero_until_turn_end(self):
        spell = make_card("Vakito Fust", card_type="Ige")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        target = CsataEgyseg(make_card("Celpont", atk=5, hp=4))
        enemy.horizont[0] = target

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertEqual(target.akt_tamadas, 0)
        self.assertEqual(getattr(target, "temp_atk_penalty_until_turn_end", 0), 5)

    def test_vakito_fust_burst_uses_same_attack_zero_handler(self):
        spell = make_card("Vakito Fust", card_type="Ige")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        target = CsataEgyseg(make_card("Burst Celpont", atk=3, hp=4))
        enemy.horizont[1] = target

        result = resolve_card_handler(spell, category="burst", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertEqual(target.akt_tamadas, 0)

    def test_surgeto_hullam_reactivates_exhausted_ally_but_prevents_attack(self):
        spell = make_card("Surgeto Hullam", card_type="Ige")
        owner = make_player("Caster")
        exhausted = CsataEgyseg(make_card("Faradt Szovetseg", atk=3, hp=4))
        exhausted.kimerult = True
        owner.horizont[0] = exhausted

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertFalse(exhausted.kimerult)
        self.assertTrue(exhausted.cannot_attack_until_turn_end)

    def test_surgeto_hullam_burst_uses_same_reactivation_handler(self):
        spell = make_card("Surgeto Hullam", card_type="Ige")
        owner = make_player("Caster")
        exhausted = CsataEgyseg(make_card("Burst Faradt", atk=2, hp=5))
        exhausted.kimerult = True
        owner.horizont[1] = exhausted

        result = resolve_card_handler(spell, category="burst", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertFalse(exhausted.kimerult)
        self.assertTrue(exhausted.cannot_attack_until_turn_end)

    def test_fustbomba_moves_own_target_back_to_matching_zenit_and_stops_attack(self):
        spell = make_card("Fustbomba", card_type="Ige")
        owner = make_player("Caster")
        target = CsataEgyseg(make_card("Mentett", atk=3, hp=4))
        owner.horizont[1] = target

        result = resolve_card_handler(
            spell,
            category="burst",
            jatekos=owner,
            current_target=("horizont", 1, target),
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["stop_attack"])
        self.assertIsNone(owner.horizont[1])
        self.assertIs(owner.zenit[1], target)

    def test_fustbomba_returns_partial_when_no_empty_zenit_behind_target(self):
        spell = make_card("Fustbomba", card_type="Ige")
        owner = make_player("Caster")
        target = CsataEgyseg(make_card("Mentett", atk=3, hp=4))
        blocker = CsataEgyseg(make_card("Hatso", atk=1, hp=2))
        owner.horizont[0] = target
        owner.zenit[0] = blocker

        result = resolve_card_handler(
            spell,
            category="burst",
            jatekos=owner,
            current_target=("horizont", 0, target),
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["partial"])
        self.assertIs(owner.horizont[0], target)
        self.assertIs(owner.zenit[0], blocker)

    def test_magma_elemental_deals_one_damage_on_summon(self):
        unit = make_card("Magma-Elemental")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        target = CsataEgyseg(make_card("Celpont", atk=2, hp=4))
        enemy.horizont[0] = target

        result = resolve_card_handler(unit, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertEqual(target.akt_hp, 3)

    def test_magma_elemental_returns_partial_without_enemy_horizon_target(self):
        unit = make_card("Magma-Elemental")
        owner = make_player("Caster")
        enemy = make_player("Enemy")

        result = resolve_card_handler(unit, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertTrue(result["partial"])

    def test_kodbe_vesz_grants_temporary_ethereal_to_own_horizon_unit(self):
        spell = make_card("Ködbe Vész", card_type="Ige")
        owner = make_player("Caster")
        front = CsataEgyseg(make_card("Vedett", atk=2, hp=3))
        owner.horizont[0] = front

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertFalse(result["partial"])
        self.assertIn("ethereal", getattr(front, "temp_granted_keywords", set()))

    def test_kodbe_vesz_returns_partial_without_own_horizon_unit(self):
        spell = make_card("Ködbe Vész", card_type="Ige")
        owner = make_player("Caster")

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertTrue(result["partial"])

    def test_vakito_seregek_buffs_allied_aegis_units_on_horizon(self):
        spell = make_card("Vakito Seregek", card_type="Ige")
        owner = make_player("Caster")
        aegis_unit = CsataEgyseg(make_card("Oltalmazott", atk=2, hp=3))
        normal_unit = CsataEgyseg(make_card("Sima", atk=3, hp=3))
        aegis_unit.granted_keywords = {"aegis"}
        owner.horizont[0] = aegis_unit
        owner.horizont[1] = normal_unit

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertFalse(result["partial"])
        self.assertEqual(aegis_unit.akt_tamadas, 4)
        self.assertEqual(aegis_unit.temp_atk_bonus_until_turn_end, 2)
        self.assertEqual(normal_unit.akt_tamadas, 3)

    def test_vakito_seregek_returns_partial_without_aegis_unit(self):
        spell = make_card("Vakito Seregek", card_type="Ige")
        owner = make_player("Caster")
        owner.horizont[0] = CsataEgyseg(make_card("Sima", atk=3, hp=3))

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertTrue(result["partial"])

    def test_buborek_pajzs_grants_spell_damage_immunity_until_turn_end(self):
        spell = make_card("Buborek-pajzs", card_type="Ige")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        protected = CsataEgyseg(make_card("Vedett", atk=2, hp=4))
        owner.horizont[0] = protected

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertFalse(result["partial"])
        self.assertTrue(protected.spell_damage_immunity_until_turn_end)

    def test_buborek_pajzs_blocks_spell_damage(self):
        spell = make_card("Buborek-pajzs", card_type="Ige")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        protected = CsataEgyseg(make_card("Vedett", atk=2, hp=4))
        owner.horizont[0] = protected

        resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=enemy)
        destroyed = EffectEngine._deal_damage_to_target("Villam", 3, ("horizont", 0, protected), owner, "Kepesseg", enemy)

        self.assertFalse(destroyed)
        self.assertEqual(protected.akt_hp, 4)

    def test_tulhevult_kazan_triggers_on_own_machine_death(self):
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        owner.zenit[0] = make_card("TĂşlhevĂĽlt KazĂˇn", card_type="Jel")
        enemy.horizont[0] = CsataEgyseg(make_card("Ellenseg 1", atk=1, hp=2))
        enemy.horizont[1] = CsataEgyseg(make_card("Ellenseg 2", atk=1, hp=3))
        source_card = make_card("Elesett Gepezet", atk=1, hp=1)
        source_card.faj = "Gepezet"

        trigger_engine.dispatch(
            "on_destroyed",
            source=source_card,
            owner=owner,
            target=enemy,
            payload={"zone": "horizont"},
        )

        self.assertIsNone(owner.zenit[0])
        self.assertIsNone(enemy.horizont[0])
        self.assertEqual(enemy.horizont[1].akt_hp, 1)

    def test_goblin_taktika_summons_two_tokens(self):
        spell = make_card("Goblin Taktika", card_type="RituĂˇlĂ©")
        owner = make_player("Caster", realm="Ignis")

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(sum(1 for x in owner.horizont if x is not None), 2)

    def test_a_feny_utja_can_resolve_from_burst(self):
        burst = make_card("A FĂ©ny Ăštja", card_type="Jel")
        owner = make_player("Caster")
        owner.horizont[0] = CsataEgyseg(make_card("Vedett", atk=2, hp=2))

        result = resolve_card_handler(burst, category="burst", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertTrue(owner.horizont[0].survival_shield_until_turn_end)

    def test_tukrozodo_remeny_buffs_other_unit_after_damage(self):
        owner = make_player("Owner")
        owner.tukrozodo_remeny_aktiv = True
        damaged = CsataEgyseg(make_card("Elso", atk=1, hp=3))
        target = CsataEgyseg(make_card("Masik", atk=2, hp=2))
        owner.horizont[0] = damaged
        owner.horizont[1] = target

        trigger_engine.dispatch(
            "on_damage_taken",
            source=CsataEgyseg(make_card("Tamado", atk=3, hp=3)),
            owner=make_player("Enemy"),
            target=damaged,
            payload={"damage": 2, "zone": "horizont", "target_owner": owner, "source_zone": "horizont", "source_index": 0, "combat": True},
        )

        self.assertEqual(target.bonus_max_hp, 2)
        self.assertEqual(target.akt_hp, 4)

    def test_vamszedo_pont_copies_extra_draw(self):
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        owner_huzas = {"db": 0}
        enemy_huzas = {"db": 0}

        def owner_draw(extra=False, trigger_watch=True):
            owner_huzas["db"] += 1
            return True

        def enemy_draw(extra=False, trigger_watch=True):
            enemy_huzas["db"] += 1
            if extra and trigger_watch and enemy.vamszedo_pont_figyelo is not None:
                enemy.vamszedo_pont_figyelo.huzas(extra=True, trigger_watch=False)
            return True

        owner.huzas = owner_draw
        enemy.huzas = enemy_draw

        resolve_card_handler(make_card("VĂˇmszedĹ‘ Pont", card_type="SĂ­k"), category="on_play", jatekos=owner, ellenfel=enemy)
        enemy.huzas(extra=True)

        self.assertEqual(enemy_huzas["db"], 1)
        self.assertEqual(owner_huzas["db"], 1)

    def test_szegecsvihar_hits_two_different_targets(self):
        spell = make_card("Szegecsvihar", card_type="Ige")
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(make_card("A", atk=1, hp=2))
        enemy.horizont[1] = CsataEgyseg(make_card("B", atk=1, hp=3))

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=enemy)

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[0])
        self.assertEqual(enemy.horizont[1].akt_hp, 1)

    def test_a_termeszet_szava_searches_bestia(self):
        spell = make_card("A TermĂ©szet Szava", card_type="RituĂˇlĂ©")
        owner = make_player("Caster")
        bestia = make_card("Farkas", card_type="EntitĂˇs")
        bestia.faj = "Bestia"
        owner.pakli = [bestia]

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(owner.kez[-1].nev, "Farkas")

    def test_ujjaszuletes_fenye_revives_to_same_slot_exhausted(self):
        spell = make_card("ĂšjjĂˇszĂĽletĂ©s FĂ©nye", card_type="RituĂˇlĂ©")
        owner = make_player("Caster")
        owner.horizont[1] = CsataEgyseg(make_card("Aldozat", atk=1, hp=1))
        revived = make_card("Visszatero", atk=4, hp=4)
        owner.temeto = [revived]

        result = resolve_card_handler(spell, category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(owner.horizont[1].lap.nev, "Visszatero")
        self.assertTrue(owner.horizont[1].kimerult)

    def test_benito_fagy_stops_attack_and_keeps_attacker_exhausted_next_turn(self):
        trap = make_card("Bénító Fagy", card_type="Jel")
        attacker_owner = make_player("Attacker")
        attacker = CsataEgyseg(make_card("Tamado", atk=3, hp=3))
        attacker_owner.horizont[0] = attacker

        result = resolve_card_handler(trap, category="trap", tamado_egyseg=attacker, tamado=attacker_owner, vedo=make_player("Defender"))

        self.assertTrue(result["resolved"])
        self.assertTrue(result["stop_attack"])
        self.assertEqual(attacker.extra_exhausted_turns, 1)

    def test_csuszos_talaj_slides_attacker_sideways(self):
        trap = make_card("Csúszós Talaj", card_type="Jel")
        attacker_owner = make_player("Attacker")
        attacker = CsataEgyseg(make_card("Tamado", atk=3, hp=3))
        attacker_owner.horizont[2] = attacker

        result = resolve_card_handler(trap, category="trap", tamado_egyseg=attacker, tamado=attacker_owner, vedo=make_player("Defender"))

        self.assertTrue(result["resolved"])
        self.assertTrue(result["stop_attack"])
        self.assertIsNone(attacker_owner.horizont[2])
        self.assertIsNotNone(attacker_owner.horizont[1] or attacker_owner.horizont[3])
        self.assertTrue(attacker.cannot_attack_until_turn_end)

    def test_zart_sorkepzes_cancels_targeted_spell_and_buffs_target(self):
        owner = make_player("Owner")
        target = CsataEgyseg(make_card("Vedett", atk=2, hp=2))
        owner.horizont[0] = target
        owner.zenit[0] = make_card("Zárt Sorképzés", card_type="Jel")

        result = resolve_spell_redirect(
            spell_card=make_card("Villam", card_type="Ige"),
            caster=make_player("Enemy"),
            target_owner=owner,
            current_target=("horizont", 0, target),
        )

        self.assertTrue(result["resolved"])
        self.assertTrue(result["cancelled_spell"])
        self.assertEqual(target.bonus_max_hp, 2)

    def test_a_valtozo_sziget_swaps_enemy_same_lane_on_awakening(self):
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        resolve_card_handler(make_card("A Változó Sziget", card_type="Sík"), category="on_play", jatekos=owner, ellenfel=enemy)
        owner.horizont[1] = CsataEgyseg(make_card("Sajat", atk=1, hp=2))
        enemy.horizont[1] = CsataEgyseg(make_card("Elol", atk=4, hp=4))
        enemy.zenit[1] = CsataEgyseg(make_card("Hatul", atk=1, hp=1))

        trigger_engine.dispatch("on_awakening_phase", owner=owner, target=enemy, payload={})

        self.assertEqual(enemy.horizont[1].lap.nev, "Hatul")
        self.assertEqual(enemy.zenit[1].lap.nev, "Elol")

    def test_melytengeri_nyomas_halves_attack_until_turn_end(self):
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(make_card("Celpont", atk=5, hp=4))

        result = resolve_card_handler(make_card("Mélytengeri Nyomás", card_type="Ige"), category="on_play", jatekos=owner, ellenfel=enemy)
        self.assertTrue(result["resolved"])
        self.assertEqual(enemy.horizont[0].akt_tamadas, 2)

        trigger_engine.dispatch("on_turn_end", owner=enemy, target=owner, payload={})
        self.assertEqual(enemy.horizont[0].akt_tamadas, 5)

    def test_lelekmentes_resolves_from_burst(self):
        owner = make_player("Owner")
        owner.temeto.append(make_card("Elesett", atk=2, hp=2))

        result = resolve_card_handler(make_card("Lélekmentés", card_type="Jel"), category="burst", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(owner.kez[-1].nev, "Elesett")

    def test_aeterna_aldasa_rebuilds_broken_seal_from_deck_top(self):
        owner = make_player("Owner")
        owner.pecsetek = [make_card("Megmaradt Pecset", card_type="Pecsét")]
        owner.pakli = [make_card("Uj Pecset", card_type="Ige")]

        result = resolve_card_handler(make_card("Aeterna Áldása", card_type="Ige"), category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertEqual(len(owner.pecsetek), 2)
        self.assertEqual(owner.pecsetek[-1].nev, "Uj Pecset")

    def test_sirba_teres_returns_unit_to_same_slot_active(self):
        owner = make_player("Owner")
        owner.horizont[2] = CsataEgyseg(make_card("Alany", atk=3, hp=4))

        result = resolve_card_handler(make_card("Sírba Térés", card_type="Ige"), category="on_play", jatekos=owner, ellenfel=None)

        self.assertTrue(result["resolved"])
        self.assertIsNotNone(owner.horizont[2])
        self.assertEqual(owner.horizont[2].lap.nev, "Alany")
        self.assertFalse(owner.horizont[2].kimerult)
        self.assertEqual(owner.horizont[2].akt_hp, 4)

if __name__ == "__main__":
    unittest.main()

