import random
from utils.logger import naplo
from stats.analyzer import stats
from engine.player import Jatekos
from engine.card import CsataEgyseg
from engine.effects import EffectEngine


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

    def kijatszas_fazis(self, jatekos):
        lehetosegek = [
            l for l in jatekos.kez
            if jatekos.elerheto_aura() >= l.aura_koltseg
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
                        stats.faj_statisztika(lap.faj)
                        naplo.ir(f"⚔️ {jatekos.nev} megidézte: {lap.nev}")

                        ellenfel = self.p2 if jatekos == self.p1 else self.p1
                        EffectEngine.trigger_on_play(lap, jatekos, ellenfel)
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
                eredmeny = EffectEngine.trigger_on_play(lap, jatekos, ellenfel)

                if eredmeny == "JATEK_VEGE":
                    return jatekos.nev

        return None

    def _aktivalhato_burst(self, vedo, p):
        if not p.reakcio_e:
            return

        naplo.ir("✨ Reakció (Burst) aktiválódik")
        tamado = self.p1 if vedo == self.p2 else self.p2
        EffectEngine.trigger_on_burst(p, vedo, tamado)

    def harc_fazis(self, tamado, vedo):
        burst_aktivalt_ebben_a_harcban = False
        tamadas_tortent = False

        for i in range(6):
            egyseg = tamado.horizont[i]

            if egyseg and not egyseg.kimerult:
                tamadas_tortent = True
                egyseg.kimerult = True
                eredeti_atk = egyseg.akt_tamadas

                if tamado.zenit[i] and isinstance(tamado.zenit[i], CsataEgyseg):
                    hatso = tamado.zenit[i]
                    if "harmonizálás" in hatso.lap.kepesseg.lower():
                        if hatso.lap.magnitudo <= 4:
                            bonusz = 2
                        elif hatso.lap.magnitudo <= 8:
                            bonusz = 1
                        else:
                            bonusz = 0

                        if bonusz > 0:
                            egyseg.akt_tamadas += bonusz
                            naplo.ir(f"🎶 Harmonizálás +{bonusz} ATK")

                naplo.ir(f"--- TÁMADÁS: {egyseg.lap.nev} ({egyseg.akt_tamadas}) ---")

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
                                tamado.temeto.append(egyseg.lap)
                                tamado.horizont[i] = None
                                jel_megallitotta = True
                            break

                if jel_megallitotta:
                    continue

                blokkolok = [e for e in vedo.horizont if e and not e.kimerult]

                if "légies" in egyseg.lap.kepesseg.lower():
                    blokkolok = [
                        e for e in blokkolok
                        if "légies" in e.lap.kepesseg.lower()
                    ]
                    naplo.ir("👻 Csak légies blokkolhat")

                if blokkolok:
                    b = random.choice(blokkolok)
                    b.kimerult = True

                    naplo.ir(f"🛡️ Blokkol: {b.lap.nev}")

                    blokkolo_meghalt = False

                    if b.serul(egyseg.akt_tamadas):
                        vedo.temeto.append(b.lap)
                        vedo.horizont[vedo.horizont.index(b)] = None
                        blokkolo_meghalt = True

                    if egyseg.serul(b.akt_tamadas):
                        tamado.temeto.append(egyseg.lap)
                        tamado.horizont[i] = None

                    if "métely" in egyseg.lap.kepesseg.lower() and not blokkolo_meghalt:
                        vedo.temeto.append(b.lap)
                        idx = vedo.horizont.index(b)
                        vedo.horizont[idx] = None
                        naplo.ir(f"☠️ Métely: {b.lap.nev} a fázis végéig elpusztul")

                    if "hasítás" in egyseg.lap.kepesseg.lower() and blokkolo_meghalt:
                        if vedo.pecsetek:
                            plusz = vedo.pecsetek.pop()
                            stats.feltort_pecsetek += 1

                            if plusz.magnitudo > len(vedo.osforras):
                                vedo.osforras.append({"lap": plusz, "hasznalt": False})
                                naplo.ir("✨ Hasítás + Gondviselés")
                            else:
                                vedo.kez.append(plusz)
                                naplo.ir(f"💥 Hasítás: extra pecsét tört ({plusz.nev})")

                            if plusz.reakcio_e and not burst_aktivalt_ebben_a_harcban:
                                self._aktivalhato_burst(vedo, plusz)
                                burst_aktivalt_ebben_a_harcban = True

                else:
                    if vedo.zenit[i] and isinstance(vedo.zenit[i], CsataEgyseg):
                        z = vedo.zenit[i]

                        naplo.ir(f"🎯 Zenit támadás: {z.lap.nev}")

                        if z.serul(egyseg.akt_tamadas):
                            vedo.temeto.append(z.lap)
                            vedo.zenit[i] = None

                        if egyseg.serul(z.akt_tamadas):
                            tamado.temeto.append(egyseg.lap)
                            tamado.horizont[i] = None

                        continue

                    if vedo.pecsetek:
                        p = vedo.pecsetek.pop()
                        stats.feltort_pecsetek += 1

                        if p.magnitudo > len(vedo.osforras):
                            vedo.osforras.append({"lap": p, "hasznalt": False})
                            naplo.ir("✨ Gondviselés aktiválódott")
                        else:
                            vedo.kez.append(p)
                            naplo.ir(f"💔 Pecsét feltört: {p.nev}")

                        if p.reakcio_e and not burst_aktivalt_ebben_a_harcban:
                            self._aktivalhato_burst(vedo, p)
                            burst_aktivalt_ebben_a_harcban = True

                    else:
                        naplo.ir(f"☠️ {tamado.nev} nyert (Overflow)")
                        return tamado.nev

                if tamado.horizont[i]:
                    tamado.horizont[i].akt_tamadas = eredeti_atk

        if tamado.kell_tamadnia_kovetkezo_korben and tamadas_tortent:
            tamado.kell_tamadnia_kovetkezo_korben = False

        return None

    def kor_futtatasa(self):
        naplo.ir(f"\n>>>> {self.kor}. KÖR <<<<")

        for index, (akt, ell) in enumerate([(self.p1, self.p2), (self.p2, self.p1)]):
            akt.uj_kor_inditasa()

            if self.kor == 1 and index == 0:
                naplo.ir("⚖️ Kezdőjátékos: nem húz és nem támadhat az első körben")
            else:
                akt.huzas()
                akt.huzas()

            akt.osforras_bovites()

            eredmeny = self.kijatszas_fazis(akt)
            if eredmeny:
                akt.kor_vegi_heal()
                ell.kor_vegi_heal()
                return eredmeny

            kotelezo_tamadas = akt.kell_tamadnia_kovetkezo_korben

            if not (self.kor == 1 and index == 0):
                eredmeny = self.harc_fazis(akt, ell)
                if eredmeny:
                    akt.kor_vegi_heal()
                    ell.kor_vegi_heal()
                    return eredmeny

                if kotelezo_tamadas:
                    tud_tamadni = any(
                        isinstance(e, CsataEgyseg) and not e.kimerult
                        for e in akt.horizont
                    )
                    if tud_tamadni:
                        akt.kell_tamadnia_kovetkezo_korben = False

            akt.kor_vegi_heal()
            ell.kor_vegi_heal()

        self.kor += 1
        return None