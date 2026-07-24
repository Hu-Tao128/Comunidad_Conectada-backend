#!/bin/sh

echo "Esperando a MySQL en $DB_HOST:$DB_PORT..."

MAX_ATTEMPTS=90
ATTEMPT=1

check_mysql() {
    python -c "
import os, sys
try:
    import pymysql
    host = os.environ.get('DB_HOST')
    port = int(os.environ.get('DB_PORT', '3306'))
    user = os.environ.get('DB_USER', '')
    password = os.environ.get('DB_PASSWORD', '')
    database = os.environ.get('DB_NAME', '')
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, connect_timeout=3)
    conn.close()
    print('MySQL disponible')
    sys.exit(0)
except Exception as e:
    print(f'Esperando MySQL en {host}:{port}... ({e})')
    sys.exit(1)
"
}

until check_mysql; do
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
        echo "ERROR: MySQL no disponible después de $MAX_ATTEMPTS intentos"
        exit 1
    fi
    sleep 3
done

echo "Aplicando migraciones..."
for i in 1 2 3; do
    if python manage.py migrate --noinput; then
        echo "Migraciones aplicadas correctamente."
        break
    else
        echo "Intento $i de migraciones falló, reintentando en 3s..."
        sleep 3
    fi
done

echo "Iniciando Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
