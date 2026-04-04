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

    def start_log(self, file_path, header_lines=None):
        self.fajlnev = file_path
        os.makedirs(os.path.dirname(self.fajlnev), exist_ok=True)

        with open(self.fajlnev, "w", encoding="utf-8") as f:
            if header_lines:
                for sor in header_lines:
                    f.write(repair_mojibake(sor) + "\n")
            else:
                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                f.write(f"AETERNA LOG - {now}\n\n")

    def uj_log_fajl(self, mappa):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.start_log(os.path.join(mappa, f"log_{now}.txt"))

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
