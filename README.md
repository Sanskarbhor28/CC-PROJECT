# Cloud-Based Smart Parking Management and AI Prediction System

A college mini-project: **parking events → cloud API → database → AI/ML → web dashboard**.

> **Data note:** Synthetic data is used for development and demonstration. No physical sensors are needed:
> a Python simulator plays the role of IoT sensors. Camera-based vehicle detection and real IoT hardware are future scope.

## Features
- Total / available / occupied slots, occupancy %, per-slot live view (zones A, B, C)
- Vehicle entry (auto slot assignment), exit (duration calculated), full history with filters
- Analytics: occupancy trend, daily and weekly patterns, peak / least-busy hours, entries vs exits, average duration
- AI: occupancy prediction (30 and 60 min ahead) and demand level (Low / Medium / High), with real evaluation metrics
- REST API with Swagger docs, input validation and clear error codes
- Sensor simulator with configurable speed, arrival / departure probability, and a seed
- Optional API-key protection for write endpoints, ready-made free-cloud deployment files (Render + Neon + Streamlit Cloud)
- 25 automated tests (run on SQLite and PostgreSQL)

## Architecture
```
Simulator (IoT stand-in) --HTTP--> FastAPI --> Database (SQLite locally / PostgreSQL on AWS RDS)
                                      |  loads saved model (joblib)
                                      v
                           Streamlit dashboard (talks only to the API)
```
| Folder | Purpose |
|---|---|
| `backend/` | FastAPI app: routes, business rules (`crud.py`), analytics, SQLAlchemy models |
| `ml/` | data generator, shared features, training (`train.py`), prediction, evaluation |
| `simulator/` | `parking_simulator.py` |
| `frontend/` | Streamlit dashboard |
| `database/` | `schema.sql`, `seed_database.py` (loads synthetic history) |
| `tests/` | pytest suite |
| `docs/` | free-cloud guide, AWS guide, ER diagram |
| `deploy/`, `render.yaml` | cloud start-up script and Render blueprint |

## Quick start (Windows 11, Command Prompt)
```bat
cd smart-parking
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

:: 1) Train the model (once) - prints nothing much, saves ml\models\
python -m ml.train
python -m ml.evaluate

:: 2) Create the database and load SYNTHETIC history
python -m database.seed_database --reset

:: 3) Start the API (keep this window open)  -> http://localhost:8000/docs
uvicorn backend.main:app --reload
```
Open **new** Command Prompt windows (run `venv\Scripts\activate` in each):
```bat
:: 4) Dashboard -> http://localhost:8501
streamlit run frontend/app.py

:: 5) Simulator (live sensor events)
python -m simulator.parking_simulator --interval 1 --arrival-prob 0.6 --departure-prob 0.08 --seed 1
```
The default database is SQLite (`data/smart_parking.db`), so nothing else needs installing and no AWS account is needed.

## Configuration (`.env`)
| Variable | Meaning |
|---|---|
| `DATABASE_URL` | `sqlite:///./data/smart_parking.db` (default) or `postgresql+psycopg2://user:pass@host:5432/db` |
| `TOTAL_SLOTS` | number of slots (default 30). If you change it, retrain: `python -m ml.train --slots N` and reseed |
| `MODEL_DIR` | where trained models are stored |
| `API_URL` | used by dashboard and simulator (default `http://localhost:8000`) |
| `API_KEY` | optional. If set on the API, entry/exit requests must send header `X-API-Key`. Dashboard and simulator read the same variable |
| `SEED_DEMO_DATA` | cloud start-up only: `true` (default) loads synthetic history into an empty database |
| `TZ` | server time zone, e.g. `Asia/Kolkata` (cloud servers default to UTC) |

Never commit `.env`. Passwords are never written in source code.

## PostgreSQL
Set `DATABASE_URL` to a PostgreSQL URL and restart. Tables are created automatically at startup
(`database/schema.sql` is the same design in plain SQL). `postgres://` and `postgresql://` URLs from cloud providers are accepted as they are. Or run everything with Docker:
```bat
docker compose up --build
```
> **Tested:** the application code, the SQL schema, seeding, API, simulator and the full test suite were run against a real local PostgreSQL 16.
> **Not tested:** `docker-compose.yml` / `Dockerfile` (no Docker in the build environment) and the cloud platforms themselves.

