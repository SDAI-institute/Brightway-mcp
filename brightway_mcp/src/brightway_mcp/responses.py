"""Structured response envelopes for Brightway MCP tools.

Mirrors the sibling ``openlca_mcp`` conventions: every tool returns a plain dict
carrying a ``success`` boolean. Errors additionally carry ``error_code``,
``recoverable``, and ``suggested_next_actions`` so an agent can branch on
failures rather than parsing a message string.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


class BrightwayToolError(Exception):
    """A recoverable, agent-legible error raised by a tool.

    Carries the structured fields that go into the error envelope.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "INTERNAL_ERROR",
        recoverable: bool = True,
        suggested_next_actions: Optional[List[str]] = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.recoverable = recoverable
        self.suggested_next_actions = suggested_next_actions or []


def success(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Build a JSON-safe success envelope."""
    body: Dict[str, Any] = {"success": True}
    body.update(payload)
    return _json_safe(body)


def error_body(exc: Exception, *, error_code: str = "INTERNAL_ERROR") -> Dict[str, Any]:
    """Build a JSON-safe error envelope from any exception."""
    if isinstance(exc, BrightwayToolError):
        return _json_safe({
            "success": False,
            "is_error": True,
            "error_code": exc.error_code,
            "message": str(exc),
            "recoverable": exc.recoverable,
            "suggested_next_actions": exc.suggested_next_actions,
        })
    return _json_safe({
        "success": False,
        "is_error": True,
        "error_code": error_code,
        "message": str(exc),
        "recoverable": False,
        "suggested_next_actions": [],
    })


def read_only_error(action: str) -> Dict[str, Any]:
    """Standard envelope for a write blocked by read-only mode."""
    return error_body(
        BrightwayToolError(
            f"'{action}' is a write operation and the server is in read-only mode.",
            error_code="READ_ONLY",
            recoverable=False,
            suggested_next_actions=[
                "Unset BRIGHTWAY_READ_ONLY to allow writes, or use a read tool instead.",
            ],
        )
    )


def _json_safe(obj: Any) -> Any:
    """Recursively coerce non-finite floats to None so output is valid JSON."""
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return obj
