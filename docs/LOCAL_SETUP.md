# Local Setup (No Docker)

Requirements: Python 3.11, PostgreSQL 15+ with PostGIS

1. Create virtual env: `python -m venv venv && source venv/bin/activate`
2. Install: `pip install -r backend/requirements.txt`
3. Create DB: `createdb zimrental`
4. Enable PostGIS: `psql zimrental -c "CREATE EXTENSION postgis;"`
5. Copy `.env.example` to `.env` and set `DATABASE_URL`
6. Run migrations: `cd backend && alembic upgrade head`
7. Start: `cd backend && uvicorn app.main:app --reload`
