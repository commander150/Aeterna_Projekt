"""CLI for governed canonical runtime-package promotion."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .publisher import PromotionError, preflight, promote


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise PromotionError("PROMOTION_INPUT_NOT_CANONICAL_MATERIALIZATION", message)


def main(argv: list[str] | None = None) -> int:
    parser = _ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Verified canonical materialization under repository TEMP/.")
    parser.add_argument("--apply", action="store_true", help="Apply the validated promotion transaction.")
    try:
        args = parser.parse_args(argv)
        result = promote(args.source) if args.apply else preflight(args.source)
    except PromotionError as exc:
        print(
            json.dumps(
                {"status": "blocked", "code": exc.code, "message": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    payload = result.as_dict()
    payload["status"] = "applied" if result.applied else "preflight_pass"
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
