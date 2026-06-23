"""Compatibility wrapper for the official keyword engine.

The active runtime implementation lives in ``engine.keyword_engine``.
This module remains only so older imports can keep working during the
transition without carrying parallel keyword logic.
"""

from engine.keyword_engine import KeywordEngine

__all__ = ["KeywordEngine"]
