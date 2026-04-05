import random
from engine.board_utils import (
    _is_board_entity,
    _object_name,
    _object_type,
    is_attackable_zenit_target,
    is_trap,
    is_zenit_entity,
    set_zone_slot,
)
from engine.combat import CombatResolver
from engine.config import get_active_engine_config
from engine.game_state import MatchState
from engine.phases import PhaseRunner
from utils.text import normalize_lookup_text
from utils.logger import naplo
from stats.analyzer import stats
from engine.player import Jatekos
from engine.card import CsataEgyseg
from engine.effects import EffectEngine
from engine.keyword_engine import KeywordEngine
from engine.triggers import trigger_engine
from cards.resolver import can_activate_trap, resolve_card_handler, resolve_lethal_trap, resolve_spell_cast_trap, handle_sivatagi_kem_pecset_sebzes


class AeternaSzimulacio:
    def __init__(self, b1_nev, b2_nev, kartyak, engine_config=None):
        self.p1 = Jatekos("Jatekos_1", b1_nev, kartyak)
        self.p2 = Jatekos("Jatekos_2", b2_nev, kartyak)
        self.kor = 1
        self.engine_config = engine_config or get_active_engine_config()
        self.state = MatchState(self.p1, self.p2, self.kor)
        self.phase_runner = PhaseRunner(self)
        self.combat_resolver = CombatResolver(self)
        self.elokeszites()

    def elokeszites(self):
        for _ in range(5):
            self.p1.huzas()
            self.p2.huzas()

        for _ in range(5):
            if self.p1.pakli:
                self.p1.pecsetek.append(self.p1.pakli.pop())
            if self.p2.pakli:
                self.p2.pecsetek.append(self.p2.pakli.pop())

        trigger_engine.dispatch("on_manifestation_phase", owner=self.p1, payload={"phase": "setup"})
        trigger_engine.dispatch("on_manifestation_phase", owner=self.p2, payload={"phase": "setup"})

    def kijatszas_fazis(self, jatekos):
        lehetosegek = [
            l for l in jatekos.kez
            if jatekos.elerheto_aura() >= jatekos.effektiv_aura_koltseg(l)
            and l.magnitudo <= len(jatekos.osforras)
        ]

        if not lehetosegek:
            return None

        lap = random.choice(lehetosegek)

        if lap.egyseg_e:
            zona = jatekos.horizont if random.random() < 0.7 else jatekos.zenit

            for i in range(6):
                if zona[i] is None:
                    if jatekos.fizet(lap):
                        jatekos.kez.remove(lap)
                        egyseg = CsataEgyseg(lap)
                        egyseg.owner = jatekos
                        zona_nev = "horizont" if zona is jatekos.horizont else "zenit"
                        set_zone_slot(jatekos, zona_nev, i, egyseg, f"summon:{lap.nev}")
                        jatekos.megidezett_entitasok_ebben_a_korben += 1
                        stats.faj_statisztika(lap.faj)
                        naplo.ir(f"{jatekos.nev} megidezte: {lap.nev}")

                        trigger_engine.dispatch(
                            "on_summon",
                            source=egyseg,
                            owner=jatekos,
                            payload={"zone": zona_nev},
                        )
                        ellenfel = self.p2 if jatekos == self.p1 else self.p1
                        trigger_engine.dispatch(
                            "on_enemy_summon",
                            source=egyseg,
                            owner=ellenfel,
                            target=jatekos,
                            payload={"zone": zona_nev, "summoner": jatekos},
                        )
                        self._resolve_summon_traps(egyseg, jatekos, ellenfel)
                        if getattr(jatekos, zona_nev)[i] is None:
                            break
                        gyoztes = self._alkalmaz_kartya_hatast(lap, jatekos, ellenfel)
                        if gyoztes:
                            return gyoztes
                        break

        elif lap.jel_e:
            jelek_szama = len([
                z for z in jatekos.zenit
                if is_trap(z)
            ])

            if jelek_szama >= 2:
                for i in range(6):
                    if is_trap(jatekos.zenit[i]):
                        kidobott = jatekos.zenit[i]
                        jatekos.temeto.append(kidobott)
                        set_zone_slot(jatekos, "zenit", i, None, "jel_limit_discard")
                        naplo.ir(f"Jel limit: {kidobott.nev} eldobva")
                        break

            for i in range(6):
                if jatekos.zenit[i] is None:
                    if jatekos.fizet(lap):
                        jatekos.kez.remove(lap)
                        set_zone_slot(jatekos, "zenit", i, lap, f"trap_play:{lap.nev}")
                        naplo.ir(f"{jatekos.nev} Jelet rakott: {lap.nev}")
                        break

        else:
            if jatekos.fizet(lap):
                jatekos.kez.remove(lap)
                jatekos.temeto.append(lap)

                naplo.ir(f"{jatekos.nev} varazsol: {lap.nev}")

                ellenfel = self.p2 if jatekos == self.p1 else self.p1
                trap_result = self._resolve_spell_cast_traps(lap, jatekos, ellenfel)
                if self._spell_cancelled_by_trap(trap_result):
                    naplo.ir(f"{jatekos.nev} varazslata megszakadt: {lap.nev}")
                    return None
                gyoztes = self._alkalmaz_kartya_hatast(lap, jatekos, ellenfel)
                if gyoztes:
                    return gyoztes

        return None

    def _aktivalhato_burst(self, vedo, p):
        if not p.reakcio_e:
            return

        naplo.ir("Reakcio (Burst) aktivalodik")
        tamado = self.p1 if vedo == self.p2 else self.p2
        EffectEngine.trigger_on_burst(p, vedo, tamado)

    def _ellenfel(self, jatekos):
        return self.p2 if jatekos == self.p1 else self.p1

    def _overflow_gyoztes(self):
        if self.p1.overflow_vereseg:
            return self.p1.overflow_gyoztes_nev or self.p2.nev
        if self.p2.overflow_vereseg:
            return self.p2.overflow_gyoztes_nev or self.p1.nev
        return None

    def _ellenoriz_gyoztest(self):
        return self._overflow_gyoztes()

    def _alkalmaz_kartya_hatast(self, lap, jatekos, ellenfel):
        trigger_engine.dispatch("on_play", source=lap, owner=jatekos, target=ellenfel)
        if not lap.egyseg_e:
            trigger_engine.dispatch(
                "on_enemy_spell_played",
                source=lap,
                owner=ellenfel,
                target=jatekos,
                payload={"caster": jatekos},
            )
        EffectEngine.trigger_on_play(lap, jatekos, ellenfel)
        return self._ellenoriz_gyoztest()

    def _jelol_harc_overflowot(self, tamado, vedo):
        vedo.jelol_overflow_vereseget(tamado.nev)
        naplo.ir(f"{tamado.nev} nyert (Overflow)")
        return self._ellenoriz_gyoztest()

    def _elpusztit_egyseget(self, jatekos, zona_nev, index, ok="harc"):
        return EffectEngine.destroy_unit(
            jatekos, zona_nev, index, self._ellenfel(jatekos), ok
        )

    def _feltor_pecset(self, vedo, burst_aktivalt_ebben_a_harcban, forras=None):
        if not vedo.pecsetek:
            return False, burst_aktivalt_ebben_a_harcban

        p = vedo.pecsetek.pop()
        stats.feltort_pecsetek += 1

        if p.magnitudo > len(vedo.osforras):
            vedo.osforras.append({"lap": p, "hasznalt": False})
            if forras:
                naplo.ir(f"{forras} + Gondviseles")
            else:
                naplo.ir("Gondviseles aktivalodott")
        else:
            vedo.kez.append(p)
            if forras:
                naplo.ir(f"{forras}: extra pecset tort ({p.nev})")
            else:
                naplo.ir(f"Pecset feltort: {p.nev}")

        if p.reakcio_e and not burst_aktivalt_ebben_a_harcban:
            self._aktivalhato_burst(vedo, p)
            burst_aktivalt_ebben_a_harcban = True

        return True, burst_aktivalt_ebben_a_harcban

    def _resolve_summon_traps(self, summoned_unit, owner, opponent):
        if opponent.hasznalt_jelek_ebben_a_korben >= 2:
            return False

        for index, trap in enumerate(opponent.zenit):
            if not is_trap(trap):
                continue

            result = resolve_card_handler(
                trap,
                category="summon_trap",
                vedo=opponent,
                tamado=owner,
                summoned_unit=summoned_unit,
            )
            if result.get("consume_trap"):
                opponent.temeto.append(trap)
                set_zone_slot(opponent, "zenit", index, None, f"summon_trap_consumed:{getattr(trap, 'nev', 'ismeretlen')}")
                opponent.hasznalt_jelek_ebben_a_korben += 1
                stats.aktivalt_jelek += 1
                if result.get("destroy_summoned"):
                    if summoned_unit in owner.horizont:
                        self._elpusztit_egyseget(owner, "horizont", owner.horizont.index(summoned_unit), "csapda")
                    elif summoned_unit in owner.zenit:
                        self._elpusztit_egyseget(owner, "zenit", owner.zenit.index(summoned_unit), "csapda")
                return True

        return False

    def _resolve_spell_cast_traps(self, spell_card, caster, defender):
        if defender.hasznalt_jelek_ebben_a_korben >= 2:
            return False

        for index, trap in enumerate(defender.zenit):
            if not is_trap(trap):
                continue

            result = resolve_spell_cast_trap(
                trap,
                varazslat=spell_card,
                jatekos=defender,
                ellenfel=caster,
            )
            if result.get("consume_trap"):
                defender.temeto.append(trap)
                set_zone_slot(defender, "zenit", index, None, f"spell_trap_consumed:{getattr(trap, 'nev', 'ismeretlen')}")
                defender.hasznalt_jelek_ebben_a_korben += 1
                stats.aktivalt_jelek += 1
                return result
        return False

    def _spell_cancelled_by_trap(self, trap_result):
        if not isinstance(trap_result, dict):
            return False
        return bool(trap_result.get("cancelled_spell") or trap_result.get("stop_spell"))

    def _can_direct_attack_exhausted_unit(self, celpont):
        return _is_board_entity(celpont) and celpont.kimerult

    def _attackable_exhausted_unit(self, vedo, lane_index):
        celpont = vedo.horizont[lane_index]
        if self._can_direct_attack_exhausted_unit(celpont):
            return lane_index, celpont
        return None, None

    def _select_direct_attack_target(self, vedo, lane_index):
        lane_unit = vedo.horizont[lane_index]
        lane_zenit = vedo.zenit[lane_index]

        if lane_unit is None and is_attackable_zenit_target(lane_zenit):
            return "zenit", lane_index, lane_zenit

        cel_index, celpont = self._attackable_exhausted_unit(vedo, lane_index)
        if celpont is not None:
            return "horizont", cel_index, celpont

        return "seal", None, None

    def _can_attack_with_unit(self, tamado, egyseg):
        if egyseg is None:
            return False

        lap = getattr(egyseg, "lap", None)
        lap_nev = normalize_lookup_text(getattr(lap, "nev", ""))
        if lap_nev != "vulkani golem":
            return True

        sajat_birodalom = normalize_lookup_text(getattr(lap, "birodalom", ""))
        aktiv_ignis_tarsak = 0
        for zona in (getattr(tamado, "horizont", []), getattr(tamado, "zenit", [])):
            for masik in zona:
                if masik is None or masik is egyseg or not _is_board_entity(masik):
                    continue
                if getattr(masik, "kimerult", True):
                    continue
                masik_lap = getattr(masik, "lap", None)
                if normalize_lookup_text(getattr(masik_lap, "birodalom", "")) != sajat_birodalom:
                    continue
                aktiv_ignis_tarsak += 1
                if aktiv_ignis_tarsak >= 2:
                    return True

        naplo.ir(
            f"Vulkani Golem: {getattr(lap, 'nev', 'ismeretlen')} nem tamadhat, mert nincs 2 masik aktiv Ignis entitas a Dominiumon."
        )
        return False

    def _scaled_combat_damage(self, celpont, sebzes, zone_name):
        if sebzes <= 0:
            return 0
        if zone_name == "horizont" and getattr(celpont, "half_damage_on_horizon_until_turn_end", False):
            uj = sebzes // 2
            naplo.ir(
                f"Folyekony Pancel: {celpont.lap.nev} a Horizonton {sebzes} helyett {uj} harci sebzest szenvedett el."
            )
            return uj
        return sebzes

    def harc_fazis(self, tamado, vedo):
        burst_aktivalt_ebben_a_harcban = False
        tamadas_tortent = False
        trigger_engine.dispatch("on_combat_phase_start", owner=tamado, target=vedo, payload={"turn": self.kor})

        for i in range(6):
            egyseg = tamado.horizont[i]
            if egyseg is not None and not _is_board_entity(egyseg):
                naplo.ir(
                    f"[DEBUG:INVALID_ATTACKER_ENTRY] {tamado.nev} | horizont[{i}] | tipus={_object_type(egyseg)} | nev={_object_name(egyseg)}"
                )
                continue

            if egyseg and not egyseg.kimerult and not getattr(egyseg, "cannot_attack_until_turn_end", False):
                if not self._can_attack_with_unit(tamado, egyseg):
                    continue
                tamadas_tortent = True
                egyseg.kimerult = True
                trigger_engine.dispatch("on_attack_declared", source=egyseg, owner=tamado, target=vedo, payload={"lane_index": i})
                eredeti_atk = egyseg.akt_tamadas
                egyseg.attack_damage_zero_this_combat = False

                if is_zenit_entity(tamado.zenit[i]):
                    hatso = tamado.zenit[i]
                    bonusz = KeywordEngine.get_harmonize_bonus(egyseg, hatso)
                    if bonusz > 0:
                        egyseg.akt_tamadas += bonusz

                naplo.ir(f"TAMADAS: {egyseg.lap.nev} ({egyseg.akt_tamadas})")

                jel_megallitotta = False
                if vedo.hasznalt_jelek_ebben_a_korben < 2:
                    for j in range(6):
                        if is_trap(vedo.zenit[j]):
                            jel = vedo.zenit[j]
                            if not can_activate_trap(jel, tamado_egyseg=egyseg, tamado=tamado, vedo=vedo):
                                continue
                            set_zone_slot(vedo, "zenit", j, None, f"combat_trap_consumed:{getattr(jel, 'nev', 'ismeretlen')}")
                            vedo.temeto.append(jel)

                            vedo.hasznalt_jelek_ebben_a_korben += 1
                            stats.aktivalt_jelek += 1

                            trap_result = EffectEngine.trigger_on_trap(jel, egyseg, tamado, vedo)
                            if isinstance(trap_result, dict) and trap_result.get("stop_attack"):
                                jel_megallitotta = True
                            elif isinstance(trap_result, dict) and trap_result.get("continue_attack"):
                                jel_megallitotta = False
                            elif trap_result:
                                self._elpusztit_egyseget(tamado, "horizont", i, "csapda")
                                jel_megallitotta = True
                            break

                if jel_megallitotta:
                    continue

                blokkolok = KeywordEngine.get_blockers(vedo)
                blokkolok = KeywordEngine.filter_blockers_for_attacker(egyseg, blokkolok)

                if blokkolok:
                    b = random.choice(blokkolok)
                    b.kimerult = True

                    naplo.ir(f"Blokkol: {b.lap.nev}")

                    blokkolo_meghalt = False
                    blokkolo_index = vedo.horizont.index(b)

                    bejovo_sebzes = 0 if getattr(egyseg, "attack_damage_zero_this_combat", False) else self._scaled_combat_damage(b, egyseg.akt_tamadas, "horizont")
                    trigger_engine.dispatch(
                        "on_damage_taken",
                        source=egyseg,
                        owner=tamado,
                        target=b,
                        payload={"damage": bejovo_sebzes, "zone": "horizont", "target_owner": vedo, "source_zone": "horizont", "source_index": i, "combat": True},
                    )
                    if getattr(b, "damage_immunity_until_turn_end", False):
                        naplo.ir(f"Vakito Ragyogas: {b.lap.nev} sebzesimmunis volt, a harci sebzes elmaradt.")
                    elif bejovo_sebzes > 0 and b.serul(bejovo_sebzes):
                        lethal_result = resolve_lethal_trap(owner=vedo, unit=b, attacker=egyseg, zone_name="horizont", index=blokkolo_index)
                        if lethal_result and lethal_result.get("prevented_death"):
                            blokkolo_meghalt = False
                        else:
                            blokkolo_meghalt = self._elpusztit_egyseget(vedo, "horizont", blokkolo_index)

                    KeywordEngine.on_damage_dealt(egyseg, b)

                    visszautes = self._scaled_combat_damage(egyseg, b.akt_tamadas, "horizont")
                    trigger_engine.dispatch(
                        "on_damage_taken",
                        source=b,
                        owner=vedo,
                        target=egyseg,
                        payload={"damage": visszautes, "zone": "horizont", "target_owner": tamado, "source_zone": "horizont", "source_index": blokkolo_index, "combat": True},
                    )
                    if getattr(egyseg, "damage_immunity_until_turn_end", False):
                        naplo.ir(f"Vakito Ragyogas: {egyseg.lap.nev} sebzesimmunis volt, a visszautes elmaradt.")
                    elif egyseg.serul(visszautes):
                        lethal_result = resolve_lethal_trap(owner=tamado, unit=egyseg, attacker=b, zone_name="horizont", index=i)
                        if not (lethal_result and lethal_result.get("prevented_death")):
                            self._elpusztit_egyseget(tamado, "horizont", i)

                    KeywordEngine.on_damage_dealt(b, egyseg)

                    KeywordEngine.resolve_bane(
                        egyseg,
                        b,
                        lambda: self._elpusztit_egyseget(vedo, "horizont", blokkolo_index, "metely")
                    )

                    sundering_result = KeywordEngine.resolve_sundering(
                        egyseg,
                        blokkolo_meghalt,
                        lambda: self._feltor_pecset(vedo, burst_aktivalt_ebben_a_harcban, "Hasitas")
                    )
                    if sundering_result:
                        _, burst_aktivalt_ebben_a_harcban = sundering_result
                        gyoztes = self._ellenoriz_gyoztest()
                        if gyoztes:
                            return gyoztes

                else:
                    target_kind, target_index, target_unit = self._select_direct_attack_target(vedo, i)

                    if target_kind == "zenit":
                        z = target_unit

                        naplo.ir(f"Zenit tamadas: {z.lap.nev}")

                        zenit_sebzes = 0 if getattr(egyseg, "attack_damage_zero_this_combat", False) else egyseg.akt_tamadas
                        trigger_engine.dispatch(
                            "on_damage_taken",
                            source=egyseg,
                            owner=tamado,
                            target=target_unit,
                            payload={"damage": zenit_sebzes, "zone": "zenit", "target_owner": vedo, "source_zone": "horizont", "source_index": i, "combat": True},
                        )
                        if getattr(target_unit, "damage_immunity_until_turn_end", False):
                            naplo.ir(f"Vakito Ragyogas: {target_unit.lap.nev} sebzesimmunis volt, a Zenit sebzes elmaradt.")
                        elif zenit_sebzes > 0 and target_unit.serul(zenit_sebzes):
                            lethal_result = resolve_lethal_trap(owner=vedo, unit=target_unit, attacker=egyseg, zone_name="zenit", index=target_index)
                            if not (lethal_result and lethal_result.get("prevented_death")):
                                self._elpusztit_egyseget(vedo, "zenit", target_index)

                        KeywordEngine.on_damage_dealt(egyseg, target_unit)

                        zenit_visszautes = self._scaled_combat_damage(egyseg, target_unit.akt_tamadas, "horizont")
                        trigger_engine.dispatch(
                            "on_damage_taken",
                            source=target_unit,
                            owner=vedo,
                            target=egyseg,
                            payload={"damage": zenit_visszautes, "zone": "horizont", "target_owner": tamado, "source_zone": "zenit", "source_index": target_index, "combat": True},
                        )
                        if getattr(egyseg, "damage_immunity_until_turn_end", False):
                            naplo.ir(f"Vakito Ragyogas: {egyseg.lap.nev} sebzesimmunis volt, a Zenit visszautes elmaradt.")
                        elif egyseg.serul(zenit_visszautes):
                            lethal_result = resolve_lethal_trap(owner=tamado, unit=egyseg, attacker=target_unit, zone_name="horizont", index=i)
                            if not (lethal_result and lethal_result.get("prevented_death")):
                                self._elpusztit_egyseget(tamado, "horizont", i)

                        KeywordEngine.on_damage_dealt(target_unit, egyseg)

                        continue

                    if target_kind == "horizont":
                        naplo.ir(f"Kozvetlen tamadas kimerult egysegre: {target_unit.lap.nev}")

                        kozvetlen_sebzes = 0 if getattr(egyseg, "attack_damage_zero_this_combat", False) else self._scaled_combat_damage(target_unit, egyseg.akt_tamadas, "horizont")
                        trigger_engine.dispatch(
                            "on_damage_taken",
                            source=egyseg,
                            owner=tamado,
                            target=target_unit,
                            payload={"damage": kozvetlen_sebzes, "zone": "horizont", "target_owner": vedo, "source_zone": "horizont", "source_index": i, "combat": True},
                        )
                        if getattr(target_unit, "damage_immunity_until_turn_end", False):
                            naplo.ir(f"Vakito Ragyogas: {target_unit.lap.nev} sebzesimmunis volt, a direkt sebzes elmaradt.")
                        elif kozvetlen_sebzes > 0 and target_unit.serul(kozvetlen_sebzes):
                            lethal_result = resolve_lethal_trap(owner=vedo, unit=target_unit, attacker=egyseg, zone_name="horizont", index=target_index)
                            if not (lethal_result and lethal_result.get("prevented_death")):
                                self._elpusztit_egyseget(vedo, "horizont", target_index)

                        KeywordEngine.on_damage_dealt(egyseg, target_unit)

                        continue

                    direct_trap_stopped = False
                    if vedo.hasznalt_jelek_ebben_a_korben < 2:
                        for j in range(6):
                            jel = vedo.zenit[j]
                            if not is_trap(jel):
                                continue
                            if not can_activate_trap(jel, tamado_egyseg=egyseg, tamado=tamado, vedo=vedo, target_kind="seal"):
                                continue
                            result = resolve_card_handler(jel, category="trap", tamado_egyseg=egyseg, tamado=tamado, vedo=vedo, target_kind="seal")
                            if result.get("consume_trap"):
                                vedo.temeto.append(jel)
                                set_zone_slot(vedo, "zenit", j, None, f"direct_attack_trap_consumed:{getattr(jel, 'nev', 'ismeretlen')}")
                                vedo.hasznalt_jelek_ebben_a_korben += 1
                                stats.aktivalt_jelek += 1
                            if result.get("stop_attack"):
                                direct_trap_stopped = True
                                break
                        if direct_trap_stopped:
                            continue

                    trigger_engine.dispatch(
                        "on_breach_phase",
                        source=egyseg,
                        owner=tamado,
                        target=vedo,
                        payload={"lane_index": i},
                    )
                    pecset_tort, burst_aktivalt_ebben_a_harcban = self._feltor_pecset(
                        vedo, burst_aktivalt_ebben_a_harcban
                    )
                    handle_sivatagi_kem_pecset_sebzes(egyseg, vedo)
                    gyoztes = self._ellenoriz_gyoztest()
                    if gyoztes:
                        return gyoztes

                    if not pecset_tort:
                        return self._jelol_harc_overflowot(tamado, vedo)

                if _is_board_entity(tamado.horizont[i]):
                    tamado.horizont[i].akt_tamadas = eredeti_atk
                    tamado.horizont[i].attack_damage_zero_this_combat = False

        if tamado.kell_tamadnia_kovetkezo_korben and tamadas_tortent:
            tamado.kell_tamadnia_kovetkezo_korben = False

        return None

    def kor_futtatasa(self):
        self.state.kor = self.kor
        naplo.ir(f"\n>>>> {self.kor}. KOR <<<<")

        for index, (akt, ell) in enumerate([(self.p1, self.p2), (self.p2, self.p1)]):
            akt.uj_kor_inditasa()
            trigger_engine.dispatch("on_turn_start", owner=akt, target=ell, payload={"turn": self.kor})
            trigger_engine.dispatch("on_awakening_phase", owner=akt, target=ell, payload={"turn": self.kor})

            if akt.kell_tamadnia_kovetkezo_korben:
                naplo.ir(f"{akt.nev} Kenyszerites/Provoke hatas alatt all: ha tud, tamadnia kell ebben a korben.")

            if self.kor == 1 and index == 0:
                naplo.ir("Kezdojatekos: nem huz es nem tamadhat az elso korben")
            else:
                akt.huzas()
                akt.huzas()

            akt.osforras_bovites()
            trigger_engine.dispatch("on_manifestation_phase", owner=akt, target=ell, payload={"turn": self.kor})

            eredmeny = self.phase_runner.run_play_phase(akt)
            if eredmeny:
                akt.kor_vegi_heal()
                ell.kor_vegi_heal()
                return eredmeny

            kotelezo_tamadas = akt.kell_tamadnia_kovetkezo_korben
            volt_tamadasra_kepes = any(
                _is_board_entity(e) and not e.kimerult
                for e in akt.horizont
            )

            if not (self.kor == 1 and index == 0):
                eredmeny = self.combat_resolver.resolve_attack_phase(akt, ell)
                if eredmeny:
                    akt.kor_vegi_heal()
                    ell.kor_vegi_heal()
                    return eredmeny

                if kotelezo_tamadas:
                    if volt_tamadasra_kepes:
                        if not akt.kell_tamadnia_kovetkezo_korben:
                            naplo.ir(f"{akt.nev} teljesitette a kotelezo tamadast.")
                    else:
                        naplo.ir(f"{akt.nev} Kenyszerites/Provoke alatt allt, de nem volt tamadasra kepes Horizont egysege.")

            akt.kor_vegi_heal()
            ell.kor_vegi_heal()
            trigger_engine.dispatch("on_turn_end", owner=akt, target=ell, payload={"turn": self.kor})

        self.kor += 1
        return None
