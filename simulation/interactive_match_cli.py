from __future__ import annotations

import argparse
from datetime import datetime
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
DEFAULT_CLI_LOG_DIR = os.path.join(PROGRAM_MAPPA, "test_logs_workspace", "interactive_cli")


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


class InteractiveCliSessionLogger:
    def __init__(self, log_dir: str = DEFAULT_CLI_LOG_DIR):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.path = os.path.join(self.log_dir, f"INTERACTIVE_CLI_{timestamp}.txt")

    def write(self, category: str, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] [{category}] {message}\n")

    def write_block(self, category: str, lines: Sequence[str]) -> None:
        self.write(category, "---")
        for line in list(lines or []):
            self.write(category, str(line))


def _human_player_name(snapshot: Optional[Dict], human_player_id: str) -> Optional[str]:
    if not snapshot:
        return None
    player_key = "p1" if human_player_id == "p1" else "p2"
    return ((snapshot.get(player_key) or {}).get("name")) or human_player_id


def render_snapshot(snapshot: Optional[Dict], *, human_player_id: str = "p1") -> List[str]:
    if not snapshot:
        return ["Nincs elerheto snapshot."]

    active_player = snapshot.get("active_player")
    human_player_name = _human_player_name(snapshot, human_player_id)
    turn_owner = "EMBER" if active_player == human_player_name else "AI"
    lines = [
        "=== AKTUALIS ALLAPOT ===",
        f"Kor: {snapshot.get('turn')} | Aktiv jatekos: {active_player} | Fazis: {snapshot.get('phase')}",
        f"Emberi oldal: {human_player_id} ({human_player_name or '-'}) | Soron: {turn_owner}",
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


def render_command_help() -> List[str]:
    return [
        "=== PARANCSOK ===",
        "szam = legal action vegrehajtasa",
        "a / ai = egy egyszeru AI step az aktualis aktiv jatekosnak",
        "o / opp = auto-opponent jellegu tovabblepes a kovetkezo emberi ponthoz",
        "r = allapot frissitese",
        "e = teljes event log",
        "h / ? = parancslista",
        "q = kilepes",
    ]


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
    parser.add_argument("--log-dir", default=DEFAULT_CLI_LOG_DIR, help="Kulon interactive CLI logkonyvtar.")
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
    log_dir: str = DEFAULT_CLI_LOG_DIR,
    input_func: Callable[[str], str] = input,
    print_func: Callable[[str], None] = print,
) -> Dict:
    match_id = None
    event_cursor = 0
    last_response = None
    session_logger = InteractiveCliSessionLogger(log_dir=log_dir)
    print_func(f"CLI naplo: {session_logger.path}")
    session_logger.write("SESSION_START", f"config={match_config}")
    session_logger.write("SESSION_START", f"human_player={human_player_id}")

    try:
        match_id = create_match(match_config)
    except Exception as exc:
        print_func("Nem sikerult meccset letrehozni.")
        print_func(f"Hiba: {exc}")
        session_logger.write("ERROR", f"startup_error={exc}")
        session_logger.write("SESSION_END", "status=startup_error")
        return {"status": "startup_error", "reason": str(exc), "match_id": None, "last_response": None, "log_path": session_logger.path}

    try:
        while True:
            snapshot = get_snapshot(match_id)
            result = get_match_result(match_id)

            snapshot_lines = render_snapshot(snapshot, human_player_id=human_player_id)
            for line in snapshot_lines:
                print_func(line)
            session_logger.write_block("SNAPSHOT", snapshot_lines)

            incremental_events = get_event_log(match_id, since_index=event_cursor)
            if incremental_events.get("reason") is None:
                new_events = incremental_events.get("events", [])
                if new_events:
                    event_lines = render_events(new_events)
                    for line in event_lines:
                        print_func(line)
                    session_logger.write_block("EVENTS", event_lines)
                event_cursor = incremental_events.get("next_index", event_cursor)

            if result and result.get("finished"):
                print_func("=== MECCS VEGE ===")
                print_func(
                    f"Gyoztes: {result.get('winner') or '-'} | ok: {result.get('victory_reason') or '-'}"
                )
                session_logger.write("SESSION_END", f"status=finished | winner={result.get('winner')} | reason={result.get('victory_reason')}")
                return {
                    "status": "finished",
                    "reason": result.get("victory_reason"),
                    "match_id": match_id,
                    "last_response": last_response,
                    "log_path": session_logger.path,
                }

            active_player = (snapshot or {}).get("active_player")
            actions = get_legal_actions(match_id, active_player) or []
            action_lines = render_legal_actions(actions)
            for line in action_lines:
                print_func(line)
            session_logger.write_block("LEGAL_ACTIONS", action_lines)
            for line in render_command_help():
                print_func(line)

            if not actions:
                print_func("Nincs tamogatott legal action ezen a ponton. A CLI itt megall.")
                session_logger.write("SESSION_END", "status=no_legal_actions")
                return {
                    "status": "no_legal_actions",
                    "reason": "no_legal_actions",
                    "match_id": match_id,
                    "last_response": last_response,
                    "log_path": session_logger.path,
                }

            print_func("Valassz akciot: szam | a=AI step | o=auto opponent | r=frissit | e=event log | h=segitseg | q=kilepes")
            raw_choice = input_func("> ").strip().lower()
            session_logger.write("COMMAND", f"choice={raw_choice or '<empty>'} | active_player={active_player}")
            if raw_choice == "q":
                session_logger.write("SESSION_END", "status=quit")
                return {"status": "quit", "reason": None, "match_id": match_id, "last_response": last_response, "log_path": session_logger.path}
            if raw_choice == "r":
                continue
            if raw_choice in {"h", "?"}:
                for line in render_command_help():
                    print_func(line)
                continue
            if raw_choice == "e":
                full_log = get_event_log(match_id, since_index=0)
                full_event_lines = render_events(full_log.get("events", []), header="=== TELJES EVENT LOG ===")
                for line in full_event_lines:
                    print_func(line)
                session_logger.write_block("FULL_EVENT_LOG", full_event_lines)
                continue
            if raw_choice in {"a", "ai"}:
                step_result = run_ai_step(match_id)
                last_response = step_result.get("response") or last_response
                session_logger.write("AI_STEP", f"player={step_result.get('player')} | action={step_result.get('action')}")
                ai_lines = render_ai_step_result(step_result)
                for line in ai_lines:
                    print_func(line)
                session_logger.write_block("AI_STEP", ai_lines)
                if step_result.get("response"):
                    action_result_lines = render_action_result(step_result["response"])
                    for line in action_result_lines:
                        print_func(line)
                    session_logger.write_block("ACTION_RESULT", action_result_lines)
                    response_event_lines = render_events(step_result["response"].get("events", []))
                    for line in response_event_lines:
                        print_func(line)
                    session_logger.write_block("EVENTS", response_event_lines)
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
                    session_logger.write("AUTO_OPPONENT", f"mode=end_turn_handover | human_player={human_player_id}")
                    auto_result_lines = render_action_result(auto_response)
                    for line in auto_result_lines:
                        print_func(line)
                    session_logger.write_block("ACTION_RESULT", auto_result_lines)
                    auto_event_lines = render_events(auto_response.get("events", []))
                    for line in auto_event_lines:
                        print_func(line)
                    session_logger.write_block("EVENTS", auto_event_lines)
                    if auto_response.get("events"):
                        last_event = auto_response["events"][-1]
                        if last_event.get("index") is not None:
                            event_cursor = int(last_event["index"]) + 1
                else:
                    step_result = run_ai_step(match_id, active_player)
                    last_response = step_result.get("response") or last_response
                    print_func("=== AUTO OPPONENT ===")
                    session_logger.write("AUTO_OPPONENT", f"mode=single_ai_step | player={active_player}")
                    auto_ai_lines = render_ai_step_result(step_result)
                    for line in auto_ai_lines:
                        print_func(line)
                    session_logger.write_block("AI_STEP", auto_ai_lines)
                    if step_result.get("response"):
                        auto_action_lines = render_action_result(step_result["response"])
                        for line in auto_action_lines:
                            print_func(line)
                        session_logger.write_block("ACTION_RESULT", auto_action_lines)
                        auto_event_lines = render_events(step_result["response"].get("events", []))
                        for line in auto_event_lines:
                            print_func(line)
                        session_logger.write_block("EVENTS", auto_event_lines)
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
            session_logger.write("USER_ACTION", f"action={action}")
            validation = validate_action(match_id, active_player, action)
            if not validation.get("valid"):
                print_func(f"Az action validacioja megbukott: {validation.get('reason')}")
                session_logger.write("VALIDATION_FAIL", f"reason={validation.get('reason')} | action={action}")
                continue

            response = apply_action(match_id, active_player, action)
            last_response = response
            action_result_lines = render_action_result(response)
            for line in action_result_lines:
                print_func(line)
            session_logger.write_block("ACTION_RESULT", action_result_lines)
            response_event_lines = render_events(response.get("events", []))
            for line in response_event_lines:
                print_func(line)
            session_logger.write_block("EVENTS", response_event_lines)
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
        log_dir=args.log_dir,
        input_func=input_func,
        print_func=print_func,
    )


if __name__ == "__main__":
    main()
