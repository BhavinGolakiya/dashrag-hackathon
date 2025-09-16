#!/usr/bin/env bash
set -e

# Where to keep the sqlite DB (mounted volume)
: "${SQLITE_PATH:=/app/data/db.sqlite3}"
mkdir -p "$(dirname "$SQLITE_PATH")"

# Fix Hugging Face cache perms
mkdir -p /app/.cache/huggingface/transformers
chown -R $(id -u):$(id -g) /app/.cache

# Ensure SQLite data dir exists and is writable
mkdir -p /app/data
chown -R "$(id -u)":"$(id -g)" /app/data || true

echo ">> Using SQLite at: $SQLITE_PATH"

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

# Optionally create a superuser (set DJANGO_SUPERUSER_CREATE=true in env)
if [ "${DJANGO_SUPERUSER_CREATE:-false}" = "true" ]; then
  python manage.py createsuperuser --noinput || true
fi

# Auto-seed ONLY when DEMO_SEED=true and DB is empty
if [ "${DEMO_SEED:-false}" = "true" ]; then
  if python - <<'PY'
from django.db import connection
from django.apps import apps
Ticket = apps.get_model("core", "Ticket")
print("EMPTY" if (Ticket is None or not Ticket.objects.exists()) else "NONEMPTY")
PY
    grep -q "EMPTY"; then
    echo ">> Seeding demo data..."
    python manage.py seed_data --count "${DEMO_SEED_COUNT:-10000}"
  else
    echo ">> Demo data present; skipping seed."
  fi
fi

#python manage.py schema_index --noinput

# Start gunicorn
exec gunicorn hackathon_ai_dashboard.wsgi:application \
  --config /app/gunicorn.conf.py