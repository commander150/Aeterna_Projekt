from __future__ import annotations

import argparse
import os
from typing import Callable, Dict, List, Optional, Sequence

from backend.facade import (
    apply_action,
    create_match,
    drop_match,
    get_event_log,
    get_legal_actions,
    get_match_result,
    get_snapshot,
    run_ai_step,
    validate_action,
)
from simulation.config import normalize_realm_name


PROGRAM_MAPPA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_XLSX_PATH = os.path.join(PROGRAM_MAPPA, "cards.xlsx")


def build_match_config(
    *,
    player1_realm: Optional[str] = None,
    player2_realm: Optional[str] = None,
    random_seed: Optional[int] = None,
    random_realm_fallback: bool = True,
    xlsx_path: str = DEFAULT_XLSX_PATH,
    extra_config: Optional[Dict] = None,
) -> Dict:
    config = {
        "player1_realm": normalize_realm_name(player1_realm),
        "player2_realm": normalize_realm_name(player2_realm),
        "random_seed": random_seed,
        "random_realm_fallback": random_realm_fallback,
        "xlsx_path": xlsx_path,
    }
    if extra_config:
        config.update(dict(extra_config))
    return config


def _slot_label(slot: Optional[Dict]) -> str:
    if not slot or slot.get("kind") == "empty":
        return "."
    card = slot.get("card") or {}
    name = card.get("name") or "?"
    if slot.get("hidden"):
        return f"[hidden:{name}]"
    return name


def _summarize_cards(cards: Sequence[Dict], max_items: int = 6) -> str:
    names = [str((card or {}).get("name") or "?") for card in list(cards or [])]
    if not names:
        return "-"
    if len(names) <= max_items:
        return ", ".join(names)
    visible = ", ".join(names[:max_items])
    return f"{visible}, ... (+{len(names) - max_items})"


def render_snapshot(snapshot: Optional[Dict]) -> List[str]:
    if not snapshot:
        return ["Nincs elerheto snapshot."]

    lines = [
        "=== AKTUALIS ALLAPOT ===",
        f"Kor: {snapshot.get('turn')} | Aktiv jatekos: {snapshot.get('active_player')} | Fazis: {snapshot.get('phase')}",
        f"Meccs vege: {'igen' if snapshot.get('match_finished') else 'nem'} | Gyoztes: {snapshot.get('winner') or '-'}",
    ]

    for player_key in ("p1", "p2"):
        player = snapshot.get(player_key) or {}
        lines.append(
            f"{player_key.upper()} | nev={player.get('name')} | realm={player.get('realm')} | "
            f"pecset={player.get('seal_count')} | kez={player.get('hand_size')} | "
            f"osforras={player.get('source_count')} | pakli={player.get('deck_size')} | temeto={player.get('graveyard_size')}"
        )
        lines.append(f"  Kez: {_summarize_cards(player.get('hand_cards') or [])}")
        horizont = " | ".join(
            f"{index}:{_slot_label(slot)}" for index, slot in enumerate(player.get("horizont") or [])
        )
        zenit = " | ".join(
            f"{index}:{_slot_label(slot)}" for index, slot in enumerate(player.get("zenit") or [])
        )
        lines.append(f"  Horizont: {horizont or '-'}")
        lines.append(f"  Zenit: {zenit or '-'}")

    return lines


def render_legal_actions(actions: Sequence[Dict]) -> List[str]:
    if not actions:
        return ["Nincs jelenleg tamogatott legal action."]

    lines = ["=== LEGAL AKCIOK ==="]
    for index, action in enumerate(actions, start=1):
        parts = [f"{index}.", str(action.get("action_type") or "?")]
        if action.get("card_name"):
            parts.append(f"lap={action['card_name']}")
        if action.get("zone"):
            parts.append(f"zona={action['zone']}")
        if action.get("lane") is not None:
            parts.append(f"lane={action['lane']}")
        if action.get("reason"):
            parts.append(f"ok={action['reason']}")
        if action.get("source"):
            parts.append(f"source={action['source']}")
        lines.append(" | ".join(parts))
    return lines


def render_events(events: Sequence[Dict], *, header: str = "=== UJ ESEMENYEK ===") -> List[str]:
    if not events:
        return [f"{header}", "Nincs uj esemeny."]

    lines = [header]
    for event in events:
        parts = [str(event.get("type") or "?")]
        if event.get("index") is not None:
            parts.append(f"idx={event['index']}")
        if event.get("player"):
            parts.append(f"player={event['player']}")
        if event.get("card_name"):
            parts.append(f"lap={event['card_name']}")
        if event.get("zone"):
            parts.append(f"zona={event['zone']}")
        if event.get("lane") is not None:
            parts.append(f"lane={event['lane']}")
        details = event.get("details") or {}
        if details:
            parts.append(f"details={details}")
        lines.append(" | ".join(parts))
    return lines


