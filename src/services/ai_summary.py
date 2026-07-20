import json
from datetime import date

from sqlalchemy import text

from src.config.settings import settings
from src.database.connection import engine
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _build_fallback_summary(payload: dict) -> str:
    kpis = payload.get("kpis", {})
    top_products = payload.get("top_products", [])
    inventory_alerts = payload.get("inventory_alerts", [])

    top_product_line = "No product data available."
    if top_products:
        top = top_products[0]
        top_product_line = (
            f"Top product: {top.get('product_name')} "
            f"with revenue ${float(top.get('revenue', 0)):,.2f}."
        )

    alert_line = (
        f"{len(inventory_alerts)} products are below reorder level."
        if inventory_alerts
        else "Inventory levels are healthy."
    )

    return (
        f"Executive Summary for {kpis.get('report_date', date.today())}\n\n"
        f"1. What happened: Revenue was ${float(kpis.get('total_revenue', 0)):,.2f} "
        f"from {int(kpis.get('total_orders', 0))} orders. "
        f"Profit was ${float(kpis.get('total_profit', 0)):,.2f} "
        f"with AOV ${float(kpis.get('avg_order_value', 0)):,.2f}.\n"
        f"2. Why it happened: {top_product_line}\n"
        f"3. Business impact: Daily performance metrics are available for leadership review.\n"
        f"4. Recommended action: {alert_line}"
    )


def generate_executive_summary(payload: dict) -> str:
    summary_text = _build_fallback_summary(payload)
    model_name = "fallback-template"

    if settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = f"""
You are a senior business analyst.

Use ONLY the JSON data below.
Do NOT invent numbers.

Explain:
1. What happened
2. Why it happened
3. Business impact
4. Recommended action

JSON:
{json.dumps(payload, default=str)}
"""
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            summary_text = response.choices[0].message.content or summary_text
            model_name = settings.OPENAI_MODEL
        except Exception as exc:
            logger.warning("OpenAI summary failed, using fallback: %s", exc)

    report_date = payload.get("kpis", {}).get("report_date", date.today())

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO audit.ai_summaries (
                    report_date, kpis_json, summary_text, model_name, prompt_version
                )
                VALUES (
                    :report_date, CAST(:kpis_json AS JSONB),
                    :summary_text, :model_name, :prompt_version
                )
            """),
            {
                "report_date": report_date,
                "kpis_json": json.dumps(payload, default=str),
                "summary_text": summary_text,
                "model_name": model_name,
                "prompt_version": settings.PROMPT_VERSION,
            },
        )

    return summary_text
