# Production Setup

This guide covers deploying Zim Rental Manager in production using Docker Compose with multi-stage builds, Nginx, and persistent volumes.

## Prerequisites

- Docker Engine 24.0+
- Docker Compose plugin
- A server with at least **2 GB RAM** and **20 GB disk**
- Domain name (recommended) or static IP
- SSL certificate (Let's Encrypt or self-signed)

## Environment Configuration

Create a production `.env` file with strong secrets:

```env
# Database
DB_USER=zimrental
DB_PASSWORD=<strong-random-password>
DB_NAME=zimrental
DB_PORT=5432
DATABASE_URL=postgresql+psycopg2://zimrental:<strong-random-password>@db:5432/zimrental

# Security
SECRET_KEY=<64-char-random-hex>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Ports
API_PORT=8000
FRONTEND_PORT=80

# SMS (Africa's Talking)
SMS_API_KEY=your_live_api_key
SMS_SENDER_ID=ZimRental
```

> Generate a strong secret key:
> ```bash
> openssl rand -hex 32
> ```

## First Deployment

### 1. Prepare directories

```bash
mkdir -p backend/app/static/receipts backend/app/static/reports backend/app/static/uploads
cp .env.example .env
# Edit .env with production values
```

### 2. Start the stack

```bash
docker compose up --build -d
```

Services started:

| Service | Container | Exposed Port | Internal Port |
|---------|-----------|--------------|---------------|
| PostgreSQL + PostGIS | `zim-rental-db` | `${DB_PORT:-5432}` | 5432 |
| FastAPI (uvicorn) | `zim-rental-api` | `${API_PORT:-8000}` | 8000 |
| React + Nginx | `zim-rental-frontend` | `${FRONTEND_PORT:-80}` | 80 |

### 3. Initialize the database

```bash
# Run migrations
docker compose exec api alembic upgrade head

# (Optional) Seed with demo data — skip in real production
docker compose exec api python -m seeds.seed_data
```

### 4. Create the first manager

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "full_name=Admin%20User" \
  -d "national_id=63-1234567A89" \
  -d "phone=0772123456" \
  -d "password=your_secure_password" \
  -d "email=admin@yourdomain.com"
```

## Architecture Notes

### Multi-stage Frontend Build

The production `Dockerfile` for the frontend:
1. **Build stage:** Node image runs `npm ci && vite build`
2. **Serve stage:** Nginx Alpine serves the static `dist/` folder

This means the frontend is entirely static — no Node runtime in production.

### API Serving Strategy

The production `docker-compose.yml` uses:
```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

For production, you should remove `--reload` and consider using Gunicorn with Uvicorn workers:
```yaml
command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Add `gunicorn` to `requirements.txt` if you choose this path.

### Reverse Proxy / SSL

For a public-facing deployment, place Nginx or Traefik in front:

```nginx
server {
    listen 443 ssl http2;
    server_name zimrental.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:80;  # frontend container
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://localhost:8000/docs;
    }
}
```

Or use **Traefik** with Docker labels for automatic Let's Encrypt:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.zimrental.rule=Host(`zimrental.yourdomain.com`)"
  - "traefik.http.routers.zimrental.tls.certresolver=letsencrypt"
```

### Backup Strategy

```bash
# Automated daily backup (add to crontab)
0 2 * * * cd /opt/zimrental && docker compose exec -T db pg_dump -U zimrental zimrental | gzip > backups/zimrental_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz
```

### Updating Production

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose down
docker compose up --build -d

# Run any pending migrations
docker compose exec api alembic upgrade head
```

## Security Checklist

- [ ] Change default `SECRET_KEY` to a 64-character random string
- [ ] Change default database password
- [ ] Restrict `allow_origins` in `app/main.py` CORS middleware to your domain
- [ ] Disable `/docs` and `/redoc` in production (or protect behind auth)
- [ ] Use HTTPS everywhere
- [ ] Set up firewall rules (only 443 and 22 open)
- [ ] Configure log rotation for Docker containers
- [ ] Enable PostgreSQL automated backups
- [ ] Set `DEBUG=False` equivalent (FastAPI doesn't have a global debug flag, but remove `--reload`)

## Troubleshooting

### Frontend shows blank page

Check that the API base URL is reachable from the browser. In production, the frontend is served by Nginx and makes API calls relative to the same origin. Ensure your reverse proxy forwards `/api/` correctly.

### PDF receipts fail to generate

WeasyPrint requires system fonts. The production Dockerfile should include:
```dockerfile
RUN apt-get update && apt-get install -y libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
```

### Database connection refused

Ensure the `db` service is healthy before the `api` starts. The `docker-compose.yml` already uses `depends_on` with `condition: service_healthy`.
