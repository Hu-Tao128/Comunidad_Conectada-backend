#!/bin/sh

# Solo esperar a MySQL si DB_HOST está definido
if [ -n "$DB_HOST" ]; then
    echo "Esperando a MySQL en $DB_HOST:$DB_PORT..."
    
    MAX_ATTEMPTS=30
    ATTEMPT=1
    
    until python - <<'PY'
import socket
import os
import sys

host = os.environ.get("DB_HOST")
port = os.environ.get("DB_PORT", "3306")

if not host:
    print("DB_HOST no definido, saltando espera")
    sys.exit(0)

try:
    socket.create_connection((host, port), timeout=2)
    print("MySQL disponible")
    sys.exit(0)
except OSError as e:
    print(f"Esperando MySQL en {host}:{port}... ({e})")
    sys.exit(1)
PY
    do
        echo "Intento $ATTEMPTS de $MAX_ATTEMPTS..."
        ATTEMPT=$((ATTEMPT + 1))
        
        if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
            echo "ERROR: MySQL no disponible después de $MAX_ATTEMPTS intentos"
            exit 1
        fi
        
        sleep 2
    done
else
    echo "DB_HOST no definido, saltando espera de MySQL"
fi

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Iniciando Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
