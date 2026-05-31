"""SQLite-backed persistence for analysis jobs.

The job store keeps analysis state in a SQLite file instead of an in-memory dict,
which buys two things the previous approach lacked:

  * Durability - status and results survive a process restart.
  * Bounded growth - rows are not kept in memory forever; `prune_expired` reclaims
    old rows together with their uploaded file and generated Excel report, so the
    database, upload dir, and reports dir stay bounded.

SQLite ships with the Python standard library, so the app still clones-and-runs
with no external service. Each operation uses its own short-lived connection
(SQLite handles this well), and WAL mode lets the polling reads run concurrently
with the background task's writes.
"""

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

from app.models.schemas import AnalysisStatus

logger = logging.getLogger(__name__)

_StatusLike = Union[AnalysisStatus, str]


def _status_value(status: _StatusLike) -> str:
    return status.value if isinstance(status, AnalysisStatus) else str(status)


class JobStore:
    """Durable store for analysis jobs, backed by a single SQLite file."""

    def __init__(self, db_path: str = "./analyses.db") -> None:
        self.db_path = db_path
        parent = os.path.dirname(os.path.abspath(db_path))
        os.makedirs(parent, exist_ok=True)
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id          TEXT PRIMARY KEY,
                    status      TEXT NOT NULL,
                    progress    INTEGER NOT NULL DEFAULT 0,
                    file_path   TEXT NOT NULL,
                    filename    TEXT NOT NULL,
                    file_size   INTEGER NOT NULL,
                    created_at  TEXT NOT NULL,
                    message     TEXT,
                    result      TEXT,
                    error       TEXT
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, file_path: str, filename: str, file_size: int) -> str:
        """Insert a new PENDING job and return its id."""
        analysis_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO analyses
                    (id, status, progress, file_path, filename, file_size, created_at, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    AnalysisStatus.PENDING.value,
                    0,
                    file_path,
                    filename,
                    file_size,
                    datetime.now(timezone.utc).isoformat(),
                    "Analysis queued",
                ),
            )
        return analysis_id

    def update(
        self,
        analysis_id: str,
        status: _StatusLike,
        progress: int,
        message: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update a job's status/progress/message and (optionally) result or error.

        `result` is serialized to JSON (datetimes via isoformat). Identity columns
        (file_path, filename, file_size, created_at) are never touched.
        """
        result_json = json.dumps(result, default=str) if result is not None else None
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE analyses
                   SET status = ?, progress = ?, message = ?, result = ?, error = ?
                 WHERE id = ?
                """,
                (_status_value(status), progress, message, result_json, error, analysis_id),
            )

    def get(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Return the job as a dict (result parsed back to a dict), or None."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
            ).fetchone()
        if row is None:
            return None
        job = dict(row)
        job["result"] = json.loads(job["result"]) if job["result"] else None
        return job

    def get_report_path(self, analysis_id: str) -> Optional[str]:
        """Return the Excel report path for a completed job, if any."""
        job = self.get(analysis_id)
        if job and job.get("result"):
            return job["result"].get("excel_report_path")
        return None

    def prune_expired(self, retention_hours: int) -> int:
        """Delete jobs older than `retention_hours`, with their files. Returns the count.

        Best-effort file removal: a missing or already-deleted file is not an error.
        """
        if retention_hours <= 0:
            return 0
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=retention_hours)).isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, file_path, result FROM analyses WHERE created_at < ?", (cutoff,)
            ).fetchall()
            for row in rows:
                self._remove_file(row["file_path"])
                if row["result"]:
                    report_path = json.loads(row["result"]).get("excel_report_path")
                    self._remove_file(report_path)
            conn.execute("DELETE FROM analyses WHERE created_at < ?", (cutoff,))
        if rows:
            logger.info("Pruned %d analyses older than %dh", len(rows), retention_hours)
        return len(rows)

    @staticmethod
    def _remove_file(path: Optional[str]) -> None:
        if not path:
            return
        try:
            os.remove(path)
        except OSError:
            pass
