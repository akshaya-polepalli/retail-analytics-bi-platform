from sqlalchemy import text

from src.database.connection import engine
from src.services.monitoring import log_run_finish, log_run_start
from src.services.notifications import send_slack_message
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_health_check() -> None:
    run_id = log_run_start("health_check")
    logger.info("Starting health check")

    try:
        query = text("""
            SELECT COUNT(*) AS failed_count
            FROM audit.workflow_runs
            WHERE status = 'FAILED'
              AND started_at >= NOW() - INTERVAL '24 hours'
        """)

        with engine.connect() as conn:
            failed_count = conn.execute(query).scalar() or 0

        if failed_count > 0:
            message = f"ALERT: {failed_count} workflow failure(s) in the last 24 hours."
            send_slack_message(message)

            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO audit.alerts (alert_type, alert_message, severity)
                        VALUES ('WORKFLOW_FAILURE', :message, 'HIGH')
                    """),
                    {"message": message},
                )

        log_run_finish(run_id, "SUCCESS", int(failed_count))
        logger.info("Health check completed")

    except Exception as exc:
        log_run_finish(run_id, "FAILED", error_message=str(exc))
        logger.exception("Health check failed")
        raise


if __name__ == "__main__":
    run_health_check()
