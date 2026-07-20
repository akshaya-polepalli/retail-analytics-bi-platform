import pytest
from sqlalchemy import text

from src.database.connection import engine


@pytest.fixture(scope="session")
def db_available():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest.fixture
def requires_db(db_available):
    if not db_available:
        pytest.skip("PostgreSQL is not available")
