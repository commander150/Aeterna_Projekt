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
        keyword_text = KeywordEngine._keyword_text(forras)
        return any(KeywordRegistry.has_keyword(keyword_text, kulcsszo) for kulcsszavak in [kulcsszavak] for kulcsszo in kulcsszavak)

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
            naplo.ir(f"⚡ {egyseg.lap.nev} azonnal támadhat (Celerity)")

    @staticmethod
    def modify_attack(attacker):
        bonus = 0
        if KeywordEngine._has_keyword(attacker, "resonance"):
            owner = getattr(attacker, "owner", None)
            bonus += getattr(owner, "rezonancia_aura", 0)
            if bonus > 0:
                naplo.ir(f"✨ Rezonancia +{bonus} ATK")
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
            naplo.ir(f"🎶 Harmonizálás +{bonusz} ATK")
        return bonusz

    @staticmethod
    def on_damage_dealt(attacker, defender):
        if KeywordEngine._has_keyword(attacker, "sundering"):
            naplo.ir("💢 Hasítás aktiválódik")
        if KeywordEngine._has_keyword(attacker, "bane") and defender is not None:
            defender.bane_target = True
            naplo.ir("☠️ Métely megjelölte a célpontot")

    @staticmethod
    def get_blockers(vedo):
        aegis = [
            e for e in vedo.horizont
            if e and not e.kimerult and not getattr(e, "cannot_block_until_turn_end", False) and KeywordEngine._has_keyword(e, "aegis")
        ]
        if aegis:
            naplo.ir("🛡️ Aegis kötelező blokkolás")
            return aegis
        return [e for e in vedo.horizont if e and not e.kimerult and not getattr(e, "cannot_block_until_turn_end", False)]

    @staticmethod
    def filter_blockers_for_attacker(attacker, blockers):
        if not KeywordEngine._has_keyword(attacker, "ethereal"):
            return blockers
        ervenyes = [blocker for blocker in blockers if KeywordEngine._has_keyword(blocker, "ethereal")]
        naplo.ir("👻 Csak légies blokkolhat")
        return ervenyes

    @staticmethod
    def resolve_bane(attacker, defender, destroy_defender):
        if defender is None or not getattr(defender, "bane_target", False):
            return False
        if not KeywordEngine._has_keyword(attacker, "bane"):
            return False
        if destroy_defender():
            naplo.ir(f"☠️ Métely: {defender.lap.nev} a fázis végéig elpusztul")
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
