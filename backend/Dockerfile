# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system libs with cached apt state
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    libgdal32 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps with cached pip downloads
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic.ini .
COPY scripts ./scripts
COPY seeds ./seeds
COPY migrations ./migrations

RUN mkdir -p app/static/receipts app/static/reports app/static/uploads

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]