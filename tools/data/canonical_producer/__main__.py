"""CLI for the deterministic canonical component candidate producer."""

from __future__ import annotations

import argparse
import json
import sys

from .producer import ProducerConfig, ProducerError, build_candidate, default_config


def main(argv: list[str] | None = None) -> int:
    defaults = default_config()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--carddatabase", default=defaults.carddatabase_path)
    parser.add_argument("--registry", default=defaults.registry_path)
    args = parser.parse_args(argv)
    config = ProducerConfig(
        repository_root=defaults.repository_root,
        carddatabase_path=args.carddatabase,
        registry_path=args.registry,
    )
    try:
        result = build_candidate(config)
    except ProducerError as exc:
        print(json.dumps({"status": "blocked", "code": exc.code, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "candidate_root": result.candidate_root.relative_to(config.repository_root).as_posix(),
                "candidate_id": result.candidate_id,
                "component_count": result.component_count,
                "file_count": result.file_count,
                "package_set_id": result.package_set_id,
                "production_ready": result.production_ready,
                "publish_allowed": result.publish_allowed,
                "status": "CANONICAL_PRODUCER_SCAFFOLD_READY",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
