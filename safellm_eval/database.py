from __future__ import annotations

import sqlite3
from pathlib import Path

from .schemas import EvaluationResult


SCHEMA = """
CREATE TABLE IF NOT EXISTS eval_results (
    run_id TEXT NOT NULL,
    case_id TEXT NOT NULL,
    risk_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    prompt TEXT NOT NULL,
    expected_behavior TEXT NOT NULL,
    model_name TEXT NOT NULL,
    response TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    verdict TEXT NOT NULL,
    score REAL NOT NULL,
    reason TEXT NOT NULL,
    needs_review INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_eval_results_run_id ON eval_results(run_id);
CREATE INDEX IF NOT EXISTS idx_eval_results_risk_type ON eval_results(risk_type);
CREATE INDEX IF NOT EXISTS idx_eval_results_verdict ON eval_results(verdict);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(Path(db_path))
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def insert_results(
    connection: sqlite3.Connection,
    run_id: str,
    results: list[EvaluationResult],
) -> None:
    rows = [
        (
            run_id,
            result.test_case.id,
            result.test_case.risk_type,
            result.test_case.severity,
            result.test_case.prompt,
            result.test_case.expected_behavior,
            result.model_response.model_name,
            result.model_response.content,
            result.model_response.latency_ms,
            result.verdict,
            result.score,
            result.reason,
            1 if result.needs_review else 0,
        )
        for result in results
    ]
    connection.executemany(
        """
        INSERT INTO eval_results (
            run_id, case_id, risk_type, severity, prompt, expected_behavior,
            model_name, response, latency_ms, verdict, score, reason, needs_review
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    connection.commit()


def list_runs(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT
            run_id,
            model_name,
            COUNT(*) AS total,
            ROUND(AVG(score), 3) AS avg_score,
            ROUND(AVG(latency_ms), 1) AS avg_latency_ms,
            MAX(created_at) AS created_at
        FROM eval_results
        GROUP BY run_id, model_name
        ORDER BY created_at DESC
        """
    ).fetchall()


def compare_runs(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT
            run_id,
            model_name,
            COUNT(*) AS total,
            SUM(CASE WHEN verdict = 'safe' THEN 1 ELSE 0 END) AS safe_count,
            SUM(CASE WHEN verdict = 'unsafe' THEN 1 ELSE 0 END) AS unsafe_count,
            SUM(CASE WHEN verdict = 'review' THEN 1 ELSE 0 END) AS review_count,
            ROUND(
                100.0 * SUM(CASE WHEN verdict = 'safe' THEN 1 ELSE 0 END) / COUNT(*),
                1
            ) AS pass_rate,
            ROUND(AVG(score), 3) AS avg_score,
            ROUND(AVG(latency_ms), 1) AS avg_latency_ms,
            MAX(created_at) AS created_at
        FROM eval_results
        GROUP BY run_id, model_name
        ORDER BY created_at DESC
        """
    ).fetchall()


def load_run_results(connection: sqlite3.Connection, run_id: str) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT *
        FROM eval_results
        WHERE run_id = ?
        ORDER BY case_id
        """,
        (run_id,),
    ).fetchall()


def summarize_run(connection: sqlite3.Connection, run_id: str) -> dict[str, object]:
    totals = connection.execute(
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN verdict = 'safe' THEN 1 ELSE 0 END) AS safe_count,
            SUM(CASE WHEN verdict = 'unsafe' THEN 1 ELSE 0 END) AS unsafe_count,
            SUM(CASE WHEN verdict = 'review' THEN 1 ELSE 0 END) AS review_count,
            ROUND(AVG(score), 3) AS avg_score,
            ROUND(AVG(latency_ms), 1) AS avg_latency_ms
        FROM eval_results
        WHERE run_id = ?
        """,
        (run_id,),
    ).fetchone()
    by_risk = connection.execute(
        """
        SELECT
            risk_type,
            COUNT(*) AS total,
            SUM(CASE WHEN verdict = 'safe' THEN 1 ELSE 0 END) AS safe_count,
            SUM(CASE WHEN verdict = 'unsafe' THEN 1 ELSE 0 END) AS unsafe_count,
            SUM(CASE WHEN verdict = 'review' THEN 1 ELSE 0 END) AS review_count,
            ROUND(AVG(score), 3) AS avg_score
        FROM eval_results
        WHERE run_id = ?
        GROUP BY risk_type
        ORDER BY avg_score ASC, total DESC
        """,
        (run_id,),
    ).fetchall()
    failures = connection.execute(
        """
        SELECT case_id, risk_type, severity, prompt, response, verdict, reason
        FROM eval_results
        WHERE run_id = ? AND verdict IN ('unsafe', 'review')
        ORDER BY
            CASE verdict WHEN 'unsafe' THEN 0 ELSE 1 END,
            CASE severity WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,
            case_id
        LIMIT 20
        """,
        (run_id,),
    ).fetchall()
    return {"totals": totals, "by_risk": by_risk, "failures": failures}
