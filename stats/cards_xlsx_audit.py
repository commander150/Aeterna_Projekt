"""Simple xlsx audit without external dependencies.

Usage:
    python stats/cards_xlsx_audit.py cards.xlsx
    python stats/cards_xlsx_audit.py cards.xlsx --keyword-audit --realm Ignis --clan Hamvaskezű
"""

from __future__ import annotations

import collections
import csv
import inspect
import pathlib
import re
import sys
import unicodedata
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
    text = repair_mojibake(str(row.get("Képesség", "") or ""))
    lower = normalize_lookup_text(text)
    keyword_like = set(KEYWORD_DEFINITIONS)

    for tag in raw_tags:
        if tag in keyword_like:
            continue
        if tag == "damage" and "deal_damage" not in tags:
            tags.append("deal_damage")
        elif tag in {"atk_mod", "atk_buff"} and "grant_temp_attack" not in tags:
            tags.append("grant_temp_attack")
        elif tag in {"hp_mod", "hp_buff"} and "grant_max_hp" not in tags:
            if any(
                phrase in lower
                for phrase in (
                    "maximalis hp-t kap",
                    "+1 maximalis hp",
                    "+2 maximalis hp",
                    "+3 maximalis hp",
                    "plusz 1 hp",
                    "plusz 2 hp",
                    "plusz 3 hp",
                )
            ):
                tags.append("grant_max_hp")
        elif tag == "exhaust" and "exhaust_target" not in tags:
            tags.append("exhaust_target")
        elif tag == "draw" and "draw_cards" not in tags:
            if "huzz" in lower or "lapot" in lower:
                tags.append("draw_cards")
        elif tag == "move_zenit" and "move_to_zenit" not in tags:
            if "zenitbe" in lower or "visszalep a zenitbe" in lower or "kerul a zenitbe" in lower:
                tags.append("move_to_zenit")
        elif tag == "move_horizont" and "move_to_horizon" not in tags:
            if "horizontra" in lower or "vissza a horizontra" in lower or "ures mezore" in lower:
                tags.append("move_to_horizon")
        elif tag == "return_to_hand" and "return_to_hand" not in tags:
            tags.append("return_to_hand")
        elif tag == "reactivate" and "reactivate" not in tags:
            tags.append("reactivate")
        elif tag == "heal" and "heal" not in tags:
            tags.append("heal")
        elif tag == "destroy" and "destroy_target" not in tags:
            if any(phrase in lower for phrase in ("semmisits", "pusztitsd el", "ebbe belehal", "ha belehal")):
                tags.append("destroy_target")
        elif tag == "cannot_attack" and "restrict_attack" not in tags:
            tags.append("restrict_attack")
        elif tag == "seal_damage" and "seal_damage" not in tags:
            tags.append("seal_damage")

    if re.search(r"\+\s*\d+\s*atk", lower) and "grant_temp_attack" not in tags:
        tags.append("grant_temp_attack")
    if any(
        phrase in lower
        for phrase in (
            "maximalis hp-t kap",
            "+1 maximalis hp",
            "+2 maximalis hp",
            "+3 maximalis hp",
        )
    ) and "grant_max_hp" not in tags:
        tags.append("grant_max_hp")
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


def _safe_slugify(value: str) -> str:
    text = repair_mojibake(value or "").strip().lower()
    text = "".join(
        ch for ch in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(ch)
    )
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "no_clan"


def _resolver_registry_snapshot():
    import cards.resolver as resolver

    return {
        "on_play": set(getattr(resolver, "ON_PLAY_HANDLERS", {})),
        "burst": set(getattr(resolver, "BURST_HANDLERS", {})),
        "trap": set(getattr(resolver, "TRAP_HANDLERS", {})),
        "trap_preview": set(getattr(resolver, "TRAP_PREVIEW_HANDLERS", {})),
        "summon_trap": set(getattr(resolver, "SUMMON_TRAP_HANDLERS", {})),
    }


def _normalized_card_name(row: dict[str, str]) -> str:
    return normalize_lookup_text(row.get("Kártya név", ""))


