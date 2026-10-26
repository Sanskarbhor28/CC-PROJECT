"""Test setup: use a throw-away database and a small model, so tests never touch real data."""
import os
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp(prefix="parking_tests_"))
# Tests DROP ALL TABLES in the database they use. By default that is a throw-away SQLite file.
# To run the suite against PostgreSQL, set TEST_DATABASE_URL to an EMPTY test database (never your real one).
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL") or f"sqlite:///{_tmp / 'test.db'}"
os.environ["API_KEY"] = ""               # tests start with the key disabled
os.environ["TOTAL_SLOTS"] = "5"          # small lot so 'lot full' is easy to test
os.environ["MODEL_DIR"] = str(_tmp / "models")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from ml.train import train_all  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def small_model():
    """Train a quick model on 21 days of synthetic data."""
    train_all(days=21, seed=1, total_slots=30, model_dir=Path(os.environ["MODEL_DIR"]))


@pytest.fixture()
def client():
    from backend.database import Base, engine
    from backend.main import app

    Base.metadata.drop_all(bind=engine)  # fresh tables for every test
    with TestClient(app) as c:           # startup event recreates tables + slots
        yield c
