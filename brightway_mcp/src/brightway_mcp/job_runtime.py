"""Bounded Brightway compatibility jobs with optional Redis persistence."""

from __future__ import annotations

import os
import threading
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .job_persistence import RedisJobPersistence

ENGINE_LOCK = threading.RLock()
_TERMINAL = {"completed", "failed", "cancelled", "interrupted"}


@dataclass
class JobRecord:
    job_id: str
    tool_name: str
    status: str = "queued"
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    future: Optional[Future] = field(default=None, repr=False)

    def public(self) -> dict[str, Any]:
        body = {
            "success": True,
            "job_id": self.job_id,
            "tool_name": self.tool_name,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "terminal": self.status in _TERMINAL,
        }
        if self.error:
            body["error"] = self.error
        return body

    def persisted(self) -> dict[str, Any]:
        return {**self.public(), "result": self.result if self.status == "completed" else None}

    @classmethod
    def restore(cls, payload: dict[str, Any]) -> "JobRecord":
        return cls(
            job_id=str(payload["job_id"]),
            tool_name=str(payload.get("tool_name") or "unknown"),
            status=str(payload.get("status") or "failed"),
            created_at=float(payload.get("created_at") or time.time()),
            started_at=payload.get("started_at"),
            completed_at=payload.get("completed_at"),
            result=payload.get("result"),
            error=payload.get("error"),
        )


class JobManager:
    def __init__(
        self,
        max_workers: int = 1,
        ttl_seconds: int = 3600,
        persistence: Any = None,
        persistence_url: Optional[str] = None,
    ) -> None:
        self.ttl_seconds = max(60, int(ttl_seconds))
        self._executor = ThreadPoolExecutor(
            max_workers=max(1, int(max_workers)), thread_name_prefix="brightway-mcp-job"
        )
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.RLock()
        self._persistence = persistence or RedisJobPersistence(
            persistence_url if persistence_url is not None else os.getenv("BRIGHTWAY_JOB_REDIS_URL"),
            "brightway",
            self.ttl_seconds,
        )
        self._restore()

    def _persist(self, rec: JobRecord) -> None:
        self._persistence.save(rec.persisted())

    def _restore(self) -> None:
        now = time.time()
        cutoff = now - self.ttl_seconds
        for payload in self._persistence.load_all():
            try:
                rec = JobRecord.restore(payload)
            except (KeyError, TypeError, ValueError):
                continue
            if rec.completed_at is not None and float(rec.completed_at) < cutoff:
                self._persistence.delete(rec.job_id)
                continue
            if rec.status in {"queued", "running"}:
                rec.status = "interrupted"
                rec.completed_at = now
