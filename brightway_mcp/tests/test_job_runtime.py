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
