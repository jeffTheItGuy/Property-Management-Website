# Zim Rental Manager

> Low-tech, high-performance property management built for Zimbabwe.

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostGIS](https://img.shields.io/badge/PostGIS-336791?logo=postgresql)](https://postgis.net)
[![React](https://img.shields.io/badge/React-61DAFB?logo=react)](https://react.dev)

---

## What is this?

**Zim Rental Manager** is a full-stack property management system designed specifically for the Zimbabwean rental market. It handles multi-currency rent collection (USD / ZiG), geospatial property tracking, automated SMS reminders, PDF receipt generation, and maintenance workflows — all through a clean, responsive web interface.

### Why it exists

Most property management tools are built for Western markets and don't account for:
- **Mobile money payments** (EcoCash, Zipit, OneMoney, Innbucks)
- **Dual-currency environments** (USD + ZiG)
- **Informal communication channels** (SMS over email)
- **Geographic dispersion** of properties across cities like Harare, Bulawayo, and Mutare

This system bridges that gap with a low-tech backend that runs reliably on modest infrastructure and a frontend that works on everything from desktops to entry-level smartphones.

---

## Features

| Module | Capabilities |
|--------|-------------|
| **Properties** | GPS-tagged listings, PostGIS-powered nearby search, GeoJSON export |
| **Units** | Bedsitters to 4-bed houses, offices, shops, warehouses |
| **Leases** | Active / Draft / Ended / Breached status with auto unit occupancy updates |
| **Payments** | Multi-method recording (Cash, Bank, EcoCash, Zipit, OneMoney, Innbucks), auto PDF receipts via WeasyPrint |
| **Schedules** | Auto-generated rent schedules with overdue detection |
| **Maintenance** | Photo uploads, priority triage (Low → Emergency), status workflow |
| **Communications** | Bulk & individual SMS via Africa's Talking (or mock in dev) |
| **Reports** | Monthly Excel income/expense reports, payment ledgers, GeoJSON exports |
| **Auth** | JWT-based login, manager-scoped access |

### Optimizations

- **Geospatial indexing** — PostGIS `ST_DWithin` with geography casts for accurate km-radius searches
- **Lazy receipt generation** — PDFs are generated on first download, then cached on disk
- **Idempotent seeding** — Run the seed script multiple times without creating duplicates
- **Hot reload dev environment** — Vite HMR frontend + uvicorn `--reload` backend
- **Multi-stage Docker builds** — Nginx-served static frontend in production, minimal image size
- **Alembic migrations** — Database versioning with autogenerate support

---

## Tech Stack

**Backend**
- Python 3.11 + FastAPI
- SQLAlchemy 2.0 + GeoAlchemy2 (PostGIS bindings)
- Pydantic v2 for validation
- WeasyPrint (PDF receipts)
- OpenPyXL + Pandas (Excel reports)
- GeoPandas + Shapely (spatial data)

**Database**
- PostgreSQL 15 + PostGIS 3.4

**Frontend**
- React 18 + Vite
- TailwindCSS
- React-Leaflet (interactive maps)
- Axios (API client with JWT interceptors)

**DevOps**
- Docker + Docker Compose
- Nginx (production static file serving)
- Make (common task shortcuts)

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Git

### 1. Clone & Configure

```bash
git clone <repo-url>
cd Property-Management-Website
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY and DB_PASSWORD
```

### 2. Create runtime directories

```bash
mkdir -p backend/app/static/receipts backend/app/static/reports backend/app/static/uploads
```

### 3. Launch (Development)

```bash
docker compose -f docker-compose.dev.yml up --build
```

- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Database:** localhost:5432

### 4. Initialize the database

```bash
# First terminal — run migrations
docker compose -f docker-compose.dev.yml exec api alembic upgrade head

# Seed with realistic Zimbabwe data
docker compose -f docker-compose.dev.yml exec api python -m seeds.seed_data
```

### 5. Log in

| Field | Value |
|-------|-------|
| Phone | `0772123456` |
| Password | `password123` |

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # REST route handlers
│   │   ├── core/                # Security, exceptions
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # Business logic (PDF, reports, SMS, GIS)
│   │   ├── templates/           # Jinja2 receipt templates
│   │   └── static/              # Uploads, receipts, reports
│   ├── migrations/              # Alembic revisions
│   ├── seeds/                   # Database seed data
│   ├── scripts/                 # CLI utilities (reminders, reports)
│   └── tests/                   # Pytest suite
├── frontend/
│   ├── src/
│   │   ├── pages/               # Route-level components
│   │   ├── components/          # Reusable UI (DataTable, MapView, Layout)
│   │   ├── context/             # AuthContext (JWT state)
│   │   └── api/client.js        # Axios instance with interceptors
│   └── index.html
├── db/
│   └── init-postgis.sql         # PostGIS extension bootstrap
├── docker-compose.dev.yml       # Dev stack (hot reload)
├── docker-compose.yml           # Production stack (multi-stage)
└── Makefile                     # Common commands
```

---

## Documentation

- **[Development Setup](docs/DEV_SETUP.md)** — Docker-based hot reload environment
- **[Production Setup](docs/PROD_SETUP.md)** — Multi-stage builds, Nginx, SSL considerations
- **[Local Setup (No Docker)](docs/LOCAL_SETUP.md)** — Native Python/PostgreSQL install
- **[Architecture](docs/ARCHITECTURE.md)** — Database design, API patterns, geospatial notes

---

## Daily Operations

```bash
# Send rent reminders (upcoming + overdue)
docker compose exec api python scripts/send_rent_reminders.py

# Generate monthly Excel report
docker compose exec api python scripts/generate_monthly_report.py --year 2026 --month 7

# Database backup
docker compose exec db pg_dump -U zimrental zimrental > backup_$(date +%Y%m%d_%H%M%S).sql

# View API logs
docker compose logs -f api
```

---

## API Highlights

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/login` | OAuth2Password form login |
| `GET /api/v1/auth/me` | Current manager profile |
| `GET /api/v1/properties/geo/nearby?lat=-17.8252&lon=31.0335&radius_km=5` | Nearby properties (PostGIS) |
| `GET /api/v1/properties/geo/all` | All properties as GeoJSON |
| `GET /api/v1/reports/properties/geojson` | Downloadable GeoJSON export |
| `GET /api/v1/payments/{id}/receipt` | PDF receipt download |

Full interactive docs available at `/docs` when the API is running.

---

## License

MIT — Built for the Zimbabwean property management community.
