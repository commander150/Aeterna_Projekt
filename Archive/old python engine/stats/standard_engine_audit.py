from __future__ import annotations

import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.loader import load_card_rows_xlsx
from engine.card_metadata import parse_semicolon_list

XLSX_PATH = ROOT / "cards.xlsx"
SUMMARY_PATH = ROOT / "stats" / "standard_integration_summary.md"
AUDIT_PATH = ROOT / "stats" / "standard_engine_compliance_audit.md"


INTEGRATION_FILES = [
    "data/loader.py",
    "engine/card.py",
    "engine/card_metadata.py",
    "engine/structured_effects.py",
    "tests/test_card_model.py",
    "tests/test_structured_effects.py",
]


def _split_tokens(value):
    tokens = []
    for item in parse_semicolon_list(value):
        for part in str(item).replace(",", ";").split(";"):
            cleaned = part.strip()
            if cleaned:
                tokens.append(cleaned)
    return tokens


def _uniq(rows, field_name):
    values = []
    for row in rows:
        for token in _split_tokens(row.get(field_name, "")):
            if token not in values:
                values.append(token)
    return values


def _condition_patterns(rows):
    patterns = collections.Counter()
    for row in rows:
        raw = (row.get("feltetel_felismerve") or "").strip()
        if not raw:
            continue
        lowered = raw.lower()
        if any(key in lowered for key in ("kovetkezo", "next")):
            patterns["next_turn_effect"] += 1
        if any(key in lowered for key in ("elso", "masodik", "harmadik", "first", "second", "third")):
            patterns["nth_time_in_turn"] += 1
        if any(key in lowered for key in ("aura", "rezonancia", "harmoniz")):
            patterns["aura_state_dependent"] += 1
        if any(key in lowered for key in ("lane", "aramlat", "oszlop")):
            patterns["lane_dependent"] += 1
        if any(key in lowered for key in ("temeto", "graveyard", "uresseg")):
            patterns["graveyard_state"] += 1
        if any(key in lowered for key in ("pecset", "seal")):
            patterns["seal_state"] += 1
        if not any(
            key in lowered
            for key in ("kovetkezo", "next", "elso", "masodik", "harmadik", "first", "second", "third", "aura", "rezonancia", "harmoniz", "lane", "aramlat", "oszlop", "temeto", "graveyard", "uresseg", "pecset", "seal")
        ):
            patterns["simple_other"] += 1
    return patterns


ZONE_SUPPORT = {
    "horizont": ("teljesen támogatott", ["engine/game.py", "engine/actions.py", "engine/structured_effects.py"], "A core harc- és zónalogika explicit Horizont-támogatással fut."),
    "zenit": ("teljesen támogatott", ["engine/game.py", "engine/actions.py", "engine/structured_effects.py"], "A Zenit zóna külön sorlogikával és mozgással támogatott."),
    "dominium": ("részben támogatott", ["engine/game.py", "cards/priority_handlers.py"], "A Domínium több helyen összefoglaló fogalomként szerepel, de nem minden effect-route használ explicit dominium-szűrést."),
    "graveyard": ("teljesen támogatott", ["engine/actions.py", "cards/priority_handlers.py"], "Temető/Üresség alapú mozgatások és recursion már léteznek."),
    "hand": ("teljesen támogatott", ["engine/actions.py", "engine/player.py"], "Kézbe visszavétel és húzás támogatott."),
    "deck": ("teljesen támogatott", ["engine/player.py", "engine/structured_effects.py"], "Pakli tetejére helyezés és húzás támogatott."),
    "source": ("teljesen támogatott", ["engine/player.py", "cards/priority_handlers.py"], "Ősforrás/Aura kezelés külön runtime-logikával él."),
    "seal_row": ("teljesen támogatott", ["engine/game.py", "engine/effects.py"], "Pecsét-sor és direkt Pecsét-sebzés támogatott."),
    "aeternal": ("részben támogatott", ["engine/game.py", "engine/effects.py"], "A játékos/Aeternal közvetlen sebzése megvan, de nem minden célzás routolt explicit `aeternal` tokenre."),
    "lane": ("beköthető kis módosítással", ["engine/game.py", "engine/actions.py"], "Az áramlat/lane index a motorban implicit jelen van, de kevés helyen strukturált mezőből vezetett."),
}

