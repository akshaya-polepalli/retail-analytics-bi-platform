from sqlalchemy import text

from src.database.connection import engine


def _execute_batch(query: str, records: list[dict]) -> int:
    if not records:
        return 0

    with engine.begin() as conn:
        conn.execute(text(query), records)

    return len(records)


def load_customers(records: list[dict]) -> int:
    query = """
        INSERT INTO core.customers (
            customer_id, customer_name, email, city, signup_date
        )
        VALUES (
            :customer_id, :customer_name, :email, :city, :signup_date
        )
        ON CONFLICT (customer_id) DO UPDATE SET
            customer_name = EXCLUDED.customer_name,
            email = EXCLUDED.email,
            city = EXCLUDED.city,
            signup_date = EXCLUDED.signup_date
    """
    return _execute_batch(query, records)


def load_products(records: list[dict]) -> int:
    query = """
        INSERT INTO core.products (
            product_id, product_name, category, unit_cost, unit_price
        )
        VALUES (
            :product_id, :product_name, :category, :unit_cost, :unit_price
        )
        ON CONFLICT (product_id) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            category = EXCLUDED.category,
            unit_cost = EXCLUDED.unit_cost,
            unit_price = EXCLUDED.unit_price
    """
    return _execute_batch(query, records)


def load_inventory(records: list[dict]) -> int:
    query = """
        INSERT INTO core.inventory (
            product_id, stock_qty, reorder_level
        )
        VALUES (
            :product_id, :stock_qty, :reorder_level
        )
        ON CONFLICT (product_id) DO UPDATE SET
            stock_qty = EXCLUDED.stock_qty,
            reorder_level = EXCLUDED.reorder_level,
            updated_at = NOW()
    """
    return _execute_batch(query, records)


def load_orders(records: list[dict]) -> int:
    query = """
        INSERT INTO core.orders (
            order_id, customer_id, product_id, order_date,
            quantity, unit_price, total_amount, profit_amount
        )
        VALUES (
            :order_id, :customer_id, :product_id, :order_date,
            :quantity, :unit_price, :total_amount, :profit_amount
        )
        ON CONFLICT (order_id) DO UPDATE SET
            customer_id = EXCLUDED.customer_id,
            product_id = EXCLUDED.product_id,
            order_date = EXCLUDED.order_date,
            quantity = EXCLUDED.quantity,
            unit_price = EXCLUDED.unit_price,
            total_amount = EXCLUDED.total_amount,
            profit_amount = EXCLUDED.profit_amount,
            updated_at = NOW()
    """
    return _execute_batch(query, records)


def load_rejected_orders(records: list[dict]) -> int:
    query = """
        INSERT INTO staging.orders_rejects (source_payload, reject_reason)
        VALUES (CAST(:source_payload AS JSONB), :reject_reason)
    """
    return _execute_batch(query, records)
