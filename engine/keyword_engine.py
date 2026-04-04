from engine.board_utils import _is_board_entity, _object_name, _object_type
from engine.keyword_registry import KEYWORD_DEFINITIONS, KeywordRegistry
from engine.targeting import TargetingEngine
from engine.triggers import trigger_engine
from utils.logger import naplo


class KeywordEngine:
    KEYWORDS = KEYWORD_DEFINITIONS

    @staticmethod
    def _normalize(szoveg):
        return KeywordRegistry.normalize_keyword_name(szoveg)

    @staticmethod
    def _keyword_text(forras):
        return getattr(forras.lap, "kepesseg", getattr(forras, "kepesseg", ""))

    @staticmethod
    def _has_keyword(forras, *kulcsszavak):
        temp_removed = set(getattr(forras, "temp_removed_keywords", set()) or set())
        granted = set(getattr(forras, "granted_keywords", set()) or set())
        temp_granted = set(getattr(forras, "temp_granted_keywords", set()) or set())
        keyword_text = KeywordEngine._keyword_text(forras)
        card_keywords = set(getattr(getattr(forras, "lap", forras), "keywords_normalized", []) or [])
        for kulcsszo in kulcsszavak:
            normalized = KeywordRegistry.normalize_keyword_name(kulcsszo)
            if normalized in temp_removed:
                continue
            if normalized in granted or normalized in temp_granted:
                return True
            if normalized in card_keywords:
                return True
            if KeywordRegistry.has_keyword(keyword_text, kulcsszo):
                return True
        return False

    @staticmethod
    def apply_static_keyword_states(egyseg):
        state = TargetingEngine.target_state(egyseg)
        if KeywordEngine._has_keyword(egyseg, "aegis"):
            state.trap_negate = False
        if KeywordEngine._has_keyword(egyseg, "ethereal"):
            state.exhaust_target_allowed = True
        if KeywordEngine._has_keyword(egyseg, "resonance"):
            state.return_to_hand_allowed = True
        if KeywordEngine._has_keyword(egyseg, "burst"):
            state.burst_response = True
        return state

    @staticmethod
    def on_summon(egyseg):
        KeywordEngine.apply_static_keyword_states(egyseg)
        if KeywordEngine._has_keyword(egyseg, "celerity"):
            egyseg.kimerult = False
            naplo.ir(f"Celerity: {egyseg.lap.nev} azonnal tamadhat.")

    @staticmethod
    def modify_attack(attacker):
        bonus = 0
        if KeywordEngine._has_keyword(attacker, "resonance"):
            owner = getattr(attacker, "owner", None)
            bonus += getattr(owner, "rezonancia_aura", 0)
            if bonus > 0:
                naplo.ir(f"Rezonancia +{bonus} ATK")
        return bonus

    @staticmethod
    def get_harmonize_bonus(attacker, support_unit):
        if support_unit is None:
            return 0
        if not KeywordEngine._has_keyword(support_unit, "harmonize"):
            return 0
        if support_unit.lap.magnitudo <= 4:
            bonusz = 2
        elif support_unit.lap.magnitudo <= 8:
            bonusz = 1
        else:
            bonusz = 0
        if bonusz > 0:
            naplo.ir(f"Harmonizalas +{bonusz} ATK")
        return bonusz

    @staticmethod
    def on_damage_dealt(attacker, defender):
        if KeywordEngine._has_keyword(attacker, "sundering"):
            naplo.ir("Hasitas aktivalodik")
        if KeywordEngine._has_keyword(attacker, "bane") and defender is not None:
            defender.bane_target = True
            naplo.ir("Metely megjelolte a celpontot")

    @staticmethod
    def get_blockers(vedo):
        valid_blockers = []
        for index, entity in enumerate(vedo.horizont):
            if entity is None:
                continue
            if not _is_board_entity(entity):
                naplo.ir(
                    f"[DEBUG:INVALID_BLOCKER_ENTRY] {getattr(vedo, 'nev', 'ismeretlen')} | horizont[{index}] | tipus={_object_type(entity)} | nev={_object_name(entity)}"
                )
                continue
            if getattr(entity, "kimerult", True):
                continue
            if getattr(entity, "cannot_block_until_turn_end", False):
                continue
            valid_blockers.append(entity)

        aegis = [
            entity for entity in valid_blockers
            if KeywordEngine._has_keyword(entity, "aegis")
        ]
        if aegis:
            naplo.ir("Aegis kotelezo blokk")
            return aegis
        return valid_blockers

    @staticmethod
    def filter_blockers_for_attacker(attacker, blockers):
        if not KeywordEngine._has_keyword(attacker, "ethereal"):
            return blockers
        ervenyes = [blocker for blocker in blockers if KeywordEngine._has_keyword(blocker, "ethereal")]
        naplo.ir("Csak legies blokkolhat")
        return ervenyes

    @staticmethod
    def resolve_bane(attacker, defender, destroy_defender):
        if defender is None or not getattr(defender, "bane_target", False):
            return False
        if not KeywordEngine._has_keyword(attacker, "bane"):
            return False
        if destroy_defender():
            naplo.ir(f"Metely: {defender.lap.nev} elpusztul")
            return True
        return False

    @staticmethod
    def resolve_sundering(attacker, defender_died_from_damage, break_extra_seal):
        if not defender_died_from_damage:
            return False
        if not KeywordEngine._has_keyword(attacker, "sundering"):
            return False
        return break_extra_seal()

    @staticmethod
    def spell_allows_direct_damage(source):
        return KeywordEngine._has_keyword(source, "clarion")

    @staticmethod
    def has_echo(source):
        return KeywordEngine._has_keyword(source, "echo")

    @staticmethod
    def has_burst(source):
        return KeywordEngine._has_keyword(source, "burst")


def _register_keyword_trigger_handlers():
    def _on_summon(context):
        if context.source is not None:
            KeywordEngine.on_summon(context.source)

    trigger_engine.register("on_summon", _on_summon)


_register_keyword_trigger_handlers()