KEYWORD_SUPPORT = {
    "aegis": ("teljesen támogatott", ["engine/keyword_engine.py", "engine/targeting.py", "engine/game.py"], "Blokkolási és célzási következményekkel együtt kezelt keyword."),
    "bane": ("teljesen támogatott", ["engine/keyword_engine.py"], "Sebzés utáni megjelölés és megsemmisítés támogatott."),
    "burst": ("részben támogatott", ["engine/effect_diagnostics_v2.py", "cards/resolver.py"], "Burst runtime-ban kezelt, de szabálykönyvileg Surge-kapcsolt és nem mindenhol teljesen generic."),
    "celerity": ("teljesen támogatott", ["engine/keyword_engine.py", "engine/card.py"], "Gyorsaság belépéskor azonnal feloldja a kimerülést."),
    "clarion": ("részben támogatott", ["engine/effect_diagnostics_v2.py", "cards/resolver.py"], "Több Clarion lap explicit kezelt, de nem minden Clarion generic keywordként oldódik fel."),
    "echo": ("részben támogatott", ["engine/keyword_engine.py", "cards/resolver.py"], "Van death-route és több explicit handler, de nem minden Echo teljesen generikus."),
    "ethereal": ("teljesen támogatott", ["engine/keyword_engine.py", "engine/targeting.py"], "Légi/ethereal blokkolási és célzási korlátok támogatottak."),
    "harmonize": ("teljesen támogatott", ["engine/keyword_engine.py", "engine/game.py"], "Harmonize bonusz explicit runtime függvénnyel kezelt."),
    "resonance": ("teljesen támogatott", ["engine/keyword_engine.py", "engine/player.py"], "Rezonancia támadásmódosítóként támogatott."),
    "sundering": ("teljesen támogatott", ["engine/keyword_engine.py", "engine/game.py"], "Hasítás extra pecséttörés útvonallal támogatott."),
    "taunt": ("beköthető kis módosítással", ["engine/keyword_engine.py", "engine/game.py"], "A kötelező célzás logikája még nincs explicit keywordként végigvezetve."),
}

