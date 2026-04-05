"""Simple xlsx audit without external dependencies.

Usage:
    python stats/cards_xlsx_audit.py cards.xlsx
    python stats/cards_xlsx_audit.py cards.xlsx --keyword-audit --realm Ignis --clan Hamvaskezű
"""

from __future__ import annotations

import collections
import csv
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from engine.keyword_registry import KEYWORD_DEFINITIONS, KeywordRegistry
from utils.text import normalize_lookup_text, repair_mojibake

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
}

KNOWN_ENGINE_TRIGGERS = {
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

KEYWORD_AUDIT_SIMPLE_STATUSES = {
    "passziv_kulcsszo",
    "passziv_vagy_egyszeru",
}

SIMPLE_EFFECT_AUDIT_ALLOWED_STATUSES = {
    "elso_koros_gepi_ertelmezes",
    "passziv_vagy_egyszeru",
}

KEYWORD_SUPPORT_MATRIX = {
    "aegis": (
        "partial",
        ["engine/keyword_registry.py", "engine/keyword_engine.py", "engine/game.py"],
        "Regisztralt keyword, explicit blokkolo runtime aggal, de a jelenlegi bizonyitek kevesebb, mint a legerosebb keywordoknel.",
    ),
    "ethereal": (
        "supported",
        ["engine/keyword_registry.py", "engine/keyword_engine.py", "tests/test_keywords.py"],
        "Regisztralt keyword, specialis blokkolo-szures es runtime keyword-engine tamogatassal.",
    ),
    "celerity": (
        "supported",
        ["engine/keyword_registry.py", "engine/keyword_engine.py", "engine/card.py"],
        "Regisztralt keyword, on_summon ujraaktivalo logikaval.",
    ),
    "sundering": (
        "partial",
        ["engine/keyword_registry.py", "engine/keyword_engine.py", "engine/game.py"],
        "Regisztralt keyword, harci sebzes utani runtime aggal, de a jelenlegi bizonyitek konzervativan csak reszlegesnek eleg eros.",
    ),
    "bane": (
        "supported",
        ["engine/keyword_registry.py", "engine/keyword_engine.py"],
        "Regisztralt keyword, sebzes utani megjeloles es pusztitas tamogatassal.",
    ),
    "harmonize": (
        "supported",
        ["engine/keyword_registry.py", "engine/keyword_engine.py", "engine/game.py"],
        "Regisztralt keyword, tamadasi bonusz szamolassal.",
    ),
    "resonance": (
        "uncertain",
        ["engine/keyword_registry.py", "engine/keyword_engine.py"],
        "Regisztralt keyword es van kulon runtime helper, de a jelenlegi kodban a fo harci utvonalra kotese nem eleg egyertelmu.",
    ),
    "clarion": (
        "partial",
        ["engine/keyword_registry.py", "engine/keyword_engine.py", "cards/resolver.py"],
        "A keyword fel van ismerve, de a konkret Clarion gameplay tobbnyire kartya-specifikus handlerekben el.",
    ),
    "echo": (
        "partial",
        ["engine/keyword_registry.py", "engine/keyword_engine.py", "engine/effects.py"],
        "A keyword fel van ismerve, de a teljes halalos / visszatero szemantika nem altalanos keyword-only motorlogika.",
    ),
    "burst": (
        "partial",
        ["engine/keyword_registry.py", "engine/keyword_engine.py", "engine/card.py", "cards/resolver.py"],
        "A keyword fel van ismerve es a burst-reakcio mintak leteznek, de a konkret runtime sokszor lap-specifikus.",
    ),
    "untargetable": (
        "partial",
        ["engine/targeting.py", "engine/structured_effects.py"],
        "Celozhatatlansaghoz vannak celzasi allapotok, de a generic keyword-tamogatas nem teljesen keyword-engine alapu.",
    ),
}

EFFECT_TAG_SUPPORT_MATRIX = {
    "deal_damage": (
        "supported",
        ["engine/effects.py", "engine/structured_effects.py", "cards/priority_handlers.py"],
        "Van kozponti sebzes-helper es tobb lokalis/runtime handler ugyanarra a primitive-re.",
    ),
    "grant_temp_attack": (
        "supported",
        ["cards/priority_handlers.py", "engine/structured_effects.py", "engine/player.py"],
        "Van kulon ideiglenes ATK-buff helper es korvegi takaritas.",
    ),
    "grant_max_hp": (
        "partial",
        ["cards/priority_handlers.py", "engine/player.py"],
        "Van bonus_max_hp hasznalat, de nem teljesen egyseges primitive-kent.",
    ),
    "exhaust_target": (
        "supported",
        ["engine/actions.py", "engine/structured_effects.py", "cards/priority_handlers.py"],
        "Van kimeritesi helper/structured ut es tobb kartya-specifikus runtime pelda.",
    ),
    "draw_cards": (
        "supported",
        ["engine/player.py", "engine/structured_effects.py", "cards/priority_handlers.py"],
        "Van kozos huzasi motor es strukturalt/runtime draw hasznalat.",
    ),
    "move_to_zenit": (
        "supported",
        ["engine/actions.py", "engine/structured_effects.py", "cards/priority_handlers.py"],
        "Van kozos Horizon->Zenit mozgatas helper es tobb runtime pelda.",
    ),
    "grant_keyword_temp": (
        "supported",
        ["cards/priority_handlers.py", "engine/player.py", "tests/test_priority_handlers.py"],
        "Van ideiglenes keyword-grant helper, korvegi cleanup es konkret tesztelt peldak.",
    ),
    "restrict_attack": (
        "supported",
        ["engine/player.py", "engine/game.py", "engine/structured_effects.py", "cards/priority_handlers.py"],
        "Van cannot_attack flag, combat ellenorzes es korvegi reset.",
    ),
    "move_to_horizon": (
        "partial",
        ["engine/structured_effects.py", "cards/priority_handlers.py"],
        "Van support a Horizonra mozgatasra, de kevesbe egyseges primitive-kent.",
    ),
    "return_to_hand": (
        "supported",
        ["engine/actions.py", "engine/structured_effects.py", "cards/priority_handlers.py"],
        "Van kozos kezbe visszavevo helper es strukturalt/runtime hasznalat.",
    ),
    "reactivate": (
        "supported",
        ["engine/player.py", "engine/structured_effects.py", "cards/priority_handlers.py"],
        "Van kozos ujraaktivalt_egyseget logika es runtime peldak.",
    ),
    "heal": (
        "supported",
        ["engine/effects.py", "engine/structured_effects.py", "cards/priority_handlers.py"],
        "Van kozos gyogyitasi runtime es strukturalt tamogatas.",
    ),
    "destroy_target": (
        "supported",
        ["engine/effects.py", "engine/structured_effects.py", "cards/priority_handlers.py"],
        "Van kozos destroy primitive es tobb runtime utvonal.",
    ),
    "seal_damage": (
        "supported",
        ["engine/effects.py", "engine/structured_effects.py"],
        "Van kozos pecset-sebzes primitive.",
    ),
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


def load_cards_rows(path: str):
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
                row_map = {headers[i]: repair_mojibake(row[i]) for i in range(len(headers))}
                row_map["_sheet"] = sheet_name
                all_rows.append(row_map)
    return all_rows


def _parse_semicolon_or_csv(value: str) -> list[str]:
    if not value:
        return []
    text = repair_mojibake(str(value)).replace("|", ";")
    if ";" not in text and "," in text:
        text = text.replace(",", ";")
    return [item.strip() for item in text.split(";") if item.strip()]


def _normalize_keyword_list(value: str) -> list[str]:
    normalized = []
    for item in _parse_semicolon_or_csv(value):
        keyword = KeywordRegistry.normalize_keyword_name(item)
        if keyword in KEYWORD_DEFINITIONS and keyword not in normalized:
            normalized.append(keyword)
    return normalized


def _detect_keywords(row: dict[str, str]) -> list[str]:
    detected = []
    for keyword in _normalize_keyword_list(row.get("Kulcsszavak_Felismerve", "")):
        if keyword not in detected:
            detected.append(keyword)

    raw_ability = row.get("Képesség", "")
    for keyword_name, definition in KEYWORD_DEFINITIONS.items():
        if KeywordRegistry.has_keyword(raw_ability, keyword_name) and keyword_name not in detected:
            detected.append(keyword_name)
        elif any(KeywordRegistry.has_keyword(raw_ability, alias) for alias in definition.aliases) and keyword_name not in detected:
            detected.append(keyword_name)
    return detected


def _keyword_support(keyword: str):
    if keyword in KEYWORD_SUPPORT_MATRIX:
        return KEYWORD_SUPPORT_MATRIX[keyword]
    if keyword in KEYWORD_DEFINITIONS:
        return (
            "uncertain",
            ["engine/keyword_registry.py"],
            "A keyword regisztralva van, de ehhez a korhoz nem talaltam egyertelmu runtime bizonyitekot.",
        )
    return (
        "missing",
        [],
        "Nem talaltam regisztralt vagy runtime tamogatott keyword-bizonyitekot.",
    )


def _parse_effect_tags(value: str) -> list[str]:
    return [KeywordRegistry.normalize_keyword_name(item) for item in _parse_semicolon_or_csv(value)]


def _detect_simple_effect_tags(row: dict[str, str]) -> list[str]:
    tags = []
    raw_tags = _parse_effect_tags(row.get("Hatáscímkék", ""))
    keyword_like = set(KEYWORD_DEFINITIONS)
    for tag in raw_tags:
        if tag in keyword_like:
            continue
        if tag == "damage" and "deal_damage" not in tags:
            tags.append("deal_damage")
        elif tag in {"atk_mod", "atk_buff"} and "grant_temp_attack" not in tags:
            tags.append("grant_temp_attack")
        elif tag in {"hp_mod", "hp_buff"} and "grant_max_hp" not in tags:
            tags.append("grant_max_hp")
        elif tag == "exhaust" and "exhaust_target" not in tags:
            tags.append("exhaust_target")
        elif tag == "draw" and "draw_cards" not in tags:
            tags.append("draw_cards")
        elif tag == "move_zenit" and "move_to_zenit" not in tags:
            tags.append("move_to_zenit")
        elif tag == "move_horizont" and "move_to_horizon" not in tags:
            tags.append("move_to_horizon")
        elif tag == "return_to_hand" and "return_to_hand" not in tags:
            tags.append("return_to_hand")
        elif tag == "reactivate" and "reactivate" not in tags:
            tags.append("reactivate")
        elif tag == "heal" and "heal" not in tags:
            tags.append("heal")
        elif tag == "destroy" and "destroy_target" not in tags:
            tags.append("destroy_target")
        elif tag == "cannot_attack" and "restrict_attack" not in tags:
            tags.append("restrict_attack")
        elif tag == "seal_damage" and "seal_damage" not in tags:
            tags.append("seal_damage")

    text = repair_mojibake(str(row.get("Képesség", "") or ""))
    lower = normalize_lookup_text(text)

    if re.search(r"\+\s*\d+\s*atk", lower) and "grant_temp_attack" not in tags:
        tags.append("grant_temp_attack")
    if ("kor veg" in lower or "kor vegeig" in lower) and "megkapja" in lower:
        if any(
            KeywordRegistry.has_keyword(text, keyword)
            for keyword in ("aegis", "ethereal", "celerity", "sundering", "harmonize", "resonance")
        ) and "grant_keyword_temp" not in tags:
            tags.append("grant_keyword_temp")
    if ("okoz" in lower or "sebzest" in lower or "sebzest kap" in lower) and "deal_damage" not in tags:
        if re.search(r"\b[1-9]\d*\b", lower):
            tags.append("deal_damage")
    if "kimerult" in lower and "exhaust_target" not in tags:
        tags.append("exhaust_target")
    if ("huzz" in lower or "lapot" in lower) and "draw_cards" not in tags:
        tags.append("draw_cards")
    if ("zenitbe" in lower or "zenitbe kerul" in lower or "visszalep a zenitbe" in lower) and "move_to_zenit" not in tags:
        tags.append("move_to_zenit")
    if ("nem tamadhat" in lower or "kotelezoen tamadnia kell" in lower) and "restrict_attack" not in tags:
        tags.append("restrict_attack")

    return tags


def _effect_support(tag: str):
    return EFFECT_TAG_SUPPORT_MATRIX.get(
        tag,
        (
            "uncertain",
            [],
            "Ehhez az effekt-primitivhez ebben a korben nem talaltam eleg eros altalanos bizonyitekot.",
        ),
    )


def _aggregate_support(statuses: list[str]) -> str:
    if not statuses:
        return "missing"
    if "missing" in statuses:
        return "missing"
    if "uncertain" in statuses:
        return "uncertain"
    if "partial" in statuses:
        return "partial"
    return "supported"


def _slugify(value: str) -> str:
    text = repair_mojibake(value or "").strip().lower()
    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ö": "o",
        "ő": "o",
        "ú": "u",
        "ü": "u",
        "ű": "u",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "no_clan"


def generate_simple_effect_support_audit(path: str, realm: str, clan: str = ""):
    rows = load_cards_rows(path)
    clan_value = repair_mojibake(clan or "")
    scoped_rows = []

    for row in rows:
        if row.get("Birodalom", "") != realm:
            continue
        if row.get("Klán", "") != clan_value:
            continue
        if row.get("Értelmezési_Státusz", "") not in SIMPLE_EFFECT_AUDIT_ALLOWED_STATUSES:
            continue

        detected_keywords = _detect_keywords(row)
        detected_effect_tags = _detect_simple_effect_tags(row)

        if not detected_keywords:
            continue
        if not detected_effect_tags:
            continue
        if len(detected_effect_tags) > 2:
            continue
        if len(detected_keywords) > 2:
            continue

        scoped_rows.append((row, detected_keywords, detected_effect_tags))

    audit_rows = []
    effect_status_counter = collections.Counter()

    for row, detected_keywords, detected_effect_tags in scoped_rows:
        keyword_statuses = [_keyword_support(keyword)[0] for keyword in detected_keywords]
        keyword_support_status = _aggregate_support(keyword_statuses) if keyword_statuses else "missing"

        effect_support_details = [_effect_support(tag) for tag in detected_effect_tags]
        effect_statuses = [detail[0] for detail in effect_support_details]
        effect_support_status = _aggregate_support(effect_statuses)
        effect_status_counter.update(effect_statuses)

        evidence_files = sorted(
            {
                item
                for keyword in detected_keywords
                for item in _keyword_support(keyword)[1]
            }
            | {
                item
                for _, files, _ in effect_support_details
                for item in files
            }
        )

        notes = []
        if detected_keywords:
            notes.append(
                "keywords: " + "; ".join(
                    f"{keyword}={_keyword_support(keyword)[0]}"
                    for keyword in detected_keywords
                )
            )
        if detected_effect_tags:
            notes.append(
                "effects: " + "; ".join(
                    f"{tag}={status}"
                    for tag, status in zip(detected_effect_tags, effect_statuses)
                )
            )

        audit_rows.append(
            {
                "card_name": row.get("Kártya név", ""),
                "realm": row.get("Birodalom", ""),
                "clan": row.get("Klán", ""),
                "raw_ability": row.get("Képesség", ""),
                "detected_keywords": ";".join(detected_keywords),
                "detected_effect_tags": ";".join(detected_effect_tags),
                "keyword_support_status": keyword_support_status,
                "effect_support_status": effect_support_status,
                "evidence_files": ";".join(evidence_files),
                "notes": " | ".join(notes),
            }
        )

    output_path = pathlib.Path("stats") / f"effect_support_audit_{_slugify(realm)}_{_slugify(clan_value)}_simple.csv"
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "card_name",
                "realm",
                "clan",
                "raw_ability",
                "detected_keywords",
                "detected_effect_tags",
                "keyword_support_status",
                "effect_support_status",
                "evidence_files",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(audit_rows)

    return {
        "output_path": str(output_path),
        "realm": realm,
        "clan": clan_value,
        "cards": audit_rows,
        "effect_status_counter": effect_status_counter,
    }


def generate_keyword_support_audit(path: str, realm: str, clan: str = ""):
    rows = load_cards_rows(path)
    clan_value = repair_mojibake(clan or "")

    scoped_rows = [
        row for row in rows
        if row.get("Birodalom", "") == realm
        and row.get("Klán", "") == clan_value
        and row.get("Értelmezési_Státusz", "") in KEYWORD_AUDIT_SIMPLE_STATUSES
    ]

    audit_rows = []
    keyword_counter = collections.Counter()
    status_counter = collections.Counter()

    for row in scoped_rows:
        detected_keywords = _detect_keywords(row)
        if not detected_keywords:
            continue

        keyword_counter.update(detected_keywords)
        support_details = [_keyword_support(keyword) for keyword in detected_keywords]
        statuses = [detail[0] for detail in support_details]
        support_status = _aggregate_support(statuses)
        status_counter[support_status] += 1

        evidence_files = sorted({item for _, files, _ in support_details for item in files})
        notes = "; ".join(
            f"{keyword}={status}"
            for keyword, status in zip(detected_keywords, statuses)
        )

        audit_rows.append(
            {
                "card_name": row.get("Kártya név", ""),
                "realm": row.get("Birodalom", ""),
                "clan": row.get("Klán", ""),
                "raw_ability": row.get("Képesség", ""),
                "detected_keywords": ";".join(detected_keywords),
                "engine_support_status": support_status,
                "evidence_files": ";".join(evidence_files),
                "notes": notes,
            }
        )

    output_clan = _slugify(clan_value)
    output_realm = _slugify(realm)
    output_path = pathlib.Path("stats") / f"keyword_support_audit_{output_realm}_{output_clan}.csv"
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "card_name",
                "realm",
                "clan",
                "raw_ability",
                "detected_keywords",
                "engine_support_status",
                "evidence_files",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(audit_rows)

    return {
        "output_path": str(output_path),
        "realm": realm,
        "clan": clan_value,
        "cards": audit_rows,
        "keyword_count": sum(keyword_counter.values()),
        "status_counter": status_counter,
    }


def audit_cards_xlsx(path: str):
    all_rows = load_cards_rows(path)

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
    args = sys.argv[1:]
    filepath = args[0] if args and not args[0].startswith("--") else "cards.xlsx"
    if "--keyword-audit" in args:
        realm = "Ignis"
        clan = ""
        if "--realm" in args:
            realm = args[args.index("--realm") + 1]
        if "--clan" in args:
            clan = args[args.index("--clan") + 1]
        result = generate_keyword_support_audit(filepath, realm, clan)
        print(f"Keyword audit generated: {result['output_path']}")
        print(f"Cards audited: {len(result['cards'])}")
        print(f"Keywords detected: {result['keyword_count']}")
        for status in ("supported", "partial", "uncertain", "missing"):
            print(f"{status}: {result['status_counter'].get(status, 0)}")
    elif "--effect-audit-simple" in args:
        realm = "Ignis"
        clan = ""
        if "--realm" in args:
            realm = args[args.index("--realm") + 1]
        if "--clan" in args:
            clan = args[args.index("--clan") + 1]
        result = generate_simple_effect_support_audit(filepath, realm, clan)
        print(f"Effect audit generated: {result['output_path']}")
        print(f"Cards audited: {len(result['cards'])}")
        for status in ("supported", "partial", "uncertain", "missing"):
            print(f"{status}: {result['effect_status_counter'].get(status, 0)}")
    else:
        audit_cards_xlsx(filepath)
