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

    def faj_statisztika(self, faj):
        if not faj or faj == "None" or faj == "-": return
        self.kijatszott_fajok[faj] = self.kijatszott_fajok.get(faj, 0) + 1

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
        naplo.ir("="*40)

# Globális statisztika példány
stats = Statisztika()