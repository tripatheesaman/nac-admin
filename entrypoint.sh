#!/bin/sh
set -e

# Wait for Postgres
if [ -n "$DATABASE_HOST" ]; then
  echo "Waiting for Postgres at $DATABASE_HOST:$DATABASE_PORT..."
  python - <<'PY'
import os, time, socket
host = os.environ.get('DATABASE_HOST', 'localhost')
port = int(os.environ.get('DATABASE_PORT', '5432'))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print('Postgres is up')
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit('Postgres not available')
PY
fi

python manage.py migrate --noinput
# Seed database (idempotent; seeders already skip existing rows)
python manage.py seed_staff || true
python manage.py seed_users || true
python manage.py collectstatic --noinput

# Create media subdirectories
mkdir -p /app/media/processed /app/media/uploads

exec "$@"


