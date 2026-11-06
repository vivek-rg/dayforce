"""One local worker over the durable queue. Never holds a database write during inference."""

import logging
import threading

from app.actions.service import execute_approved_action
from app.agent.graph import run_investigation
from app.notifications.service import run_escalation_sweep
from app.shared.db import connect
from app.shared.util import now_iso

logger = logging.getLogger("onboardiq.worker")
MAX_ATTEMPTS = 3
SWEEP_EVERY_SECONDS = 60
_stop = threading.Event()
_thread: threading.Thread | None = None


def _claim():
    with connect() as connection:
        row = connection.execute(
            "SELECT * FROM work_items WHERE state='PENDING' ORDER BY updated_at, rowid LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        cursor = connection.execute(
            "UPDATE work_items SET state='RUNNING', attempts=attempts+1, updated_at=? "
            "WHERE id=? AND state='PENDING'",
            (now_iso(), row["id"]),
        )
        return dict(row) if cursor.rowcount == 1 else None


def _finish(work_id: str, state: str) -> None:
    with connect() as connection:
        connection.execute(
            "UPDATE work_items SET state=?, updated_at=? WHERE id=?", (state, now_iso(), work_id)
        )


def process_pending_work(limit: int = 20) -> int:
    """Runs queued items in order. Returns how many ran."""
    done = 0
    while done < limit:
        item = _claim()
        if item is None:
            break
        done += 1
        try:
            if item["kind"] == "EXECUTE":
                execute_approved_action(item["action_id"])
            else:
                run_investigation(item["case_id"])
        except Exception:  # noqa: BLE001 - one failed item must not stop the worker
            logger.exception("Work item failed: %s", item["id"])
            _finish(item["id"], "FAILED")
            with connect() as connection:
                connection.execute(
                    "UPDATE cases SET state='ESCALATED', version=version+1 WHERE id=?",
                    (item["case_id"],),
                )
            continue
        _finish(item["id"], "DONE")
    return done


def reconcile_after_restart() -> int:
    """Work left RUNNING by a crash is retried. Stable action IDs stop a repeated effect."""
    with connect() as connection:
        rows = connection.execute("SELECT * FROM work_items WHERE state='RUNNING'").fetchall()
        for row in rows:
            state = "PENDING" if row["attempts"] < MAX_ATTEMPTS else "FAILED"
            connection.execute(
                "UPDATE work_items SET state=?, updated_at=? WHERE id=?",
                (state, now_iso(), row["id"]),
            )
            if state == "FAILED":
                connection.execute(
                    "UPDATE cases SET state='ESCALATED', version=version+1 WHERE id=?",
                    (row["case_id"],),
                )
    return len(rows)


def _loop() -> None:
    reconcile_after_restart()
    ticks = 0
    while not _stop.is_set():
        try:
            process_pending_work()
            if ticks % (SWEEP_EVERY_SECONDS * 2) == 0:
                with connect() as connection:
                    run_escalation_sweep(connection)
        except Exception:  # noqa: BLE001
            logger.exception("Worker cycle failed")
        ticks += 1
        _stop.wait(0.5)


def start_worker() -> None:
    global _thread
    _stop.clear()
    _thread = threading.Thread(target=_loop, name="onboardiq-worker", daemon=True)
    _thread.start()


def stop_worker() -> None:
    _stop.set()
    if _thread is not None:
        _thread.join(timeout=5)
