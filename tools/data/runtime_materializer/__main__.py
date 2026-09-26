"""CLI for deterministic canonical runtime materialization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .materializer import MaterializationError, materialize


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, help="Verified canonical candidate directory.")
    parser.add_argument(
        "--output-root",
        default="TEMP/runtime_materialization",
        help="Repository-TEMP output root. No consumer publish is performed.",
    )
    args = parser.parse_args(argv)
    try:
        result = materialize(args.candidate, args.output_root)
    except MaterializationError as exc:
        print(
            json.dumps(
                {"status": "blocked", "code": exc.code, "message": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result.as_dict(Path.cwd().resolve()), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
