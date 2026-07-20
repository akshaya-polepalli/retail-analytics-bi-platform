from src.analytics.kpis import (
    get_daily_kpis,
    get_inventory_alerts,
    get_top_products,
)
from src.services.ai_summary import generate_executive_summary
from src.services.monitoring import log_run_finish, log_run_start
from src.services.notifications import send_email_report, send_slack_message
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_executive_report() -> str:
    run_id = log_run_start("executive_report")
    logger.info("Starting executive report job")

    try:
        kpis = get_daily_kpis()
        top_products = get_top_products().to_dict(orient="records")
        inventory_alerts = get_inventory_alerts().to_dict(orient="records")

        payload = {
            "kpis": kpis,
            "top_products": top_products,
            "inventory_alerts": inventory_alerts,
        }

        summary = generate_executive_summary(payload)

        message = (
            f"*Daily Executive Report*\n"
            f"Revenue: ${float(kpis['total_revenue']):,.2f}\n"
            f"Orders: {int(kpis['total_orders'])}\n"
            f"Profit: ${float(kpis['total_profit']):,.2f}\n\n"
            f"{summary}"
        )

        send_slack_message(message)
        send_email_report("Daily Executive Report", message)

        log_run_finish(run_id, "SUCCESS", 1)
        logger.info("Executive report completed")
        return summary

    except Exception as exc:
        log_run_finish(run_id, "FAILED", error_message=str(exc))
        logger.exception("Executive report failed")
        raise


if __name__ == "__main__":
    run_executive_report()
