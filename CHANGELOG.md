# Changelog

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-07-20

### Added
- PostgreSQL layered schema (raw, staging, core, analytics, audit)
- Python ETL pipeline with validation, transform, and idempotent load
- KPI SQL views for daily metrics, products, customers, inventory, and revenue trends
- Scheduled jobs via APScheduler (daily ETL, executive report, health check)
- AI executive summary service with OpenAI support and template fallback
- Optional Slack and email notifications
- Streamlit dashboard with seven analytical pages
- Docker Compose setup for PostgreSQL, worker, and dashboard services
- Unit and integration tests
- GitHub Actions CI workflow
- Architecture, deployment, interview, and demo documentation
- Screenshot generation script for README assets

### Notes
- Code-only orchestration replaces n8n workflows from the original playbook
- OpenAI and Slack integrations are optional