TRIGGER_SUPPORT = {
    "static": ("teljesen támogatott", ["engine/structured_effects.py", "engine/effect_diagnostics_v2.py"], "Passzív/statikus lapok elkülönítése megvan."),
    "on_play": ("teljesen támogatott", ["cards/resolver.py", "engine/effect_diagnostics_v2.py"], "On-play handler routing stabil."),
    "on_summon": ("teljesen támogatott", ["engine/triggers.py", "engine/game.py", "cards/priority_handlers.py"], "Summon dispatch és runtime routing támogatott."),
    "on_enemy_summon": ("teljesen támogatott", ["engine/game.py", "cards/priority_handlers.py"], "Ellenséges idézésre reagáló dispatch létezik."),
    "on_enemy_zenit_summon": ("beköthető kis módosítással", ["engine/game.py"], "A summon payloadban zóna adott, de kevés explicit trap/handler használja generikusan."),
    "on_attack_declared": ("teljesen támogatott", ["engine/game.py", "cards/priority_handlers.py"], "Támadásdeklarációs csapdák és reakciók működnek."),
    "on_attack_hits": ("részben támogatott", ["engine/game.py"], "Betörés és találat útvonal megvan, de nincs teljes generic trigger routing."),
    "on_combat_damage_dealt": ("teljesen támogatott", ["engine/keyword_engine.py", "engine/triggers.py"], "Külön trigger dispatch létezik."),
    "on_combat_damage_taken": ("beköthető kis módosítással", ["engine/triggers.py", "engine/effects.py"], "Sebzés payload rendelkezésre áll, de kevés explicit consumer használja."),
    "on_block_survived": ("részben támogatott", ["engine/keyword_engine.py"], "Első túlélés/combat survived részben támogatott, de nem teljes generic blokktúlélési trigger."),
    "on_damage_survived": ("részben támogatott", ["engine/effects.py", "cards/priority_handlers.py"], "Damage-survive jellegű állapot levezethető, de nincs egységes generic routing."),
    "on_enemy_spell_target": ("teljesen támogatott", ["engine/game.py", "cards/priority_handlers.py"], "Spell-target reakciók explicit útvonallal támogatottak."),
    "on_enemy_spell_or_ritual_played": ("beköthető kis módosítással", ["engine/effect_diagnostics_v2.py", "cards/resolver.py"], "Spell/ritual kategória részben routolható, de nincs mindenhol egységes esemény."),
    "on_turn_end": ("teljesen támogatott", ["engine/game.py"], "Kör végi cleanup és időzített buffok támogatottak."),
    "on_next_own_awakening": ("beköthető kis módosítással", ["engine/game.py"], "Körfázisok adottak, de következő saját ébredésre célzott markerkezelés még nem egységes."),
    "on_influx_phase": ("beköthető kis módosítással", ["engine/game.py"], "Beáramlás fázis létezik, de kevés strukturált effect route használja."),
    "on_heal": ("beköthető kis módosítással", ["engine/structured_effects.py"], "Gyógyítás támogatott, de heal-trigger routing nem teljes."),
    "on_position_swap": ("beköthető kis módosítással", ["engine/actions.py", "engine/triggers.py"], "Pozícióváltás trigger dispatch létezik, de kevés explicit subscriberrel."),
    "on_entity_enters_horizont": ("beköthető kis módosítással", ["engine/actions.py", "engine/game.py"], "Zónamozgásból levezethető."),
    "on_source_placement": ("beköthető kis módosítással", ["main.py", "engine/player.py"], "Ősforrásba helyezés játékszinten megvan, trigger routing korlátozott."),
    "on_seal_break": ("részben támogatott", ["engine/game.py"], "Surge/Burst alaphelyzet megvan, de nem minden seal-break trigger generic."),
    "on_bounce": ("beköthető kis módosítással", ["engine/actions.py", "cards/priority_handlers.py"], "Kézbe visszavétel van, bounce event kevésbé egységes."),
    "on_trap_triggered": ("beköthető kis módosítással", ["engine/game.py", "cards/priority_handlers.py"], "Trap fogyasztási pontok adottak, de külön meta-trigger nincs végigkötve."),
    "on_ready_from_exhausted": ("beköthető kis módosítással", ["engine/game.py", "engine/player.py"], "Újraaktiválási limit és állapot van, de nincs külön generic esemény."),
    "on_stat_gain": ("új engine-logikát igényel", ["engine/triggers.py"], "Stat gain routing nincs explicit globális triggerként felépítve."),
    "on_gain_keyword": ("beköthető kis módosítással", ["cards/priority_handlers.py"], "Ideiglenes keyword-adás támogatott, de esemény-dispatch nem egységes."),
    "on_destroy": ("teljesen támogatott", ["engine/effects.py", "engine/triggers.py", "cards/priority_handlers.py"], "Megsemmisítés és halál trigger útvonal támogatott."),
    "on_discard": ("beköthető kis módosítással", ["engine/player.py", "cards/priority_handlers.py"], "Dobatás részben van, discard-trigger routing nem egységes."),
    "on_enemy_card_played": ("beköthető kis módosítással", ["engine/game.py"], "Kijátszási pontok felismerhetők, de nincs teljesen közös esemény minden laptípusra."),
    "on_enemy_second_summon_in_turn": ("új engine-logikát igényel", ["engine/game.py"], "Turn-scoped summon számláló nincs általánosan modellezve."),
    "on_start_of_turn": ("teljesen támogatott", ["engine/game.py"], "Turn start/awakening fázis explicit."),
}

