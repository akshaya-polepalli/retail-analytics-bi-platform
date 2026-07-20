# Interview Guide

## Elevator Pitch

"I built an Enterprise AI Business Intelligence Automation Platform that automates the complete reporting lifecycle. Using scheduled Python jobs, PostgreSQL analytics views, and optional AI-generated summaries, the platform ingests retail data, validates and transforms it, calculates KPIs, updates an executive dashboard, and logs every workflow run for monitoring."

## Project Overview

### What business problem does it solve?
Retail executives need daily visibility into revenue, orders, profit, inventory health, and customer growth without manual spreadsheet work.

### Why Python instead of n8n?
Python gives full version control, unit tests, easier debugging, and a stronger story for data analyst and data engineer interviews.

### Why PostgreSQL?
It provides reliable storage, SQL analytics, constraints, indexes, and audit tables in one system.

## Architecture Questions

### Explain the end-to-end workflow
CSV data is extracted, validated, transformed, and loaded into PostgreSQL. Analytics views compute KPIs. A scheduled job generates an executive summary from validated KPI JSON. Results appear in Streamlit and optional notification channels.

### How does data move through the system?
`raw` → validation → `core` tables → `analytics` views → dashboard and AI summary → `audit` logs.

### Why modular architecture?
Separate modules for ETL, analytics, services, and jobs make the system easier to test, extend, and explain.

## Analytics Questions

### Which KPIs did you calculate?
- Revenue
- Orders
- Profit
- Average order value
- Top products
- Customer growth
- Inventory health

### Why are those KPIs important?
They give executives a daily snapshot of sales performance, product demand, customer acquisition, and operational risk from low inventory.

## AI Questions

### How is AI integrated?
The executive report job queries KPI views, builds structured JSON, and sends it to the AI summary service. The result is stored in `audit.ai_summaries`.

### How do you prevent hallucinations?
The model only receives validated KPI JSON. It is instructed not to invent numbers. A template fallback is used when no API key is configured.

## Deployment Questions

### Why Docker?
Docker standardizes PostgreSQL and application services across machines and simplifies onboarding for reviewers.

### How would you scale to millions of records?
Use incremental loads, batch processing, indexing, partitioning, materialized views, and eventually a dedicated warehouse such as Snowflake or BigQuery.

## Resume Bullets

- Developed an enterprise AI-powered Business Intelligence automation platform using Python, PostgreSQL, APScheduler, and Streamlit.
- Built a modular ETL pipeline with validation, reject handling, idempotent loading, and audit logging.
- Designed PostgreSQL analytics views and an executive dashboard for KPI monitoring and business storytelling.
- Implemented workflow monitoring, optional AI-assisted reporting, and stakeholder notification hooks.

## Future Improvements

- Role-based dashboard access
- Forecasting with time-series models
- Real-time ingestion
- Cloud deployment with CI/CD promotion
- Power BI or Metabase integration
