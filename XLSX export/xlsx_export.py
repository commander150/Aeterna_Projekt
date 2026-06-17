"""Standalone XLSX worksheet exporter for JSONL and TSV output."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Iterable, Sequence

from openpyxl import load_workbook


PROGRAM_DIR = Path(__file__).resolve().parent
SOURCE_DIR = PROGRAM_DIR / "source"
DEFAULT_OUTPUT_DIR = PROGRAM_DIR / "exports"


class ExportError(Exception):
    """An expected error that can be shown directly to the user."""


def normalize_value(value: Any) -> Any:
    if value is None:
        return "none"
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    return value


def load_headers(first_row: Sequence[Any] | None) -> list[str]:
    if first_row is None:
        raise ExportError("A kiválasztott munkalap üres, nincs fejlécsora.")

    headers = [str(normalize_value(value)) for value in first_row]
    if len(set(headers)) != len(headers):
        raise ExportError("A fejléc oszlopnevei nem lehetnek azonosak.")
    return headers


def iter_records(rows: Iterable[Sequence[Any]], headers: Sequence[str]):
    for row in rows:
        values = [normalize_value(row[index] if index < len(row) else None) for index in range(len(headers))]
        yield dict(zip(headers, values))


def safe_filename_part(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value).strip().rstrip(".")
    return cleaned or "névtelen"


def default_output_path(xlsx_path: Path, sheet_name: str, output_format: str) -> Path:
    source_name = safe_filename_part(xlsx_path.stem)
    sheet_part = safe_filename_part(sheet_name)
    return DEFAULT_OUTPUT_DIR / f"{source_name}__{sheet_part}.{output_format}"


def export_worksheet(xlsx_path: Path, sheet_name: str, output_path: Path, output_format: str) -> int:
    xlsx_path = Path(xlsx_path)
    output_path = Path(output_path)
    if xlsx_path.resolve() == output_path.resolve():
        raise ExportError("A kimeneti fájl nem lehet azonos a forrás .xlsx fájllal.")

    workbook = load_workbook(xlsx_path, read_only=True, data_only=True)
    try:
        if sheet_name not in workbook.sheetnames:
            raise ExportError(f"Nincs ilyen munkalap: {sheet_name}")

        rows = workbook[sheet_name].iter_rows(values_only=True)
        headers = load_headers(next(rows, None))
        records = iter_records(rows, headers)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as output_file:
            if output_format == "jsonl":
                count = write_jsonl(output_file, records)
            else:
                count = write_tsv(output_file, headers, records)
        return count
    finally:
        workbook.close()


def write_jsonl(output_file, records: Iterable[dict[str, Any]]) -> int:
    count = 0
    for record in records:
        output_file.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        count += 1
    return count


def write_tsv(output_file, headers: Sequence[str], records: Iterable[dict[str, Any]]) -> int:
    writer = csv.DictWriter(output_file, fieldnames=headers, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    count = 0
    for record in records:
        writer.writerow(record)
        count += 1
    return count


def list_sheets(xlsx_path: Path) -> list[str]:
    workbook = load_workbook(xlsx_path, read_only=True, data_only=True)
    try:
        return workbook.sheetnames
    finally:
        workbook.close()


def find_xlsx_files() -> list[Path]:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    files = {path.resolve() for path in SOURCE_DIR.glob("*.xlsx") if not path.name.startswith("~$")}
    return sorted(files, key=lambda path: path.name.casefold())


def validate_source_path(xlsx_path: Path) -> Path:
    resolved_path = xlsx_path.resolve()
    if resolved_path.parent != SOURCE_DIR.resolve():
        raise ExportError(f"A forrás XLSX fájlnak ebben a mappában kell lennie: {SOURCE_DIR}")
    return resolved_path


def choose_from_menu(title: str, options: Sequence[Any], label_func=str, input_func=input, print_func=print):
    if not options:
        raise ExportError(f"Nincs választható elem: {title}")

    print_func(f"\n{title}")
    for index, option in enumerate(options, start=1):
        print_func(f"  {index}. {label_func(option)}")
    print_func("  0. Kilépés")

    while True:
        answer = input_func("Választás: ").strip()
        if answer == "0":
            return None
        try:
            selected_index = int(answer) - 1
        except ValueError:
            selected_index = -1
        if 0 <= selected_index < len(options):
            return options[selected_index]
        print_func("Érvénytelen választás. Adj meg egy sorszámot.")


def interactive_menu(input_func=input, print_func=print) -> int:
    print_func("XLSX EXPORT")
    print_func(f"Forrásmappa: {SOURCE_DIR}")
    print_func("A kimeneti fájlok az exports mappába kerülnek.")

    xlsx_path = choose_from_menu(
        "Válaszd ki a forrás XLSX fájlt:",
        find_xlsx_files(),
        label_func=lambda path: path.name,
        input_func=input_func,
        print_func=print_func,
    )
    if xlsx_path is None:
        return 0

    sheet_name = choose_from_menu(
        "Válaszd ki az exportálandó munkalapot:",
        list_sheets(xlsx_path),
        input_func=input_func,
        print_func=print_func,
    )
    if sheet_name is None:
        return 0

    output_format = choose_from_menu(
        "Válaszd ki a kimeneti formátumot:",
        ("jsonl", "tsv"),
        input_func=input_func,
        print_func=print_func,
    )
    if output_format is None:
        return 0

    output_path = default_output_path(xlsx_path, sheet_name, output_format)
    count = export_worksheet(xlsx_path, sheet_name, output_path, output_format)
    print_func(f"\nExportált sorok száma: {count}")
    print_func(f"Kimeneti fájl: {output_path.resolve()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="XLSX munkalap exportálása JSONL vagy TSV formátumba.")
    parser.add_argument("xlsx", nargs="?", type=Path, help="A forrás .xlsx fájl")
    parser.add_argument("--list-sheets", action="store_true", help="A munkalapok kilistázása")
    parser.add_argument("--sheet", help="Az exportálandó munkalap neve")
    parser.add_argument("--format", choices=("jsonl", "tsv"), dest="output_format", help="Kimeneti formátum")
    parser.add_argument(
        "--output",
        type=Path,
        help="Egyedi kimeneti fájl. Ha nincs megadva, az exports mappába készül automatikus névvel.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.xlsx is None:
            return interactive_menu()
        args.xlsx = validate_source_path(args.xlsx)
        if not args.xlsx.is_file():
            raise ExportError(f"A forrásfájl nem található: {args.xlsx}")
        if args.xlsx.suffix.lower() != ".xlsx":
            raise ExportError("A forrásfájlnak .xlsx kiterjesztésűnek kell lennie.")

        if args.list_sheets:
            for sheet_name in list_sheets(args.xlsx):
                print(sheet_name)
            return 0

        missing = [
            option
            for option, value in (("--sheet", args.sheet), ("--format", args.output_format))
            if value is None
        ]
        if missing:
            raise ExportError(f"Exportáláshoz kötelező argumentum(ok): {', '.join(missing)}")

        output_path = args.output or default_output_path(args.xlsx, args.sheet, args.output_format)
        count = export_worksheet(args.xlsx, args.sheet, output_path, args.output_format)
        print(f"Exportált sorok száma: {count}")
        print(f"Kimeneti fájl: {output_path.resolve()}")
        return 0
    except (ExportError, OSError, ValueError) as exc:
        print(f"Hiba: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Hiba az XLSX fájl feldolgozásakor: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
