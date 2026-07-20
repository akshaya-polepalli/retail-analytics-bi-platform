from sqlalchemy import text

from src.analytics.kpis import get_daily_kpis, get_top_products
from src.database.connection import engine
from src.jobs.daily_etl import run_daily_etl
from src.jobs.executive_report import run_executive_report


def test_daily_etl_loads_core_tables(requires_db):
    run_daily_etl()

    with engine.connect() as conn:
        customers = conn.execute(text("SELECT COUNT(*) FROM core.customers")).scalar()
        products = conn.execute(text("SELECT COUNT(*) FROM core.products")).scalar()
        orders = conn.execute(text("SELECT COUNT(*) FROM core.orders")).scalar()
        runs = conn.execute(
            text("SELECT status FROM audit.workflow_runs WHERE job_name = 'daily_etl' ORDER BY run_id DESC LIMIT 1")
        ).scalar()

    assert customers == 20
    assert products == 15
    assert orders == 70
    assert runs == "SUCCESS"


def test_executive_report_creates_summary(requires_db):
    run_daily_etl()
    run_executive_report()

    kpis = get_daily_kpis()
    products = get_top_products()

    assert kpis["total_orders"] >= 0
    assert not products.empty

    with engine.connect() as conn:
        summary_count = conn.execute(text("SELECT COUNT(*) FROM audit.ai_summaries")).scalar()
        report_status = conn.execute(
            text("SELECT status FROM audit.workflow_runs WHERE job_name = 'executive_report' ORDER BY run_id DESC LIMIT 1")
        ).scalar()

    assert summary_count >= 1
    assert report_status == "SUCCESS"


def test_kpi_views_return_expected_shape(requires_db):
    run_daily_etl()
    kpis = get_daily_kpis()

    assert {"report_date", "total_orders", "total_revenue", "total_profit", "avg_order_value"} <= set(kpis.keys())
