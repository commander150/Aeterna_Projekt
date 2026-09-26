"""Deterministic canonical-candidate to runtime-package materialization."""

from .materializer import (
    BuildResult,
    MaterializationError,
    compute_runtime_package_id,
    materialize,
    validate_runtime_package,
)

__all__ = [
    "BuildResult",
    "MaterializationError",
    "compute_runtime_package_id",
    "materialize",
    "validate_runtime_package",
]
