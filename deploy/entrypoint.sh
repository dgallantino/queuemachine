#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE=queue_machine.settings

echo "==> Waiting for database..."
python << 'PY'
import os, sys, time
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "queue_machine.settings")
django.setup()
from django.db import connection
for i in range(30):
    try:
        connection.ensure_connection()
        break
    except Exception:
        time.sleep(2)
else:
    sys.exit("Database not reachable")
PY

echo "==> Running migrations"
python manage.py migrate --noinput

echo "==> Collecting static files"
python manage.py collectstatic --noinput --clear

echo "==> Starting Gunicorn"
exec gunicorn queue_machine.wsgi:application --config deploy/gunicorn.conf.py
