# AWS deployment guide (simplest sensible design)

> **Status: instructions only.** This has NOT been executed on AWS by the author of the code (the application itself was tested with PostgreSQL locally).
> Follow it step by step and check current AWS prices and Free Tier terms in your own account before creating anything.

## Design
```
Internet -> EC2 (one small Linux server: FastAPI :8000 + Streamlit :8501) -> RDS PostgreSQL (private)
```
| Service | Why |
|---|---|
| **EC2** (the smallest instance type your account plan allows) | runs backend + dashboard on one machine |
| **RDS PostgreSQL** (smallest instance, single-AZ, small storage) | the cloud database |
| **Security groups** | firewall: only your IP can reach the server; only the server can reach the database |
| **CloudWatch** (optional) | basic CPU graphs are automatic; keep custom logs minimal to avoid cost |
| S3 (optional) | back up `ml/models/*.joblib`. Not required |
Deliberately NOT used: Lambda, IoT Core, load balancers, NAT gateways, Elastic Beanstalk (extra cost/complexity). IoT Core is future scope.

## Costs - read first (AWS changed its free tier in July 2025)
- **New accounts** (created after 15 July 2025) choose a **Free plan** or a **Paid plan**. Both start with about $100 of credits (up to $200 by completing onboarding activities).
- **Free plan:** lasts up to 6 months or until credits run out, whichever comes first. Usage is charged to credits, not your card, but **the account is then closed automatically
  unless you upgrade**, and you lose its resources and data. Some services (possibly including parts of RDS) may not be available on the Free plan; check the eligible-services list.
- **Paid plan:** you get the credits too, but anything beyond them is billed to your card. Delete resources after the demo.
- Credits expire 12 months after the account is created. Accounts created before 15 July 2025 stay on the old 12-month Free Tier rules.
- EC2 and RDS accrue charges per hour while running. A public IPv4 address, NAT gateways and load balancers can add monthly charges.
- Set a **Billing budget alert** before starting. Confirm all of this on the current AWS Free Tier page; terms change.
- If you want no credit card and no expiry, use `docs/FREE_CLOUD_DEPLOYMENT.md` instead.

## Steps
1. **Region + budget:** pick one region (e.g. Asia Pacific (Mumbai)) and create a budget alert.
2. **Security groups:**
   - `sg-web`: inbound 22 (SSH) from *My IP*, 8000 and 8501 from *My IP* (or your college IP range). Never `0.0.0.0/0` for SSH.
   - `sg-db`: inbound 5432 **only from `sg-web`**.
3. **RDS:** Create database -> PostgreSQL -> the cheapest / dev template your plan allows -> initial db name `smart_parking`, user `parking_user`,
   a strong password (store it in a password manager), **Public access: No**, attach `sg-db`, disable extra features (Performance Insights, etc.).
4. **EC2:** Launch Ubuntu 24.04 LTS, attach `sg-web`, create a key pair (keep the `.pem` private).
5. **On the server** (SSH in):
   ```bash
   sudo apt update && sudo apt install -y python3-venv git
   # upload the project (git clone your repo, or scp the ZIP) then:
   cd smart-parking && python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env && nano .env      # set DATABASE_URL to the RDS endpoint, API_URL=http://localhost:8000, API_KEY=a-long-random-string
   python -m ml.train
   python -m database.seed_database --reset     # loads SYNTHETIC demo history
   ```
   `.env` example: `DATABASE_URL=postgresql+psycopg2://parking_user:YOUR_PASSWORD@YOUR-RDS-ENDPOINT:5432/smart_parking`
6. **Run as services** (so they survive logout) - simplest for a demo: `tmux`, or create two `systemd` units running
   `uvicorn backend.main:app --host 0.0.0.0 --port 8000` and `streamlit run frontend/app.py --server.address 0.0.0.0 --server.port 8501`.
7. **Open** `http://EC2-PUBLIC-IP:8501` (dashboard) and `:8000/docs` (API). Run the simulator with `--api http://localhost:8000` on the server,
   or from your laptop with `--api http://EC2-PUBLIC-IP:8000` to show "sensor -> cloud".
8. **Security notes:** plain HTTP is fine for a short demo only. The API has no login. Do not leave it open to the internet
   long-term; add HTTPS (a domain + reverse proxy) and authentication before any real use.
9. **Monitor:** EC2 -> Monitoring tab (CPU), RDS -> Monitoring tab (connections, storage).
10. **Clean up after the demo:** terminate the EC2 instance, delete the RDS instance (skip final snapshot if you don't need it),
    release any Elastic IP, delete unused security groups, and check the Billing dashboard the next day.

## Troubleshooting
- Timeout connecting to RDS: `sg-db` must allow 5432 from `sg-web`, and both must be in the same VPC.
- `password authentication failed`: check special characters in the password (URL-encode `@`, `:` and `/`).
- Dashboard cannot reach API: `API_URL` must be reachable from the *dashboard process*.
