"""
Structured memory for the Agentic Workflow.

This module stores:

1. Workflow state (run status, task graph, draft, etc.)
2. Agent execution memory (node outputs)

Everything is persisted in SQLite.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

from config import settings
from models.schemas import TaskGraph, RunStatus

Path(settings.sqlite_db_path).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def _conn():
    conn = sqlite3.connect(settings.sqlite_db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _conn() as conn:

        # Workflow state
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                goal TEXT NOT NULL,
                status TEXT NOT NULL,
                task_graph_json TEXT,
                draft TEXT,
                quality_score INTEGER,
                retries_used INTEGER DEFAULT 0,
                docx_path TEXT
            )
            """
        )

        # Audit logs
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                ts TEXT NOT NULL,
                step TEXT NOT NULL,
                detail TEXT
            )
            """
        )

        # Agent Memory
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                task TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


# ---------------------------------------------------
# Workflow State
# ---------------------------------------------------

def create_run(run_id: str, goal: str, task_graph: TaskGraph):
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO runs
            (run_id, goal, status, task_graph_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                run_id,
                goal,
                RunStatus.PENDING_APPROVAL.value,
                task_graph.model_dump_json(),
            ),
        )


def get_run(run_id: str):
    with _conn() as conn:
        cur = conn.execute(
            "SELECT * FROM runs WHERE run_id=?",
            (run_id,),
        )
        return cur.fetchone()


def update_status(run_id: str, status: RunStatus):
    with _conn() as conn:
        conn.execute(
            "UPDATE runs SET status=? WHERE run_id=?",
            (status.value, run_id),
        )


def save_task_graph(run_id: str, task_graph: TaskGraph):
    with _conn() as conn:
        conn.execute(
            """
            UPDATE runs
            SET task_graph_json=?
            WHERE run_id=?
            """,
            (
                task_graph.model_dump_json(),
                run_id,
            ),
        )


def save_draft(run_id: str, draft: str):
    with _conn() as conn:
        conn.execute(
            "UPDATE runs SET draft=? WHERE run_id=?",
            (draft, run_id),
        )


def save_quality(run_id: str, score: int, retries_used: int):
    with _conn() as conn:
        conn.execute(
            """
            UPDATE runs
            SET quality_score=?,
                retries_used=?
            WHERE run_id=?
            """,
            (
                score,
                retries_used,
                run_id,
            ),
        )


def save_docx_path(run_id: str, path: str):
    with _conn() as conn:
        conn.execute(
            """
            UPDATE runs
            SET docx_path=?
            WHERE run_id=?
            """,
            (path, run_id),
        )


def log_audit_event(run_id: str, ts: str, step: str, detail: str):
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO audit_log
            (run_id, ts, step, detail)
            VALUES (?, ?, ?, ?)
            """,
            (
                run_id,
                ts,
                step,
                detail,
            ),
        )


# ---------------------------------------------------
# Agent Memory
# ---------------------------------------------------

def save_memory(
    run_id: str,
    node_id: str,
    task: str,
    result: str,
):
    """Store one completed node output."""

    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO memories
            (run_id, node_id, task, result)
            VALUES (?, ?, ?, ?)
            """,
            (
                run_id,
                node_id,
                task,
                result,
            ),
        )


def get_run_memories(run_id: str):
    """Return all previous node outputs."""

    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT node_id, task, result
            FROM memories
            WHERE run_id=?
            ORDER BY id
            """,
            (run_id,),
        )

        rows = cur.fetchall()

    return [
        f"""
Node: {row["node_id"]}

Task:
{row["task"]}

Result:
{row["result"]}
"""
        for row in rows
    ]


def clear_memories(run_id: str):
    with _conn() as conn:
        conn.execute(
            "DELETE FROM memories WHERE run_id=?",
            (run_id,),
        )