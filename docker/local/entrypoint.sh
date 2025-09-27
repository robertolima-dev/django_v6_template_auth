#!/usr/bin/env bash
set -Eeuo pipefail

cd /app

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-api_core.settings.dev}"

echo "==> Django checks"
python manage.py check

echo "==> Migrations"
python manage.py migrate --noinput || true
python manage.py migrate --run-syncdb --noinput || true

if [ "${COLLECTSTATIC:-0}" = "1" ]; then
  echo "==> Collectstatic"
  python manage.py collectstatic --noinput || true
fi

echo "==> Starting ASGI (uvicorn --reload)"
exec uvicorn api_core.asgi:application --host 0.0.0.0 --port 8000 --reload


