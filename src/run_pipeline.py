"""Run the full pipeline once: ETL then executive report."""

from src.jobs.daily_etl import run_daily_etl
from src.jobs.executive_report import run_executive_report
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    logger.info("Running full pipeline")
    run_daily_etl()
    run_executive_report()
    logger.info("Full pipeline completed")


if __name__ == "__main__":
    main()
