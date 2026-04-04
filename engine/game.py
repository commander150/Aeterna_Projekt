import random
from engine.combat import CombatResolver
from engine.config import get_active_engine_config
from engine.game_state import MatchState
from engine.phases import PhaseRunner
from utils.logger import naplo
from stats.analyzer import stats
from engine.player import Jatekos
from engine.card import CsataEgyseg
from engine.effects import EffectEngine
from engine.keywords import KeywordEngine
from engine.triggers import trigger_engine
from cards.resolver import can_activate_trap, resolve_card_handler, resolve_lethal_trap, resolve_spell_cast_trap


class AeternaSzimulacio:
    def __init__(self, b1_nev, b2_nev, kartyak, engine_config=None):
        self.p1 = Jatekos("Játékos_1", b1_nev, kartyak)
        self.p2 = Jatekos("Játékos_2", b2_nev, kartyak)
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
                        zona[i] = CsataEgyseg(lap)
                        zona[i].owner = jatekos
                        jatekos.megidezett_entitasok_ebben_a_korben += 1
                        stats.faj_statisztika(lap.faj)
                        naplo.ir(f"⚔️ {jatekos.nev} megidézte: {lap.nev}")

                        trigger_engine.dispatch(
                            "on_summon",
                            source=zona[i],
                            owner=jatekos,
                            payload={"zone": "horizont" if zona is jatekos.horizont else "zenit"},
                        )
                        ellenfel = self.p2 if jatekos == self.p1 else self.p1
                        self._resolve_summon_traps(zona[i], jatekos, ellenfel)
                        if zona[i] is None:
                            break
                        gyoztes = self._alkalmaz_kartya_hatast(lap, jatekos, ellenfel)
                        if gyoztes:
                            return gyoztes
                        break

        elif lap.jel_e:
            jelek_szama = len([
                z for z in jatekos.zenit
                if z is not None and not isinstance(z, CsataEgyseg)
            ])

            if jelek_szama >= 2:
                for i in range(6):
                    if jatekos.zenit[i] and not isinstance(jatekos.zenit[i], CsataEgyseg):
                        kidobott = jatekos.zenit[i]
                        jatekos.temeto.append(kidobott)
                        jatekos.zenit[i] = None
                        naplo.ir(f"⚠️ Jel limit: {kidobott.nev} eldobva")
                        break

            for i in range(6):
                if jatekos.zenit[i] is None:
                    if jatekos.fizet(lap):
                        jatekos.kez.remove(lap)
                        jatekos.zenit[i] = lap
                        naplo.ir(f"🪤 {jatekos.nev} Jelet rakott: {lap.nev}")
                        break

        else:
            if jatekos.fizet(lap):
                jatekos.kez.remove(lap)
                jatekos.temeto.append(lap)

                naplo.ir(f"🔮 {jatekos.nev} varázsol: {lap.nev}")

                ellenfel = self.p2 if jatekos == self.p1 else self.p1
                gyoztes = self._alkalmaz_kartya_hatast(lap, jatekos, ellenfel)
                self._resolve_spell_cast_traps(lap, jatekos, ellenfel)
                if gyoztes:
                    return gyoztes

        return None

    def _aktivalhato_burst(self, vedo, p):
        if not p.reakcio_e:
            return

        naplo.ir("✨ Reakció (Burst) aktiválódik")
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
        EffectEngine.trigger_on_play(lap, jatekos, ellenfel)
        return self._ellenoriz_gyoztest()

    def _jelol_harc_overflowot(self, tamado, vedo):
        vedo.jelol_overflow_vereseget(tamado.nev)
        naplo.ir(f"☠️ {tamado.nev} nyert (Overflow)")
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
                naplo.ir(f"✨ {forras} + Gondviselés")
            else:
                naplo.ir("✨ Gondviselés aktiválódott")
        else:
            vedo.kez.append(p)
            if forras:
                naplo.ir(f"💥 {forras}: extra pecsét tört ({p.nev})")
            else:
                naplo.ir(f"💔 Pecsét feltört: {p.nev}")

        if p.reakcio_e and not burst_aktivalt_ebben_a_harcban:
            self._aktivalhato_burst(vedo, p)
            burst_aktivalt_ebben_a_harcban = True

        return True, burst_aktivalt_ebben_a_harcban

    def _resolve_summon_traps(self, summoned_unit, owner, opponent):
        if opponent.hasznalt_jelek_ebben_a_korben >= 2:
            return False

        for index, trap in enumerate(opponent.zenit):
            if trap is None or isinstance(trap, CsataEgyseg):
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
                opponent.zenit[index] = None
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
            if trap is None or isinstance(trap, CsataEgyseg):
                continue

            result = resolve_spell_cast_trap(
                trap,
                varazslat=spell_card,
                jatekos=defender,
                ellenfel=caster,
            )
            if result.get("consume_trap"):
                defender.temeto.append(trap)
                defender.zenit[index] = None
                defender.hasznalt_jelek_ebben_a_korben += 1
                stats.aktivalt_jelek += 1
                return True
        return False

    def _can_direct_attack_exhausted_unit(self, celpont):
        return isinstance(celpont, CsataEgyseg) and celpont.kimerult

    def _attackable_exhausted_unit(self, vedo, lane_index):
        celpont = vedo.horizont[lane_index]
        if self._can_direct_attack_exhausted_unit(celpont):
            return lane_index, celpont
        return None, None

    def _select_direct_attack_target(self, vedo, lane_index):
        lane_unit = vedo.horizont[lane_index]
        lane_zenit = vedo.zenit[lane_index]

        if lane_unit is None and isinstance(lane_zenit, CsataEgyseg):
            return "zenit", lane_index, lane_zenit

        cel_index, celpont = self._attackable_exhausted_unit(vedo, lane_index)
        if celpont is not None:
            return "horizont", cel_index, celpont

        return "seal", None, None

    def harc_fazis(self, tamado, vedo):
        burst_aktivalt_ebben_a_harcban = False
        tamadas_tortent = False

        for i in range(6):
            egyseg = tamado.horizont[i]

            if egyseg and not egyseg.kimerult and not getattr(egyseg, "cannot_attack_until_turn_end", False):
                tamadas_tortent = True
                egyseg.kimerult = True
                trigger_engine.dispatch("on_attack_declared", source=egyseg, owner=tamado, target=vedo, payload={"lane_index": i})
                eredeti_atk = egyseg.akt_tamadas

                if tamado.zenit[i] and isinstance(tamado.zenit[i], CsataEgyseg):
                    hatso = tamado.zenit[i]
                    bonusz = KeywordEngine.get_harmonize_bonus(egyseg, hatso)
                    if bonusz > 0:
                        egyseg.akt_tamadas += bonusz

                naplo.ir(f"--- TÁMADÁS: {egyseg.lap.nev} ({egyseg.akt_tamadas}) ---")

                jel_megallitotta = False
                if vedo.hasznalt_jelek_ebben_a_korben < 2:
                    for j in range(6):
                        if vedo.zenit[j] and not isinstance(vedo.zenit[j], CsataEgyseg):
                            jel = vedo.zenit[j]
                            if not can_activate_trap(jel, tamado_egyseg=egyseg, tamado=tamado, vedo=vedo):
                                continue
                            vedo.zenit[j] = None
                            vedo.temeto.append(jel)

                            vedo.hasznalt_jelek_ebben_a_korben += 1
                            stats.aktivalt_jelek += 1

                            trap_result = EffectEngine.trigger_on_trap(jel, egyseg, tamado, vedo)
                            if isinstance(trap_result, dict) and trap_result.get("stop_attack"):
                                jel_megallitotta = True
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

                    naplo.ir(f"🛡️ Blokkol: {b.lap.nev}")

                    blokkolo_meghalt = False
                    blokkolo_index = vedo.horizont.index(b)

                    if b.serul(egyseg.akt_tamadas):
                        lethal_result = resolve_lethal_trap(owner=vedo, unit=b, attacker=egyseg, zone_name="horizont", index=blokkolo_index)
                        if lethal_result and lethal_result.get("prevented_death"):
                            blokkolo_meghalt = False
                        else:
                            blokkolo_meghalt = self._elpusztit_egyseget(vedo, "horizont", blokkolo_index)

                    KeywordEngine.on_damage_dealt(egyseg, b)

                    if egyseg.serul(b.akt_tamadas):
                        lethal_result = resolve_lethal_trap(owner=tamado, unit=egyseg, attacker=b, zone_name="horizont", index=i)
                        if not (lethal_result and lethal_result.get("prevented_death")):
                            self._elpusztit_egyseget(tamado, "horizont", i)

                    KeywordEngine.on_damage_dealt(b, egyseg)

                    KeywordEngine.resolve_bane(
                        egyseg,
                        b,
                        lambda: self._elpusztit_egyseget(vedo, "horizont", blokkolo_index, "métely")
                    )

                    sundering_result = KeywordEngine.resolve_sundering(
                        egyseg,
                        blokkolo_meghalt,
                        lambda: self._feltor_pecset(vedo, burst_aktivalt_ebben_a_harcban, "Has?t?s")
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

                        naplo.ir(f"🎯 Zenit támadás: {z.lap.nev}")

                        if target_unit.serul(egyseg.akt_tamadas):
                            lethal_result = resolve_lethal_trap(owner=vedo, unit=target_unit, attacker=egyseg, zone_name="zenit", index=target_index)
                            if not (lethal_result and lethal_result.get("prevented_death")):
                                self._elpusztit_egyseget(vedo, "zenit", target_index)

                        KeywordEngine.on_damage_dealt(egyseg, target_unit)

                        if egyseg.serul(target_unit.akt_tamadas):
                            lethal_result = resolve_lethal_trap(owner=tamado, unit=egyseg, attacker=target_unit, zone_name="horizont", index=i)
                            if not (lethal_result and lethal_result.get("prevented_death")):
                                self._elpusztit_egyseget(tamado, "horizont", i)

                        KeywordEngine.on_damage_dealt(target_unit, egyseg)

                        continue

                    if target_kind == "horizont":
                        naplo.ir(f"Kozvetlen tamadas kimerult egysegre: {target_unit.lap.nev}")

                        if target_unit.serul(egyseg.akt_tamadas):
                            lethal_result = resolve_lethal_trap(owner=vedo, unit=target_unit, attacker=egyseg, zone_name="horizont", index=target_index)
                            if not (lethal_result and lethal_result.get("prevented_death")):
                                self._elpusztit_egyseget(vedo, "horizont", target_index)

                        KeywordEngine.on_damage_dealt(egyseg, target_unit)

                        continue

                    pecset_tort, burst_aktivalt_ebben_a_harcban = self._feltor_pecset(
                        vedo, burst_aktivalt_ebben_a_harcban
                    )
                    gyoztes = self._ellenoriz_gyoztest()
                    if gyoztes:
                        return gyoztes

                    if not pecset_tort:
                        return self._jelol_harc_overflowot(tamado, vedo)

                if tamado.horizont[i]:
                    tamado.horizont[i].akt_tamadas = eredeti_atk

        if tamado.kell_tamadnia_kovetkezo_korben and tamadas_tortent:
            tamado.kell_tamadnia_kovetkezo_korben = False

        return None

    def kor_futtatasa(self):
        self.state.kor = self.kor
        naplo.ir(f"\n>>>> {self.kor}. KÖR <<<<")

        for index, (akt, ell) in enumerate([(self.p1, self.p2), (self.p2, self.p1)]):
            akt.uj_kor_inditasa()
            trigger_engine.dispatch("on_turn_start", owner=akt, target=ell, payload={"turn": self.kor})
            trigger_engine.dispatch("on_awakening_phase", owner=akt, target=ell, payload={"turn": self.kor})

            if akt.kell_tamadnia_kovetkezo_korben:
                naplo.ir(f"⚠️ {akt.nev} Kényszerítés/Provoke hatás alatt áll: ha tud, támadnia kell ebben a körben.")

            if self.kor == 1 and index == 0:
                naplo.ir("⚖️ Kezdőjátékos: nem húz és nem támadhat az első körben")
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
                isinstance(e, CsataEgyseg) and not e.kimerult
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
                            naplo.ir(f"✅ {akt.nev} teljesítette a kötelező támadást.")
                    else:
                        naplo.ir(f"ℹ️ {akt.nev} Kényszerítés/Provoke alatt állt, de nem volt támadásra képes Horizont egysége.")

            akt.kor_vegi_heal()
            ell.kor_vegi_heal()
            trigger_engine.dispatch("on_turn_end", owner=akt, target=ell, payload={"turn": self.kor})

        self.kor += 1
        return None
