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

    def _write_line(self, sor):
        if self.konzol_kiiras:
            try:
                print(sor)
            except UnicodeEncodeError:
                encoding = sys.stdout.encoding or "utf-8"
                print(sor.encode(encoding, errors="replace").decode(encoding, errors="replace"))

        if self.fajlnev:
            with open(self.fajlnev, "a", encoding="utf-8") as f:
                f.write(sor + "\n")

    def ir(self, uzenet):
        sor = f"[{datetime.now().strftime('%H:%M:%S')}] {repair_mojibake(uzenet)}"
        self._write_line(sor)

    def tech(self, category, message):
        self.ir(f"[TECH:{category}] {message}")

    def skip(self, category, message):
        self.ir(f"[SKIP:{category}] {message}")

    def summary(self, title, lines=None):
        self.ir(f"[SUMMARY] {title}")
        for line in lines or []:
            self.ir(f"[SUMMARY] {line}")

    def separator(self, title=None, char="="):
        if title:
            self.ir(f"{char * 8} {title} {char * 8}")
        else:
            self.ir(char * 32)


naplo = Naplozo()