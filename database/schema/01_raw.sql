CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE raw.orders (
    id SERIAL PRIMARY KEY,
    source_name TEXT NOT NULL,
    payload JSONB NOT NULL,
    ingested_at TIMESTAMP DEFAULT NOW()
);
