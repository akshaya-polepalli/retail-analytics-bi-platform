import pandas as pd

from src.etl.validate import validate_orders


def test_validate_rejects_invalid_quantity():
    df = pd.DataFrame(
        [
            {
                "order_id": 1,
                "customer_id": 1,
                "product_id": 101,
                "order_date": "2026-07-19",
                "quantity": 0,
                "unit_price": 25.0,
                "total_amount": 0.0,
            }
        ]
    )

    valid_df, reject_df = validate_orders(df)
    assert valid_df.empty
    assert len(reject_df) == 1
    assert "Invalid quantity" in reject_df.iloc[0]["reject_reason"]


def test_validate_accepts_valid_row():
    df = pd.DataFrame(
        [
            {
                "order_id": 1,
                "customer_id": 1,
                "product_id": 101,
                "order_date": "2026-07-19",
                "quantity": 2,
                "unit_price": 25.0,
                "total_amount": 50.0,
            }
        ]
    )

    valid_df, reject_df = validate_orders(df)
    assert len(valid_df) == 1
    assert reject_df.empty
