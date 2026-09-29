"""Convert exporter runtime card JSONL into runtime package cards JSONL."""

from __future__ import annotations

import json
from importlib import util
from pathlib import Path


try:
    from runtime_card_mapper import map_export_runtime_card
except ModuleNotFoundError:
    mapper_path = Path(__file__).resolve().with_name("runtime_card_mapper.py")
    spec = util.spec_from_file_location("runtime_card_mapper", mapper_path)
    runtime_card_mapper = util.module_from_spec(spec)
    spec.loader.exec_module(runtime_card_mapper)
    map_export_runtime_card = runtime_card_mapper.map_export_runtime_card


def convert_export_runtime_jsonl_to_cards_jsonl(input_path, output_path, strict=False):
    """Convert EXPORT_RUNTIME-style JSONL rows to runtime card JSONL rows."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    records = []
    diagnostics = []
    records_read = 0
    ok_count = 0
    error_count = 0

    with input_path.open("r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            if not line.strip():
                continue
            try:
                export_record = json.loads(line)
            except json.JSONDecodeError as exc:
                diagnostics.append(_diagnostic("INVALID_JSON", line_number, str(exc), blocking=True))
                error_count += 1
                continue

            if not isinstance(export_record, dict):
                diagnostics.append(_diagnostic("INVALID_RECORD", line_number, "JSONL row is not an object.", blocking=True))
                error_count += 1
                continue

            records_read += 1
            runtime_card = map_export_runtime_card(export_record)
            if runtime_card.get("mapping_status") == "error":
                error_count += 1
                diagnostics.append(
                    {
                        "severity": "error",
                        "code": "MAPPING_ERROR",
                        "line_number": line_number,
                        "blocking": True,
                        "record_diagnostics": runtime_card.get("diagnostics", []),
                    }
                )
            else:
                ok_count += 1
            records.append(runtime_card)

    should_write = not strict or error_count == 0
    records_written = 0
    if should_write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
            for record in records:
                output_file.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                records_written += 1

    return {
        "records_read": records_read,
        "records_written": records_written,
        "ok_count": ok_count,
        "error_count": error_count,
        "diagnostics": diagnostics,
    }


def _diagnostic(code, line_number, message, blocking):
    return {
        "severity": "error",
        "code": code,
        "line_number": line_number,
        "message": message,
        "blocking": blocking,
    }
