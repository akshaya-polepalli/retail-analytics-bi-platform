import pandas as pd

from src.etl.transform import transform_orders


def test_transform_calculates_profit():
    orders = pd.DataFrame(
        [
            {
                "order_id": 1,
                "customer_id": 1,
                "product_id": 101,
                "order_date": "2026-07-19",
                "quantity": 2,
                "unit_price": 999.0,
                "total_amount": 1998.0,
            }
        ]
    )
    products = pd.DataFrame(
        [{"product_id": 101, "unit_cost": 700.0, "unit_price": 999.0}]
    )

    result = transform_orders(orders, products)
    assert float(result.iloc[0]["profit_amount"]) == 598.0
