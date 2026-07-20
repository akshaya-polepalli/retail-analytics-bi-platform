import pandas as pd

from src.etl.extract import extract_csv, log_raw_orders
from src.etl.load import (
    load_customers,
    load_inventory,
    load_orders,
    load_products,
    load_rejected_orders,
)
from src.etl.transform import transform_orders
from src.etl.validate import validate_orders
from src.services.monitoring import log_run_finish, log_run_start
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_daily_etl() -> int:
    run_id = log_run_start("daily_etl")
    logger.info("Starting daily ETL")

    try:
        customers_df = extract_csv("customers.csv")
        products_df = extract_csv("products.csv")
        inventory_df = extract_csv("inventory.csv")
        orders_df = extract_csv("orders.csv")

        log_raw_orders(orders_df, "orders.csv")

        customer_count = load_customers(customers_df.to_dict(orient="records"))
        product_count = load_products(products_df.to_dict(orient="records"))
        inventory_count = load_inventory(inventory_df.to_dict(orient="records"))

        valid_df, reject_df = validate_orders(orders_df)
        load_rejected_orders(reject_df.to_dict(orient="records"))

        transformed_df = transform_orders(valid_df, products_df)
        order_count = load_orders(transformed_df.to_dict(orient="records"))

        total_processed = customer_count + product_count + inventory_count + order_count
        log_run_finish(run_id, "SUCCESS", total_processed)
        logger.info("Daily ETL completed: %s records processed", total_processed)
        return total_processed

    except Exception as exc:
        log_run_finish(run_id, "FAILED", error_message=str(exc))
        logger.exception("Daily ETL failed")
        raise


if __name__ == "__main__":
    run_daily_etl()
