import pandas as pd


def transform_orders(orders_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    if orders_df.empty:
        return orders_df

    df = orders_df.merge(
        products_df[["product_id", "unit_cost"]],
        on="product_id",
        how="left",
    )
    df["profit_amount"] = df["total_amount"] - (df["unit_cost"] * df["quantity"])
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].astype(float)
    df["total_amount"] = df["total_amount"].astype(float)
    df["profit_amount"] = df["profit_amount"].astype(float)
    return df
