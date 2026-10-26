# Free cloud deployment: Neon + Render + Streamlit Community Cloud

```
Simulator (your laptop or anywhere) --HTTPS + API key--> Render (FastAPI)  --> Neon (PostgreSQL)
                                                              ^
Streamlit Community Cloud (dashboard) ----HTTPS + API key-----+
```
| Part | Service | Why |
|---|---|---|
| Database | **Neon** (free PostgreSQL) | real cloud PostgreSQL, no card needed to start (check at signup) |
| API + ML model | **Render** free web service | deploys straight from GitHub using `render.yaml` |
| Dashboard | **Streamlit Community Cloud** | made for Streamlit apps, deploys from GitHub |

> **Status:** the code paths were tested against a real local PostgreSQL 16 (tests, bootstrap, seeding, API key, dashboard secrets).
> The three platforms themselves (Neon, Render, Streamlit Cloud) were **not** used, because they need your accounts. If a step below
> differs from what you see, trust the platform's current screen and tell me what changed.

## Free-tier facts (checked 21 Oct 2026 from public summaries, so verify on each pricing page)
- **Render free web service:** sleeps after about 15 minutes without traffic; waking takes about a minute; there is a monthly free-hours allowance. Free bandwidth limits are reported differently by different sources, so check Render's page.
- **Neon free:** about 0.5 GB storage per project; compute sleeps after 5 minutes idle and wakes on the next query.
- **Streamlit Community Cloud:** free, needs a GitHub account; the app sleeps after about 12 hours without visitors; about 1 GB memory (sources differ); one private app.
- Free tiers change. Do not rely on them for anything important, and never put real personal data in a demo.

## Step 0 - Put the project on GitHub
```bat
cd smart-parking
git init
git add .
git commit -m "Smart parking project"
```
Create an empty repository on github.com (public is simplest), then run the two commands GitHub shows (`git remote add origin ...`, `git push -u origin main`).
Check that `.env` and `*.db` are **not** in the repository (they are in `.gitignore`).

## Step 1 - Neon database
1. Sign up at neon.tech, create a project (region closest to you), database name `smart_parking`.
2. Click **Connect** and copy the connection string. It looks like `postgresql://USER:PASSWORD@HOST/smart_parking?sslmode=require`.
3. Keep it secret. You paste it only into Render's environment settings, never into code or GitHub.
The app accepts this URL as-is (it converts `postgresql://` to the driver form automatically).

## Step 2 - Render API
1. Sign up at render.com with GitHub. **New -> Blueprint**, choose your repository. Render reads `render.yaml`.
2. When asked for `DATABASE_URL`, paste the Neon string. `API_KEY` is generated automatically.
3. Deploy. **Build** installs `requirements-api.txt` and trains the ML model. **Start** runs `python -m deploy.bootstrap`, which waits for the database, loads the
   SYNTHETIC demo history the first time (set `SEED_DEMO_DATA=false` to skip), then starts the API.
4. Open `https://YOUR-SERVICE.onrender.com/health` (the first call may take about a minute) and `/docs`.
5. In the Render dashboard open **Environment** and copy the generated `API_KEY`.
`TZ=Asia/Kolkata` is set so "hour of day" means Indian time. `PYTHON_VERSION` is pinned to 3.12.3; if Render rejects it, choose a version Render lists.

## Step 3 - Streamlit Community Cloud dashboard
1. Sign in at share.streamlit.io with GitHub. **Create app** -> your repository, branch `main`, **main file path `frontend/app.py`**.
2. **Advanced settings -> Secrets**, paste (see `.streamlit/secrets.toml.example`):
   ```toml
   API_URL = "https://YOUR-SERVICE.onrender.com"
   API_KEY = "the key copied from Render"
   ```
3. Deploy. The dashboard installs `frontend/requirements.txt` (small). On first open it waits for the API to wake up and shows a message.

## Step 4 - Send live data from the simulator
```bat
python -m simulator.parking_simulator --api https://YOUR-SERVICE.onrender.com --api-key YOUR_KEY --interval 2 --arrival-prob 0.6 --departure-prob 0.08
```
(or set `API_URL` and `API_KEY` in your `.env`). Keep the dashboard's **Auto-refresh** on to watch slots change from another device.

## Before a demo / viva
- Open the API `/health` URL and the dashboard 5 minutes earlier, so both are awake.
- Keep a local backup (`docker compose up --build`, or the normal local run) and a short screen recording.
- Say which parts are real cloud services and that the data is synthetic.

## Security notes
- `POST /parking/entry` and `/parking/exit` require the `X-API-Key` header when `API_KEY` is set. Reads (GET) are open, which is acceptable only because the demo data is synthetic.
- This is a shared secret, not user login. For real use add proper authentication and HTTPS-only access controls.
- Rotate the key (change it in Render and in Streamlit secrets) if it leaks. Never commit it.

## Troubleshooting
| Problem | Fix |
|---|---|
| Dashboard: "Cannot reach the API" | Open `/health` on the Render URL, wait ~1 min, reload the dashboard. Check `API_URL` in secrets (no trailing path). |
| Entry form says "Invalid or missing API key" | `API_KEY` in Streamlit secrets must equal Render's `API_KEY`. |
| Render deploy fails at build | Open the build log; most often the Python version or a typo in `render.yaml`. |
| API logs "Could not connect to the database" | Re-copy the Neon string; it must include `?sslmode=require`; make sure the Neon project is not suspended. |
| `/prediction/*` returns 503 | The build step did not finish training. Redeploy, or run `python -m ml.train` in a Render shell if available. |
| Dashboard has no history | `SEED_DEMO_DATA` is `false`, or seeding failed; see the start log. Run `python -m database.seed_database` with `DATABASE_URL` set. |
| Neon storage limit | Demo data is a few MB; the `predictions` table grows slowly. |

## Alternatives if you prefer something else
- **Docker anywhere:** `docker compose up --build` (PostgreSQL + API + dashboard). Works on any machine or VM with Docker.
- **Google Cloud Run:** can run the `Dockerfile` with a free monthly allowance, but it needs a payment method; not tested here.
- **Supabase** as the database instead of Neon: also PostgreSQL; free projects pause after a week of inactivity.
- **AWS:** see `docs/AWS_DEPLOYMENT.md` (credit-based plan, time-limited).
