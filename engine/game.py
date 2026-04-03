import random
from utils.logger import naplo
from stats.analyzer import stats
from engine.player import Jatekos
from engine.card import CsataEgyseg
from engine.effects import EffectEngine
from engine.keywords import KeywordEngine


class AeternaSzimulacio:
    def __init__(self, b1_nev, b2_nev, kartyak):
        self.p1 = Jatekos("Játékos_1", b1_nev, kartyak)
        self.p2 = Jatekos("Játékos_2", b2_nev, kartyak)
        self.kor = 1
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

    def _unit_zone(self, jatekos, zona_nev):
        if zona_nev == "horizont":
            return jatekos.horizont
        if zona_nev == "zenit":
            return jatekos.zenit
        raise ValueError(f"Ismeretlen zona: {zona_nev}")

    def _destroy_unit(self, jatekos, zona_nev, index):
        zona = self._unit_zone(jatekos, zona_nev)
        egyseg = zona[index]

        if isinstance(egyseg, CsataEgyseg):
            jatekos.temeto.append(egyseg.lap)
            zona[index] = None
            return True

        return False

    def _deal_combat_damage(self, tamado_egyseg, vedo_egyseg, sebzes, vedo_jatekos, vedo_zona, vedo_index):
        if tamado_egyseg is None or vedo_egyseg is None:
            return False

        meghalt = vedo_egyseg.serul(sebzes)
        KeywordEngine.on_damage_dealt(tamado_egyseg, vedo_egyseg)

        if meghalt:
            self._destroy_unit(vedo_jatekos, vedo_zona, vedo_index)

        return meghalt

    def kijatszas_fazis(self, jatekos):
        lehetosegek = [
            l for l in jatekos.kez
            if jatekos.elerheto_aura() >= l.aura_koltseg
            and l.magnitudo <= len(jatekos.osforras)
        ]

        if not lehetosegek:
            return None

        lap = random.choice(lehetosegek)

        # 🔹 ENTITÁS
        if lap.egyseg_e:
            zona = jatekos.horizont if random.random() < 0.7 else jatekos.zenit

            for i in range(6):
                if zona[i] is None:
                    if jatekos.fizet(lap):
                        jatekos.kez.remove(lap)
                        zona[i] = CsataEgyseg(lap)
                        stats.faj_statisztika(lap.faj)

                        naplo.ir(f"⚔️ {jatekos.nev} megidézte: {lap.nev}")

                        ellenfel = self.p2 if jatekos == self.p1 else self.p1
                        EffectEngine.trigger_on_play(lap, jatekos, ellenfel)
                        break

        # 🔹 JEL
        elif lap.jel_e:
            jelek_szama = len([
                z for z in jatekos.zenit
                if z is not None and not isinstance(z, CsataEgyseg)
            ])

            # max 2 jel
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

        # 🔹 VARÁZSLAT
        else:
            if jatekos.fizet(lap):
                jatekos.kez.remove(lap)
                jatekos.temeto.append(lap)

                naplo.ir(f"🔮 {jatekos.nev} varázsol: {lap.nev}")

                ellenfel = self.p2 if jatekos == self.p1 else self.p1
                eredmeny = EffectEngine.trigger_on_play(lap, jatekos, ellenfel)

                if eredmeny == "JATEK_VEGE":
                    return jatekos.nev

        return None

    def harc_fazis(self, tamado, vedo):
        for i in range(6):
            egyseg = tamado.horizont[i]

            if egyseg and not egyseg.kimerult:
                egyseg.kimerult = True
                eredeti_atk = egyseg.akt_tamadas

                # 🎶 Harmonizálás
                if tamado.zenit[i] and isinstance(tamado.zenit[i], CsataEgyseg):
                    if "harmonizálás" in tamado.zenit[i].lap.kepesseg.lower():
                        bonusz = tamado.zenit[i].akt_tamadas // 2
                        egyseg.akt_tamadas += bonusz
                        naplo.ir(f"🎶 Harmonizálás +{bonusz} ATK")

                naplo.ir(f"--- TÁMADÁS: {egyseg.lap.nev} ({egyseg.akt_tamadas}) ---")

                # 🔥 CSAPDA
                jel_megallitotta = False
                if vedo.hasznalt_jelek_ebben_a_korben < 2:
                    for j in range(6):
                        if vedo.zenit[j] and not isinstance(vedo.zenit[j], CsataEgyseg):
                            jel = vedo.zenit[j]
                            vedo.zenit[j] = None
                            vedo.temeto.append(jel)

                            vedo.hasznalt_jelek_ebben_a_korben += 1
                            stats.aktivalt_jelek += 1

                            if EffectEngine.trigger_on_trap(jel, egyseg, tamado, vedo):
                                self._destroy_unit(tamado, "horizont", i)
                                jel_megallitotta = True
                            break

                if jel_megallitotta:
                    continue

                # 👻 LÉGIES
                blokkolok = KeywordEngine.get_blockers(vedo)

                if "légies" in egyseg.lap.kepesseg.lower():
                    blokkolok = [
                        e for e in blokkolok
                        if "légies" in e.lap.kepesseg.lower()
                    ]
                    naplo.ir("👻 Csak légies blokkolhat")

                # ⚔️ BLOKK
                if blokkolok:
                    b = random.choice(blokkolok)
                    b.kimerult = True

                    naplo.ir(f"🛡️ Blokkol: {b.lap.nev}")

                    blokkolo_index = vedo.horizont.index(b)

                    self._deal_combat_damage(
                        egyseg, b, egyseg.akt_tamadas,
                        vedo, "horizont", blokkolo_index
                    )

                    self._deal_combat_damage(
                        b, egyseg, b.akt_tamadas,
                        tamado, "horizont", i
                    )

                else:
                    # 🎯 Zenit támadás
                    if vedo.zenit[i] and isinstance(vedo.zenit[i], CsataEgyseg):
                        z = vedo.zenit[i]

                        naplo.ir(f"🎯 Zenit támadás: {z.lap.nev}")

                        self._deal_combat_damage(
                            egyseg, z, egyseg.akt_tamadas,
                            vedo, "zenit", i
                        )

                        self._deal_combat_damage(
                            z, egyseg, z.akt_tamadas,
                            tamado, "horizont", i
                        )

                        continue

                    # 💔 Pecsét
                    if vedo.pecsetek:
                        p = vedo.pecsetek.pop()
                        stats.feltort_pecsetek += 1

                        if p.magnitudo > len(vedo.osforras):
                            vedo.osforras.append({"lap": p, "hasznalt": False})
                            naplo.ir("✨ Gondviselés aktiválódott")
                        else:
                            vedo.kez.append(p)
                            naplo.ir(f"💔 Pecsét feltört: {p.nev}")

                        EffectEngine.trigger_on_burst(p, vedo)

                    else:
                        naplo.ir(f"☠️ {tamado.nev} nyert (Overflow)")
                        return tamado.nev

                # visszaállítás
                if tamado.horizont[i]:
                    tamado.horizont[i].akt_tamadas = eredeti_atk

        return None

    def kor_futtatasa(self):
        naplo.ir(f"\n>>>> {self.kor}. KÖR <<<<")

        for index, (akt, ell) in enumerate([(self.p1, self.p2), (self.p2, self.p1)]):

            akt.aura_visszatoltes()

            if self.kor == 1 and index == 0:
                naplo.ir("⚖️ Kezdő nem húz")
            else:
                akt.huzas()
                akt.huzas()

            akt.osforras_bovites()

            eredmeny = self.kijatszas_fazis(akt)
            if eredmeny:
                return eredmeny

            if not (self.kor == 1 and index == 0):
                eredmeny = self.harc_fazis(akt, ell)
                if eredmeny:
                    return eredmeny

        self.kor += 1
        return None