def render_action_result(response: Optional[Dict]) -> List[str]:
    if not response:
        return ["Nincs action-valasz."]

    result = response.get("result") or {}
    lines = [
        "=== ACTION EREDMENY ===",
        f"ok={response.get('ok')} | reason={response.get('reason') or '-'}",
    ]
    if result:
        lines.append(
            " | ".join(
                [
                    f"tipus={result.get('executed_action_type')}",
                    f"status={result.get('status')}",
                    f"lap={result.get('card_name') or '-'}",
                    f"zona={result.get('zone') or '-'}",
                    f"lane={result.get('lane') if result.get('lane') is not None else '-'}",
                    f"winner={result.get('winner') or '-'}",
                ]
            )
        )
        if result.get("details"):
            lines.append(f"details={result['details']}")
    return lines


def render_ai_step_result(step_result: Optional[Dict]) -> List[str]:
    if not step_result:
        return ["Nincs AI-step valasz."]

    lines = [
        "=== AI STEP ===",
        f"ok={step_result.get('ok')} | reason={step_result.get('reason') or '-'} | player={step_result.get('player') or '-'}",
    ]
    action = step_result.get("action") or {}
    if action:
        lines.append(
            "Valasztott akcio: "
            + " | ".join(
                [
                    f"tipus={action.get('action_type') or '-'}",
                    f"lap={action.get('card_name') or '-'}",
                    f"zona={action.get('zone') or '-'}",
                    f"lane={action.get('lane') if action.get('lane') is not None else '-'}",
                ]
            )
        )
    return lines


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AETERNA felvezerelt facade CLI prototipus emberi kiprobalashoz."
    )
    parser.add_argument("--p1", dest="player1_realm", help="P1 birodalom. Uresen hagyva veletlen.")
    parser.add_argument("--p2", dest="player2_realm", help="P2 birodalom. Uresen hagyva veletlen.")
    parser.add_argument("--seed", type=int, help="OpcionAlis random seed.")
    parser.add_argument("--human", choices=["p1", "p2"], default="p1", help="Melyik oldal az ember a CLI-ben.")
    parser.add_argument(
        "--no-random-fallback",
        action="store_true",
        help="Ha a megadott birodalom nem elerheto, ne valtson veletlenre.",
    )
    parser.add_argument("--xlsx-path", default=DEFAULT_XLSX_PATH, help="cards.xlsx eleresi ut.")
    return parser


def _prompt_optional_value(
    label: str,
    *,
    input_func: Callable[[str], str],
    print_func: Callable[[str], None],
) -> Optional[str]:
    print_func(label)
    value = input_func("> ").strip()
    return value or None


def prompt_start_configuration(
    *,
    input_func: Callable[[str], str],
    print_func: Callable[[str], None],
    xlsx_path: str = DEFAULT_XLSX_PATH,
) -> Dict:
    print_func("=== AETERNA FELVEZERELT CLI ===")
    print_func("Uj meccs indul. A birodalom uresen hagyhato, ilyenkor veletlen valasztas jon.")
    player1_realm = _prompt_optional_value("P1 birodalom (pl. Ignis, Aqua, Ventus, ures = veletlen):", input_func=input_func, print_func=print_func)
    player2_realm = _prompt_optional_value("P2 birodalom (pl. Ignis, Aqua, Ventus, ures = veletlen):", input_func=input_func, print_func=print_func)
    seed_value = _prompt_optional_value("Seed (ures = random):", input_func=input_func, print_func=print_func)
    random_seed = int(seed_value) if seed_value not in (None, "") else None
    return build_match_config(
        player1_realm=player1_realm,
        player2_realm=player2_realm,
        random_seed=random_seed,
        xlsx_path=xlsx_path,
    )


