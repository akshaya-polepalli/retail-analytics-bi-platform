import json
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from src.config.settings import settings
from src.database.connection import engine


def extract_csv(filename: str) -> pd.DataFrame:
    path = settings.DATA_DIR / filename
    return pd.read_csv(path)


def log_raw_orders(df: pd.DataFrame, source_name: str) -> int:
    if df.empty:
        return 0

    records = [
        {"source_name": source_name, "payload": json.dumps(row, default=str)}
        for row in df.to_dict(orient="records")
    ]

    query = text("""
        INSERT INTO raw.orders (source_name, payload)
        VALUES (:source_name, CAST(:payload AS JSONB))
    """)

    with engine.begin() as conn:
        conn.execute(query, records)

    return len(records)
