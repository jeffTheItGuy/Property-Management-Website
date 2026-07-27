FROM python:3.11-slim

WORKDIR /app

# Runtime libraries required by WeasyPrint (PDF receipts) and GeoPandas/PostGIS stack
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    libgdal32 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app ./app
COPY alembic.ini .
COPY scripts ./scripts
COPY seeds ./seeds
COPY migrations ./migrations

# Ensure runtime output dirs exist (volumes will mount over them in compose)
RUN mkdir -p app/static/receipts app/static/reports app/static/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]