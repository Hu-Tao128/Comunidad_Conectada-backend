#!/bin/sh

echo "Esperando a MySQL..."

until python - <<'PY'
import socket
import os

host = os.environ.get("DB_HOST", "mysql.railway.internal")
port = int(os.environ.get("DB_PORT", "3306"))

try:
    socket.create_connection((host, port), timeout=2)
    print("MySQL disponible")
except OSError:
    print(f"Esperando MySQL en {host}:{port}...")
    raise SystemExit(1)
PY
do
    sleep 2
done

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Iniciando Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