def _detected_zone_dependency(row: dict[str, str], card_type: str, detected_keywords: list[str]) -> list[str]:
    raw = repair_mojibake(str(row.get("Képesség", "") or ""))
    lower = normalize_lookup_text(raw)
    deps = []

    if "[horizont]" in lower or "horizonton" in lower:
        deps.append("horizont")
    if "[zenit]" in lower or "zenitben" in lower or "zenitbe" in lower:
        deps.append("zenit")
    if "[dominium]" in lower or "[dominium]" in lower.replace("í", "i") or "dominiumon" in lower:
        deps.append("dominium")
    if "burst" in detected_keywords or "reakcio (burst)" in lower or "reakcio burst" in lower:
        deps.append("surge_only")
    if card_type == "Sík":
        deps.append("global")

    seen = []
    for dep in deps:
        if dep not in seen:
            seen.append(dep)
    return seen


def _extract_trap_parts(raw_ability: str) -> tuple[str, str]:
    text = repair_mojibake(raw_ability or "")
    match = re.search(r"Aktiválás:\s*(.*?)\.\s*Hatás:\s*(.*)", text, re.IGNORECASE)
    if not match:
        match = re.search(r"Aktiválás:\s*(.*?)\s*Hatás:\s*(.*)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "", text


def _field_scope(raw_ability: str) -> str:
    lower = normalize_lookup_text(raw_ability or "")
    if "mindket jatekos" in lower or "egyik jatekos sem" in lower:
        return "teljes Dominium"
    if "minden sajat" in lower or "sajat " in lower:
        if "horizonton" in lower:
            return "sajat Horizont"
        if "zenit" in lower:
            return "sajat Zenit"
        return "sajat oldal"
    if "minden ellenseges" in lower and "horizonton" in lower:
        return "Horizont mindket terfelen"
    if "horizonton" in lower:
        return "Horizont mindket terfelen"
    if "zenit" in lower:
        return "Zenit mindket terfelen"
    return "global"


def _card_specific_support(row: dict[str, str], registries: dict[str, set[str]]):
    card_name = row.get("Kártya név", "")
    card_type = row.get("Típus", "")
    raw_ability = row.get("Képesség", "")
    lower = normalize_lookup_text(raw_ability)
    normalized_name = _normalized_card_name(row)
    detected_keywords = _detect_keywords(row)
    detected_effect_tags = _detect_simple_effect_tags(row)

    keyword_details = [_keyword_support(keyword) for keyword in detected_keywords]
    effect_details = [_effect_support(tag) for tag in detected_effect_tags]
    keyword_status = _aggregate_support([detail[0] for detail in keyword_details]) if detected_keywords else "missing"
    effect_status = _aggregate_support([detail[0] for detail in effect_details]) if detected_effect_tags else "uncertain"

    evidence = {
        item
        for _, files, _ in keyword_details
        for item in files
    } | {
        item
        for _, files, _ in effect_details
        for item in files
    }

    notes = []
    support_status = _aggregate_support(
        [status for status in (keyword_status, effect_status) if status != "missing"]
    )
    if support_status == "missing":
        support_status = "uncertain"

    has_on_play = normalized_name in registries["on_play"]
    has_burst = normalized_name in registries["burst"]
    has_trap = normalized_name in registries["trap"]
    has_trap_preview = normalized_name in registries["trap_preview"]
    has_summon_trap = normalized_name in registries["summon_trap"]

    if has_on_play or has_burst or has_trap or has_trap_preview or has_summon_trap:
        evidence.update({"cards/resolver.py", "cards/priority_handlers.py"})

    zone_dependency = _detected_zone_dependency(row, card_type, detected_keywords)

    if card_type == "Entitás":
        notes.append(
            "entity_review: natív keyword, zónafüggés és harci kötés együtt vizsgálva."
        )
        if not detected_effect_tags and detected_keywords and keyword_status == "supported":
            support_status = "supported"
        elif any(keyword in {"clarion", "echo"} for keyword in detected_keywords):
            if has_on_play:
                support_status = "partial"
                notes.append("clarion_echo: van explicit runtime handler, de a keyword szemantika tovabbra is lap-specifikus.")
            else:
                support_status = "partial"
                notes.append("clarion_echo: parsing van, de explicit kartya-handler nem latszik.")
        elif any(token in lower for token in ("valahanyszor", "amikor", "ha ", "amig ")):
            support_status = "partial" if support_status == "supported" else support_status
            notes.append("combat_condition: triggerelt vagy allandosult harci feltetel, nem tisztan keyword-only.")
        if "horizont" in zone_dependency or "zenit" in zone_dependency or "dominium" in zone_dependency:
            notes.append("zone_dependency: " + ", ".join(zone_dependency))

    elif card_type in {"Rituálé", "Ige"}:
        burst_required = "burst" in detected_keywords or "reakcio (burst)" in lower
        notes.append("spell_review: normal kijatszas, burst, celzas es egyszeru primitivek szerint ertekelve.")
        if has_on_play:
            support_status = "supported" if effect_status == "supported" and not burst_required else "partial"
            notes.append("runtime_on_play: explicit on_play handler talalhato.")
        elif effect_status in {"supported", "partial"}:
            support_status = "partial"
            notes.append("runtime_on_play: explicit handler nincs, a kep csak strukturalt / altalanos primitiveken all.")
        else:
            support_status = "uncertain"
        if burst_required:
            if has_burst:
                evidence.add("cards/resolver.py")
                notes.append("burst_support: explicit burst handler talalhato.")
                support_status = "partial" if support_status == "supported" else support_status
            else:
                notes.append("burst_support: burst szerepel a szovegben, de explicit burst handler nem latszik.")
                support_status = "partial" if support_status != "missing" else "uncertain"
        if "horizont" in zone_dependency or "zenit" in zone_dependency:
            notes.append("zone_dependency: " + ", ".join(zone_dependency))

    elif card_type == "Jel":
        activation_condition, effect_resolution = _extract_trap_parts(raw_ability)
        trigger_tokens = [token.strip() for token in _parse_semicolon_or_csv(row.get("Trigger_Felismerve", ""))]
        normalized_triggers = [TRIGGER_ALIASES.get(token, token) for token in trigger_tokens]
        trigger_known = bool(normalized_triggers) and all(token in KNOWN_ENGINE_TRIGGERS for token in normalized_triggers)

        notes.append(f"activation_condition: {activation_condition or 'nem szetbonthato'}")
        notes.append(f"effect_resolution: {effect_resolution or 'nem szetbonthato'}")
        notes.append("trap_limit: a jatekban Jel limit es fogyasztasi logika latszik (engine/game.py).")
        evidence.update({"engine/game.py", "engine/effect_diagnostics_v2.py"})

        if has_summon_trap:
            notes.append("trigger_dispatch: summon trap registryben van.")
            support_status = "supported" if effect_status == "supported" and trigger_known else "partial"
        elif has_trap:
            notes.append("trigger_dispatch: explicit trap handler talalhato.")
            support_status = "supported" if effect_status == "supported" and (has_trap_preview or trigger_known) else "partial"
        elif trigger_known:
            notes.append("trigger_dispatch: trigger metadata alapjan felismerheto, de explicit trap handler nem latszik.")
            support_status = "partial"
        else:
            notes.append("trigger_dispatch: trigger metadata vagy explicit handler nem eleg eros.")
            support_status = "uncertain"
        if has_trap_preview:
            notes.append("activation_preview: van trap preview feltetel-ellenorzes.")

    elif card_type == "Sík":
        notes.append(f"field_scope: {_field_scope(raw_ability)}")
        notes.append("singleton_rule: explicit, dedikalt aktiv Sík slotot nem talaltam; ez jelenleg legfeljebb reszben bizonyitott.")
        evidence.add("engine/player.py")
        if has_on_play:
            notes.append("field_runtime: explicit on_play handler allando flaget allit.")
            support_status = "partial" if support_status in {"supported", "partial"} else support_status
        else:
            notes.append("field_runtime: explicit on_play handler nem latszik.")
            support_status = "uncertain" if support_status == "supported" else support_status

    if not detected_keywords:
        notes.append("keywords: none")
    if not detected_effect_tags:
        notes.append("effects: none")

    return {
        "card_name": card_name,
        "card_type": card_type,
        "raw_ability": raw_ability,
        "zone_dependency": ";".join(zone_dependency),
        "detected_keywords": ";".join(detected_keywords),
        "detected_effect_tags": ";".join(detected_effect_tags),
        "support_status": support_status,
        "evidence_files": sorted(evidence),
        "notes": notes,
    }


def generate_clan_rule_audit_by_card_type(path: str, realm: str, clan: str = ""):
    rows = load_cards_rows(path)
    clan_value = repair_mojibake(clan or "")
    registries = _resolver_registry_snapshot()

    scoped_rows = [
        row for row in rows
        if row.get("Birodalom", "") == realm
        and normalize_lookup_text(row.get("Klán", "")) == normalize_lookup_text(clan_value)
    ]

    audit_rows = [_card_specific_support(row, registries) for row in scoped_rows]
    type_counter = collections.Counter(row["card_type"] for row in audit_rows)
    status_counter = collections.Counter(row["support_status"] for row in audit_rows)
    by_type_status = collections.defaultdict(collections.Counter)
    for row in audit_rows:
        by_type_status[row["card_type"]][row["support_status"]] += 1

    output_path = pathlib.Path("stats") / f"clan_audit_{_safe_slugify(realm)}_{_safe_slugify(clan_value)}_by_card_type.md"
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# Clan Audit: {realm} / {clan_value}\n\n")
        handle.write("## Summary\n\n")
        handle.write(f"- Cards audited: {len(audit_rows)}\n")
        for card_type in ("Entitás", "Rituálé", "Ige", "Jel", "Sík"):
            if type_counter.get(card_type):
                handle.write(f"- {card_type}: {type_counter[card_type]}\n")
        handle.write("\n### Support Status\n\n")
        for status in ("supported", "partial", "uncertain", "missing"):
            handle.write(f"- {status}: {status_counter.get(status, 0)}\n")

        for card_type in ("Entitás", "Rituálé", "Ige", "Jel", "Sík"):
            typed_rows = [row for row in audit_rows if row["card_type"] == card_type]
            if not typed_rows:
                continue
            handle.write(f"\n## {card_type}\n\n")
            handle.write("| card_name | card_type | zone_dependency | detected_keywords | detected_effect_tags | support_status | evidence_files | notes |\n")
            handle.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")
            for row in typed_rows:
                notes = " ; ".join(row["notes"]).replace("\n", " ")
                raw = row["raw_ability"].replace("\n", " ")
                evidence = "; ".join(row["evidence_files"])
                handle.write(
                    f"| {row['card_name']} | {row['card_type']} | {row['zone_dependency'] or '-'} | {row['detected_keywords'] or '-'} | {row['detected_effect_tags'] or '-'} | {row['support_status']} | {evidence or '-'} | raw_ability: {raw} ; {notes} |\n"
                )

    return {
        "output_path": str(output_path),
        "realm": realm,
        "clan": clan_value,
        "cards": audit_rows,
        "type_counter": type_counter,
        "status_counter": status_counter,
        "by_type_status": by_type_status,
    }


TRAP_VALIDATION_RULES = {
    "forro talaj": {
        "activation_status": "supported",
        "trigger_support": "metadata trigger: on_attack_declared; engine dispatch: engine/game.py harc_fazis -> trigger_engine.dispatch('on_attack_declared'); generic combat trap consumption path bizonyitott.",
        "dispatch_support": "generic combat trap path: engine/game.py -> can_activate_trap(...) -> EffectEngine.trigger_on_trap(...); nincs explicit kartya-handler, de a generic trap adapter aktiv.",
        "effect_support": "supported",
        "final_status": "supported",
        "evidence_files": [
            "engine/game.py",
            "engine/effect_diagnostics_v2.py",
            "engine/structured_effects.py",
            "LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt",
        ],
        "notes": [
            "A logban tenylegesen lerakva, elfogyasztva es 2 sebzest okozva latszik.",
            "Nincs explicit handler, de mind az Aktiválás, mind a Hatás bizonyitott a generic trap utvonalon.",
        ],
    },
    "robbano pajzs": {
        "activation_status": "uncertain",
        "trigger_support": "Nincs Trigger_Felismerve metadata; az Aegis-feltetel nincs explicit preview vagy trigger-kotes ala huzva.",
        "dispatch_support": "Csak a generic combat trap utvonal latszik, amely nem bizonyitja az Aegis-specifikus aktivalasi feltetelt.",
        "effect_support": "uncertain",
        "final_status": "uncertain",
        "evidence_files": [
            "engine/game.py",
            "cards/resolver.py",
            "LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt",
        ],
        "notes": [
            "A logban a Jel lerakasa latszik, de tenyleges aktivalasi/hatas-visszaigazolas nem.",
            "A kartya csak akkor lehetne supported, ha az Aegishez kotott Aktiválás is bizonyitott lenne.",
        ],
    },
    "csapda a fustben": {
        "activation_status": "supported",
        "trigger_support": "Metadata trigger: on_enemy_summon; engine dispatch: engine/game.py _resolve_summon_traps; resolver SUMMON_TRAP_HANDLERS registryben benne van.",
        "dispatch_support": "summon trap dispatch explicit: cards/resolver.py SUMMON_TRAP_HANDLERS['csapda a fustben'] -> handle_csapda_a_fustben",
        "effect_support": "supported",
        "final_status": "supported",
        "evidence_files": [
            "cards/resolver.py",
            "cards/priority_handlers.py",
            "engine/game.py",
            "tests/test_priority_handlers.py",
            "LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt",
        ],
        "notes": [
            "A handler, a summon dispatch, a teszt es a log is egy iranyba mutat.",
            "Ez a Hamvaskezű Jel-reteg legjobban bizonyitott lapja.",
        ],
    },
    "hamis parancs": {
        "activation_status": "missing",
        "trigger_support": "Nincs Trigger_Felismerve metadata es nincs explicit trap preview/trigger-kotes a Pecsét elleni tamadas atiranyitasara.",
        "dispatch_support": "Nincs trap handler, summon trap handler vagy preview-regisztracio.",
        "effect_support": "missing",
        "final_status": "missing",
        "evidence_files": [
            "cards/resolver.py",
            "engine/game.py",
            "LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt",
        ],
        "notes": [
            "A logban a Jel lerakasa latszik, de nincs runtime bizonyitek az atiranyitasra.",
            "A Hatás komplex direct-seal attack redirect, amire jelenleg nincs konkret implementacio.",
        ],
    },
    "tuzes megtorlas": {
        "activation_status": "uncertain",
        "trigger_support": "Nincs Trigger_Felismerve metadata; a blokkolas soran meghalo tamado sajat egyseg feltetele nincs explicit modellezve.",
        "dispatch_support": "A log szerint a generic combat trap utvonal elfogyasztja, de ez nem ugyanaz, mint a szabaly szerinti Aktiválás.",
        "effect_support": "uncertain",
        "final_status": "uncertain",
        "evidence_files": [
            "engine/game.py",
            "engine/effect_diagnostics_v2.py",
            "engine/structured_effects.py",
            "LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt",
        ],
        "notes": [
            "Van logbeli aktivalas/elfogyasztas es fallback_text_resolved summary, de a hatas a logban hibasan +ATK iranyba csuszik.",
            "Ez pont tipikus pelda arra, amikor van runtime zaj, de a szabalyhuseg nincs bizonyitva.",
        ],
    },
    "langolo visszavagas": {
        "activation_status": "uncertain",
        "trigger_support": "Nincs Trigger_Felismerve metadata es nincs explicit trap preview a sajat Horizont-entitas elleni tamadasra.",
        "dispatch_support": "Nincs trap handler-regisztracio; legfeljebb a generic combat trap utvonal tudna probalkozni.",
        "effect_support": "uncertain",
        "final_status": "uncertain",
        "evidence_files": [
            "cards/resolver.py",
            "engine/game.py",
            "LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt",
        ],
        "notes": [
            "A logban a lap lerakasa latszik, de tenyleges aktivalasi/hatas-bizonyitek nem.",
            "A 4 sebzeses Hatás egyszeru lenne, de jelenleg nincs bekotve.",
        ],
    },
    "csapda a hamuban": {
        "activation_status": "supported",
        "trigger_support": "Metadata trigger: on_enemy_summon; az engine summon dispatch utvonala biztosan letezik.",
        "dispatch_support": "A summon trap dispatch letezik, de a kartya nincs benne a SUMMON_TRAP_HANDLERS registryben.",
        "effect_support": "missing",
        "final_status": "partial",
        "evidence_files": [
            "engine/game.py",
            "cards/resolver.py",
            "LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt",
        ],
        "notes": [
            "Az Aktiválás oldala bizonyitott, de a 3 sebzeses Hatásra nincs konkret runtime vegrehajtas.",
            "Ez tipikus 'trigger megvan, effect hianyzik' allapot.",
        ],
    },
    "izzo aura": {
        "activation_status": "missing",
        "trigger_support": "Nincs Trigger_Felismerve metadata; az enemy spell targetingre van ugyan engine event, de ez nincs ehhez a traphez kotve.",
        "dispatch_support": "Nincs trap handler vagy spell-trap regisztracio erre a lapra.",
        "effect_support": "missing",
        "final_status": "missing",
        "evidence_files": [
            "cards/resolver.py",
            "engine/effects.py",
            "cards/priority_handlers.py",
            "LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt",
        ],
        "notes": [
            "A lap szovege spell-negalast es kovetkezo korig tarto buffot ker.",
            "Ehhez jelenleg nincs bizonyitott Aktiválás + Hatás par a Hamvaskezű Jel retegben.",
        ],
    },
}

RULEBOOK_TRAP_BASELINES = [
    "Szabálykönyv: a Jel lapok a Zenitbe kerülnek, lefordítva.",
    "Szabálykönyv: egyszerre legfeljebb 2 aktív Jel lehet a Zenitben.",
    "Szabálykönyv: egy játékos körönként legfeljebb 2 Jelet aktiválhat.",
    "Szabálykönyv: a Jel kétlépcsős lapforma, külön Aktiválás és külön Hatás résszel.",
]


def generate_trap_validation(path: str, realm: str, clan: str = ""):
    rows = load_cards_rows(path)
    clan_value = repair_mojibake(clan or "")
    scoped_rows = [
        row for row in rows
        if row.get("Birodalom", "") == realm
        and normalize_lookup_text(row.get("Klán", "")) == normalize_lookup_text(clan_value)
        and row.get("Típus", "") == "Jel"
    ]

    validations = []
    status_counter = collections.Counter()

    for row in scoped_rows:
        name = row.get("Kártya név", "")
        raw_ability = row.get("Képesség", "")
        normalized_name = normalize_lookup_text(name)
        activation_condition, effect_resolution = _extract_trap_parts(raw_ability)
        rule = TRAP_VALIDATION_RULES.get(
            normalized_name,
            {
                "activation_status": "uncertain",
                "trigger_support": "Nincs kulon kezi validacios szabaly, csak altalanos audit-bizonyitek.",
                "dispatch_support": "Nincs kulon kezi validacios szabaly, csak altalanos audit-bizonyitek.",
                "effect_support": "uncertain",
                "final_status": "uncertain",
                "evidence_files": [],
                "notes": ["Nincs kulon kezi validacios szabaly erre a Jel lapra."],
            },
        )
        trigger_tokens = [token.strip() for token in _parse_semicolon_or_csv(row.get("Trigger_Felismerve", ""))]
        normalized_triggers = [TRIGGER_ALIASES.get(token, token) for token in trigger_tokens]
        notes = list(rule["notes"])
        notes.append("rulebook_basis: Jel = Aktiválás + Hatás; csak akkor supported, ha mindkettő bizonyított.")
        if normalized_triggers:
            notes.append("trigger_metadata: " + "; ".join(normalized_triggers))
        else:
            notes.append("trigger_metadata: none")

        validations.append(
            {
                "card_name": name,
                "raw_ability": raw_ability,
                "activation_condition": activation_condition or "-",
                "effect_resolution": effect_resolution or "-",
                "trigger_support": rule["trigger_support"],
                "dispatch_support": rule["dispatch_support"],
                "effect_support": rule["effect_support"],
                "evidence_files": rule["evidence_files"],
                "final_status": rule["final_status"],
                "notes": notes,
            }
        )
        status_counter[rule["final_status"]] += 1

    output_path = pathlib.Path("stats") / f"trap_validation_{_safe_slugify(realm)}_{_safe_slugify(clan_value)}.md"
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# Trap Validation: {realm} / {clan_value}\n\n")
        handle.write("## Rulebook Baseline\n\n")
        for line in RULEBOOK_TRAP_BASELINES:
            handle.write(f"- {line}\n")
        handle.write("\n")
        handle.write("## Summary\n\n")
        handle.write(f"- Trap cards validated: {len(validations)}\n")
        for status in ("supported", "partial", "uncertain", "missing"):
            handle.write(f"- {status}: {status_counter.get(status, 0)}\n")
        handle.write("\n")
        for row in validations:
            handle.write(f"## {row['card_name']}\n\n")
            handle.write(f"- raw_ability: {row['raw_ability']}\n")
            handle.write(f"- activation_condition: {row['activation_condition']}\n")
            handle.write(f"- effect_resolution: {row['effect_resolution']}\n")
            handle.write(f"- trigger_support: {row['trigger_support']}\n")
            handle.write(f"- dispatch_support: {row['dispatch_support']}\n")
            handle.write(f"- effect_support: {row['effect_support']}\n")
            handle.write(f"- evidence_files: {'; '.join(row['evidence_files']) or '-'}\n")
            handle.write(f"- final_status: {row['final_status']}\n")
            handle.write("- notes:\n")
            for note in row["notes"]:
                handle.write(f"  - {note}\n")
            handle.write("\n")

    return {
        "output_path": str(output_path),
        "realm": realm,
        "clan": clan_value,
        "cards": validations,
        "status_counter": status_counter,
    }


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

    output_path = pathlib.Path("stats") / f"effect_support_audit_{_safe_slugify(realm)}_{_safe_slugify(clan_value)}_simple.csv"
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

    output_clan = _safe_slugify(clan_value)
    output_realm = _safe_slugify(realm)
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
    elif "--clan-audit-by-type" in args:
        realm = "Ignis"
        clan = ""
        if "--realm" in args:
            realm = args[args.index("--realm") + 1]
        if "--clan" in args:
            clan = args[args.index("--clan") + 1]
        result = generate_clan_rule_audit_by_card_type(filepath, realm, clan)
        print(f"Clan rule audit generated: {result['output_path']}")
        print(f"Cards audited: {len(result['cards'])}")
        for card_type in ("Entitás", "Rituálé", "Ige", "Jel", "Sík"):
            print(f"{card_type}: {result['type_counter'].get(card_type, 0)}")
        for status in ("supported", "partial", "uncertain", "missing"):
            print(f"{status}: {result['status_counter'].get(status, 0)}")
    elif "--trap-validation" in args:
        realm = "Ignis"
        clan = ""
        if "--realm" in args:
            realm = args[args.index("--realm") + 1]
        if "--clan" in args:
            clan = args[args.index("--clan") + 1]
        result = generate_trap_validation(filepath, realm, clan)
        print(f"Trap validation generated: {result['output_path']}")
        print(f"Trap cards validated: {len(result['cards'])}")
        for status in ("supported", "partial", "uncertain", "missing"):
            print(f"{status}: {result['status_counter'].get(status, 0)}")
    else:
        audit_cards_xlsx(filepath)
