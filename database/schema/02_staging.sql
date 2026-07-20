CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE staging.orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    order_date DATE NOT NULL,
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE staging.orders_rejects (
    id SERIAL PRIMARY KEY,
    source_payload JSONB,
    reject_reason TEXT,
    rejected_at TIMESTAMP DEFAULT NOW()
);
