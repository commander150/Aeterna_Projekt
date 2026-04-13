import unittest

from unittest.mock import patch

from engine.actions import ActionLibrary
from engine.card import Kartya, CsataEgyseg
from engine.card_metadata import has_effect_tag, has_keyword, has_trigger, parse_semicolon_list
from engine.structured_effects import resolve_structured_effect


def make_player(name="P1"):
    class _Player:
        def __init__(self):
            self.nev = name
            self.birodalom = "Aether"
            self.pakli = []
            self.kez = []
            self.osforras = []
            self.temeto = []
            self.horizont = [None] * 6
            self.zenit = [None] * 6
            self.pecsetek = []
            self.rezonancia_aura = 0
            self.extra_huzas_ebben_a_korben = 0
            self.ideiglenes_aura_ebben_a_korben = 0
            self.ujraaktivalt_egysegek_ebben_a_korben = 0
            self.kell_tamadnia_kovetkezo_korben = False
            self.overflow_vereseg = False
            self.overflow_gyoztes_nev = None

        def huzas(self, extra=False, trigger_watch=True):
            if not self.pakli:
                return False
            self.kez.append(self.pakli.pop())
            return True

        def ujraaktivalt_egyseget(self, egyseg, forras=""):
            if egyseg is None or not egyseg.kimerult:
                return False
            egyseg.kimerult = False
            return True

        def jelol_overflow_vereseget(self, gyoztes_nev):
            self.overflow_vereseg = True
            self.overflow_gyoztes_nev = gyoztes_nev

    return _Player()


