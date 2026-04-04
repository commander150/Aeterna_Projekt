import unittest
from types import SimpleNamespace

from cards.resolver import can_activate_trap, resolve_card_handler, resolve_spell_redirect
from engine.card import CsataEgyseg
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
        self.assertFalse(
            can_activate_trap(
                trap,
                tamado_egyseg=CsataEgyseg(make_card("Tamado")),
                tamado=make_player("Attacker"),
                vedo=make_player("Defender"),
            )
        )

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

