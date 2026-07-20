import json

import pandas as pd

REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "unit_price",
    "total_amount",
]


def validate_orders(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    valid_rows: list[dict] = []
    rejected_rows: list[dict] = []

    for _, row in df.iterrows():
        reasons: list[str] = []

        if row.isnull().any():
            reasons.append("Missing required value")

        try:
            quantity = int(row["quantity"])
            unit_price = float(row["unit_price"])
            total_amount = float(row["total_amount"])
        except (TypeError, ValueError):
            reasons.append("Invalid numeric value")
            quantity = unit_price = total_amount = 0

        if quantity <= 0:
            reasons.append("Invalid quantity")

        if unit_price <= 0:
            reasons.append("Invalid unit price")

        if total_amount <= 0:
            reasons.append("Invalid total amount")

        expected_total = round(quantity * unit_price, 2)
        if abs(expected_total - total_amount) > 0.05:
            reasons.append("Total amount mismatch")

        if reasons:
            rejected_rows.append(
                {
                    "source_payload": json.dumps(row.to_dict(), default=str),
                    "reject_reason": "; ".join(reasons),
                }
            )
        else:
            valid_rows.append(row.to_dict())

    valid_df = pd.DataFrame(valid_rows)
    reject_df = pd.DataFrame(rejected_rows)
    return valid_df, reject_df
