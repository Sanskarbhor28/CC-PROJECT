"""Central configuration. All settings come from environment variables / .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _abs(path_str: str) -> Path:
    """Make relative paths relative to the project root."""
    p = Path(path_str)
    return p if p.is_absolute() else ROOT / p


def normalize_db_url(url: str) -> str:
    """Make a database URL usable by SQLAlchemy.
    * Cloud providers (Neon, Render, Heroku...) give 'postgres://' or 'postgresql://' URLs;
      SQLAlchemy needs the driver name, so we turn them into 'postgresql+psycopg2://'.
    * Relative SQLite paths become absolute (relative to the project folder)."""
    url = url.strip()
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg2://" + url[len(prefix):]
    if url.startswith("sqlite:///./"):
        return "sqlite:///" + str(_abs(url.replace("sqlite:///./", "")))
    return url


def _db_url() -> str:
    return normalize_db_url(os.getenv("DATABASE_URL", "sqlite:///./data/smart_parking.db"))


DATABASE_URL: str = _db_url()
TOTAL_SLOTS: int = int(os.getenv("TOTAL_SLOTS", "30"))
MODEL_DIR: Path = _abs(os.getenv("MODEL_DIR", "ml/models"))
DATA_DIR: Path = ROOT / "data"
API_URL: str = os.getenv("API_URL", "http://localhost:8000")
# Optional shared secret. If set, POST /parking/entry and /parking/exit require header "X-API-Key".
API_KEY: str = os.getenv("API_KEY", "")

ZONES = 3  # slots are split evenly into zones A, B, C


def slot_layout(total: int = TOTAL_SLOTS) -> list[tuple[str, str]]:
    """Return [(slot_number, zone), ...]  e.g. ('P01', 'A').
    NOTE: ml/data_generator.py uses the same formula so synthetic data matches."""
    return [(f"P{i + 1:02d}", "ABC"[min(i * ZONES // total, ZONES - 1)]) for i in range(total)]
