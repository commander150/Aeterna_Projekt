import random
from utils.logger import naplo
from engine.card import CsataEgyseg


class Jatekos:
    def __init__(self, nev, birodalom_neve, teljes_kartyatar):
        self.nev = nev
        self.birodalom = birodalom_neve

        # Saját birodalom kártyáinak szűrése
        sajat_lehetosegek = [k for k in teljes_kartyatar if k.birodalom == birodalom_neve]

        if not sajat_lehetosegek:
            sajat_lehetosegek = [
                k for k in teljes_kartyatar
                if k.birodalom in [birodalom_neve, "Aether"]
            ]

        if len(sajat_lehetosegek) < 5:
            raise ValueError(f"Hiba: {birodalom_neve} birodalomhoz nincs elég kártya a paklihoz!")

        # 40 lapos pakli
        self.pakli = []
        elerheto_lapok = sajat_lehetosegek.copy()

        while len(self.pakli) < 40 and elerheto_lapok:
            lap = random.choice(elerheto_lapok)
            if self.pakli.count(lap) < 4:  # Max 4 példány
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

    def huzas(self):
        # Ha üres a pakli, jön az újrakeverés és a büntetés
        if not self.pakli:
            if self.temeto:
                naplo.ir(
                    f"⚠️ {self.nev} paklija elfogyott! Újrakeverés és Büntetés (Refresh Penalty)!"
                )
                self.pakli = self.temeto.copy()
                self.temeto.clear()
                random.shuffle(self.pakli)

                # Büntetés levonása
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
                    return
            else:
                return

        if self.pakli:
            lap = self.pakli.pop()
            self.kez.append(lap)
            naplo.ir(f"{self.nev} húzott: {lap.nev}")

    def osforras_bovites(self):
        if self.kez:
            # A legdrágább lapot teszi le Ősforrásnak
            self.kez.sort(key=lambda k: k.aura_koltseg, reverse=True)
            lap = self.kez.pop(0)
            self.osforras.append({"lap": lap, "hasznalt": False})
            naplo.ir(
                f"🔋 {self.nev} feláldozta Ősforrásnak: {lap.nev} (Költség: {lap.aura_koltseg})"
            )

    def aura_visszatoltes(self):
        for o in self.osforras:
            o["hasznalt"] = False

        for i in range(6):
            if self.horizont[i]:
                self.horizont[i].kimerult = False
            if isinstance(self.zenit[i], CsataEgyseg):
                self.zenit[i].kimerult = False

        self.hasznalt_jelek_ebben_a_korben = 0
        self.rezonancia_aura = 0

    def elerheto_aura(self):
        alap_aura = sum(1 for o in self.osforras if not o["hasznalt"])
        return alap_aura + self.rezonancia_aura

    def fizet(self, lap):
        szabad_kartyak = [o for o in self.osforras if not o["hasznalt"]]
        fennmarado_koltseg = lap.aura_koltseg

        # Rezonancia aura (ha van)
        if self.rezonancia_aura > 0:
            levonas = min(self.rezonancia_aura, fennmarado_koltseg)
            self.rezonancia_aura -= levonas
            fennmarado_koltseg -= levonas

        if fennmarado_koltseg <= 0:
            return True

        # ENTITÁS → sima fizetés
        if lap.egyseg_e:
            if len(szabad_kartyak) >= fennmarado_koltseg:
                for i in range(fennmarado_koltseg):
                    szabad_kartyak[i]["hasznalt"] = True
                return True
            return False

        # VARÁZSLAT / JEL → büntetés logika
        sajat = [o for o in szabad_kartyak if o["lap"].birodalom == lap.birodalom]
        aether = [o for o in szabad_kartyak if o["lap"].birodalom == "Aether"]

        # Elég saját aura
        if len(sajat) >= fennmarado_koltseg:
            for i in range(fennmarado_koltseg):
                sajat[i]["hasznalt"] = True
            return True

        # Enyhe büntetés: +1 költség, ha Aether aurát is bevon
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