CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.v_daily_kpis AS
SELECT
    (CURRENT_DATE - INTERVAL '1 day')::DATE AS report_date,
    COUNT(DISTINCT order_id) AS total_orders,
    COALESCE(SUM(total_amount), 0) AS total_revenue,
    COALESCE(SUM(profit_amount), 0) AS total_profit,
    COALESCE(ROUND(AVG(total_amount), 2), 0) AS avg_order_value
FROM core.orders
WHERE order_date = (CURRENT_DATE - INTERVAL '1 day')::DATE;

CREATE OR REPLACE VIEW analytics.v_top_products AS
SELECT
    p.product_name,
    SUM(o.quantity) AS units_sold,
    SUM(o.total_amount) AS revenue
FROM core.orders o
JOIN core.products p ON o.product_id = p.product_id
WHERE o.order_date >= (CURRENT_DATE - INTERVAL '30 day')::DATE
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 10;

CREATE OR REPLACE VIEW analytics.v_customer_growth AS
SELECT
    DATE_TRUNC('month', signup_date)::DATE AS signup_month,
    COUNT(*) AS new_customers
FROM core.customers
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW analytics.v_inventory_health AS
SELECT
    p.product_name,
    i.stock_qty,
    i.reorder_level,
    CASE
        WHEN i.stock_qty <= i.reorder_level THEN 'LOW'
        ELSE 'OK'
    END AS stock_status
FROM core.inventory i
JOIN core.products p ON i.product_id = p.product_id;

CREATE OR REPLACE VIEW analytics.v_monthly_revenue AS
SELECT
    DATE_TRUNC('month', order_date)::DATE AS month_start,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(total_amount) AS total_revenue,
    SUM(profit_amount) AS total_profit
FROM core.orders
GROUP BY 1
ORDER BY 1;
