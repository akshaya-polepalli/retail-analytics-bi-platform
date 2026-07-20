# Entity Relationship Diagram

## Core Business Model

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    PRODUCTS ||--o{ ORDERS : contains
    PRODUCTS ||--|| INVENTORY : tracked_by

    CUSTOMERS {
        bigint customer_id PK
        text customer_name
        text email
        text city
        date signup_date
    }

    PRODUCTS {
        bigint product_id PK
        text product_name
        text category
        numeric unit_cost
        numeric unit_price
    }

    ORDERS {
        bigint order_id PK
        bigint customer_id FK
        bigint product_id FK
        date order_date
        int quantity
        numeric unit_price
        numeric total_amount
        numeric profit_amount
        timestamp updated_at
    }

    INVENTORY {
        bigint product_id PK,FK
        int stock_qty
        int reorder_level
        timestamp updated_at
    }
```

## Audit and Operations Model

```mermaid
erDiagram
    WORKFLOW_RUNS {
        serial run_id PK
        text job_name
        text status
        int records_processed
        text error_message
        timestamp started_at
        timestamp finished_at
    }

    AI_SUMMARIES {
        serial summary_id PK
        date report_date
        jsonb kpis_json
        text summary_text
        text model_name
        text prompt_version
        timestamp created_at
    }

    ALERTS {
        serial alert_id PK
        text alert_type
        text alert_message
        text severity
        timestamp created_at
    }

    ORDERS_REJECTS {
        serial id PK
        jsonb source_payload
        text reject_reason
        timestamp rejected_at
    }
```

## Schema Layers

```text
raw.orders              -- immutable ingest payloads
staging.orders          -- cleaned staging area
staging.orders_rejects  -- invalid records with reasons
core.*                  -- business entities
analytics.v_*           -- KPI and reporting views
audit.*                 -- operational telemetry
```
