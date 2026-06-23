"""Teljes kártya-szintű diagnosztika és meta-javaslat cards.xlsx-hez.

Futtatás:
    python stats/full_card_analysis.py cards.xlsx

Kimenet:
- stats/cards_per_card_analysis.md (minden kártya, 1 soros diagnózis)
- stats/cards_metadata_enrichment.csv (javasolt pótlások)
"""

from __future__ import annotations

import csv
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
}

KNOWN_TRIGGERS = {
    "on_play",
    "on_summon",
    "on_enemy_summon",
    "on_enemy_spell_played",
    "on_attack_declared",
    "on_combat_phase_start",
    "on_combat_damage_dealt",
    "on_first_combat_survived",
    "on_breach_phase",
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


def _normalize_tokens(raw: str):
    if not raw:
        return []
    return [t.strip() for t in re.split(r"[;,]", raw) if t.strip()]


def _col_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref)
    if not match:
        return 0
    idx = 0
    for ch in match.group(1):
        idx = idx * 26 + ord(ch) - 64
    return idx - 1


def _load_xlsx_rows(path: str):
    with zipfile.ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in shared_root.findall("a:si", NS):
                shared.append("".join((t.text or "") for t in si.iterfind(".//a:t", NS)))

        wb = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall("p:Relationship", NS)}

        cards = []
        for sheet in wb.findall("a:sheets/a:sheet", NS):
            sheet_name = sheet.attrib["name"]
            rel_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            root = ET.fromstring(archive.read("xl/" + rel_map[rel_id]))
            rows = []
            for row in root.findall(".//a:sheetData/a:row", NS):
                values = {}
                for cell in row.findall("a:c", NS):
                    idx = _col_index(cell.attrib.get("r", "A1"))
                    t = cell.attrib.get("t")
                    raw = cell.find("a:v", NS)
                    if t == "s" and raw is not None:
                        value = shared[int(raw.text)]
                    elif t == "inlineStr":
                        inline = cell.find("a:is/a:t", NS)
                        value = inline.text if inline is not None else ""
                    else:
                        value = raw.text if raw is not None else ""
                    values[idx] = value
                if not values:
                    continue
                row_values = [""] * (max(values) + 1)
                for idx, value in values.items():
                    row_values[idx] = value
                rows.append(row_values)

            if not rows:
                continue
            headers = rows[0]
            for raw in rows[1:]:
                if not raw or not (raw[0] if len(raw) > 0 else ""):
                    continue
                row = raw + [""] * (len(headers) - len(raw))
                item = {headers[i]: row[i] for i in range(len(headers))}
                if item.get("Kártya név") == "Kártya név":
                    continue
                item["_sheet"] = sheet_name
                cards.append(item)
        return cards


def infer_missing_trigger(ability_text: str, existing_triggers: list[str]):
    if existing_triggers:
        return []
    text = (ability_text or "").lower()
    if "megidéz" in text or "megidez" in text or "riadó" in text or "riado" in text:
        return ["on_summon"]
    if "elpusztul" in text or "megsemmisül" in text or "visszhang" in text:
        return ["on_destroyed"]
    if "manifesztáció" in text or "manifesztacio" in text:
        return ["on_manifestation_phase"]
    if "ébredés" in text or "ebredes" in text:
        return ["on_awakening_phase"]
    if "amikor támad" in text or "amikor tamad" in text:
        return ["on_attack_declared"]
    return []


def infer_missing_target(tags: list[str], existing_targets: list[str]):
    if existing_targets:
        return []
    if any(t in tags for t in {"damage", "destroy", "exhaust", "move_horizont", "move_zenit"}):
        return ["enemy_entity"]
    if any(t in tags for t in {"heal", "atk_mod", "hp_mod", "aegis", "untargetable"}):
        return ["own_entity"]
    return []


def main(xlsx_path: str):
    cards = _load_xlsx_rows(xlsx_path)

    out_md = Path("stats/cards_per_card_analysis.md")
    out_csv = Path("stats/cards_metadata_enrichment.csv")

    status_counter = Counter()
    unsupported_trigger_counter = Counter()
    enrichment_rows = []

    with out_md.open("w", encoding="utf-8") as md:
        md.write("# Teljes kártyaelemzés (`cards.xlsx`)\n\n")
        md.write(f"Összes feldolgozott kártya: **{len(cards)}**\n\n")

        for idx, card in enumerate(cards, start=1):
            name = card.get("Kártya név", "")
            sheet = card.get("_sheet", "")
            ability = card.get("Képesség", "")
            status = (card.get("Értelmezési_Státusz") or "").strip() or "<üres>"
            status_counter[status] += 1

            triggers = [TRIGGER_ALIASES.get(t, t) for t in _normalize_tokens(card.get("Trigger_Felismerve", ""))]
            targets = _normalize_tokens(card.get("Célpont_Felismerve", ""))
            tags = _normalize_tokens(card.get("Hatáscímkék", ""))

            inferred_triggers = infer_missing_trigger(ability, triggers)
            inferred_targets = infer_missing_target(tags, targets)

            unsupported_triggers = [t for t in triggers if t not in KNOWN_TRIGGERS]
            for trig in unsupported_triggers:
                unsupported_trigger_counter[trig] += 1

            issues = []
            if not triggers:
                issues.append("hiányzó trigger")
            if not targets and tags:
                issues.append("hiányzó célpont")
            if unsupported_triggers:
                issues.append(f"nem támogatott trigger: {', '.join(unsupported_triggers)}")

            if inferred_triggers or inferred_targets:
                enrichment_rows.append(
                    {
                        "sheet": sheet,
                        "card_name": name,
                        "existing_trigger": "; ".join(triggers),
                        "suggested_trigger": "; ".join(inferred_triggers),
                        "existing_target": "; ".join(targets),
                        "suggested_target": "; ".join(inferred_targets),
                        "tags": "; ".join(tags),
                        "status": status,
                    }
                )

            md.write(
                f"{idx:03d}. **{name}** ({sheet}) – státusz: `{status}` | "
                f"trigger: `{', '.join(triggers) or '-'}'` | "
                f"célpont: `{', '.join(targets) or '-'}'` | "
                f"javaslat: trigger=`{', '.join(inferred_triggers) or '-'}'`, célpont=`{', '.join(inferred_targets) or '-'}'`"
            )
            if issues:
                md.write(f" | ⚠️ {', '.join(issues)}")
            md.write("\n")

        md.write("\n## Összegzés\n")
        for st, cnt in status_counter.most_common():
            md.write(f"- {st}: {cnt}\n")

        if unsupported_trigger_counter:
            md.write("\n## Nem támogatott triggerek (normalizálva)\n")
            for trig, cnt in unsupported_trigger_counter.most_common():
                md.write(f"- {trig}: {cnt}\n")

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sheet",
                "card_name",
                "existing_trigger",
                "suggested_trigger",
                "existing_target",
                "suggested_target",
                "tags",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(enrichment_rows)

    print(f"Generated: {out_md}")
    print(f"Generated: {out_csv}")
    print(f"Enrichment rows: {len(enrichment_rows)}")


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "cards.xlsx"
    main(filepath)
