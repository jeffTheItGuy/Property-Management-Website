# Development Setup

This guide covers the Docker-based development environment with hot reload for both frontend and backend.

## Prerequisites

- Docker Engine 24.0+
- Docker Compose (plugin version)
- `make` (optional, for shortcuts)

## First-Time Setup

### 1. Environment File

```bash
cp .env.example .env
```

Minimum required variables:

```env
SECRET_KEY=your-super-secret-key-change-me
DB_PASSWORD=zimrental123
DATABASE_URL=postgresql+psycopg2://zimrental:zimrental123@db:5432/zimrental
SMS_API_KEY=your_sms_api_key
SMS_SENDER_ID=ZimRental
```

> In development, if `SMS_API_KEY` is unset or set to the placeholder, SMS messages are printed to stdout instead of sent.

### 2. Runtime Directories

```bash
mkdir -p backend/app/static/receipts backend/app/static/reports backend/app/static/uploads
```

These are mounted as Docker volumes so generated files persist across container restarts.

### 3. PostGIS Init Script

```bash
mkdir -p db
cat > db/init-postgis.sql << 'EOF'
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
EOF
```

## Running the Stack

```bash
docker compose -f docker-compose.dev.yml up --build
```

This starts three services:

| Service | Container Name | Port | Notes |
|---------|---------------|------|-------|
| PostgreSQL + PostGIS | `zim-rental-db-dev` | 5432 | Data persists in `postgres_data_dev` volume |
| FastAPI (uvicorn) | `zim-rental-api-dev` | 8000 | `--reload` enabled; code changes reflect immediately |
| React (Vite) | `zim-rental-frontend-dev` | 5173 | HMR enabled; `node_modules` is an anonymous volume |

### Service URLs

- **Frontend:** http://localhost:5173
- **API Base:** http://localhost:8000/api/v1
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Database Migrations

```bash
# Generate a new migration
docker compose -f docker-compose.dev.yml exec api alembic revision --autogenerate -m "add new table"

# Apply all pending migrations
docker compose -f docker-compose.dev.yml exec api alembic upgrade head

# Rollback one revision
docker compose -f docker-compose.dev.yml exec api alembic downgrade -1
```

## Seeding Data

```bash
docker compose -f docker-compose.dev.yml exec api python -m seeds.seed_data
```

This creates:
- 1 manager account (`0772123456` / `password123`)
- 3 landlords, 5 properties with GPS coordinates, 10 units
- 5 tenants, 5 active leases, 30 payment schedules
- Sample maintenance requests and expenses

Safe to run multiple times — it checks for existing records before inserting.

## Tailwind / CSS Not Loading?

If the frontend renders unstyled HTML, you are missing Tailwind config files. Create them in `frontend/`:

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

Then restart the frontend container:
```bash
docker compose -f docker-compose.dev.yml restart frontend
```

## Common Commands

```bash
# View API logs
docker compose -f docker-compose.dev.yml logs -f api

# Restart a single service
docker compose -f docker-compose.dev.yml restart api

# Open a shell in the API container
docker compose -f docker-compose.dev.yml exec api bash

# Run tests
docker compose -f docker-compose.dev.yml exec api pytest tests/ -v

# Stop everything
docker compose -f docker-compose.dev.yml down

# Wipe database and start fresh
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up --build
```

## Troubleshooting

### `command not found: docker-compose`

Use the modern plugin syntax:
```bash
docker compose -f docker-compose.dev.yml up --build
```

### Port already in use

Change the mapped ports in `.env`:
```env
DB_PORT=5433
API_PORT=8001
FRONTEND_PORT=5174
```

### Database connection errors on first start

The API container waits for the DB healthcheck, but if migrations fail on a brand-new database, ensure `db/init-postgis.sql` exists and the DB volume was created successfully.

### File upload / receipt generation fails

Ensure the runtime directories exist on the **host** before starting containers:
```bash
mkdir -p backend/app/static/{uploads,receipts,reports}
```
