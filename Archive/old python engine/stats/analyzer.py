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
        self.effect_outcomes = {
            "on_play": {},
            "trap": {},
            "burst": {},
            "death": {},
        }
        self.structured_metrics = {
            "attempted": 0,
            "resolved": 0,
            "partial": 0,
            "deferred": 0,
            "passive": 0,
            "not_applicable": 0,
            "fallback": 0,
            "runtime_supported": 0,
            "legacy_supported": 0,
            "trap_consumed_only": 0,
            "trap_resolved": 0,
            "trap_partial": 0,
            "trap_missing": 0,
            "missing": 0,
        }
        self.outcome_precedence = {
            "resolved": 100,
            "trap_resolved": 98,
            "runtime_supported": 95,
            "legacy_supported": 92,
            "fallback_text_resolved": 90,
            "partial": 80,
            "structured_partial": 80,
            "trap_partial": 78,
            "deferred": 70,
            "structured_deferred": 70,
            "passive_static_applied": 60,
            "passive_static_ignored": 55,
            "static_not_explicitly_simulated": 50,
            "trap_consumed_only": 45,
            "not_applicable": 40,
            "trap_missing": 20,
            "missing": 10,
            "missing_implementation": 10,
        }

    def faj_statisztika(self, faj):
        if not faj or faj == "None" or faj == "-":
            return
        self.kijatszott_fajok[faj] = self.kijatszott_fajok.get(faj, 0) + 1

    def rogzit_effekt_kimenetet(self, kategoria, kartya_nev, effekt_szoveg, allapot):
        if kategoria not in self.effect_outcomes:
            self.effect_outcomes[kategoria] = {}

        tisztitott_szoveg = (effekt_szoveg or "").strip() or "-"
        kulcs = (kartya_nev or "Ismeretlen lap", tisztitott_szoveg)
        kategoriak = self.effect_outcomes[kategoria]
        adat = kategoriak.get(kulcs, {"status": allapot, "db": 0})
        aktualis = adat.get("status", allapot)
        if self.outcome_precedence.get(allapot, 0) >= self.outcome_precedence.get(aktualis, 0):
            adat["status"] = allapot
        adat["db"] = adat.get("db", 0) + 1
        kategoriak[kulcs] = adat

    def rogzit_fel_nem_oldott_effektet(self, kategoria, kartya_nev, effekt_szoveg, allapot="tenylegesen_hianyzo"):
        self.rogzit_effekt_kimenetet(kategoria, kartya_nev, effekt_szoveg, allapot)

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
            tetelek = self.effect_outcomes.get(kategoria_kulcs, {})
            naplo.ir(f"  [{cimke}]")

            if not tetelek:
                naplo.ir("    - nincs feljegyzett fel nem oldott effekt")
                continue

            rendezett = sorted(
                tetelek.items(),
                key=lambda adat: (-adat[1]["db"], adat[0][0], adat[0][1]),
            )
            for (kartya_nev, effekt_szoveg), adat in rendezett:
                naplo.ir(f"    - {adat['db']}x | {adat['status']} | {kartya_nev} | {effekt_szoveg}")

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
        runtime_mukodott = (
            self.structured_metrics["resolved"]
            + self.structured_metrics["partial"]
            + self.structured_metrics["fallback"]
            + self.structured_metrics["runtime_supported"]
            + self.structured_metrics["legacy_supported"]
        )
        naplo.ir("\nOutcome osszegzes:")
        naplo.ir(f"  - runtime tenylegesen mukodott: {runtime_mukodott}")
        naplo.ir(f"  - structured teljes: {self.structured_metrics['resolved']}")
        naplo.ir(f"  - structured partial: {self.structured_metrics['partial']}")
        naplo.ir(f"  - structured deferred: {self.structured_metrics['deferred']}")
        naplo.ir(f"  - fallback text resolved: {self.structured_metrics['fallback']}")
        naplo.ir(f"  - passive/static: {self.structured_metrics['passive']}")
        naplo.ir(f"  - legacy supported: {self.structured_metrics['legacy_supported']}")
        naplo.ir(f"  - missing: {self.structured_metrics['missing']}")
        naplo.ir("\nStructured resolver osszegzes:")
        naplo.ir(f"  - structured probalkozasok: {self.structured_metrics['attempted']}")
        naplo.ir(f"  - teljes structured feloldas: {self.structured_metrics['resolved']}")
        naplo.ir(f"  - reszleges structured feloldas: {self.structured_metrics['partial']}")
        naplo.ir(f"  - deferred triggerre varakozik: {self.structured_metrics['deferred']}")
        naplo.ir(f"  - passive/static figyelmen kivul hagyva: {self.structured_metrics['passive']}")
        naplo.ir(f"  - nem alkalmazhato ebben a helyzetben: {self.structured_metrics['not_applicable']}")
        naplo.ir(f"  - text fallbackre esett: {self.structured_metrics['fallback']}")
        naplo.ir(f"  - runtime supported: {self.structured_metrics['runtime_supported']}")
        naplo.ir(f"  - legacy supported: {self.structured_metrics['legacy_supported']}")
        naplo.ir(f"  - trap consumed only: {self.structured_metrics['trap_consumed_only']}")
        naplo.ir(f"  - trap resolved: {self.structured_metrics['trap_resolved']}")
        naplo.ir(f"  - trap partial: {self.structured_metrics['trap_partial']}")
        naplo.ir(f"  - trap missing: {self.structured_metrics['trap_missing']}")
        naplo.ir(f"  - tenylegesen hianyzo maradt: {self.structured_metrics['missing']}")
        naplo.ir("=" * 40)


stats = Statisztika()
