# Zim Rental Manager (Geospatial Backend)

Low-tech property management for Zimbabwe. FastAPI + PostGIS + GeoPandas.

## Quick Start

```bash
cp .env.example .env
# Edit .env with your secrets
make run
```

## First Migration

```bash
make migrate m="init"
```

## Daily Operations

- **Send rent reminders:** `docker-compose exec api python scripts/send_rent_reminders.py`
- **Monthly report:** `docker-compose exec api python scripts/generate_monthly_report.py --year 2026 --month 7`

## API Docs

Once running: http://localhost:8000/docs

## Geospatial

- `GET /api/v1/properties/geo/nearby?lat=-17.8252&lon=31.0335&radius_km=5`
- `GET /api/v1/properties/geo/all`
- `GET /api/v1/reports/properties/geojson` (GeoPandas export)

## Tech Stack

- FastAPI
- PostgreSQL 15 + PostGIS
- GeoAlchemy2 / Shapely / GeoPandas
- WeasyPrint (PDF receipts)
- OpenPyXL (Excel reports)