TARGET_SUPPORT = {
    "self": ("teljesen támogatott", ["cards/priority_handlers.py"], "Önmagára ható route több helyen explicit."),
    "own_entity": ("teljesen támogatott", ["engine/structured_effects.py", "cards/priority_handlers.py"], "Saját entitás célzás széles körben támogatott."),
    "other_own_entity": ("teljesen támogatott", ["cards/priority_handlers.py"], "Másik saját entitás választása explicit mintákkal megoldott."),
    "enemy_entity": ("teljesen támogatott", ["engine/effects.py", "engine/structured_effects.py"], "Általános ellenséges entitás célzás támogatott."),
    "own_horizont_entity": ("teljesen támogatott", ["engine/structured_effects.py", "cards/priority_handlers.py"], "Saját Horizont célzás támogatott."),
    "enemy_horizont_entity": ("teljesen támogatott", ["engine/structured_effects.py", "engine/effects.py"], "Ellenséges Horizont célzás támogatott."),
    "own_zenit_entity": ("részben támogatott", ["cards/priority_handlers.py", "engine/actions.py"], "Zenit-entitások kezelhetők, de nem minden generic célzás fedett."),
    "enemy_zenit_entity": ("részben támogatott", ["engine/structured_effects.py", "engine/game.py"], "Zenit-célzás részben támogatott."),
    "own_entities": ("teljesen támogatott", ["cards/priority_handlers.py", "engine/actions.py"], "Tömeges saját entitás iteráció adott."),
    "enemy_entities": ("teljesen támogatott", ["engine/structured_effects.py", "engine/actions.py"], "Tömeges ellenséges entitás iteráció adott."),
    "own_seal": ("részben támogatott", ["engine/game.py"], "Saját Pecsét sor elérhető, de kevés explicit saját-pecsét célzó route van."),
    "enemy_seal": ("teljesen támogatott", ["engine/effects.py", "engine/game.py"], "Direkt Pecsét-sebzés és betörés támogatott."),
    "enemy_seals": ("teljesen támogatott", ["engine/effects.py"], "Több Pecsétre menő direkt sebzés támogatott."),
    "opponent": ("teljesen támogatott", ["engine/effects.py", "engine/game.py"], "Ellenfél/Aeternal közvetlen célpont támogatott."),
    "lane": ("beköthető kis módosítással", ["engine/game.py", "engine/actions.py"], "Lane index a motorban él, de célpont-szinten nem egységesen modellezett."),
    "own_graveyard_entity": ("részben támogatott", ["cards/priority_handlers.py", "engine/actions.py"], "Temetőből visszahozás és válogatás részben támogatott."),
    "enemy_spell": ("teljesen támogatott", ["engine/game.py", "cards/priority_handlers.py"], "Spell-target reakciók explicit úton működnek."),
    "enemy_spell_or_ritual": ("beköthető kis módosítással", ["engine/game.py", "cards/priority_handlers.py"], "Kategória részben elérhető, egységesítés kell."),
    "own_source_card": ("részben támogatott", ["engine/player.py"], "Ősforrás lapok kezelése megvan, de célzásuk nem teljesen általános."),
    "enemy_source_card": ("beköthető kis módosítással", ["engine/player.py", "cards/priority_handlers.py"], "Forrás-zóna hozzáférhető, de kevés explicit target route van."),
}