## API
Swagger UI: `http://localhost:8000/docs`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | API + database check |
| GET | `/parking/status` | totals and occupancy % |
| GET | `/parking/slots` | every slot with vehicle |
| POST | `/parking/entry` | `{"vehicle_number":"MH12AB1234","vehicle_type":"car"}` -> 201, 409 if full/duplicate |
| POST | `/parking/exit` | `{"vehicle_number":"MH12AB1234"}` -> 200, 404 if not parked |
| GET | `/parking/history` | filters: `vehicle, slot, date_from, date_to, min_duration, max_duration, status, limit, offset` |
| GET | `/analytics/summary`, `/peak-hours`, `/occupancy-trend`, `/daily`, `/weekly`, `/entries-exits` | analytics |
| GET | `/prediction/occupancy`, `/prediction/demand`, `/prediction/model-info`, `/prediction/history` | AI |

## Machine learning
- **Data:** synthetic sessions (weekday rush hours, weekend midday peak, short and long stays), aggregated into 30-minute steps.
- **Features:** hour of day, day of week, weekend flag, current occupancy %, occupancy 30 min ago, change, arrivals and departures in last 30 min.
- **Targets:** occupancy in 30 min and 60 min (regression); demand level from occupancy in 60 min (Low <40%, Medium 40-70%, High >=70%).
- **Models compared:** Linear Regression vs Random Forest (regression); Logistic Regression vs Random Forest (classification), plus a
  "nothing changes" baseline. Chronological 70/15/15 split: the validation set picks the model, the test set reports the result.
- Models are trained once (`python -m ml.train`) and only *loaded* by the API.
- See `PROJECT_REPORT.md` section 11 for the actual results. Run `python -m ml.evaluate` for yours.
- Because data is regenerated on each training run, numbers vary slightly between runs.

## Testing
```bat
python -m pytest -q
```
Uses a temporary SQLite database and a small model, so real data is untouched.
To run against PostgreSQL, create an EMPTY test database and set `TEST_DATABASE_URL` first (the tests drop all tables in it):
```bat
set TEST_DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/parking_test
python -m pytest -q
```
GitHub Actions (`.github/workflows/ci.yml`) runs both variants on every push once the project is on GitHub.

## Cloud deployment
| Option | Guide | Cost |
|---|---|---|
| **Free: Neon + Render + Streamlit Community Cloud** (recommended) | `docs/FREE_CLOUD_DEPLOYMENT.md` | free tiers, with sleep/wake-up delays |
| Docker Compose (any machine) | `docker-compose.yml` | free on your own computer |
| AWS EC2 + RDS | `docs/AWS_DEPLOYMENT.md` | uses AWS credits; the Free plan closes after 6 months |

Deployment files: `render.yaml`, `deploy/bootstrap.py`, `requirements-api.txt`, `frontend/requirements.txt`, `.streamlit/secrets.toml.example`.
**Nobody has deployed this to Render, Neon, Streamlit Cloud or AWS yet.** The guides are instructions; the code paths they rely on were tested locally. Say "deployed" only after you have done it.

## Troubleshooting
| Problem | Fix |
|---|---|
| Dashboard says "Cannot reach the API" | Local: start `uvicorn backend.main:app --reload`. Cloud: open the API `/health` URL, wait a minute, reload |
| "Invalid or missing API key" | `API_KEY` must match on the API, the dashboard (secrets/env) and the simulator (`--api-key`) |
| `/prediction/*` returns 503 | Run `python -m ml.train` |
| Everything empty / no history | Run `python -m database.seed_database --reset` |
| `ModuleNotFoundError: backend` | Run commands from the `smart-parking` folder, with `python -m ...` |
| Port already in use | Add `--port 8001` to uvicorn (and set `API_URL` in `.env`) |
| Predictions look odd after simulator runs | The model was trained on synthetic patterns; it is a demo, not a production forecaster |

## Future improvements
Real IoT sensors (AWS IoT Core / MQTT), camera-based plate detection, user login, payments, retraining on real data, time-series models.
