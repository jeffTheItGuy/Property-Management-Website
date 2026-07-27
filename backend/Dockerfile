FROM python:3.11-slim

WORKDIR /app

# Install system deps for WeasyPrint, psycopg2, Shapely
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev \
    libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 \
    libffi-dev libjpeg-dev libopenjp2-7-dev \
    libgdk-pixbuf2.0-0 libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
