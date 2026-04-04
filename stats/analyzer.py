from utils.logger import naplo


class Statisztika:
    def __init__(self):
        self.jatekok_szama = 0
        self.p1_gyozelem = 0
        self.p2_gyozelem = 0
        self.dontetlen = 0
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
        self.structured_metrics = {
            "attempted": 0,
            "resolved": 0,
            "partial": 0,
            "fallback": 0,
            "unresolved": 0,
        }

    def faj_statisztika(self, faj):
        if not faj or faj == "None" or faj == "-":
            return
        self.kijatszott_fajok[faj] = self.kijatszott_fajok.get(faj, 0) + 1

    def rogzit_fel_nem_oldott_effektet(self, kategoria, kartya_nev, effekt_szoveg, allapot="tenylegesen_hianyzo"):
        if kategoria not in self.fel_nem_oldott_effektek:
            self.fel_nem_oldott_effektek[kategoria] = {}

        tisztitott_szoveg = (effekt_szoveg or "").strip() or "-"
        kulcs = (kartya_nev or "Ismeretlen lap", tisztitott_szoveg, allapot)
        kategoriak = self.fel_nem_oldott_effektek[kategoria]
        kategoriak[kulcs] = kategoriak.get(kulcs, 0) + 1

    def rogzit_structured_kimenetet(self, statusz):
        if statusz not in self.structured_metrics:
            return
        self.structured_metrics[statusz] += 1

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

    def rogzit_meccs_eredmenyt(self, nyertes):
        if nyertes is None:
            self.dontetlen += 1
            return "dontetlen"

        nyertes_nev = getattr(nyertes, "nev", nyertes)
        if nyertes_nev == "Jatekos_1":
            self.p1_gyozelem += 1
            return "p1"
        if nyertes_nev == "Jatekos_2":
            self.p2_gyozelem += 1
            return "p2"

        naplo.ir(f"[DEBUG:UNKNOWN_WINNER] {nyertes_nev}")
        self.dontetlen += 1
        return "ismeretlen"

    def osszesites_mentese(self):
        osszes_meccs = max(1, self.jatekok_szama)
        naplo.ir("\n" + "=" * 40)
        naplo.ir("VEGSO SZIMULACIOS STATISZTIKA")
        naplo.ir("=" * 40)
        naplo.ir(f"Osszes lejatszott meccs: {self.jatekok_szama}")
        naplo.ir(f"P1 gyozelmi arany: {(self.p1_gyozelem / osszes_meccs) * 100:.1f}%")
        naplo.ir(f"P2 gyozelmi arany: {(self.p2_gyozelem / osszes_meccs) * 100:.1f}%")
        naplo.ir(f"Dontetlen arany: {(self.dontetlen / osszes_meccs) * 100:.1f}%")
        naplo.ir(f"Atlagos korszam: {self.osszes_kor / osszes_meccs:.2f}")
        naplo.ir(f"Osszes aktivalt Jel: {self.aktivalt_jelek}")
        naplo.ir(f"Osszes feltort Pecset: {self.feltort_pecsetek}")
        naplo.ir("\nLeggyakrabban kijatszott fajok:")

        rendezett_fajok = sorted(self.kijatszott_fajok.items(), key=lambda x: x[1], reverse=True)
        for faj, db in rendezett_fajok[:10]:
            naplo.ir(f"  - {faj}: {db} db")
        self._kiir_fel_nem_oldott_effekteket()
        naplo.ir("\nStructured resolver osszegzes:")
        naplo.ir(f"  - structured probalkozasok: {self.structured_metrics['attempted']}")
        naplo.ir(f"  - teljes structured feloldas: {self.structured_metrics['resolved']}")
        naplo.ir(f"  - reszleges structured feloldas: {self.structured_metrics['partial']}")
        naplo.ir(f"  - text fallbackre esett: {self.structured_metrics['fallback']}")
        naplo.ir(f"  - unresolved maradt: {self.structured_metrics['unresolved']}")
        naplo.ir("=" * 40)


stats = Statisztika()
