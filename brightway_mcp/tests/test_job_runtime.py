from __future__ import annotations

import threading
import time

from brightway_mcp import server
from brightway_mcp.job_runtime import JobManager


class MemoryPersistence:
    def __init__(self) -> None:
        self.rows = {}

    def save(self, payload):
        self.rows[payload["job_id"]] = dict(payload)
        return True

    def load_all(self):
        return [dict(row) for row in self.rows.values()]

    def delete(self, job_id):
        self.rows.pop(job_id, None)


def _wait_terminal(manager: JobManager, job_id: str, timeout: float = 2.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = manager.status(job_id)
        if status.get("terminal"):
            return status
        time.sleep(0.01)
    raise AssertionError(f"job {job_id} did not reach a terminal state")


def test_job_manager_completion_pagination_and_dispose() -> None:
    manager = JobManager(max_workers=1, ttl_seconds=60)
    try:
        submitted = manager.submit(
            "fake", lambda: {"success": True, "results": list(range(9))}
        )
        status = _wait_terminal(manager, submitted["job_id"])
        assert status["status"] == "completed"
        page = manager.result(submitted["job_id"], field="results", offset=2, limit=3)
        assert page["ready"] is True
        assert page["result"] == [2, 3, 4]
        assert page["pagination"]["next_offset"] == 5
        assert manager.dispose(submitted["job_id"])["disposed"] is True
    finally:
        manager.shutdown()


def test_queued_cancel_and_running_no_force_kill() -> None:
    manager = JobManager(max_workers=1, ttl_seconds=60)
    release = threading.Event()

    def blocking() -> dict:
        release.wait(timeout=1.0)
        return {"success": True}

    try:
        first = manager.submit("blocking", blocking)
        deadline = time.time() + 1.0
        while time.time() < deadline and manager.status(first["job_id"])["status"] == "queued":
            time.sleep(0.01)
        running = manager.cancel(first["job_id"])
        assert running["cancelled"] is False
        assert running["cancel_supported"] is False

        second = manager.submit("queued", lambda: {"success": True})
        queued = manager.cancel(second["job_id"])
        assert queued["cancelled"] is True
        assert queued["status"] == "cancelled"
        release.set()
        assert _wait_terminal(manager, first["job_id"])["status"] == "completed"
    finally:
        release.set()
        manager.shutdown()


def test_restart_restores_completed_and_interrupts_running() -> None:
    persistence = MemoryPersistence()
    first = JobManager(max_workers=1, ttl_seconds=60, persistence=persistence)
    try:
        submitted = first.submit("persisted", lambda: {"success": True, "rows": [1, 2]})
        assert _wait_terminal(first, submitted["job_id"])["status"] == "completed"
        completed_id = submitted["job_id"]
    finally:
        first.shutdown()

    persistence.save({
        "success": True, "job_id": "job_running_fixture", "tool_name": "fake",
        "status": "running", "created_at": time.time() - 5,
        "started_at": time.time() - 4, "completed_at": None,
        "terminal": False, "result": None,
    })
    second = JobManager(max_workers=1, ttl_seconds=60, persistence=persistence)
    try:
        assert second.result(completed_id)["result"] == {"success": True, "rows": [1, 2]}
        interrupted = second.status("job_running_fixture")
        assert interrupted["status"] == "interrupted"
        assert interrupted["terminal"] is True
    finally:
        second.shutdown()


def test_server_async_monte_carlo_roundtrip(monkeypatch) -> None:
    def fake_run_monte_carlo(**kwargs):
        return {
            "success": True,
            "seed": kwargs["seed"],
            "samples": list(range(kwargs["iterations"])),
        }

    monkeypatch.setattr(server, "run_monte_carlo", fake_run_monte_carlo)
    submitted = server.run_monte_carlo_async(
        project="p", database="d", method=["m"], iterations=8, seed=11
    )
    assert submitted["success"]
    job_id = submitted["job_id"]

    deadline = time.time() + 2.0
    while time.time() < deadline:
        status = server.get_job_status(job_id)
        if status["terminal"]:
            break
        time.sleep(0.01)
    assert status["status"] == "completed"

    page = server.get_job_result(job_id, field="samples", offset=3, limit=2)
    assert page["ready"] is True
    assert page["result"] == [3, 4]
    assert server.dispose_job(job_id)["disposed"] is True
