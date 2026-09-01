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


