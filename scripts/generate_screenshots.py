"""Generate static chart assets for README documentation."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from matplotlib import font_manager
from sqlalchemy import text

from src.analytics.kpis import get_daily_kpis, get_monthly_revenue, get_top_products
from src.database.connection import engine

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "screenshots"

COLORS = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "border": "#334155",
    "title": "#f8fafc",
    "label": "#94a3b8",
    "value": "#ffffff",
    "accent": "#3b82f6",
    "accent2": "#10b981",
    "accent3": "#8b5cf6",
    "accent4": "#f59e0b",
}


def save_kpi_card_image() -> None:
    kpis = get_daily_kpis()
    report_date = kpis["report_date"]

    fig = plt.figure(figsize=(12, 4.5), facecolor=COLORS["bg"])
    fig.text(
        0.05, 0.88, "Executive Overview",
        fontsize=22, fontweight="bold", color=COLORS["title"], ha="left",
    )
    fig.text(
        0.05, 0.79, f"Daily business performance  •  Report date: {report_date}",
        fontsize=11, color=COLORS["label"], ha="left",
    )

    metrics = [
        ("Total Revenue", f"${float(kpis['total_revenue']):,.2f}", COLORS["accent"]),
        ("Total Orders", f"{int(kpis['total_orders']):,}", COLORS["accent2"]),
        ("Total Profit", f"${float(kpis['total_profit']):,.2f}", COLORS["accent3"]),
        ("Avg Order Value", f"${float(kpis['avg_order_value']):,.2f}", COLORS["accent4"]),
    ]

    card_width = 0.21
    card_height = 0.42
    start_x = 0.05
    y = 0.22

    for i, (label, value, accent) in enumerate(metrics):
        x = start_x + i * (card_width + 0.025)
        card = mpatches.FancyBboxPatch(
            (x, y), card_width, card_height,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            linewidth=1.2, edgecolor=COLORS["border"], facecolor=COLORS["card"],
            transform=fig.transFigure, clip_on=False,
        )
        fig.patches.append(card)

        accent_bar = mpatches.Rectangle(
            (x, y + card_height - 0.025), card_width, 0.025,
            facecolor=accent, edgecolor="none", transform=fig.transFigure,
        )
        fig.patches.append(accent_bar)

        fig.text(x + 0.02, y + card_height - 0.12, label, fontsize=10, color=COLORS["label"], ha="left")
        fig.text(x + 0.02, y + 0.12, value, fontsize=18, fontweight="bold", color=COLORS["value"], ha="left")

    fig.savefig(
        OUTPUT_DIR / "executive_kpis.png",
        dpi=180,
        facecolor=COLORS["bg"],
        bbox_inches="tight",
        pad_inches=0.3,
    )
    plt.close(fig)


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
    save_kpi_card_image()
    save_top_products_chart()
    save_monthly_revenue_chart()
    save_workflow_monitoring_image()
    print(f"Screenshots saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
