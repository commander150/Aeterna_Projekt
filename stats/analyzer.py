from utils.logger import naplo

class Statisztika:
    def __init__(self):
        self.jatekok_szama = 0
        self.p1_gyozelem = 0
        self.p2_gyozelem = 0
        self.osszes_kor = 0
        self.kijatszott_fajok = {}
        self.feltort_pecsetek = 0
        self.aktivalt_jelek = 0
        self.fel_nem_oldott_effektek = {
            "on_play": {},
            "trap": {},
            "burst": {},
            "death": {},
        }

    def faj_statisztika(self, faj):
        if not faj or faj == "None" or faj == "-": return
        self.kijatszott_fajok[faj] = self.kijatszott_fajok.get(faj, 0) + 1

    def rogzit_fel_nem_oldott_effektet(self, kategoria, kartya_nev, effekt_szoveg, allapot="tenylegesen_hianyzo"):
        if kategoria not in self.fel_nem_oldott_effektek:
            self.fel_nem_oldott_effektek[kategoria] = {}

        tisztitott_szoveg = (effekt_szoveg or "").strip() or "-"
        kulcs = (kartya_nev or "Ismeretlen lap", tisztitott_szoveg, allapot)
        kategoriak = self.fel_nem_oldott_effektek[kategoria]
        kategoriak[kulcs] = kategoriak.get(kulcs, 0) + 1

    def _kiir_fel_nem_oldott_effekteket(self):
        naplo.ir("\nFel nem oldott effektek:")

        kategoriak = [
            ("on_play", "On Play"),
            ("trap", "Trap"),
            ("burst", "Burst"),
            ("death", "Death"),
        ]

        for kategoria_kulcs, cimke in kategoriak:
            tetelek = self.fel_nem_oldott_effektek.get(kategoria_kulcs, {})
            naplo.ir(f"  [{cimke}]")

            if not tetelek:
                naplo.ir("    - nincs feljegyzett fel nem oldott effekt")
                continue

            rendezett = sorted(
                tetelek.items(),
                key=lambda adat: (-adat[1], adat[0][0], adat[0][1]),
            )
            for (kartya_nev, effekt_szoveg, allapot), db in rendezett:
                naplo.ir(f"    - {db}x | {allapot} | {kartya_nev} | {effekt_szoveg}")

    def osszesites_mentese(self):
        naplo.ir("\n" + "="*40)
        naplo.ir("VÉGSŐ SZIMULÁCIÓS STATISZTIKA")
        naplo.ir("="*40)
        naplo.ir(f"Összes lejátszott meccs: {self.jatekok_szama}")
        naplo.ir(f"P1 győzelmi arány: {(self.p1_gyozelem/max(1,self.jatekok_szama))*100:.1f}%")
        naplo.ir(f"P2 győzelmi arány: {(self.p2_gyozelem/max(1,self.jatekok_szama))*100:.1f}%")
        naplo.ir(f"Átlagos körszám: {self.osszes_kor/max(1,self.jatekok_szama):.2f}")
        naplo.ir(f"Összes aktivált Jel: {self.aktivalt_jelek}")
        naplo.ir(f"Összes feltört Pecsét: {self.feltort_pecsetek}")
        naplo.ir("\nLeggyakrabban kijátszott fajok:")
        
        rendezett_fajok = sorted(self.kijatszott_fajok.items(), key=lambda x: x[1], reverse=True)
        for faj, db in rendezett_fajok[:10]:
            naplo.ir(f"  - {faj}: {db} db")
        self._kiir_fel_nem_oldott_effekteket()
        naplo.ir("="*40)

# Globális statisztika példány
stats = Statisztika()
