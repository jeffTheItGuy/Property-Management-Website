FROM python:3.11-slim

WORKDIR /app

# System deps for WeasyPrint, psycopg2, and compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic.ini .
COPY scripts ./scripts
COPY seeds ./seeds
COPY migrations ./migrations

RUN mkdir -p app/static/uploads app/static/receipts app/static/reports

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]