# Cardeep application image (autonomy-e2e Punto 3) — the API and the autopilot daemon share ONE
# image (identical code, different command). Build:  docker compose build
# Run the whole system:  docker compose up -d   (pg -> api + autopilot, see docker-compose.yml)
FROM python:3.11-slim

# libpq runtime for psycopg2-binary / asyncpg. --no-install-recommends keeps the image lean.
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# Dependency layer first — cached until requirements.txt changes (fast rebuilds on code edits).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then the source.
COPY . .

# Default command = the API. The autopilot service OVERRIDES it with the scheduler daemon in compose.
EXPOSE 8090
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8090"]
