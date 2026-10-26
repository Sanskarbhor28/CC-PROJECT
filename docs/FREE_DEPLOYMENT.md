# Free cloud deployment: Neon (database) + Render (API) + Streamlit Community Cloud (dashboard)

> **Status: code is tested locally, the cloud steps are NOT.** I ran the exact start-up sequence (`train` -> `deploy.bootstrap` -> `uvicorn`) against a fresh
> local database, with the API key on, the simulator and all five dashboard pages. I did **not** deploy to Neon, Render or Streamlit Cloud,
> so expect to fix small things. Free-tier limits change often: check each provider's pricing page first.

```
Simulator / browser --> Dashboard (Streamlit Cloud) --HTTPS + X-API-Key--> API (Render) --> PostgreSQL (Neon)
```

## What the project already contains for this
| File | Job |
|---|---|
| `render.yaml` | Render blueprint: build = install + train model; start = bootstrap + uvicorn; `API_KEY` auto-generated |
| `deploy/bootstrap.py` | Waits for the database to wake, creates tables, trains the model if missing, loads **synthetic** demo data if the DB is empty |
| `requirements-api.txt` | Smaller dependency list for the API build |
| `frontend/requirements.txt` | Small dependency list for the dashboard on Streamlit Cloud |
| `backend/security.py` | If `API_KEY` is set, entry/exit POSTs require header `X-API-Key` (reading stays open) |
| `backend/config.py` | Turns Neon's `postgres://` / `postgresql://` URLs into the form SQLAlchemy needs |
| `.streamlit/secrets.toml.example` | The two secrets the dashboard needs |

## Steps
1. **GitHub:** push the project to a GitHub repo (`.env`, `*.db`, models and CSVs are git-ignored). Streamlit Community Cloud requires GitHub.
2. **Neon:** create a free project and copy the connection string (it should include `sslmode=require`).
3. **Render:** New -> Blueprint -> pick the repo. When asked, paste the Neon string as `DATABASE_URL`. Render generates `API_KEY`. After the first deploy open
   `https://<your-service>.onrender.com/health` and `/docs`. The first start trains the model and loads the demo data, so allow a few minutes.
4. **Streamlit Community Cloud:** New app -> repo -> main file `frontend/app.py`. Under Advanced settings -> Secrets paste:
   ```toml
   API_URL = "https://<your-service>.onrender.com"
   API_KEY = "<the API_KEY value from Render's Environment tab>"
   ```
5. **Simulator from your laptop (the "sensor -> cloud" demo):**
   ```bat
   python -m simulator.parking_simulator --api https://<your-service>.onrender.com --api-key <API_KEY> --interval 2
   ```

## Known limits of the free setup
- Render free services sleep after inactivity; the first request can take about a minute. Open `/health` a few minutes before your demo.
- Neon's free compute pauses when idle and wakes on the next query (bootstrap waits for this). Storage is small.
- Streamlit Community Cloud apps hibernate after a period without visitors and need a click to wake.
- Render's free disk is not persistent, so the model is retrained at each build. The database lives in Neon, so history is kept.
- Plain `API_KEY` protection is basic: no per-user login, and the key is visible to anyone with access to your Streamlit secrets.
- Have a backup: a screen recording, or `docker compose up --build` on your laptop.

## Troubleshooting
| Symptom | Likely cause |
|---|---|
| Dashboard: "Cannot reach the API" | Render service asleep (wait ~1 min and refresh) or wrong `API_URL` secret |
| Entry/exit from dashboard says 401 | `API_KEY` secret differs from Render's value |
| Render deploy fails at build | Check logs; build runs `python -m ml.train`, which needs the packages in `requirements-api.txt` |
| `could not connect to server` | `DATABASE_URL` missing/typo; Neon string must keep `?sslmode=require` |
