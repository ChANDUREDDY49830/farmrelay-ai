"""FarmPlan Guard: small, dependency-free schedule validation helpers."""
from .guard import detect_conflicts, validate_schedule

__all__ = ["detect_conflicts", "validate_schedule"]
