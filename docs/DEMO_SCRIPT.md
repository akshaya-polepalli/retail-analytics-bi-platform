# Demo Video Script (2–3 minutes)

Use this script to record a short portfolio demo.

## Setup Before Recording

1. Start PostgreSQL: `cd docker && docker compose up -d postgres`
2. Run pipeline: `python -m src.run_pipeline`
3. Start dashboard: `streamlit run dashboards/app.py`
4. Optional: generate README assets with `python scripts/generate_screenshots.py`

## Script

### 0:00 – Introduction (20 sec)
"This is my Enterprise AI Business Intelligence Automation Platform. It automates daily retail reporting using Python, PostgreSQL, and Streamlit."

### 0:20 – Business Problem (20 sec)
"Executives need daily KPIs for revenue, orders, profit, inventory, and customer growth. This project replaces manual reporting with an automated pipeline."

### 0:40 – Architecture (30 sec)
Show README architecture diagram.
"CSV data flows through a Python ETL pipeline into PostgreSQL. Scheduled jobs compute KPIs, generate an executive summary, and log every run for monitoring."

### 1:10 – Run Pipeline (30 sec)
In terminal, run:
```powershell
python -m src.run_pipeline
```
Highlight SUCCESS logs and records processed.

### 1:40 – Dashboard Walkthrough (50 sec)
Open Streamlit and show:
1. Executive Overview — KPI cards and summary
2. Sales Performance — revenue trend
3. Product Performance — top products
4. Workflow Monitoring — successful job history

### 2:30 – Data Quality and AI (20 sec)
"M invalid rows go to a reject table, loads are idempotent, and AI summaries only use validated KPI JSON."

### 2:50 – Close (10 sec)
"This project demonstrates ETL engineering, SQL analytics, automation, dashboarding, and production-minded audit logging."

## Suggested Recording Tools
- OBS Studio
- Loom
- Windows Xbox Game Bar

Save the final video as `docs/demo.mp4` or upload to YouTube/Loom and link it from the README.
