# Changelog
## 2026-10-21 - Version 1.1.0 (free cloud deployment)
- Free deployment path: Neon + Render + Streamlit Community Cloud (`render.yaml`, `deploy/bootstrap.py`, `docs/FREE_DEPLOYMENT.md`)
- Optional `API_KEY` protection for POST /parking/entry and /parking/exit (`backend/security.py`); dashboard and simulator send the key
- Database URLs from Neon/Render are normalised for SQLAlchemy
- `python -m ml.train` now honours the `MODEL_DIR` setting
- AWS guide updated for the credit-based free plan; 25 tests passing
- Note: `render.yaml` was rewritten from the surrounding files; the Render deployment itself has not been run

## 2026-10-21 - Version 1.1.0 (free cloud deployment)
- Added free-cloud deployment: `render.yaml` (Render blueprint), `deploy/bootstrap.py` (waits for DB, trains if needed, seeds if empty),
  `requirements-api.txt` / `frontend/requirements.txt`, `.streamlit/secrets.toml.example`, `docs/FREE_CLOUD_DEPLOYMENT.md`
- Database URLs from Neon/Render (`postgres://`, `postgresql://`) are accepted; connection pool recycles idle connections
- Optional `API_KEY` protection for POST /parking/entry and /parking/exit (`backend/security.py`); dashboard and simulator send it
- Dashboard reads API URL/key from Streamlit secrets or environment, waits for a sleeping API, and shows clear key errors
- Simulator: `--api-key`, waits for a sleeping cloud API (single quick try for localhost)
- GitHub Actions CI (SQLite + PostgreSQL); tests can target PostgreSQL via `TEST_DATABASE_URL`
- Rewrote AWS guide for AWS's credit-based Free plan (July 2025 change)
- Verified on real PostgreSQL 16: full test suite (25 tests), `schema.sql`, seeding, bootstrap, API, simulator, dashboard
- Fixed: Streamlit theme file was never loaded (must be at `.streamlit/config.toml` in the folder you launch from); moved it

## 2026-09-30 - Version 1.0.0
- Project scaffold, config via `.env`, SQLAlchemy models (SQLite + PostgreSQL capable)
- FastAPI endpoints: health, parking (status, slots, entry, exit, history), analytics (6), prediction (4)
- Synthetic data generator; ML training with model comparison, baseline, chronological split, saved models and metrics
- Parking sensor simulator (configurable interval, probabilities, seed)
- Streamlit dashboard (5 pages)
- 21 pytest tests (all passing on SQLite); dashboard pages run headlessly without exceptions
- Docker files, `database/schema.sql`, AWS guide (documented, untested)
- Documentation: README, PROJECT_REPORT, DEMO_GUIDE, VIVA_QUESTIONS
- Fixed: timestamp nanosecond warning in seeding (rounded to seconds); switched dashboard to `width="stretch"`
