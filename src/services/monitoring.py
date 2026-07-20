from datetime import datetime, timezone

from sqlalchemy import text

from src.database.connection import engine


def log_run_start(job_name: str) -> int:
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO audit.workflow_runs (job_name, status)
                VALUES (:job_name, 'RUNNING')
                RETURNING run_id
            """),
            {"job_name": job_name},
        )
        return result.scalar_one()


def log_run_finish(
    run_id: int,
    status: str,
    records_processed: int = 0,
    error_message: str | None = None,
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE audit.workflow_runs
                SET status = :status,
                    records_processed = :records_processed,
                    error_message = :error_message,
                    finished_at = :finished_at
                WHERE run_id = :run_id
            """),
            {
                "run_id": run_id,
                "status": status,
                "records_processed": records_processed,
                "error_message": error_message,
                "finished_at": datetime.now(timezone.utc),
            },
        )
