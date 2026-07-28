# Local Setup (No Docker)

For developers who prefer running Python and Node directly on their machine instead of Docker.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ with PostGIS extension
- Node.js 20+ and npm
- `libpango-1.0-0` and related libraries (for WeasyPrint PDF generation)

## Backend Setup

### 1. Create virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> On Ubuntu/Debian, install WeasyPrint system deps first:
> ```bash
> sudo apt-get install -y libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
> ```

### 3. Create database

```bash
sudo -u postgres createdb zimrental
sudo -u postgres psql zimrental -c "CREATE EXTENSION postgis;"
sudo -u postgres psql zimrental -c "CREATE EXTENSION postgis_topology;"
```

Or if you use `psql` directly:
```bash
psql -U postgres -c "CREATE DATABASE zimrental;"
psql -U postgres -d zimrental -c "CREATE EXTENSION postgis;"
```

### 4. Environment variables

```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql+psycopg2://postgres:yourpassword@localhost:5432/zimrental
SECRET_KEY=dev-secret-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
SMS_API_KEY=
SMS_SENDER_ID=ZimRental
```

### 5. Run migrations

```bash
cd backend
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at http://localhost:8000

## Frontend Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Tailwind config (if missing)

Ensure these files exist:

**`tailwind.config.js`**
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
```

**`postcss.config.js`**
```js
export default {
  plugins: { tailwindcss: {}, autoprefixer: {} },
}
```

### 3. Start dev server

```bash
npm run dev
```

Frontend available at http://localhost:5173

> The Vite dev server proxies `/api` to `http://localhost:8000` automatically via `vite.config.js`.

## Seeding Data

```bash
cd backend
python -m seeds.seed_data
```

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Useful Commands

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1

# API logs (if not using --reload)
# Just watch the terminal where uvicorn is running
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'app'`

Ensure you're running commands from the `backend/` directory and that `backend/` itself is on the Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### `psycopg2.OperationalError: could not connect to server`

PostgreSQL is not running or the connection string is wrong. Verify:
```bash
sudo systemctl status postgresql
```

### WeasyPrint crashes with font errors

Install system fonts:
```bash
sudo apt-get install -y fonts-liberation
```
