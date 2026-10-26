Project: Cloud-Based Smart Parking Management and AI Prediction System
Current Phase: v1.1.0 - all build phases complete, free-cloud deployment files added
Status: Working locally on SQLite and on real PostgreSQL 16. Tested here.
Completed: Backend API, database, simulator, synthetic data, ML training + evaluation, Streamlit dashboard (5 pages), API-key protection,
           25 pytest tests (SQLite + PostgreSQL), Render blueprint, bootstrap script, GitHub Actions CI, Docker files, SQL schema,
           README, PROJECT_REPORT, DEMO_GUIDE, VIVA_QUESTIONS, FREE_CLOUD_DEPLOYMENT, AWS guide
In Progress: -
Next (student): push to GitHub; follow docs/FREE_CLOUD_DEPLOYMENT.md (Neon -> Render -> Streamlit Cloud); take screenshots into docs/screenshots/;
                then update PROJECT_REPORT section 13 with what you really deployed
Known Issues / NOT verified:
  - Free deployment (Neon/Render/Streamlit Cloud) written and the start-up sequence tested locally, but NOT deployed
  - Neon, Render, Streamlit Community Cloud, AWS: not used by the author of the code (need your accounts). render.yaml and the guide are untested on the platforms
  - Docker / docker-compose: not run (no Docker in the build environment)
  - Not run on Windows 11 (built on Linux, Python 3.12); dashboard not viewed in a real browser
  - Data is synthetic; ML metrics apply to synthetic data only and vary slightly between training runs
  - API key is a shared secret, not user authentication; no HTTPS handling in the app itself
  - Free tiers sleep when idle and change over time
Environment: Python 3.11+ (tested on 3.12), venv, requirements.txt
Database: SQLite default; PostgreSQL via DATABASE_URL (tested on local PostgreSQL 16)
Cloud: Free stack designed (Neon + Render + Streamlit Cloud); AWS alternative documented. Not deployed.
AI Model: Random Forest selected for +30/+60 min occupancy and demand (ml/models/metrics.json after training)
Frontend: Streamlit, frontend/app.py
Backend: FastAPI, backend/main.py
Deployment: Not deployed
Last Updated: 2026-10-21