class TestStructuredEffects(unittest.TestCase):
    def test_parse_semicolon_list(self):
        self.assertEqual(parse_semicolon_list("Sebzes; LapHuzas ;"), ["Sebzes", "LapHuzas"])

    def test_card_loads_structured_fields(self):
        card = Kartya(
            {
                "kartya_nev": "Teszt Lap",
                "tipus": "Ige",
                "birodalom": "Aether",
                "kepesseg": "Flavor text",
                "kepesseg_canonical": "Okozz 2 sebzest.",
                "kulcsszavak_felismerve": "Burst; Echo",
                "trigger_felismerve": "on_play; on_destroyed",
                "celpont_felismerve": "Horizont; Pecset",
                "hatascimkek": "Sebzes; PecsetSebzes",
                "ertelmezesi_statusz": "structured",
            }
        )

        self.assertEqual(card.canonical_text, "Okozz 2 sebzest.")
        self.assertTrue(has_keyword(card, "burst"))
        self.assertTrue(has_trigger(card, "on_play"))
        self.assertTrue(has_effect_tag(card, "sebzes"))

    def test_card_loads_new_sheet_layout_without_canonical_column(self):
        card = Kartya(
            {
                "kartya_nev": "Teszt Entitas",
                "tipus": "Entitas",
                "birodalom": "Lux",
                "magnitudo": 3,
                "aura": 2,
                "atk": 4,
                "hp": 5,
                "kepesseg": "[HORIZONT] Oltalom",
                "kulcsszavak_felismerve": "Oltalom",
                "trigger_felismerve": "",
                "celpont_felismerve": "",
                "hatascimkek": "",
                "ertelmezesi_statusz": "passziv_kulcsszo",
            }
        )

        self.assertEqual(card.kartyatipus, "Entitas")
        self.assertTrue(card.egyseg_e)
        self.assertEqual(card.aura_koltseg, 2)
        self.assertEqual(card.tamadas, 4)
        self.assertEqual(card.eletero, 5)


    def test_trigger_aliases_are_normalized_from_sheet_values(self):
        card = Kartya(
            {
                "kartya_nev": "Alias Teszt",
                "kartyatipus": "Entitas",
                "trigger_felismerve": "on_spell_targeted; on_destroyed",
            }
        )

        self.assertTrue(has_trigger(card, "on_enemy_spell_target"))
        self.assertTrue(has_trigger(card, "on_destroyed"))

    def test_structured_damage_hits_enemy_unit(self):
        card = Kartya(
            {
                "kartya_nev": "Structured Sebzes",
                "kartyatipus": "Ige",
                "kepesseg": "-",
                "kepesseg_canonical": "Okozz 2 sebzest egy ellenseges Horizont Entitasnak.",
                "hatascimkek": "Sebzes",
                "celpont_felismerve": "Horizont",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(Kartya({"kartya_nev": "Celpont", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[0])

    def test_structured_seal_damage_breaks_seal(self):
        card = Kartya(
            {
                "kartya_nev": "Structured Pecset",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Okozz 1 kozvetlen sebzest az ellenfel Pecsetjenek.",
                "hatascimkek": "Sebzes; PecsetSebzes",
                "celpont_felismerve": "Pecset",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.pecsetek = [Kartya({"kartya_nev": "Pecset", "kartyatipus": "Pecset", "magnitudo": 1})]

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertEqual(len(enemy.pecsetek), 0)

    def test_structured_damage_does_not_convert_to_seal_break(self):
        card = Kartya(
            {
                "kartya_nev": "Hibas Direktsugar",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Okozz 3 sebzest az ellenfel Pecsetjenek.",
                "hatascimkek": "Sebzes",
                "celpont_felismerve": "Pecset",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.pecsetek = [
            Kartya({"kartya_nev": "Pecset 1", "kartyatipus": "Pecset", "magnitudo": 1}),
            Kartya({"kartya_nev": "Pecset 2", "kartyatipus": "Pecset", "magnitudo": 1}),
            Kartya({"kartya_nev": "Pecset 3", "kartyatipus": "Pecset", "magnitudo": 1}),
        ]

        tech_logs = []
        with patch("utils.logger.naplo.tech", side_effect=lambda category, message: tech_logs.append((category, message))):
            result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertFalse(result["resolved"])
        self.assertEqual(len(enemy.pecsetek), 3)
        self.assertTrue(any(category == "SEAL_RULE_BLOCKED" for category, _ in tech_logs))
        self.assertTrue(any(category == "REVIEW_NEEDED" for category, _ in tech_logs))

    def test_structured_explicit_seal_break_is_blocked_by_front_lane_unit(self):
        card = Kartya(
            {
                "kartya_nev": "Celzott Pecséttoro",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Törj fel 1 Pecsetet a celzott Aramlatban.",
                "hatascimkek": "Sebzes; PecsetSebzes",
                "celpont_felismerve": "Pecset",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.pecsetek = [Kartya({"kartya_nev": "Pecset", "kartyatipus": "Pecset", "magnitudo": 1})]
        enemy.horizont[0] = CsataEgyseg(
            Kartya({"kartya_nev": "Front Vedő", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2})
        )

        tech_logs = []
        with patch("utils.logger.naplo.tech", side_effect=lambda category, message: tech_logs.append((category, message))):
            result = resolve_structured_effect(card, owner, enemy, {"category": "on_play", "lane_index": 0})

        self.assertFalse(result["resolved"])
        self.assertEqual(len(enemy.pecsetek), 1)
        self.assertTrue(any(category == "LANE_SEAL_BLOCKED" for category, _ in tech_logs))
        self.assertTrue(any(category == "REVIEW_NEEDED" for category, _ in tech_logs))

    def test_structured_move_to_zenit_does_not_bounce_back_to_horizon_same_resolution(self):
        card = Kartya(
            {
                "kartya_nev": "Viz alatti Borton",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Mozgasd az ellenseges Horizont Entitast a Zenitbe.",
                "hatascimkek": "Kimerites; Mozgatas_Horizontra; Mozgatas_Zenitbe",
                "celpont_felismerve": "enemy_entity; Horizont; Zenit",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        target = CsataEgyseg(Kartya({"kartya_nev": "Celpont", "kartyatipus": "Entitas", "tamadas": 2, "eletero": 3}))
        enemy.horizont[0] = target
        enemy.zenit[0] = None

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[0])
        self.assertIs(enemy.zenit[0], target)
        self.assertTrue(enemy.zenit[0].kimerult)

    def test_structured_damage_prefers_zone_from_recognized_zone_metadata(self):
        card = Kartya(
            {
                "kartya_nev": "Zenit Csapas",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Okozz 2 sebzest egy ellenseges Zenit Entitasnak.",
                "hatascimkek": "Sebzes",
                "zona_felismerve": "zenit",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(Kartya({"kartya_nev": "Front", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 5}))
        enemy.zenit[0] = CsataEgyseg(Kartya({"kartya_nev": "Back", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertIsNotNone(enemy.horizont[0])
        self.assertIsNone(enemy.zenit[0])

    def test_structured_grant_keyword_uses_canonical_tag_and_target_selector(self):
        card = Kartya(
            {
                "kartya_nev": "Provokalo Kialtas",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Adj Taunt kulcsszot egy masik sajat Entitasnak a kor vegeig.",
                "hatascimkek": "grant_keyword",
                "celpont_felismerve": "other_own_entity",
                "idotartam_felismerve": "until_turn_end",
            }
        )
        owner = make_player("Caster")
        source = CsataEgyseg(Kartya({"kartya_nev": "Forras", "kartyatipus": "Entitas", "tamadas": 2, "eletero": 3}))
        other = CsataEgyseg(Kartya({"kartya_nev": "Cel", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 4}))
        source.owner = owner
        other.owner = owner
        owner.horizont[0] = source
        owner.horizont[1] = other

        result = resolve_structured_effect(card, owner, None, {"category": "on_play", "source_unit": source})

        self.assertTrue(result["resolved"])
        self.assertIn("taunt", getattr(other, "temp_granted_keywords", set()))
        self.assertNotIn("taunt", getattr(source, "temp_granted_keywords", set()))

    def test_structured_ready_uses_canonical_tag(self):
        card = Kartya(
            {
                "kartya_nev": "Ujra Ebredes",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Kesits fel egy sajat Entitast.",
                "hatascimkek": "ready",
                "celpont_felismerve": "own_entity",
            }
        )
        owner = make_player("Caster")
        target = CsataEgyseg(Kartya({"kartya_nev": "Faradt", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))
        target.owner = owner
        target.kimerult = True
        owner.horizont[0] = target

        result = resolve_structured_effect(card, owner, None, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertFalse(target.kimerult)

    def test_structured_return_to_hand_can_target_own_entity(self):
        card = Kartya(
            {
                "kartya_nev": "Mentolanc",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Vedd vissza egy sajat Horizont Entitasodat a kezedbe.",
                "hatascimkek": "return_to_hand",
                "celpont_felismerve": "own_horizont_entity",
            }
        )
        owner = make_player("Caster")
        target = CsataEgyseg(Kartya({"kartya_nev": "Szovetseg", "kartyatipus": "Entitas", "tamadas": 2, "eletero": 2}))
        target.owner = owner
        owner.horizont[0] = target

        result = resolve_structured_effect(card, owner, make_player("Enemy"), {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertIsNone(owner.horizont[0])
        self.assertEqual(owner.kez[-1].nev, "Szovetseg")

    def test_structured_move_to_horizont_uses_enemy_zenit_selector(self):
        card = Kartya(
            {
                "kartya_nev": "Lehivas",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Mozgasd az ellenseges Zenit Entitast a Horizontra.",
                "hatascimkek": "move_horizont",
                "celpont_felismerve": "enemy_zenit_entity",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        target = CsataEgyseg(Kartya({"kartya_nev": "Hatso Vedo", "kartyatipus": "Entitas", "tamadas": 2, "eletero": 3}))
        target.owner = enemy
        enemy.zenit[0] = target

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertIs(enemy.horizont[0], target)
        self.assertIsNone(enemy.zenit[0])
        self.assertTrue(target.kimerult)

    def test_structured_damage_uses_opposing_entity_selector(self):
        card = Kartya(
            {
                "kartya_nev": "Soron Tulel",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Okozz 2 sebzest a szemben allo Entitasnak.",
                "hatascimkek": "damage",
                "celpont_felismerve": "opposing_entity",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        source = CsataEgyseg(Kartya({"kartya_nev": "Tamado", "kartyatipus": "Entitas", "tamadas": 2, "eletero": 2}))
        target = CsataEgyseg(Kartya({"kartya_nev": "Vedett", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))
        source.owner = owner
        target.owner = enemy
        owner.horizont[1] = source
        enemy.horizont[1] = target

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play", "source_unit": source, "lane_index": 1})

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[1])

    def test_canonical_plural_target_selectors_return_expected_units(self):
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        own_front = CsataEgyseg(Kartya({"kartya_nev": "OwnFront", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))
        own_back = CsataEgyseg(Kartya({"kartya_nev": "OwnBack", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))
        enemy_front = CsataEgyseg(Kartya({"kartya_nev": "EnemyFront", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))
        enemy_back = CsataEgyseg(Kartya({"kartya_nev": "EnemyBack", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))
        owner.horizont[0] = own_front
        owner.zenit[0] = own_back
        enemy.horizont[0] = enemy_front
        enemy.zenit[0] = enemy_back

        self.assertEqual(len(ActionLibrary.targets_for_key(owner, enemy, "own_entities")), 2)
        self.assertEqual(len(ActionLibrary.targets_for_key(owner, enemy, "enemy_entities")), 2)
        self.assertEqual(len(ActionLibrary.targets_for_key(owner, enemy, "own_horizont_entities")), 1)
        self.assertEqual(len(ActionLibrary.targets_for_key(owner, enemy, "enemy_horizont_entities")), 1)
        self.assertIs(ActionLibrary.targets_for_key(owner, enemy, "own_zenit_entity")[0][2], own_back)
        self.assertIs(ActionLibrary.targets_for_key(owner, enemy, "own_zenit_entities")[0][2], own_back)

    def test_structured_attack_restrict_uses_enemy_entities_selector(self):
        card = Kartya(
            {
                "kartya_nev": "Tamadastilto Hullam",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Az osszes ellenseges Entitas nem tamadhat ebben a korben.",
                "hatascimkek": "attack_restrict",
                "celpont_felismerve": "enemy_entities",
            }
        )
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(Kartya({"kartya_nev": "A", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))
        enemy.zenit[0] = CsataEgyseg(Kartya({"kartya_nev": "B", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertTrue(enemy.horizont[0].cannot_attack_until_turn_end)
        self.assertTrue(enemy.zenit[0].cannot_attack_until_turn_end)

    def test_structured_block_restrict_uses_own_zenit_entity_selector(self):
        card = Kartya(
            {
                "kartya_nev": "Hatso Zar",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Egy sajat Zenit Entitas nem blokkolhat ebben a korben.",
                "hatascimkek": "block_restrict",
                "celpont_felismerve": "own_zenit_entity",
            }
        )
        owner = make_player("Owner")
        owner.zenit[0] = CsataEgyseg(Kartya({"kartya_nev": "Vedett", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))

        result = resolve_structured_effect(card, owner, None, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertTrue(owner.zenit[0].cannot_block_until_turn_end)

    def test_structured_graveyard_recursion_summons_entity_from_graveyard(self):
        card = Kartya(
            {
                "kartya_nev": "Siri Visszahivas",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Hozz vissza egy Entitast az Uressegbol a Horizontra.",
                "hatascimkek": "graveyard_recursion",
            }
        )
        owner = make_player("Owner")
        fallen = Kartya({"kartya_nev": "Elesett", "kartyatipus": "Entitas", "tamadas": 2, "eletero": 3})
        owner.temeto.append(fallen)

        result = resolve_structured_effect(card, owner, None, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertIsNotNone(owner.horizont[0])
        self.assertEqual(owner.horizont[0].lap.nev, "Elesett")

    def test_structured_summon_uses_shared_context_card(self):
        card = Kartya(
            {
                "kartya_nev": "Azonnali Idezes",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Idezz meg egy Entitast a Horizontra.",
                "hatascimkek": "summon",
            }
        )
        owner = make_player("Owner")
        summon_card = Kartya({"kartya_nev": "Erkezo", "kartyatipus": "Entitas", "tamadas": 3, "eletero": 2})

        result = resolve_structured_effect(card, owner, None, {"category": "on_play", "summon_card": summon_card, "lane_index": 2, "summon_exhausted": False})

        self.assertTrue(result["resolved"])
        self.assertIsNotNone(owner.horizont[2])
        self.assertEqual(owner.horizont[2].lap.nev, "Erkezo")
        self.assertFalse(owner.horizont[2].kimerult)

    def test_structured_summon_token_uses_shared_helper(self):
        card = Kartya(
            {
                "kartya_nev": "Token Hivas",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Idezz meg 2 tokent a Horizontra.",
                "hatascimkek": "summon_token",
            }
        )
        owner = make_player("Owner")

        result = resolve_structured_effect(
            card,
            owner,
            None,
            {"category": "on_play", "token_name": "Goblin Token", "token_atk": 1, "token_hp": 1, "token_race": "Goblin"},
        )

        self.assertTrue(result["resolved"])
        self.assertEqual(sum(1 for unit in owner.horizont if unit is not None), 2)

    def test_structured_counterspell_marks_context_cancelled(self):
        card = Kartya(
            {
                "kartya_nev": "Semlegesito Jel",
                "kartyatipus": "Jel",
                "kepesseg_canonical": "Semlegesits egy Iget.",
                "hatascimkek": "counterspell",
            }
        )
        owner = make_player("Owner")
        ctx = {"category": "trap", "spell_card": Kartya({"kartya_nev": "Villam", "kartyatipus": "Ige"})}

        result = resolve_structured_effect(card, owner, make_player("Enemy"), ctx)

        self.assertTrue(result["resolved"])
        self.assertTrue(ctx["cancelled_spell"])

    def test_collection_target_selectors_cover_batch_three_targets(self):
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        owner.kez = [Kartya({"kartya_nev": "OwnHandCard", "kartyatipus": "Ige"})]
        owner.pakli = [Kartya({"kartya_nev": "OwnDeckCard", "kartyatipus": "Ige"})]
        owner.temeto = [Kartya({"kartya_nev": "OwnDeadUnit", "kartyatipus": "Entitas"})]
        enemy.kez = [Kartya({"kartya_nev": "EnemyHandCard", "kartyatipus": "Ige"})]
        enemy_spell = Kartya({"kartya_nev": "EnemySpell", "kartyatipus": "Ige"})

        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "own_hand")[0][2].nev, "OwnHandCard")
        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "own_deck")[0][2].nev, "OwnDeckCard")
        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "own_graveyard_entity")[0][2].nev, "OwnDeadUnit")
        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "enemy_hand")[0][2].nev, "EnemyHandCard")
        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "enemy_spell", source=enemy_spell)[0][2].nev, "EnemySpell")
        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "enemy_spell_or_ritual", source=enemy_spell)[0][2].nev, "EnemySpell")

    def test_collection_target_selectors_cover_batch_four_targets(self):
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        owner.temeto = [
            Kartya({"kartya_nev": "OwnDeadSpell", "kartyatipus": "Ige"}),
            Kartya({"kartya_nev": "OwnDeadUnit", "kartyatipus": "Entitas"}),
        ]
        owner.osforras = [{"lap": Kartya({"kartya_nev": "OwnSourceCard", "kartyatipus": "Ige"}), "hasznalt": False}]
        enemy.osforras = [{"lap": Kartya({"kartya_nev": "EnemySourceCard", "kartyatipus": "Ige"}), "hasznalt": False}]
        enemy.kez = [Kartya({"kartya_nev": "EnemyHandSingle", "kartyatipus": "Ige"})]

        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "own_graveyard")[0][2].nev, "OwnDeadSpell")
        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "own_source_card")[0][2].nev, "OwnSourceCard")
        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "enemy_source_card")[0][2].nev, "EnemySourceCard")
        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "enemy_hand_card")[0][2].nev, "EnemyHandSingle")
        self.assertEqual(ActionLibrary.targets_for_key(owner, enemy, "lane", lane_index=3)[0][2], 3)

    def test_structured_return_to_deck_moves_own_hand_card_to_top(self):
        card = Kartya(
            {
                "kartya_nev": "Visszakeveres",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Tedd vissza egy sajat kezben levo lapodat a pakli tetejere.",
                "hatascimkek": "return_to_deck",
                "celpont_felismerve": "own_hand",
            }
        )
        owner = make_player("Owner")
        owner.kez = [Kartya({"kartya_nev": "Kezben", "kartyatipus": "Ige"})]

        result = resolve_structured_effect(card, owner, None, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertEqual(len(owner.kez), 0)
        self.assertEqual(owner.pakli[-1].nev, "Kezben")

    def test_structured_deck_bottom_moves_enemy_hand_card_to_bottom(self):
        card = Kartya(
            {
                "kartya_nev": "Aljara Kuldes",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Tedd az ellenfel kezebol egy lapot a pakli aljara.",
                "hatascimkek": "deck_bottom",
                "celpont_felismerve": "enemy_hand",
            }
        )
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        enemy.kez = [Kartya({"kartya_nev": "Ellenseges Lap", "kartyatipus": "Ige"})]

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertEqual(len(enemy.kez), 0)
        self.assertEqual(enemy.pakli[0].nev, "Ellenseges Lap")

    def test_structured_move_to_source_uses_own_graveyard_entity(self):
        card = Kartya(
            {
                "kartya_nev": "Forrasba Emeles",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Helyezz egy sajat Entitast az Uressegbol az Osforrasaid koze.",
                "hatascimkek": "move_to_source",
                "celpont_felismerve": "own_graveyard_entity",
            }
        )
        owner = make_player("Owner")
        owner.temeto = [Kartya({"kartya_nev": "Elesett", "kartyatipus": "Entitas"})]

        result = resolve_structured_effect(card, owner, None, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertEqual(len(owner.temeto), 0)
        self.assertEqual(owner.osforras[-1]["lap"].nev, "Elesett")

    def test_structured_resource_gain_uses_shared_helper(self):
        card = Kartya(
            {
                "kartya_nev": "Forrasnyeres",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Kapj 2 osforrast.",
                "hatascimkek": "resource_gain",
            }
        )
        owner = make_player("Owner")
        owner.pakli = [
            Kartya({"kartya_nev": "F1", "kartyatipus": "Ige"}),
            Kartya({"kartya_nev": "F2", "kartyatipus": "Ige"}),
        ]

        result = resolve_structured_effect(card, owner, None, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertEqual(len(owner.osforras), 2)

    def test_structured_cost_mod_uses_shared_helper(self):
        card = Kartya(
            {
                "kartya_nev": "Olcsositas",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "A kovetkezo Entitasod 2 auraval olcsobb.",
                "hatascimkek": "cost_mod",
            }
        )
        owner = make_player("Owner")

        result = resolve_structured_effect(card, owner, None, {"category": "on_play", "cost_mod_scope": "entity"})

        self.assertTrue(result["resolved"])
        self.assertEqual(owner.kovetkezo_entitas_kedvezmeny, 2)

    def test_structured_untargetable_uses_shared_helper(self):
        card = Kartya(
            {
                "kartya_nev": "Rejto Fatyol",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Egy sajat Entitas nem celozhato.",
                "hatascimkek": "untargetable",
                "celpont_felismerve": "own_entity",
            }
        )
        owner = make_player("Owner")
        owner.horizont[0] = CsataEgyseg(Kartya({"kartya_nev": "Vedett", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))

        result = resolve_structured_effect(card, owner, None, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertTrue(owner.horizont[0].targeting_state_override.untargetable)

    def test_structured_ability_lock_uses_shared_helper(self):
        card = Kartya(
            {
                "kartya_nev": "Nema Halo",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Egy ellenseges Entitas kepessegei le vannak tiltva a kor vegeig.",
                "hatascimkek": "ability_lock",
                "celpont_felismerve": "enemy_entity",
            }
        )
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(Kartya({"kartya_nev": "Celpont", "kartyatipus": "Entitas", "tamadas": 2, "eletero": 3}))

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertTrue(enemy.horizont[0].abilities_locked_until_turn_end)

    def test_structured_position_lock_uses_shared_helper(self):
        card = Kartya(
            {
                "kartya_nev": "Mozgas Gat",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Egy ellenseges Entitas addig nem valthat poziciot.",
                "hatascimkek": "position_lock",
                "celpont_felismerve": "enemy_entity",
            }
        )
        owner = make_player("Owner")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(Kartya({"kartya_nev": "Celpont", "kartyatipus": "Entitas", "tamadas": 2, "eletero": 3}))

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertEqual(enemy.horizont[0].position_lock_awakenings, 1)

    def test_structured_source_manipulation_uses_shared_helper(self):
        card = Kartya(
            {
                "kartya_nev": "Forrasba Tereles",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Helyezz egy sajat lapot az Uressegbol az Osforrasaid koze.",
                "hatascimkek": "source_manipulation",
                "celpont_felismerve": "own_graveyard",
            }
        )
        owner = make_player("Owner")
        owner.temeto = [Kartya({"kartya_nev": "Elesett Lap", "kartyatipus": "Ige"})]

        result = resolve_structured_effect(card, owner, None, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertEqual(len(owner.temeto), 0)
        self.assertEqual(owner.osforras[-1]["lap"].nev, "Elesett Lap")


if __name__ == "__main__":
    unittest.main()
