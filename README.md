# Zim Rental Manager (Geospatial Backend)

Low-tech property management for Zimbabwe. FastAPI + PostGIS + GeoPandas.

## First-Time Setup

```bash
# 1. Environment
cp .env.example .env
# Edit .env with your secrets (at minimum: SECRET_KEY, DB_PASSWORD)

# 2. Create runtime directories (avoids permission issues)
mkdir -p backend/app/static/receipts backend/app/static/reports backend/app/static/uploads

# 3. PostGIS init script
mkdir -p docker/postgres
cat > docker/postgres/init-postgis.sql << 'EOF'
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
EOF
```

## Development (recommended)

Hot-reload on both frontend and backend.

```bash
docker-compose -f docker-compose.dev.yml up --build
```

- **Frontend (Vite HMR):** http://localhost:5173
- **API docs:** http://localhost:8000/docs
- **Database:** localhost:5432

### First Migration

```bash
docker-compose -f docker-compose.dev.yml exec api alembic revision --autogenerate -m "init"
docker-compose -f docker-compose.dev.yml exec api alembic upgrade head
```

## Production

Multi-stage builds with Nginx for the frontend.

```bash
docker-compose up --build
```

- **Frontend:** http://localhost
- **API docs:** http://localhost:8000/docs

### First Migration

```bash
docker-compose exec api alembic upgrade head
```

## Daily Operations

```bash
# Send rent reminders
docker-compose exec api python scripts/send_rent_reminders.py

# Monthly report
docker-compose exec api python scripts/generate_monthly_report.py --year 2026 --month 7
```

## Geospatial Endpoints

- `GET /api/v1/properties/geo/nearby?lat=-17.8252&lon=31.0335&radius_km=5`
- `GET /api/v1/properties/geo/all`
- `GET /api/v1/reports/properties/geojson` (GeoPandas export)

## Tech Stack

- FastAPI
- PostgreSQL 15 + PostGIS
- GeoAlchemy2 / Shapely / GeoPandas
- WeasyPrint (PDF receipts)
- OpenPyXL (Excel reports)
- React 18 + Vite + TailwindCSS + Leaflet
