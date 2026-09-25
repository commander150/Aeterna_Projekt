"""Deterministic canonical component candidate producer."""

from .producer import (
    BuildResult,
    ProducerConfig,
    ProducerError,
    build_candidate,
    default_config,
    verify_candidate,
)

__all__ = (
    "BuildResult",
    "ProducerConfig",
    "ProducerError",
    "build_candidate",
    "default_config",
    "verify_candidate",
)

