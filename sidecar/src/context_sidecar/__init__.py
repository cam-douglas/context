"""Context sidecar: local analysis, intent, and arrangement planning."""

from context_sidecar.intent import empty_intent, validate_intent, validate_project_snapshot
from context_sidecar.schema import empty_arrangement, validate_arrangement
from context_sidecar.snapshot import build_project_snapshot

__version__ = "0.1.0"

__all__ = [
    "build_project_snapshot",
    "empty_arrangement",
    "empty_intent",
    "validate_arrangement",
    "validate_intent",
    "validate_project_snapshot",
]
