import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://bi_user:bi_pass@localhost:5433/bi_platform",
    )
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: str = os.getenv("SMTP_PORT", "587")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    REPORT_EMAIL_TO: str = os.getenv("REPORT_EMAIL_TO", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "database" / "seed"))
    PROMPT_VERSION: str = "v1"
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


settings = Settings()
