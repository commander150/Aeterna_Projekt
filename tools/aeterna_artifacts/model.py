"""Small contract models shared by parsing, classification and validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class Scope(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVE = "ARCHIVE"
    LEARNING = "LEARNING"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKING = "BLOCKING"


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: Severity
    message: str
    field: str | None = None


@dataclass(frozen=True)
class ArtifactMetadata:
    """Unvalidated YAML fields with a read-only top-level snapshot.

    Nested values retain their YAML types so validation can distinguish a list
    from a scalar or mapping. This model is intentionally shallowly immutable.
    Unknown fields are retained for future contract versions, without validation.
    """

    fields: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "fields", MappingProxyType(dict(self.fields)))


@dataclass(frozen=True)
class ParseResult:
    metadata: ArtifactMetadata | None = None
    diagnostics: tuple[Diagnostic, ...] = ()
