import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text

from src.analytics.kpis import (
    get_customer_growth,
    get_date_bounds,
    get_inventory_health,
    get_kpis_for_range,
    get_latest_ai_summary,
    get_monthly_revenue,
    get_top_products_for_range,
    get_workflow_runs,
)
from src.database.connection import engine

# ---------------------------------------------------------------------------
# Page config & styling
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Retail BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = {
    "Executive Overview": "Daily KPIs and business summary",
    "Sales Performance": "Revenue and profit trends over time",
    "Product Performance": "Best-selling products by revenue",
    "Customer Analytics": "New customer signups by month",
    "Inventory Health": "Stock levels and low-stock alerts",
    "AI Insights": "Automated executive summary",
    "System Health": "ETL job monitoring (technical)",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60)
def check_database() -> tuple[bool, str, date | None, date | None]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            min_date, max_date = get_date_bounds()
        if min_date and max_date:
            return True, "Database connected", min_date, max_date
        return True, "Connected — no order data yet", None, None
    except Exception as exc:
        return False, f"Database unavailable: {exc}", None, None


def filter_by_date_range(
    df: pd.DataFrame, column: str, start_date: date, end_date: date
) -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return df
    series = pd.to_datetime(df[column], errors="coerce")
    mask = (series >= pd.Timestamp(start_date)) & (series <= pd.Timestamp(end_date))
    return df.loc[mask].copy()


def format_currency(value) -> str:
    return f"${float(value):,.2f}"


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def render_summary(text: str) -> None:
    with st.container(border=True):
        st.markdown(text)


def style_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fafafa"),
    )
    return fig


def download_csv(df: pd.DataFrame, filename: str) -> None:
    if df.empty:
        return
    st.download_button(
        "Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


def filter_monthly_by_range(
    df: pd.DataFrame, start_date: date, end_date: date
) -> pd.DataFrame:
    """Include months that overlap the selected date range."""
    if df.empty:
        return df
    result = df.copy()
    result["month_start"] = pd.to_datetime(result["month_start"])
    month_end = result["month_start"] + pd.offsets.MonthEnd(0)
    mask = (result["month_start"].dt.date <= end_date) & (month_end.dt.date >= start_date)
    return result.loc[mask].copy()


def render_trend_chart(df: pd.DataFrame, x: str, y_cols: list[str], title: str) -> None:
    if df.empty:
        st.info("No data to display for the selected period.")
        return

    plot_df = df.copy()
    plot_df["period"] = pd.to_datetime(plot_df[x]).dt.strftime("%Y-%m")

    if len(plot_df) == 1:
        melted = plot_df.melt(id_vars=["period"], value_vars=y_cols, var_name="Metric", value_name="Amount")
        fig = px.bar(
            melted, x="period", y="Amount", color="Metric", barmode="group", title=title,
            labels={"period": "Month", "Amount": "USD ($)"},
        )
    else:
        melted = plot_df.melt(id_vars=["period"], value_vars=y_cols, var_name="Metric", value_name="Amount")
        fig = px.line(
            melted, x="period", y="Amount", color="Metric", markers=True, title=title,
            labels={"period": "Month", "Amount": "USD ($)"},
        )
        fig.update_xaxes(type="category")

    fig.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20), legend_title_text="")
    st.plotly_chart(style_chart(fig), width="stretch")


def render_monthly_bar_chart(
    df: pd.DataFrame, date_col: str, value_col: str, title: str, y_label: str = "Count"
) -> None:
    if df.empty:
        st.info("No data to display for the selected period.")
        return

    plot_df = df.copy()
    plot_df["month"] = pd.to_datetime(plot_df[date_col]).dt.strftime("%Y-%m")
    plot_df = plot_df.sort_values("month")

    fig = px.bar(
        plot_df,
        x="month",
        y=value_col,
        text=value_col,
        title=title,
        labels={"month": "Month", value_col: y_label},
    )
    fig.update_traces(textposition="outside", width=0.6)
    fig.update_xaxes(type="category", title="Month")
    fig.update_yaxes(dtick=1, rangemode="tozero")
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20), bargap=0.3)
    st.plotly_chart(style_chart(fig), width="stretch")