EFFECT_SUPPORT = {
    "damage": ("teljesen támogatott", ["engine/effects.py", "engine/structured_effects.py", "cards/priority_handlers.py"], "Célzott sebzés központi pipeline-on megy."),
    "deal_damage": ("teljesen támogatott", ["engine/effects.py", "engine/structured_effects.py"], "A `damage` aliasa."),
    "heal": ("teljesen támogatott", ["engine/structured_effects.py", "cards/priority_handlers.py"], "Gyógyítás támogatott."),
    "draw": ("teljesen támogatott", ["engine/player.py", "engine/structured_effects.py"], "Húzás és extra húzás támogatott."),
    "discard": ("részben támogatott", ["cards/priority_handlers.py"], "Dobatás több lokális handlerben megvan, de nincs teljesen generikus pipeline."),
    "destroy": ("teljesen támogatott", ["engine/effects.py", "engine/structured_effects.py"], "Megsemmisítés támogatott."),
    "return_to_hand": ("teljesen támogatott", ["engine/actions.py", "engine/structured_effects.py"], "Kézbe visszavétel támogatott."),
    "seal_damage": ("teljesen támogatott", ["engine/effects.py", "engine/game.py"], "Direkt Pecsét-sebzés támogatott."),
    "move_horizont": ("teljesen támogatott", ["engine/actions.py", "engine/structured_effects.py"], "Horizontra mozgatás támogatott."),
    "move_zenit": ("teljesen támogatott", ["engine/actions.py", "engine/structured_effects.py"], "Zenitbe mozgatás támogatott."),
    "exhaust": ("teljesen támogatott", ["engine/structured_effects.py", "engine/game.py"], "Kimerítés támogatott."),
    "grant_keyword": ("részben támogatott", ["cards/priority_handlers.py", "engine/keyword_engine.py"], "Ideiglenes kulcsszóadás több helyen van, de nem teljesen generikus."),
    "cost_mod": ("részben támogatott", ["engine/player.py", "cards/priority_handlers.py"], "Költségmódosítás részben támogatott, de nem teljesen általános."),
    "graveyard_recursion": ("részben támogatott", ["engine/actions.py", "cards/priority_handlers.py"], "Visszahozás és temető-interakció több helyen működik."),
    "damage_prevention": ("részben támogatott", ["engine/effects.py", "cards/priority_handlers.py"], "Sebzésmegelőzés több lokális mintával működik."),
    "attack_restrict": ("részben támogatott", ["engine/game.py", "cards/priority_handlers.py"], "Támadástiltás van, de nem minden mintára egységes."),
    "block_restrict": ("beköthető kis módosítással", ["engine/keyword_engine.py", "engine/game.py"], "Blokkolási tiltás részben levezethető, de külön generic pipeline gyenge."),
    "once_per_turn": ("új engine-logikát igényel", ["engine/game.py"], "Általános turn-scoped once-per-turn state nincs egységesen modellálva."),
    "grant_attack": ("teljesen támogatott", ["cards/priority_handlers.py", "engine/structured_effects.py"], "ATK-bónusz támogatott."),
    "grant_temp_attack": ("teljesen támogatott", ["cards/priority_handlers.py", "engine/structured_effects.py"], "Ideiglenes ATK-bónusz támogatott."),
    "grant_hp": ("részben támogatott", ["cards/priority_handlers.py", "engine/structured_effects.py"], "HP-bónusz támogatott, de életciklus és cleanup nem mindenhol egységes."),
    "grant_max_hp": ("részben támogatott", ["cards/priority_handlers.py"], "Max HP növelés több explicit handlerben megvan."),
    "swap_position": ("részben támogatott", ["engine/actions.py", "engine/structured_effects.py"], "Pozíciócsere több explicit helyen létezik, de teljes lane-rearrangement még nem."),
    "reactivate": ("teljesen támogatott", ["engine/player.py", "engine/structured_effects.py"], "Újraaktiválás támogatott."),
    "immunity": ("részben támogatott", ["cards/priority_handlers.py", "engine/structured_effects.py"], "Immunitás lokális flag-ekkel részben támogatott."),
}

DURATION_SUPPORT = {
    "until_end_of_turn": ("teljesen támogatott", ["engine/game.py", "cards/priority_handlers.py"], "Kör végi cleanup széles körben támogatott."),
    "until_end_of_next_own_turn": ("részben támogatott", ["cards/priority_handlers.py"], "Van rá lokális minta, de még nincs teljesen általános időzítés-réteg."),
    "until_end_of_combat": ("teljesen támogatott", ["engine/game.py", "engine/structured_effects.py"], "Harc végi buff-cleanup támogatott."),
    "permanent": ("részben támogatott", ["cards/priority_handlers.py", "engine/card.py"], "Állandó buffok és max HP növelések több helyen megvannak, de nincs egységes permanens effect réteg."),
    "static": ("részben támogatott", ["engine/structured_effects.py", "engine/effect_diagnostics_v2.py"], "Passzív/statikus lapok felismerése megvan, de nem mind explicit szimulált."),
    "instant": ("teljesen támogatott", ["engine/effect_diagnostics_v2.py", "cards/resolver.py"], "Azonnali kijátszású hatások támogatottak."),
}

