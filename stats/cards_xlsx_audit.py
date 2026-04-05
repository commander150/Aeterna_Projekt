"""Simple xlsx audit without external dependencies.

Usage:
    python stats/cards_xlsx_audit.py cards.xlsx
"""

from __future__ import annotations

import collections
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
}

KNOWN_ENGINE_TRIGGERS = {
    "on_play",
    "on_summon",
    "on_attack_declared",
    "on_spell_targeted",
    "on_damage_taken",
    "on_destroyed",
    "on_turn_start",
    "on_turn_end",
    "on_manifestation_phase",
    "on_awakening_phase",
    "on_position_changed",
}

TRIGGER_ALIASES = {
    "on_manifest_phase": "on_manifestation_phase",
    "on_death": "on_destroyed",
    "death": "on_destroyed",
}


def _col_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref)
    if not match:
        return 0
    idx = 0
    for ch in match.group(1):
        idx = idx * 26 + ord(ch) - 64
    return idx - 1


def _load_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values = []
    for si in root.findall("a:si", NS):
        values.append("".join((t.text or "") for t in si.iterfind(".//a:t", NS)))
    return values


def _iter_sheet_rows(archive: zipfile.ZipFile, target_path: str, shared: list[str]):
    root = ET.fromstring(archive.read(target_path))
    for row in root.findall(".//a:sheetData/a:row", NS):
        values: dict[int, str] = {}
        for cell in row.findall("a:c", NS):
            idx = _col_index(cell.attrib.get("r", "A1"))
            cell_type = cell.attrib.get("t")
            raw = cell.find("a:v", NS)
            if cell_type == "s" and raw is not None:
                value = shared[int(raw.text)]
            elif cell_type == "inlineStr":
                inline = cell.find("a:is/a:t", NS)
                value = inline.text if inline is not None else ""
            else:
                value = raw.text if raw is not None else ""
            values[idx] = value
        if not values:
            continue
        max_idx = max(values)
        row_values = [""] * (max_idx + 1)
        for idx, value in values.items():
            row_values[idx] = value
        yield row_values


def audit_cards_xlsx(path: str):
    with zipfile.ZipFile(path) as archive:
        shared = _load_shared_strings(archive)

        wb = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall("p:Relationship", NS)}

        all_rows = []
        for sheet in wb.findall("a:sheets/a:sheet", NS):
            sheet_name = sheet.attrib["name"]
            rel_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            rows = list(_iter_sheet_rows(archive, "xl/" + rel_map[rel_id], shared))
            if not rows:
                continue
            headers = rows[0]
            for raw in rows[1:]:
                if not raw or not (raw[0] if len(raw) > 0 else ""):
                    continue
                row = raw + [""] * (len(headers) - len(raw))
                row_map = {headers[i]: row[i] for i in range(len(headers))}
                row_map["_sheet"] = sheet_name
                all_rows.append(row_map)

    print(f"Total cards: {len(all_rows)}")

    status_counts = collections.Counter((row.get("Értelmezési_Státusz") or "").strip() for row in all_rows)
    print("\nStatus distribution:")
    for status, count in status_counts.most_common():
        print(f"  {count:>4}  {status or '<empty>'}")

    triggers = collections.Counter()
    for row in all_rows:
        raw = (row.get("Trigger_Felismerve") or "").replace(";", ",")
        for token in [t.strip() for t in raw.split(",") if t.strip()]:
            normalized = TRIGGER_ALIASES.get(token, token)
            triggers[normalized] += 1

    print("\nTrigger usage (normalized):")
    for trigger, count in triggers.most_common():
        marker = "" if trigger in KNOWN_ENGINE_TRIGGERS else "  <-- not in engine trigger list"
        print(f"  {count:>4}  {trigger}{marker}")


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "cards.xlsx"
    audit_cards_xlsx(filepath)
