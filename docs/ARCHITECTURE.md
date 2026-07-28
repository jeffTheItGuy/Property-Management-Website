# Architecture & Design

This document explains how Zim Rental Manager is structured, why certain decisions were made, and how the major subsystems interact.

---

## System Overview

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   React 18      │──────▶   FastAPI       │──────▶  PostgreSQL 15  │
│   (Vite + HMR)  │◀──────│   (Python 3.11) │◀──────│   + PostGIS     │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                        │
        │                        ▼
        │               ┌─────────────────┐
        │               │  WeasyPrint     │
        │               │  OpenPyXL       │
        │               │  Africa's Talk. │
        │               └─────────────────┘
        ▼
   Leaflet Map
```

---

## Database Design

### Core Entities

```
PropertyManager ──1:N──► Property ──1:N──► Unit ──1:N──► Lease
                                              │            │
                                              │            ├──1:N──► PaymentSchedule
                                              │            ├──1:N──► RentPayment
                                              │            ├──1:N──► Deposit
                                              │            ├──1:N──► MaintenanceRequest
                                              │            └──1:N──► Inspection
                                              │
                                              └──1:N──► Expense

Landlord ──1:N──► Property
Tenant ──1:N──► LeaseTenant (junction) ──N:1──► Lease
Tenant ──1:N──► TenantGuarantor
```

### Geospatial Layer

Properties store coordinates in a PostGIS `GEOMETRY(POINT, 4326)` column named `geom`.

**Why PostGIS instead of plain lat/lon floats?**
- Accurate distance queries using `ST_DWithin` with geography casts (meters, not degrees)
- Native GeoJSON export via GeoPandas
- Spatial indexing (GiST) for fast nearby searches
- Future-proof for polygon boundaries, route analysis, etc.

**Nearby search implementation:**
```python
# Uses geography cast for true meter-based distance
func.ST_DWithin(
    func.ST_GeogFromWKB(Property.geom),
    func.ST_GeogFromText(f"SRID=4326;POINT({lon} {lat})"),
    radius_km * 1000
)
```

---

## API Design

### Authentication

- **OAuth2 Password Bearer** flow with JWT tokens
- Tokens expire after 8 hours (`ACCESS_TOKEN_EXPIRE_MINUTES=480`)
- Phone number used as username (fits Zimbabwe market where email penetration is lower)
- Passwords hashed with bcrypt via Passlib

### Response Patterns

| Pattern | Example |
|---------|---------|
| List | `GET /api/v1/properties/` — returns array, supports `?search=` and `?city=` |
| Create | `POST /api/v1/properties/` — returns created object, 200 OK |
| Read | `GET /api/v1/properties/{id}` — returns object or 404 |
| Update | `PUT /api/v1/properties/{id}` — partial updates via `exclude_unset=True` |
| Delete | `DELETE /api/v1/properties/{id}` — returns `{"detail": "..."}` |

### Serialization Strategy

SQLAlchemy 2.0 `Mapped` columns + Pydantic v2 `ConfigDict(from_attributes=True)`.

**The WKBElement problem:** PostGIS returns binary WKB elements that Pydantic cannot natively serialize. Solved in `PropertyResponse` with:
- A `@model_validator(mode='before')` that extracts `latitude`/`longitude` from `geom` via Shapely
- A `@field_serializer('geom')` that converts WKB to GeoJSON `mapping()` dict

---

## Frontend Architecture

### State Management

- **Global:** `AuthContext` holds the logged-in manager and JWT token
- **Local:** Each page fetches its own data on mount via `useEffect`
- **No Redux/Zustand** — deliberate simplicity for a CRUD-heavy admin tool

### Component Reusability

| Component | Responsibility |
|-----------|---------------|
| `DataTable` | Sortable, filterable table with search input and action slots |
| `MapView` | Leaflet map with OSM tiles, auto-centering, popup info |
| `Layout` | Responsive sidebar nav (vertical desktop, horizontal mobile) |

### API Client

Axios instance with interceptors:
- **Request:** Attaches `Authorization: Bearer <token>` from `localStorage`
- **Response:** On 401, clears token and redirects to `/login`

**File downloads** (reports, receipts, GeoJSON) use `api.get(url, { responseType: 'blob' })` so the JWT header is sent — plain `<a>` tags fail with 401 on protected endpoints.

---

## Business Logic Services

### Receipt Service (`services/receipt_service.py`)

1. Jinja2 renders `receipt_base.html` with payment + tenant data
2. WeasyPrint converts HTML → PDF
3. PDF saved to `app/static/receipts/{receipt_number}.pdf`
4. Subsequent downloads serve the cached file directly

### Report Service (`services/report_service.py`)

- **Monthly Report:** Pandas DataFrames for Income, Expenses, and Summary sheets → OpenPyXL
- **Payment Ledger:** Filtered `RentPayment` query → Excel
- **GeoJSON Export:** GeoPandas `GeoDataFrame` with Shapely geometries → `to_file(driver="GeoJSON")`

### SMS Service (`services/sms_service.py`)

- **Development:** Prints to stdout, returns `True`
- **Production:** Africa's Talking REST API
- **Templates:** Jinja2 `.txt` files for late notices and lease expiry reminders

### Geospatial Service (`services/geospatial_service.py`)

- `search_properties_nearby()` — PostGIS `ST_DWithin` with geography cast
- `properties_to_geojson()` — Converts SQLAlchemy objects to GeoJSON `FeatureCollection`

---

## Dev vs Production Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| Frontend server | Vite dev server (port 5173) | Nginx serving static build (port 80) |
| API reload | `uvicorn --reload` | `uvicorn` or Gunicorn workers |
| CORS | `allow_origins=["*"]` | Restricted to domain |
| API docs | `/docs` and `/redoc` enabled | Consider disabling or IP-restricting |
| SMS | Mock (stdout) | Africa's Talking live |
| Database | Named volume `postgres_data_dev` | Named volume `postgres_data` |
| Static files | Bind-mounted from host | Copied into image at build time |

---

## Security Model

- All endpoints (except `/auth/login` and `/auth/register`) require a valid JWT
- `get_current_manager` dependency resolves the token to a database user on every request
- Passwords hashed with bcrypt (cost factor 12)
- File uploads are saved with UUID-prefixed filenames to prevent collisions/overwrites
- No raw SQL — all queries use SQLAlchemy ORM to prevent injection

---

## Performance Considerations

1. **Database pooling** — SQLAlchemy `pool_pre_ping=True` recycles stale connections
2. **Lazy receipt generation** — PDFs generated on first request, then cached
3. **GeoJSON streaming** — Report service writes to disk, then `FileResponse` streams it
4. **Frontend build** — Vite tree-shakes unused code; production bundle is minimal
5. **No N+1** — List endpoints use `.all()` with relationship loading where needed

---

## Extending the System

### Adding a new endpoint

1. Create schema in `backend/app/schemas/`
2. Create model in `backend/app/models/` (if new table)
3. Create endpoint in `backend/app/api/v1/endpoints/`
4. Register router in `backend/app/api/v1/router.py`
5. Generate migration: `alembic revision --autogenerate -m "add x"`
6. Add frontend page or component

### Adding a new payment method

1. Update `payment_method` enum in `RentPayment` model
2. Update frontend `<select>` in `Payments.jsx`
3. No migration needed for string enums in PostgreSQL
