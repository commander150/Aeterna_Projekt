import random
from utils.logger import naplo
from engine.card import CsataEgyseg


class Jatekos:
    def __init__(self, nev, birodalom_neve, teljes_kartyatar):
        self.nev = nev
        self.birodalom = birodalom_neve

        sajat_lehetosegek = [k for k in teljes_kartyatar if k.birodalom == birodalom_neve]

        if not sajat_lehetosegek:
            sajat_lehetosegek = [
                k for k in teljes_kartyatar
                if k.birodalom in [birodalom_neve, "Aether"]
            ]

        if len(sajat_lehetosegek) < 5:
            raise ValueError(f"Hiba: {birodalom_neve} birodalomhoz nincs elég kártya a paklihoz!")

        self.pakli = []
        elerheto_lapok = sajat_lehetosegek.copy()

        while len(self.pakli) < 40 and elerheto_lapok:
            lap = random.choice(elerheto_lapok)
            if self.pakli.count(lap) < 4:
                self.pakli.append(lap)
            else:
                elerheto_lapok.remove(lap)

        random.shuffle(self.pakli)

        self.kez = []
        self.pecsetek = []
        self.osforras = []
        self.temeto = []
        self.horizont = [None] * 6
        self.zenit = [None] * 6

        self.hasznalt_jelek_ebben_a_korben = 0
        self.rezonancia_aura = 0

        # körönkénti limitek
        self.extra_huzas_ebben_a_korben = 0
        self.ideiglenes_aura_ebben_a_korben = 0
        self.ujraaktivalt_egysegek_ebben_a_korben = 0

        # anti-stall / provoke előkészítés
        self.kell_tamadnia_kovetkezo_korben = False
        self.overflow_vereseg = False
        self.overflow_gyoztes_nev = None

    def jelol_overflow_vereseget(self, gyoztes_nev):
        self.overflow_vereseg = True
        self.overflow_gyoztes_nev = gyoztes_nev

    def uj_kor_inditasa(self):
        for o in self.osforras:
            o["hasznalt"] = False

        for i in range(6):
            if isinstance(self.horizont[i], CsataEgyseg):
                self.horizont[i].kimerult = False
            if isinstance(self.zenit[i], CsataEgyseg):
                self.zenit[i].kimerult = False

        self.hasznalt_jelek_ebben_a_korben = 0
        self.rezonancia_aura = 0
        self.extra_huzas_ebben_a_korben = 0
        self.ideiglenes_aura_ebben_a_korben = 0
        self.ujraaktivalt_egysegek_ebben_a_korben = 0

    def kor_vegi_heal(self):
        for e in self.horizont:
            if isinstance(e, CsataEgyseg):
                e.akt_hp = e.lap.eletero

        for e in self.zenit:
            if isinstance(e, CsataEgyseg):
                e.akt_hp = e.lap.eletero

    def huzas(self, extra=False):
        if extra and self.extra_huzas_ebben_a_korben >= 3:
            naplo.ir(f"⛔ {self.nev} nem húzhat több extra lapot ebben a körben.")
            return False

        if not self.pakli:
            if self.temeto:
                naplo.ir(
                    f"⚠️ {self.nev} paklija elfogyott! Újrakeverés és Büntetés (Refresh Penalty)!"
                )
                self.pakli = self.temeto.copy()
                self.temeto.clear()
                random.shuffle(self.pakli)

                if self.pecsetek:
                    elvesztett = self.pecsetek.pop()
                    self.temeto.append(elvesztett)
                    naplo.ir(
                        f"💀 BÜNTETÉS: {self.nev} elvesztett egy Pecsétet ({elvesztett.nev})!"
                    )
                else:
                    naplo.ir(
                        f"💀 BÜNTETÉS: {self.nev}-nak nincs több Pecsétje a feláldozásra!"
                    )
                    return False
            else:
                return False

        if self.pakli:
            lap = self.pakli.pop()
            self.kez.append(lap)
            naplo.ir(f"📜 {self.nev} húzott: {lap.nev}")

            if extra:
                self.extra_huzas_ebben_a_korben += 1

            return True

        return False

    def ad_ideiglenes_aurat(self, mennyiseg, forras="hatás"):
        if mennyiseg <= 0:
            return 0

        maradek = max(0, 2 - self.ideiglenes_aura_ebben_a_korben)
        tenyleges = min(mennyiseg, maradek)

        if tenyleges <= 0:
            naplo.ir(f"⛔ {self.nev} nem kaphat több ideiglenes aurát ebben a körben ({forras}).")
            return 0

        self.rezonancia_aura += tenyleges
        self.ideiglenes_aura_ebben_a_korben += tenyleges

        if tenyleges < mennyiseg:
            naplo.ir(
                f"⛔ {self.nev} ideiglenes aura limitje miatt csak {tenyleges}/{mennyiseg} aura jött létre ({forras})."
            )
        else:
            naplo.ir(f"✨ {self.nev} {tenyleges} ideiglenes aurát kapott ({forras}).")

        return tenyleges

    def ujraaktivalt_egyseget(self, egyseg, forras="hatás"):
        if not isinstance(egyseg, CsataEgyseg):
            return False

        if self.ujraaktivalt_egysegek_ebben_a_korben >= 2:
            naplo.ir(f"⛔ {self.nev} nem aktiválhat újra több egységet ebben a körben ({forras}).")
            return False

        if not egyseg.kimerult:
            return False

        egyseg.kimerult = False
        self.ujraaktivalt_egysegek_ebben_a_korben += 1
        naplo.ir(f"✨ {self.nev} újraaktiválta {egyseg.lap.nev} egységet ({forras}).")
        return True

    def osforras_bovites(self):
        if self.kez:
            self.kez.sort(key=lambda k: k.aura_koltseg, reverse=True)
            lap = self.kez.pop(0)
            self.osforras.append({"lap": lap, "hasznalt": False})
            naplo.ir(f"🔋 {self.nev} Ősforrást bővített: {lap.nev}")

    def elerheto_aura(self):
        alap_aura = sum(
            1 for o in self.osforras
            if isinstance(o, dict) and not o.get("hasznalt", False)
        )
        return alap_aura + self.rezonancia_aura

    def fizet(self, lap):
        szabad_kartyak = [
            o for o in self.osforras
            if isinstance(o, dict) and not o.get("hasznalt", False)
        ]
        fennmarado_koltseg = lap.aura_koltseg

        if self.rezonancia_aura > 0:
            levonas = min(self.rezonancia_aura, fennmarado_koltseg)
            self.rezonancia_aura -= levonas
            fennmarado_koltseg -= levonas

        if fennmarado_koltseg <= 0:
            return True

        if lap.egyseg_e:
            if len(szabad_kartyak) >= fennmarado_koltseg:
                for i in range(fennmarado_koltseg):
                    szabad_kartyak[i]["hasznalt"] = True
                return True
            return False

        sajat = [o for o in szabad_kartyak if o["lap"].birodalom == lap.birodalom]
        aether = [o for o in szabad_kartyak if o["lap"].birodalom == "Aether"]

        if len(sajat) >= fennmarado_koltseg:
            for i in range(fennmarado_koltseg):
                sajat[i]["hasznalt"] = True
            return True

        buntetett = fennmarado_koltseg + 1

        if len(sajat) + len(aether) >= buntetett:
            naplo.ir("⚠️ Enyhe Büntetés aktiválódott (+1 költség)")
            hatra = buntetett

            for o in sajat:
                if hatra > 0:
                    o["hasznalt"] = True
                    hatra -= 1

            for o in aether:
                if hatra > 0:
                    o["hasznalt"] = True
                    hatra -= 1

            return True

        return False
