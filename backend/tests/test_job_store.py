"""Tests for the SQLite-backed JobStore (durability, result round-trip, pruning).

Uses a temp database and temp files so nothing touches the real ./analyses.db,
upload dir, or reports dir.
"""

import os
from datetime import datetime, timedelta, timezone

from app.models.schemas import AnalysisStatus
from app.services.job_store import JobStore


def test_create_and_get_round_trip(tmp_path):
    store = JobStore(str(tmp_path / "jobs.db"))

    job_id = store.create(file_path="/tmp/x.pdf", filename="x.pdf", file_size=1234)
    job = store.get(job_id)

    assert job is not None
    assert job["status"] == AnalysisStatus.PENDING.value
    assert job["progress"] == 0
    assert job["filename"] == "x.pdf"
    assert job["file_size"] == 1234
    assert job["result"] is None
    assert job["error"] is None


def test_get_unknown_id_returns_none(tmp_path):
    store = JobStore(str(tmp_path / "jobs.db"))
    assert store.get("does-not-exist") is None


def test_update_persists_result_as_dict(tmp_path):
    store = JobStore(str(tmp_path / "jobs.db"))
    job_id = store.create("/tmp/x.pdf", "x.pdf", 1)

    result = {"ticker": "ACME", "trade_score": {"total_score": 72.5}, "excel_report_path": "/tmp/r.xlsx"}
    store.update(job_id, AnalysisStatus.COMPLETED, 100, "done", result=result)

    job = store.get(job_id)
    assert job["status"] == AnalysisStatus.COMPLETED.value
    assert job["progress"] == 100
    assert job["result"] == result  # JSON round-trips back to the same dict
    assert store.get_report_path(job_id) == "/tmp/r.xlsx"


def test_durability_across_instances(tmp_path):
    db = str(tmp_path / "jobs.db")
    job_id = JobStore(db).create("/tmp/x.pdf", "x.pdf", 1)

    # A fresh store pointed at the same file (i.e. after a restart) sees the job.
    reopened = JobStore(db)
    assert reopened.get(job_id) is not None


def test_prune_expired_removes_old_jobs_and_files(tmp_path):
    db = str(tmp_path / "jobs.db")
    store = JobStore(db)

    upload = tmp_path / "upload.pdf"
    report = tmp_path / "report.xlsx"
    upload.write_text("data")
    report.write_text("data")

    job_id = store.create(str(upload), "upload.pdf", 4)
    store.update(
        job_id, AnalysisStatus.COMPLETED, 100, "done",
        result={"excel_report_path": str(report)},
    )

    # Backdate created_at so the row is older than the retention window.
    old = (datetime.now(timezone.utc) - timedelta(hours=200)).isoformat()
    conn = store._connect()
    conn.execute("UPDATE analyses SET created_at = ? WHERE id = ?", (old, job_id))
    conn.commit()
    conn.close()

    pruned = store.prune_expired(retention_hours=168)

    assert pruned == 1
    assert store.get(job_id) is None
    assert not os.path.exists(upload)
    assert not os.path.exists(report)


def test_prune_keeps_recent_jobs(tmp_path):
    store = JobStore(str(tmp_path / "jobs.db"))
    job_id = store.create("/tmp/x.pdf", "x.pdf", 1)

    assert store.prune_expired(retention_hours=168) == 0
    assert store.get(job_id) is not None
