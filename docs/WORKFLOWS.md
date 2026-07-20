# Workflow Documentation

This project replaces visual n8n workflows with version-controlled Python jobs.

## Workflow 1: Daily ETL

**Module:** `src/jobs/daily_etl.py`

```text
Start
  → Log run in audit.workflow_runs
  → Extract CSV files
  → Log raw payloads
  → Load customers, products, inventory
  → Validate orders
  → Save rejected rows
  → Transform and calculate profit
  → UPSERT orders into core.orders
  → Mark run SUCCESS or FAILED
```

## Workflow 2: Executive Report

**Module:** `src/jobs/executive_report.py`

```text
Start
  → Query analytics views
  → Build KPI JSON payload
  → Generate AI/template summary
  → Save to audit.ai_summaries
  → Send optional Slack/email notification
  → Mark run SUCCESS or FAILED
```

## Workflow 3: Health Check

**Module:** `src/jobs/health_check.py`

```text
Start
  → Count failed workflow runs in last 24 hours
  → If failures exist, create audit.alerts record
  → Send optional Slack alert
  → Mark run SUCCESS or FAILED
```

## Scheduler

**Module:** `src/scheduler.py`

| Job | Cron / Interval |
|-----|-----------------|
| `daily_etl` | Daily at 07:00 |
| `executive_report` | Daily at 07:15 |
| `health_check` | Every 1 hour |

## Manual Execution

```powershell
python -m src.jobs.daily_etl
python -m src.jobs.executive_report
python -m src.jobs.health_check
python -m src.run_pipeline
```
