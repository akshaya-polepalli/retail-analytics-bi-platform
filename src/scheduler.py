from apscheduler.schedulers.blocking import BlockingScheduler

from src.jobs.daily_etl import run_daily_etl
from src.jobs.executive_report import run_executive_report
from src.jobs.health_check import run_health_check
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler()

    scheduler.add_job(run_daily_etl, "cron", hour=7, minute=0, id="daily_etl")
    scheduler.add_job(
        run_executive_report, "cron", hour=7, minute=15, id="executive_report"
    )
    scheduler.add_job(run_health_check, "interval", hours=1, id="health_check")

    return scheduler


if __name__ == "__main__":
    logger.info("Starting BI platform scheduler")
    create_scheduler().start()