def launch_interactive_match_cli(
    *,
    match_config: Dict,
    human_player_id: str = "p1",
    input_func: Callable[[str], str] = input,
    print_func: Callable[[str], None] = print,
) -> Dict:
    match_id = None
    event_cursor = 0
    last_response = None

    try:
        match_id = create_match(match_config)
    except Exception as exc:
        print_func("Nem sikerult meccset letrehozni.")
        print_func(f"Hiba: {exc}")
        return {"status": "startup_error", "reason": str(exc), "match_id": None, "last_response": None}

    try:
        while True:
            snapshot = get_snapshot(match_id)
            result = get_match_result(match_id)

            for line in render_snapshot(snapshot):
                print_func(line)

            incremental_events = get_event_log(match_id, since_index=event_cursor)
            if incremental_events.get("reason") is None:
                new_events = incremental_events.get("events", [])
                if new_events:
                    for line in render_events(new_events):
                        print_func(line)
                event_cursor = incremental_events.get("next_index", event_cursor)

            if result and result.get("finished"):
                print_func("=== MECCS VEGE ===")
                print_func(
                    f"Gyoztes: {result.get('winner') or '-'} | ok: {result.get('victory_reason') or '-'}"
                )
                return {
                    "status": "finished",
                    "reason": result.get("victory_reason"),
                    "match_id": match_id,
                    "last_response": last_response,
                }

            active_player = (snapshot or {}).get("active_player")
            actions = get_legal_actions(match_id, active_player) or []
            for line in render_legal_actions(actions):
                print_func(line)

            if not actions:
                print_func("Nincs tamogatott legal action ezen a ponton. A CLI itt megall.")
                return {
                    "status": "no_legal_actions",
                    "reason": "no_legal_actions",
                    "match_id": match_id,
                    "last_response": last_response,
                }

            print_func("Valassz akciot: szam | a=egy AI-step | o=ellenfel/auto kor | r=frissit | e=teljes event log | q=kilepes")
            raw_choice = input_func("> ").strip().lower()
            if raw_choice == "q":
                return {"status": "quit", "reason": None, "match_id": match_id, "last_response": last_response}
            if raw_choice == "r":
                continue
            if raw_choice == "e":
                full_log = get_event_log(match_id, since_index=0)
                for line in render_events(full_log.get("events", []), header="=== TELJES EVENT LOG ==="):
                    print_func(line)
                continue
            if raw_choice in {"a", "ai"}:
                step_result = run_ai_step(match_id)
                last_response = step_result.get("response") or last_response
                for line in render_ai_step_result(step_result):
                    print_func(line)
                if step_result.get("response"):
                    for line in render_action_result(step_result["response"]):
                        print_func(line)
                    for line in render_events(step_result["response"].get("events", [])):
                        print_func(line)
                    if step_result["response"].get("events"):
                        last_event = step_result["response"]["events"][-1]
                        if last_event.get("index") is not None:
                            event_cursor = int(last_event["index"]) + 1
                continue
            if raw_choice in {"o", "opp", "opponent"}:
                if active_player == human_player_id or active_player == {"p1": "Jatekos_1", "p2": "Jatekos_2"}.get(human_player_id):
                    auto_response = apply_action(
                        match_id,
                        human_player_id,
                        {"action_type": "end_turn", "player": active_player},
                    )
                    last_response = auto_response
                    print_func("=== AUTO OPPONENT ===")
                    print_func("A motor az ember korvegetol a kovetkezo emberi dontesi pontig futott.")
                    for line in render_action_result(auto_response):
                        print_func(line)
                    for line in render_events(auto_response.get("events", [])):
                        print_func(line)
                    if auto_response.get("events"):
                        last_event = auto_response["events"][-1]
                        if last_event.get("index") is not None:
                            event_cursor = int(last_event["index"]) + 1
                else:
                    step_result = run_ai_step(match_id, active_player)
                    last_response = step_result.get("response") or last_response
                    print_func("=== AUTO OPPONENT ===")
                    for line in render_ai_step_result(step_result):
                        print_func(line)
                    if step_result.get("response"):
                        for line in render_action_result(step_result["response"]):
                            print_func(line)
                        for line in render_events(step_result["response"].get("events", [])):
                            print_func(line)
                        if step_result["response"].get("events"):
                            last_event = step_result["response"]["events"][-1]
                            if last_event.get("index") is not None:
                                event_cursor = int(last_event["index"]) + 1
                continue

            try:
                action_index = int(raw_choice) - 1
            except Exception:
                print_func("Ervenytelen valasztas. Adj meg egy sorszamot, vagy hasznald az r/e/q opciokat.")
                continue

            if action_index < 0 or action_index >= len(actions):
                print_func("A megadott sorszam nincs a legal action listaban.")
                continue

            action = dict(actions[action_index])
            validation = validate_action(match_id, active_player, action)
            if not validation.get("valid"):
                print_func(f"Az action validacioja megbukott: {validation.get('reason')}")
                continue

            response = apply_action(match_id, active_player, action)
            last_response = response
            for line in render_action_result(response):
                print_func(line)
            for line in render_events(response.get("events", [])):
                print_func(line)
            if response.get("events"):
                last_event = response["events"][-1]
                if last_event.get("index") is not None:
                    event_cursor = int(last_event["index"]) + 1
    finally:
        if match_id is not None:
            drop_match(match_id)


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    input_func: Callable[[str], str] = input,
    print_func: Callable[[str], None] = print,
) -> Dict:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    has_explicit_setup = any(
        value is not None
        for value in (
            args.player1_realm,
            args.player2_realm,
            args.seed,
        )
    )

    if has_explicit_setup:
        match_config = build_match_config(
            player1_realm=args.player1_realm,
            player2_realm=args.player2_realm,
            random_seed=args.seed,
            random_realm_fallback=not args.no_random_fallback,
            xlsx_path=args.xlsx_path,
        )
    else:
        match_config = prompt_start_configuration(
            input_func=input_func,
            print_func=print_func,
            xlsx_path=args.xlsx_path,
        )

    return launch_interactive_match_cli(
        match_config=match_config,
        human_player_id=args.human,
        input_func=input_func,
        print_func=print_func,
    )


if __name__ == "__main__":
    main()
