"""Fail-closed promotion of verified canonical runtime packages."""

from .publisher import PromotionError, PromotionResult, preflight, promote

__all__ = ["PromotionError", "PromotionResult", "preflight", "promote"]
