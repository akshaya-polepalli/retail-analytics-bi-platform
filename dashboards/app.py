import sys
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
from sqlalchemy import text

from src.analytics.kpis import (
    get_customer_growth,
    get_date_bounds,
    get_inventory_health,
    get_kpis_for_date,
    get_latest_ai_summary,
    get_monthly_revenue,
    get_top_products_for_range,
    get_workflow_runs,
)
from src.database.connection import engine

st.set_page_config(
    page_title="Enterprise BI Platform",
    page_icon="📊",
    layout="wide",
)

PAGES = [
    "Executive Overview",
    "Sales Performance",
    "Customer Analytics",
    "Product Performance",
    "Inventory Health",
    "Workflow Monitoring",
    "AI Insights",
]


def download_csv_button(df: pd.DataFrame, filename: str, label: str = "Download CSV") -> None:
    if df.empty:
        return
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


def render_date_filters():
    try:
        min_date, max_date = get_date_bounds()
    except Exception:
        min_date = max_date = date.today()

    if not min_date or not max_date:
        min_date = date.today() - timedelta(days=30)
        max_date = date.today()

    col1, col2 = st.sidebar.columns(2)
    start_date = col1.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
    end_date = col2.date_input("End date", max_date, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.sidebar.error("Start date must be before end date.")
    return start_date, end_date


page = st.sidebar.selectbox("Navigate", PAGES)
st.sidebar.markdown("---")
start_date, end_date = render_date_filters()
st.sidebar.caption("Code-only BI automation platform")


if page == "Executive Overview":
    st.title("Executive Overview")

    kpis = get_kpis_for_date(end_date)
    previous_date = end_date - timedelta(days=1)
    previous_kpis = get_kpis_for_date(previous_date)

    revenue_delta = float(kpis["total_revenue"]) - float(previous_kpis["total_revenue"])
    orders_delta = int(kpis["total_orders"]) - int(previous_kpis["total_orders"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenue", f"${float(kpis['total_revenue']):,.2f}", f"{revenue_delta:,.2f}")
    col2.metric("Orders", f"{int(kpis['total_orders']):,}", f"{orders_delta:,}")
    col3.metric("Profit", f"${float(kpis['total_profit']):,.2f}")
    col4.metric("AOV", f"${float(kpis['avg_order_value']):,.2f}")

    st.subheader("AI Executive Summary")
    summary = get_latest_ai_summary()
    if summary:
        st.write(summary["summary_text"])
        st.caption(f"Report date: {summary['report_date']}")
    else:
        st.info("Run the executive report job to generate an AI summary.")

    overview_df = pd.DataFrame([kpis])
    download_csv_button(overview_df, "executive_overview.csv")

elif page == "Sales Performance":
    st.title("Sales Performance")
    monthly = get_monthly_revenue()
    if monthly.empty:
        st.warning("No sales data available.")
    else:
        filtered = monthly[
            (monthly["month_start"] >= pd.to_datetime(start_date))
            & (monthly["month_start"] <= pd.to_datetime(end_date))
        ]
        st.line_chart(filtered.set_index("month_start")[["total_revenue", "total_profit"]])
        st.dataframe(filtered, use_container_width=True)
        download_csv_button(filtered, "sales_performance.csv")

elif page == "Customer Analytics":
    st.title("Customer Analytics")
    growth = get_customer_growth()
    if growth.empty:
        st.warning("No customer data available.")
    else:
        st.bar_chart(growth.set_index("signup_month")["new_customers"])
        st.dataframe(growth, use_container_width=True)
        download_csv_button(growth, "customer_growth.csv")

elif page == "Product Performance":
    st.title("Product Performance")
    products = get_top_products_for_range(start_date, end_date)
    if products.empty:
        st.warning("No product data available for selected range.")
    else:
        st.bar_chart(products.set_index("product_name")["revenue"])
        st.dataframe(products, use_container_width=True)
        download_csv_button(products, "product_performance.csv")

elif page == "Inventory Health":
    st.title("Inventory Health")
    inventory = get_inventory_health()
    if inventory.empty:
        st.warning("No inventory data available.")
    else:
        low_stock = inventory[inventory["stock_status"] == "LOW"]
        st.metric("Low Stock Items", len(low_stock))
        if len(low_stock) > 0:
            st.warning("Some products are below reorder level.")
        st.dataframe(inventory, use_container_width=True)
        download_csv_button(inventory, "inventory_health.csv")

elif page == "Workflow Monitoring":
    st.title("Workflow Monitoring")
    runs = get_workflow_runs()
    if runs.empty:
        st.info("No workflow runs logged yet.")
    else:
        success_rate = (runs["status"] == "SUCCESS").mean() * 100
        st.metric("Success Rate (recent runs)", f"{success_rate:.1f}%")
        st.dataframe(runs, use_container_width=True)
        download_csv_button(runs, "workflow_runs.csv")

elif page == "AI Insights":
    st.title("AI Insights")
    summary = get_latest_ai_summary()
    if not summary:
        st.info("No AI summaries generated yet.")
    else:
        st.write(summary["summary_text"])
        st.caption(f"Generated at: {summary['created_at']}")

    with st.expander("Recent summaries"):
        query = text("""
            SELECT report_date, model_name, created_at, summary_text
            FROM audit.ai_summaries
            ORDER BY created_at DESC
            LIMIT 10
        """)
        with engine.connect() as conn:
            history = pd.read_sql(query, conn)
        st.dataframe(history, use_container_width=True)
        download_csv_button(history, "ai_summaries.csv")
