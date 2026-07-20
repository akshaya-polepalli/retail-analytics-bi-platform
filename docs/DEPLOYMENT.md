# Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+
- Docker Desktop
- Git

### Steps

```powershell
cd enterprise-bi-platform
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
cd docker
docker compose up -d postgres
cd ..
python -m src.run_pipeline
streamlit run dashboards/app.py
```

Default PostgreSQL port is **5433** (to avoid conflicts with other local Postgres instances).

## Docker Full Stack

```powershell
cd docker
docker compose up -d --build
```

Services:
- `bi_postgres` — PostgreSQL on port 5433
- `bi_worker` — APScheduler worker
- `bi_dashboard` — Streamlit on port 8501

## Production Considerations

For a real production deployment, extend this project with:

1. Managed PostgreSQL (RDS, Cloud SQL, Azure Database)
2. Secrets manager for API keys and SMTP credentials
3. Container registry and orchestrator (ECS, Kubernetes, Render)
4. Reverse proxy and TLS termination
5. Centralized logging (CloudWatch, ELK, Datadog)
6. Alerting on failed workflow runs
7. Backup and retention policies for audit tables

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `OPENAI_API_KEY` | No | Enables OpenAI-generated summaries |
| `SLACK_WEBHOOK_URL` | No | Enables Slack notifications |
| `SMTP_*` | No | Enables email delivery |
| `LOG_LEVEL` | No | Logging verbosity |

## Health Verification

```powershell
python -m src.jobs.health_check
pytest
python -m src.run_pipeline
```

Check:
- `audit.workflow_runs` has SUCCESS entries
- Dashboard loads KPI cards
- `audit.ai_summaries` contains at least one summary
