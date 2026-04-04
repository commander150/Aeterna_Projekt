from engine.keyword_registry import KeywordRegistry
from utils.text import repair_mojibake


class Kartya:
    def __init__(self, sor_adat):
        self.nev = str(sor_adat[0]) if sor_adat[0] else "Névtelen"
        self.kartyatipus = str(sor_adat[1]) if sor_adat[1] else ""
        self.birodalom = str(sor_adat[2]) if sor_adat[2] else ""
        self.klan = str(sor_adat[3]) if sor_adat[3] else ""
        self.faj = str(sor_adat[4]) if sor_adat[4] else ""
        self.kaszt = str(sor_adat[5]) if sor_adat[5] else ""
        
        def tisztit_szam(v):
            try: return int(float(v)) if v is not None else 0
            except: return 0

        self.magnitudo = tisztit_szam(sor_adat[6])
        self.aura_koltseg = tisztit_szam(sor_adat[7])
        self.tamadas = tisztit_szam(sor_adat[8])
        self.eletero = tisztit_szam(sor_adat[9])
        self.kepesseg = str(sor_adat[10]) if len(sor_adat) > 10 and sor_adat[10] else ""

        self.egyseg_e = "Entitás" in self.kartyatipus
        self.jel_e = "Jel" in self.kartyatipus
        self.reakcio_e = "Reakció" in self.kepesseg or "Burst" in self.kepesseg
    def van_kulcsszo(self, kulcsszo):
        return kulcsszo.lower() in self.kepesseg.lower()

class CsataEgyseg:
    def __init__(self, kartya):
        self.lap = kartya
        self.akt_tamadas = kartya.tamadas
        self.akt_hp = kartya.eletero
        self.kimerult = True
        self.bane_target = False
        
        if "Gyorsaság" in kartya.kepesseg or "Celerity" in kartya.kepesseg:
            self.kimerult = False

    def serul(self, mennyiseg):
        self.akt_hp -= mennyiseg
        return self.akt_hp <= 0
