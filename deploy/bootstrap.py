"""Prepare a fresh cloud server before the API starts.  Run:  python -m deploy.bootstrap

1. Waits until the database accepts connections (serverless databases such as Neon
   need a moment to wake up).
2. Trains the ML model if no saved model exists (normally done at build time).
3. Loads the SYNTHETIC demo history if the database is empty (set SEED_DEMO_DATA=false to skip).
It is safe to run on every start: it never overwrites existing data.
"""
import os
import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from backend import config
from backend.database import engine, init_db


def wait_for_database(attempts: int = 8, delay: float = 5.0) -> None:
    for i in range(1, attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection OK")
            return
        except OperationalError as exc:
            print(f"Database not ready (attempt {i}/{attempts}): {str(exc).splitlines()[0]}")
            time.sleep(delay)
    raise SystemExit("Could not connect to the database. Check DATABASE_URL.")


def main() -> None:
    wait_for_database()
    init_db()

    model_file = config.MODEL_DIR / "parking_models.joblib"
    if not model_file.exists():
        from ml.train import train_all
        print("No trained model found - training now (synthetic data)...")
        report = train_all(days=60, seed=42, total_slots=config.TOTAL_SLOTS, model_dir=config.MODEL_DIR)
        print("Trained model", report["model_version"])
    else:
        print("Trained model found:", model_file.name)

    if os.getenv("SEED_DEMO_DATA", "true").lower() == "true":
        from database.seed_database import seed
        seed()  # does nothing if sessions already exist


if __name__ == "__main__":
    main()
