from __future__ import annotations

import pytest
from fastmcp import Client
from fastmcp_tasks import call_tool_task

from brightway_mcp import server


def _plain(value):
    if isinstance(value, dict):
        return value
    root = getattr(value, "root", None)
    if root is not None:
        return _plain(root)
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        data = dump()
        if isinstance(data, dict) and set(data) == {"root"}:
            return _plain(data["root"])
        return data
    return value