HEAVY_MECHANICS = {
    "delayed revival": ("részben támogatott", "Van temetőből visszahozás, de késleltetett időzítés nem teljesen generikus."),
    "next-turn effects": ("részben támogatott", "Vannak lokális next-turn flag-ek, de nincs teljes általános scheduler."),
    "multi-phase / second combat phase logic": ("új engine-logikát igényel", "A körfázisok egyszeriek, második harcfázis nincs modellálva."),
    "attack nullification": ("részben támogatott", "Trap és combat flag-ekkel több helyen működik, de nem teljesen általános."),
    "redirect": ("részben támogatott", "Van több lokális redirect trap, de nincs teljes generic átirányítási rendszer."),
    "bounce with compensation": ("beköthető kis módosítással", "Bounce és plusz húzás/sebzés már meglévő primitívekkel összerakható."),
    "cost tax": ("beköthető kis módosítással", "Cost mod útvonal adott, csak ellenfél-adó jellegű routing kell."),
    "aura-state dependent conditions": ("részben támogatott", "Rezonancia és aura-limit jelen van, de nem minden feltétel generic."),
    "full lane swap logic": ("új engine-logikát igényel", "Komplex teljes pályasorrend-csere nincs egységesen kezelve."),
    "enemy forced movement": ("részben támogatott", "Mozgatás van, de összetettebb ellenfél-kényszerített átrendezés már nehezebb."),
    "board-wide rearrangement": ("új engine-logikát igényel", "Teljes táblarendezés nincs meg."),
    "first time this turn / second summon this turn / third draw this turn": ("új engine-logikát igényel", "Néhány limit van, de általános számláló-réteg nincs."),
    "spell metadata driven effects": ("beköthető kis módosítással", "A strukturált mezők már elérhetők, további routing kell."),
    "source manipulation": ("részben támogatott", "Ősforrás hozzáférés van, de komplex source-manipulation még nem teljes."),
    "seal restoration": ("beköthető kis módosítással", "Pecsétsor modell adott, visszaállítás csak részben explicit."),
    "temporary control change": ("új engine-logikát igényel", "Tulajdonos/kontroll váltás nincs egységesen modellálva."),
    "top/bottom deck placement": ("részben támogatott", "Pakli teteje adott, alja nincs teljesen általános útvonalon."),
    "out-of-combat mutual damage": ("beköthető kis módosítással", "Sebzéspipeline adott, csak új routing kell."),
    "conditional replacement effects": ("új engine-logikát igényel", "Would/Instead replacement réteg nincs."),
    "\"would die instead...\" prevention/replacement": ("új engine-logikát igényel", "Halál-helyettesítő effekt-réteg nincs egységesen jelen."),
}


def _lookup(mapping, value):
    key = value.lower()
    return mapping.get(key) or ("beköthető kis módosítással", ["cards/resolver.py"], "Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik.")


def _write_summary(rows, validation_issues):
    type_counts = collections.Counter((row.get("kartyatipus") or "").strip() or "<ures>" for row in rows)
    status_counts = collections.Counter((row.get("ertelmezesi_statusz") or "").strip() or "<ures>" for row in rows)
    lines = [
        "# Új táblázat-szabvány integráció összefoglaló",
        "",
        "## Módosított fájlok",
        "",
    ]
    for path in INTEGRATION_FILES:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Mit állított át a rendszer",
            "",
            "- A `cards.xlsx` 22 oszlopos szerkezetét név-alapú fejlécekkel kezeli.",
            "- A loader normalizálja a listás mezőket, a számokat és a `blank` / `none` üresjelöléseket.",
            "- A `Kartya` modell explicit módon tartalmazza a canonical, zone, keyword, trigger, target, effect tag, duration, condition, machine description, interpretation status és engine notes mezőket.",
            "- A structured effect réteg már a felismert zónákat és az időtartam egy részét is figyelembe veszi.",
            "- A loader validációs figyelmeztetéseket ad ismeretlen enum értékekre és gyanús kombinációkra.",
            "",
            "## Jelenlegi cards.xlsx összkép",
            "",
            f"- Betöltött sorok száma: `{len(rows)}`",
            f"- Validációs figyelmeztetések: `{len(validation_issues)}`",
            "",
            "### Kártyatípus megoszlás",
            "",
        ]
    )
    for card_type, count in type_counts.most_common():
        lines.append(f"- `{card_type}`: `{count}`")
    lines.extend(["", "### Értelmezési státusz megoszlás", ""])
    for status, count in status_counts.most_common():
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(["", "### Validációs minta", ""])
    if validation_issues:
        for issue in validation_issues[:25]:
            lines.append(f"- `{issue}`")
        if len(validation_issues) > 25:
            lines.append(f"- `... további {len(validation_issues) - 25} figyelmeztetés`")
    else:
        lines.append("- Nincs validációs figyelmeztetés.")
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def _write_table(lines, title, values, mapping):
    lines.extend([f"## {title}", "", "| Elem | Besorolás | Bizonyíték | Megjegyzés |", "| --- | --- | --- | --- |"])
    for value in values:
        status, evidence, note = _lookup(mapping, value)
        evidence_text = ", ".join(f"`{item}`" for item in evidence)
        lines.append(f"| `{value}` | {status} | {evidence_text} | {note} |")
    lines.append("")


