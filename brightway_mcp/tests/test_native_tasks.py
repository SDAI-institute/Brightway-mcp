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


@pytest.mark.asyncio
async def test_run_monte_carlo_dual_protocol(monkeypatch):
    if not server.NATIVE_TASKS_ENABLED:
        pytest.skip("native Tasks disabled for this test process")

    def fake_run_monte_carlo(*args, **kwargs):
        iterations = kwargs.get("iterations", args[5] if len(args) > 5 else 3)
        seed = kwargs.get("seed", args[7] if len(args) > 7 else None)
        return {"success": True, "iterations": iterations, "seed": seed}

    monkeypatch.setattr(server, "run_monte_carlo", fake_run_monte_carlo)
    arguments = {
        "project": "fixture",
        "database": "fixture",
        "method": ["fixture", "GWP100"],
        "code": "widget",
        "iterations": 3,
        "seed": 42,
    }

    async with Client(server.mcp, mode="auto") as client:
        assert str(client.protocol_version) == "2026-07-28"
        task = await call_tool_task(client, "run_monte_carlo", arguments)
        first = await task.status()
        assert first.status in {"working", "completed"}
        result = await task.result()
        data = _plain(result.data or result.structured_content or {})
        assert data == {"success": True, "iterations": 3, "seed": 42}

    async with Client(server.mcp, mode="legacy") as client:
        legacy = await client.call_tool("run_monte_carlo", arguments)
        data = _plain(legacy.data or legacy.structured_content or {})
        assert data == {"success": True, "iterations": 3, "seed": 42}
