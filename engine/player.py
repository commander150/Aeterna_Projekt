import random
from utils.logger import naplo
from engine.card import CsataEgyseg
from engine.board_utils import is_entity, is_zenit_entity


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
            raise ValueError(f"Hiba: {birodalom_neve} birodalomhoz nincs eleg kartya a paklihoz!")

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

        self.extra_huzas_ebben_a_korben = 0
        self.ideiglenes_aura_ebben_a_korben = 0
        self.ujraaktivalt_egysegek_ebben_a_korben = 0

        self.kell_tamadnia_kovetkezo_korben = False
        self.overflow_vereseg = False
        self.overflow_gyoztes_nev = None
        self.sik_aurabonusz = 0
        self.kovetkezo_jel_kedvezmeny = 0
        self.kovetkezo_gepezet_kedvezmeny = 0
        self.kovetkezo_entitas_kedvezmeny = 0
        self.kovetkezo_kor_ideiglenes_aura = 0
        self.megidezett_entitasok_ebben_a_korben = 0
        self.tomegtermeles_gyara_triggerelt_ebben_a_korben = False
        self.vamszedo_pont_figyelo = None

    def jelol_overflow_vereseget(self, gyoztes_nev):
        self.overflow_vereseg = True
        self.overflow_gyoztes_nev = gyoztes_nev

    def uj_kor_inditasa(self):
        for o in self.osforras:
            o["hasznalt"] = False

        for i in range(6):
            if is_entity(self.horizont[i]):
                if getattr(self.horizont[i], "extra_exhausted_turns", 0) > 0:
                    self.horizont[i].extra_exhausted_turns -= 1
                    self.horizont[i].kimerult = True
                else:
                    self.horizont[i].kimerult = False
                self.horizont[i].cannot_attack_until_turn_end = False
                self.horizont[i].cannot_block_until_turn_end = False
                self.horizont[i].protect_keywords_until_turn_end = False
                self.horizont[i].protect_atk_from_enemy_until_turn_end = False
                self.horizont[i]._first_combat_survived_emitted = False
            if is_zenit_entity(self.zenit[i]):
                if getattr(self.zenit[i], "extra_exhausted_turns", 0) > 0:
                    self.zenit[i].extra_exhausted_turns -= 1
                    self.zenit[i].kimerult = True
                else:
                    self.zenit[i].kimerult = False
                self.zenit[i].cannot_attack_until_turn_end = False
                self.zenit[i].cannot_block_until_turn_end = False
                self.zenit[i].protect_keywords_until_turn_end = False
                self.zenit[i].protect_atk_from_enemy_until_turn_end = False
                self.zenit[i]._first_combat_survived_emitted = False

        self.hasznalt_jelek_ebben_a_korben = 0
        self.rezonancia_aura = 0
        self.extra_huzas_ebben_a_korben = 0
        self.ideiglenes_aura_ebben_a_korben = 0
        self.ujraaktivalt_egysegek_ebben_a_korben = 0
        self.megidezett_entitasok_ebben_a_korben = 0
        self.tomegtermeles_gyara_triggerelt_ebben_a_korben = False

    def kor_vegi_heal(self):
        for e in self.horizont:
            if is_entity(e):
                e.akt_hp = e.lap.eletero + getattr(e, "bonus_max_hp", 0)

        for e in self.zenit:
            if is_zenit_entity(e):
                e.akt_hp = e.lap.eletero + getattr(e, "bonus_max_hp", 0)

    def effektiv_aura_koltseg(self, lap):
        koltseg = lap.aura_koltseg
        if getattr(lap, "jel_e", False) and self.kovetkezo_jel_kedvezmeny > 0:
            koltseg = max(0, koltseg - 1)
        if getattr(lap, "egyseg_e", False) and self.kovetkezo_gepezet_kedvezmeny > 0:
            faj = getattr(lap, "faj", "").lower()
            if "gepezet" in faj:
                koltseg = max(0, koltseg - 1)
        if getattr(lap, "egyseg_e", False) and self.kovetkezo_entitas_kedvezmeny > 0:
            koltseg = max(0, koltseg - self.kovetkezo_entitas_kedvezmeny)
        return koltseg

    def huzas(self, extra=False, trigger_watch=True):
        if extra and self.extra_huzas_ebben_a_korben >= 3:
            naplo.ir(f"{self.nev} nem huzhat tobb extra lapot ebben a korben.")
            return False

        if not self.pakli:
            if self.temeto:
                naplo.ir(f"{self.nev} paklija elfogyott! Ujrakeveres es buntetes (Refresh Penalty)!")
                self.pakli = self.temeto.copy()
                self.temeto.clear()
                random.shuffle(self.pakli)

                if self.pecsetek:
                    elvesztett = self.pecsetek.pop()
                    self.temeto.append(elvesztett)
                    naplo.ir(f"BUNTETES: {self.nev} elvesztett egy Pecsetet ({elvesztett.nev})!")
                else:
                    naplo.ir(f"BUNTETES: {self.nev}-nak nincs tobb Pecsetje a felaldozasra!")
                    return False
            else:
                return False

        if self.pakli:
            lap = self.pakli.pop()
            self.kez.append(lap)
            naplo.ir(f"{self.nev} huzott: {lap.nev}")

            if extra:
                self.extra_huzas_ebben_a_korben += 1
                if trigger_watch and self.vamszedo_pont_figyelo is not None:
                    try:
                        self.vamszedo_pont_figyelo.huzas(extra=True, trigger_watch=False)
                        naplo.ir(
                            f"Vamszedo Pont: {getattr(self.vamszedo_pont_figyelo, 'nev', 'ismeretlen')} is huzott, mert {self.nev} normal huzasi fazison kivul lapot huzott."
                        )
                    except Exception:
                        pass

            return True

        return False

    def ad_ideiglenes_aurat(self, mennyiseg, forras="hatas"):
        if mennyiseg <= 0:
            return 0

        maradek = max(0, 2 - self.ideiglenes_aura_ebben_a_korben)
        tenyleges = min(mennyiseg, maradek)

        if tenyleges <= 0:
            naplo.ir(f"{self.nev} nem kaphat tobb ideiglenes aurat ebben a korben ({forras}).")
            return 0

        self.rezonancia_aura += tenyleges
        self.ideiglenes_aura_ebben_a_korben += tenyleges

        if tenyleges < mennyiseg:
            naplo.ir(f"{self.nev} ideiglenes aura limitje miatt csak {tenyleges}/{mennyiseg} aura jott letre ({forras}).")
        else:
            naplo.ir(f"{self.nev} {tenyleges} ideiglenes aurat kapott ({forras}).")

        return tenyleges

    def ujraaktivalt_egyseget(self, egyseg, forras="hatas"):
        if not isinstance(egyseg, CsataEgyseg):
            return False

        if self.ujraaktivalt_egysegek_ebben_a_korben >= 2:
            naplo.ir(f"{self.nev} nem aktivalhat ujra tobb egyseget ebben a korben ({forras}).")
            return False

        if not egyseg.kimerult:
            return False

        egyseg.kimerult = False
        self.ujraaktivalt_egysegek_ebben_a_korben += 1
        naplo.ir(f"{self.nev} ujraaktivalta {egyseg.lap.nev} egyseget ({forras}).")
        return True

    def osforras_bovites(self):
        if self.kez:
            self.kez.sort(key=lambda k: k.aura_koltseg, reverse=True)
            lap = self.kez.pop(0)
            self.osforras.append({"lap": lap, "hasznalt": False})
            naplo.ir(f"{self.nev} Osforrast bovitett: {lap.nev}")

    def elerheto_aura(self):
        alap_aura = sum(
            1 for o in self.osforras
            if isinstance(o, dict) and not o.get("hasznalt", False)
        )
        return alap_aura + self.rezonancia_aura + self.sik_aurabonusz

    def _fogyaszt_kedvezmenyeket(self, lap):
        if getattr(lap, "jel_e", False) and self.kovetkezo_jel_kedvezmeny > 0:
            self.kovetkezo_jel_kedvezmeny -= 1
            naplo.ir(f"{self.nev} felhasznalta a kovetkezo Jel kedvezmenyt.")
        if getattr(lap, "egyseg_e", False) and self.kovetkezo_gepezet_kedvezmeny > 0:
            faj = getattr(lap, "faj", "").lower()
            if "gepezet" in faj:
                self.kovetkezo_gepezet_kedvezmeny -= 1
                naplo.ir(f"{self.nev} felhasznalta a kovetkezo Gepezet kedvezmenyt.")
        if getattr(lap, "egyseg_e", False) and self.kovetkezo_entitas_kedvezmeny > 0:
            naplo.ir(f"{self.nev} felhasznalta a kovetkezo Entitas kedvezmenyt ({self.kovetkezo_entitas_kedvezmeny}).")
            self.kovetkezo_entitas_kedvezmeny = 0

    def fizet(self, lap):
        szabad_kartyak = [
            o for o in self.osforras
            if isinstance(o, dict) and not o.get("hasznalt", False)
        ]
        fennmarado_koltseg = self.effektiv_aura_koltseg(lap)

        if self.rezonancia_aura > 0:
            levonas = min(self.rezonancia_aura, fennmarado_koltseg)
            self.rezonancia_aura -= levonas
            fennmarado_koltseg -= levonas

        if fennmarado_koltseg <= 0:
            self._fogyaszt_kedvezmenyeket(lap)
            return True

        if lap.egyseg_e:
            if len(szabad_kartyak) >= fennmarado_koltseg:
                for i in range(fennmarado_koltseg):
                    szabad_kartyak[i]["hasznalt"] = True
                self._fogyaszt_kedvezmenyeket(lap)
                return True
            return False

        sajat = [o for o in szabad_kartyak if o["lap"].birodalom == lap.birodalom]
        aether = [o for o in szabad_kartyak if o["lap"].birodalom == "Aether"]

        if len(sajat) >= fennmarado_koltseg:
            for i in range(fennmarado_koltseg):
                sajat[i]["hasznalt"] = True
            self._fogyaszt_kedvezmenyeket(lap)
            return True

        buntetett = fennmarado_koltseg + 1

        if len(sajat) + len(aether) >= buntetett:
            naplo.ir("Enyhe buntetes aktivalodott (+1 koltseg)")
            hatra = buntetett

            for o in sajat:
                if hatra > 0:
                    o["hasznalt"] = True
                    hatra -= 1

            for o in aether:
                if hatra > 0:
                    o["hasznalt"] = True
                    hatra -= 1

            self._fogyaszt_kedvezmenyeket(lap)
            return True

        return False
