#!/usr/bin/env sh
set -e

echo "Starting KubeAudit backend..."

if [ -f "alembic.ini" ]; then
  echo "Running Alembic migrations..."
  alembic upgrade head
else
  echo "alembic.ini not found, skipping migrations."
fi

echo "Starting Uvicorn..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
