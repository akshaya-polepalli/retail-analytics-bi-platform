CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE core.customers (
    customer_id BIGINT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT,
    city TEXT,
    signup_date DATE
);

CREATE TABLE core.products (
    product_id BIGINT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    unit_cost NUMERIC(10, 2),
    unit_price NUMERIC(10, 2)
);

CREATE TABLE core.orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT REFERENCES core.customers(customer_id),
    product_id BIGINT REFERENCES core.products(product_id),
    order_date DATE NOT NULL,
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    profit_amount NUMERIC(12, 2),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE core.inventory (
    product_id BIGINT PRIMARY KEY REFERENCES core.products(product_id),
    stock_qty INT NOT NULL,
    reorder_level INT DEFAULT 10,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orders_order_date ON core.orders(order_date);
CREATE INDEX idx_orders_customer_id ON core.orders(customer_id);
CREATE INDEX idx_orders_product_id ON core.orders(product_id);