def _write_audit(rows):
    lines = [
        "# Szabvány ↔ engine megfelelőségi audit",
        "",
        f"Forrás: `{XLSX_PATH.name}` és a jelenlegi élő kód.",
        "",
        "## Döntési kategóriák",
        "",
        "- `teljesen támogatott`",
        "- `részben támogatott`",
        "- `beköthető kis módosítással`",
        "- `új engine-logikát igényel`",
        "",
    ]
    _write_table(lines, "Zóna_Felismerve", _uniq(rows, "zona_felismerve"), ZONE_SUPPORT)
    _write_table(lines, "Kulcsszavak_Felismerve", _uniq(rows, "kulcsszavak_felismerve"), KEYWORD_SUPPORT)
    _write_table(lines, "Trigger_Felismerve", _uniq(rows, "trigger_felismerve"), TRIGGER_SUPPORT)
    _write_table(lines, "Célpont_Felismerve", _uniq(rows, "celpont_felismerve"), TARGET_SUPPORT)
    _write_table(lines, "Hatáscímkék", _uniq(rows, "hatascimkek"), EFFECT_SUPPORT)
    _write_table(lines, "Időtartam_Felismerve", _uniq(rows, "idotartam_felismerve"), DURATION_SUPPORT)

    patterns = _condition_patterns(rows)
    lines.extend(["## Feltétel_Felismerve minták", "", "| Minta | Darab | Besorolás | Megjegyzés |", "| --- | --- | --- | --- |"])
    pattern_notes = {
        "next_turn_effect": ("részben támogatott", "Vannak next-turn flag-ek, de nincs teljes általános scheduler."),
        "nth_time_in_turn": ("új engine-logikát igényel", "Általános turn-scoped eseményszámláló kell hozzá."),
        "aura_state_dependent": ("részben támogatott", "Aura/rezonancia feltételek részben kezeltek."),
        "lane_dependent": ("beköthető kis módosítással", "Lane index rendelkezésre áll, explicit routing kell."),
        "graveyard_state": ("részben támogatott", "Temető állapot elérhető, de nem minden feltétel generikus."),
        "seal_state": ("részben támogatott", "Pecsétállapot kezelhető, de nem minden csomópont routolt."),
        "simple_other": ("beköthető kis módosítással", "Egyszerű feltételadapterrel levezethető."),
    }
    for key, count in patterns.items():
        status, note = pattern_notes[key]
        lines.append(f"| `{key}` | `{count}` | {status} | {note} |")
    lines.append("")

    lines.extend(["## Külön nehéz mechanikák", "", "| Mechanika | Besorolás | Megjegyzés |", "| --- | --- | --- |"])
    for mechanic, (status, note) in HEAVY_MECHANICS.items():
        lines.append(f"| `{mechanic}` | {status} | {note} |")
    lines.append("")

    AUDIT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    rows, validation_issues = load_card_rows_xlsx(str(XLSX_PATH))
    _write_summary(rows, validation_issues)
    _write_audit(rows)
    print(f"Generated: {SUMMARY_PATH}")
    print(f"Generated: {AUDIT_PATH}")


if __name__ == "__main__":
    main()
