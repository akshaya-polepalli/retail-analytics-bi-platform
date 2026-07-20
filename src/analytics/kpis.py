import pandas as pd
from sqlalchemy import text

from src.database.connection import engine


def get_kpis_for_date(report_date) -> dict:
    query = text("""
        SELECT
            :report_date AS report_date,
            COUNT(DISTINCT order_id) AS total_orders,
            COALESCE(SUM(total_amount), 0) AS total_revenue,
            COALESCE(SUM(profit_amount), 0) AS total_profit,
            COALESCE(ROUND(AVG(total_amount), 2), 0) AS avg_order_value
        FROM core.orders
        WHERE order_date = :report_date
    """)
    with engine.connect() as conn:
        row = conn.execute(query, {"report_date": report_date}).mappings().one()
    return dict(row)


def get_top_products_for_range(start_date, end_date) -> pd.DataFrame:
    query = text("""
        SELECT
            p.product_name,
            SUM(o.quantity) AS units_sold,
            SUM(o.total_amount) AS revenue
        FROM core.orders o
        JOIN core.products p ON o.product_id = p.product_id
        WHERE o.order_date BETWEEN :start_date AND :end_date
        GROUP BY p.product_name
        ORDER BY revenue DESC
        LIMIT 10
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"start_date": start_date, "end_date": end_date})


def get_date_bounds() -> tuple:
    query = text("SELECT MIN(order_date) AS min_date, MAX(order_date) AS max_date FROM core.orders")
    with engine.connect() as conn:
        row = conn.execute(query).mappings().one()
    return row["min_date"], row["max_date"]


def get_daily_kpis() -> dict:
    query = text("SELECT * FROM analytics.v_daily_kpis")
    with engine.connect() as conn:
        row = conn.execute(query).mappings().one()
    return dict(row)


def get_top_products() -> pd.DataFrame:
    query = text("SELECT * FROM analytics.v_top_products")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_customer_growth() -> pd.DataFrame:
    query = text("SELECT * FROM analytics.v_customer_growth")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_inventory_health() -> pd.DataFrame:
    query = text("SELECT * FROM analytics.v_inventory_health")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_inventory_alerts() -> pd.DataFrame:
    query = text("""
        SELECT * FROM analytics.v_inventory_health
        WHERE stock_status = 'LOW'
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_monthly_revenue() -> pd.DataFrame:
    query = text("SELECT * FROM analytics.v_monthly_revenue")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_latest_ai_summary() -> dict | None:
    query = text("""
        SELECT summary_text, report_date, created_at
        FROM audit.ai_summaries
        ORDER BY created_at DESC
        LIMIT 1
    """)
    with engine.connect() as conn:
        row = conn.execute(query).mappings().first()
    return dict(row) if row else None


def get_workflow_runs(limit: int = 20) -> pd.DataFrame:
    query = text("""
        SELECT run_id, job_name, status, records_processed,
               error_message, started_at, finished_at
        FROM audit.workflow_runs
        ORDER BY started_at DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"limit": limit})
