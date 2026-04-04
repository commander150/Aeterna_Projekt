import os
import sys
from datetime import datetime
from utils.text import repair_mojibake

class Naplozo:
    def __init__(self, konzol_kiiras=True):
        self.konzol_kiiras = konzol_kiiras
        self.fajlnev = None
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    def uj_log_fajl(self, mappa):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.fajlnev = os.path.join(mappa, f"log_{now}.txt")

        with open(self.fajlnev, "w", encoding="utf-8") as f:
            f.write(f"AETERNA LOG - {now}\n\n")

    def ir(self, uzenet):
        sor = f"[{datetime.now().strftime('%H:%M:%S')}] {repair_mojibake(uzenet)}"

        if self.konzol_kiiras:
            try:
                print(sor)
            except UnicodeEncodeError:
                print(sor.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8", errors="replace"))

        if self.fajlnev:
            with open(self.fajlnev, "a", encoding="utf-8") as f:
                f.write(sor + "\n")


naplo = Naplozo()
