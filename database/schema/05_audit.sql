CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE audit.workflow_runs (
    run_id SERIAL PRIMARY KEY,
    job_name TEXT NOT NULL,
    status TEXT NOT NULL,
    records_processed INT DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    finished_at TIMESTAMP
);

CREATE TABLE audit.ai_summaries (
    summary_id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    kpis_json JSONB NOT NULL,
    summary_text TEXT NOT NULL,
    model_name TEXT,
    prompt_version TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audit.alerts (
    alert_id SERIAL PRIMARY KEY,
    alert_type TEXT NOT NULL,
    alert_message TEXT NOT NULL,
    severity TEXT DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT NOW()
);
