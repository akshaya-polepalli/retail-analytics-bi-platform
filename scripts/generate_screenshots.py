"""Generate static chart assets for README documentation."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import text

from src.analytics.kpis import get_daily_kpis, get_monthly_revenue, get_top_products
from src.database.connection import engine

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "screenshots"


def save_top_products_chart() -> None:
    df = get_top_products()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(df["product_name"], df["revenue"], color="#2563eb")
    ax.set_title("Top Products by Revenue (Last 30 Days)")
    ax.set_xlabel("Revenue ($)")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "top_products.png", dpi=150)
    plt.close(fig)


def save_monthly_revenue_chart() -> None:
    df = get_monthly_revenue()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["month_start"], df["total_revenue"], marker="o", label="Revenue")
    ax.plot(df["month_start"], df["total_profit"], marker="o", label="Profit")
    ax.set_title("Monthly Revenue and Profit")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount ($)")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "monthly_revenue.png", dpi=150)
    plt.close(fig)


def save_kpi_card_image() -> None:
    kpis = get_daily_kpis()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    text = (
        f"Executive KPIs ({kpis['report_date']})\n\n"
        f"Revenue: ${float(kpis['total_revenue']):,.2f}\n"
        f"Orders: {int(kpis['total_orders'])}\n"
        f"Profit: ${float(kpis['total_profit']):,.2f}\n"
        f"AOV: ${float(kpis['avg_order_value']):,.2f}"
    )
    ax.text(0.05, 0.5, text, fontsize=16, va="center", family="monospace")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "executive_kpis.png", dpi=150)
    plt.close(fig)


def save_workflow_monitoring_image() -> None:
    query = text("""
        SELECT job_name, status, records_processed, started_at
        FROM audit.workflow_runs
        ORDER BY started_at DESC
        LIMIT 10
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.4)
    ax.set_title("Recent Workflow Runs", pad=20)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "workflow_monitoring.png", dpi=150)
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_top_products_chart()
    save_monthly_revenue_chart()
    save_kpi_card_image()
    save_workflow_monitoring_image()
    print(f"Screenshots saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
