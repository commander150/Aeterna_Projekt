"""Prepare converted runtime card records for the sample package builder."""

from __future__ import annotations

import json
import uuid
from importlib import util
from pathlib import Path


try:
    from runtime_cards_jsonl_converter import convert_export_runtime_jsonl_to_cards_jsonl
except ModuleNotFoundError:
    converter_path = Path(__file__).resolve().with_name("runtime_cards_jsonl_converter.py")
    spec = util.spec_from_file_location("runtime_cards_jsonl_converter", converter_path)
    runtime_cards_jsonl_converter = util.module_from_spec(spec)
    spec.loader.exec_module(runtime_cards_jsonl_converter)
    convert_export_runtime_jsonl_to_cards_jsonl = (
        runtime_cards_jsonl_converter.convert_export_runtime_jsonl_to_cards_jsonl
    )


DEFAULT_RUNTIME_STATUS = "mapped_from_export"
DEFAULT_ENGINE_SUPPORT_STATUS = "not_evaluated"


def load_builder_cards_from_export_runtime_jsonl(
    input_path,
    strict=True,
    runtime_status=DEFAULT_RUNTIME_STATUS,
    engine_support_status=DEFAULT_ENGINE_SUPPORT_STATUS,
):
    """Return builder-compatible card records from an EXPORT_RUNTIME-style JSONL file."""
    input_path = Path(input_path)
    converted_path = input_path.with_name(".aeterna_runtime_cards_builder_%s.jsonl" % uuid.uuid4().hex)
    try:
        summary = convert_export_runtime_jsonl_to_cards_jsonl(input_path, converted_path, strict=strict)
        cards = _read_converted_cards(converted_path) if converted_path.exists() else []
    finally:
        if converted_path.exists():
            converted_path.unlink()

    builder_cards = [
        add_builder_card_defaults(
            card,
            runtime_status=runtime_status,
            engine_support_status=engine_support_status,
        )
        for card in cards
    ]

    return {
        "cards": builder_cards,
        "summary": {
            "records_read": summary["records_read"],
            "records_written": summary["records_written"],
            "ok_count": summary["ok_count"],
            "error_count": summary["error_count"],
            "diagnostics": summary["diagnostics"],
            "records_loaded": len(builder_cards),
        },
    }


def add_builder_card_defaults(
    runtime_card,
    runtime_status=DEFAULT_RUNTIME_STATUS,
    engine_support_status=DEFAULT_ENGINE_SUPPORT_STATUS,
):
    """Return a copy of one runtime card with fields expected by the sample builder."""
    builder_card = dict(runtime_card)
    builder_card.setdefault("runtime_status", runtime_status)
    builder_card.setdefault("engine_support_status", engine_support_status)
    return builder_card


def _read_converted_cards(path):
    cards = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                cards.append(json.loads(line))
    return cards