def render_bar_chart(df: pd.DataFrame, category_col: str, value_col: str, title: str) -> None:
    if df.empty:
        st.info("No data to display for the selected period.")
        return
    fig = px.bar(
        df, x=value_col, y=category_col, orientation="h", title=title,
        labels={value_col: "USD ($)", category_col: ""},
    )
    fig.update_layout(height=max(320, len(df) * 36), margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(style_chart(fig), width="stretch")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("Retail BI Platform")
st.sidebar.caption("Automated business intelligence for retail executives")

db_ok, db_message, min_date, max_date = check_database()

if db_ok:
    st.sidebar.success(f"Database connected")
else:
    st.sidebar.error(db_message)
    st.error("Cannot load dashboard. Start PostgreSQL and run: `python -m src.run_pipeline`")
    st.stop()

if min_date and max_date:
    st.sidebar.markdown(f"**Data available:** {min_date} → {max_date}")
    default_end = max_date
    default_start = min_date
else:
    default_start = date.today() - timedelta(days=30)
    default_end = date.today()

st.sidebar.markdown("---")
st.sidebar.markdown("**Navigate**")
page = st.sidebar.radio(
    "Page",
    list(PAGES.keys()),
    format_func=lambda p: p,
    label_visibility="collapsed",
)
st.sidebar.caption(PAGES[page])

st.sidebar.markdown("---")
st.sidebar.markdown("**Date range**")
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input(
    "From", default_start, min_value=min_date or default_start, max_value=max_date or default_end,
    label_visibility="collapsed",
)
end_date = col2.date_input(
    "To", default_end, min_value=min_date or default_start, max_value=max_date or default_end,
    label_visibility="collapsed",
)

if start_date > end_date:
    st.sidebar.error("Start date must be on or before end date.")
    st.stop()

st.sidebar.caption(f"Showing: {start_date} to {end_date}")


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

if page == "Executive Overview":
    page_header(
        "Executive Overview",
        "Business question: How did the business perform in the selected period?",
    )

    kpis = get_kpis_for_range(start_date, end_date)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", format_currency(kpis["total_revenue"]))
    c2.metric("Total Orders", f"{int(kpis['total_orders']):,}")
    c3.metric("Total Profit", format_currency(kpis["total_profit"]))
    c4.metric("Avg Order Value", format_currency(kpis["avg_order_value"]))

    st.markdown("---")
    st.subheader("Executive Summary")

    summary = get_latest_ai_summary()
    if summary:
        render_summary(summary["summary_text"])
        st.caption(f"Last generated: {summary['created_at']}")
    else:
        st.info("No summary yet. Run `python -m src.run_pipeline` to generate one.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Top Products")
        products = get_top_products_for_range(start_date, end_date)
        if products.empty:
            st.info("No product sales in this period.")
        else:
            render_bar_chart(products.head(5), "product_name", "revenue", "Top 5 Products")
    with col_b:
        st.subheader("Inventory Alerts")
        inventory = get_inventory_health()
        low = inventory[inventory["stock_status"] == "LOW"] if not inventory.empty else inventory
        if low.empty:
            st.success("All products are above reorder level.")
        else:
            st.warning(f"{len(low)} product(s) need restocking")
            st.dataframe(low[["product_name", "stock_qty", "reorder_level"]], hide_index=True, width="stretch")

elif page == "Sales Performance":
    page_header(
        "Sales Performance",
        "Business question: How are revenue and profit trending month over month?",
    )

    monthly = get_monthly_revenue()
    filtered = filter_monthly_by_range(monthly, start_date, end_date)

    if filtered.empty:
        st.warning("No sales data for the selected date range.")
    else:
        total_rev = filtered["total_revenue"].sum()
        total_profit = filtered["total_profit"].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Period Revenue", format_currency(total_rev))
        c2.metric("Period Profit", format_currency(total_profit))
        c3.metric("Months in View", len(filtered))

        render_trend_chart(
            filtered, "month_start", ["total_revenue", "total_profit"], "Monthly Revenue & Profit"
        )

        display = filtered.copy()
        display["month_start"] = pd.to_datetime(display["month_start"]).dt.strftime("%Y-%m")
        display["total_revenue"] = display["total_revenue"].map(lambda x: format_currency(x))
        display["total_profit"] = display["total_profit"].map(lambda x: format_currency(x))
        display.columns = ["Month", "Orders", "Revenue", "Profit"]
        st.dataframe(display, hide_index=True, width="stretch")
        download_csv(filtered, "sales_performance.csv")

elif page == "Product Performance":
    page_header(
        "Product Performance",
        "Business question: Which products drive the most revenue?",
    )

    products = get_top_products_for_range(start_date, end_date)
    if products.empty:
        st.warning("No product sales for the selected date range.")
    else:
        c1, c2 = st.columns(2)
        c1.metric("Products Sold", len(products))
        c2.metric("Top Product Revenue", format_currency(products.iloc[0]["revenue"]))

        render_bar_chart(products, "product_name", "revenue", "Revenue by Product")

        display = products.copy()
        display["revenue"] = display["revenue"].map(lambda x: format_currency(x))
        display.columns = ["Product", "Units Sold", "Revenue"]
        st.dataframe(display, hide_index=True, width="stretch")
        download_csv(products, "product_performance.csv")

elif page == "Customer Analytics":
    page_header(
        "Customer Analytics",
        "Business question: How is customer acquisition growing over time?",
    )

    growth = get_customer_growth()
    if growth.empty:
        st.warning("No customer data available.")
    else:
        total_customers = growth["new_customers"].sum()
        latest_month = growth.iloc[-1]["new_customers"] if len(growth) > 0 else 0
        avg_monthly = growth["new_customers"].mean()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total New Customers", f"{int(total_customers):,}")
        c2.metric("Latest Month Signups", f"{int(latest_month):,}")
        c3.metric("Avg Signups / Month", f"{avg_monthly:.1f}")

        render_monthly_bar_chart(
            growth, "signup_month", "new_customers", "New Customers by Month", "New Customers"
        )

        plot_df = growth.copy()
        plot_df["month"] = pd.to_datetime(plot_df["signup_month"]).dt.strftime("%Y-%m")
        plot_df = plot_df.sort_values("month")
        plot_df["cumulative_customers"] = plot_df["new_customers"].cumsum()

        fig = px.line(
            plot_df, x="month", y="cumulative_customers", markers=True, text="cumulative_customers",
            title="Cumulative Customer Growth",
            labels={"month": "Month", "cumulative_customers": "Total Customers"},
        )
        fig.update_traces(textposition="top center")
        fig.update_xaxes(type="category")
        fig.update_yaxes(dtick=1, rangemode="tozero")
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(style_chart(fig), width="stretch")

        display = growth.copy()
        display["signup_month"] = pd.to_datetime(display["signup_month"]).dt.strftime("%Y-%m")
        display.columns = ["Month", "New Customers"]
        st.dataframe(display, hide_index=True, width="stretch")
        download_csv(growth, "customer_growth.csv")

elif page == "Inventory Health":
    page_header(
        "Inventory Health",
        "Business question: Do we have enough stock to fulfill demand?",
    )

    inventory = get_inventory_health()
    if inventory.empty:
        st.warning("No inventory data available.")
    else:
        low = inventory[inventory["stock_status"] == "LOW"]
        ok = inventory[inventory["stock_status"] == "OK"]

        c1, c2, c3 = st.columns(3)
        c1.metric("Total SKUs", len(inventory))
        c2.metric("Healthy Stock", len(ok))
        c3.metric("Low Stock", len(low))

        if len(low) > 0:
            st.warning(f"Action needed: {len(low)} product(s) are at or below reorder level.")
        else:
            st.success("All products are above reorder level.")

        display = inventory.copy()
        display["status_label"] = display["stock_status"].map({"OK": "✓ OK", "LOW": "⚠ Low"})
        display = display[["product_name", "stock_qty", "reorder_level", "status_label"]]
        display.columns = ["Product", "Stock Qty", "Reorder Level", "Status"]
        st.dataframe(display, hide_index=True, width="stretch")
        download_csv(inventory, "inventory_health.csv")

elif page == "AI Insights":
    page_header(
        "AI Insights",
        "Business question: What should management know and do next?",
    )

    summary = get_latest_ai_summary()
    if not summary:
        st.info("No AI summary generated yet. Run `python -m src.run_pipeline` first.")
    else:
        st.markdown("### Latest Summary")
        render_summary(summary["summary_text"])
        st.caption(f"Report date: {summary['report_date']} | Generated: {summary['created_at']}")

    with st.expander("View summary history"):
        query = text("""
            SELECT report_date, model_name, created_at,
                   LEFT(summary_text, 200) AS summary_preview
            FROM audit.ai_summaries
            ORDER BY created_at DESC
            LIMIT 10
        """)
        with engine.connect() as conn:
            history = pd.read_sql(query, conn)
        if history.empty:
            st.info("No history yet.")
        else:
            history.columns = ["Report Date", "Model", "Created At", "Preview"]
            st.dataframe(history, hide_index=True, width="stretch")

elif page == "System Health":
    page_header(
        "System Health",
        "Technical view: Are automated data pipelines running successfully?",
    )

    runs = get_workflow_runs()
    if runs.empty:
        st.info("No pipeline runs logged yet. Run `python -m src.run_pipeline`.")
    else:
        success = (runs["status"] == "SUCCESS").sum()
        failed = (runs["status"] == "FAILED").sum()
        rate = success / len(runs) * 100 if len(runs) else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Success Rate", f"{rate:.0f}%")
        c2.metric("Successful Runs", success)
        c3.metric("Failed Runs", failed)

        display = runs.copy()
        display["started_at"] = pd.to_datetime(display["started_at"]).dt.strftime("%Y-%m-%d %H:%M")
        display["finished_at"] = pd.to_datetime(display["finished_at"]).dt.strftime("%Y-%m-%d %H:%M")
        display = display[["job_name", "status", "records_processed", "started_at", "finished_at", "error_message"]]
        display.columns = ["Job", "Status", "Records", "Started", "Finished", "Error"]
        st.dataframe(display, hide_index=True, width="stretch")
        download_csv(runs, "workflow_runs.csv")
