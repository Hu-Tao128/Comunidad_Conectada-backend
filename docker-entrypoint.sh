#!/bin/sh

export MYSQL_CONNECTION_ATTEMPTS=0

resolve_db_vars() {
    if [ -n "$DATABASE_URL" ]; then
        echo "Usando DATABASE_URL: $DATABASE_URL"
        local stripped="${DATABASE_URL#mysql://}"
        local userpass="${stripped%%@*}"
        local hostport="${stripped#*@}"
        local host="${hostport%%:*}"
        local port="${hostport#*:}"
        port="${port%%/*}"
        local db="${hostport#*/}"
        db="${db%%\?*}"
        export DB_HOST="${DB_HOST:-$host}"
        export DB_PORT="${DB_PORT:-${port:-3306}}"
        export DB_USER="${DB_USER:-${userpass%%:*}}"
        export DB_PASSWORD="${DB_PASSWORD:-${userpass#*:}}"
        export DB_NAME="${DB_NAME:-$db}"
    fi
}

resolve_db_vars

echo "============================================"
echo "Diagnóstico de conexión MySQL:"
echo "  DB_HOST:     ${DB_HOST:-no definido}"
echo "  DB_PORT:     ${DB_PORT:-3306}"
echo "  DB_USER:     ${DB_USER:-no definido}"
echo "  DB_NAME:     ${DB_NAME:-no definido}"
echo "  DATABASE_URL: ${DATABASE_URL:-no definido}"
echo "============================================"

echo "Esperando a MySQL en $DB_HOST:$DB_PORT..."

MAX_ATTEMPTS=60
ATTEMPT=1

check_mysql() {
    python -c "
import os, sys
try:
    import pymysql
    host = os.environ.get('DB_HOST', '')
    port = int(os.environ.get('DB_PORT', '3306'))
    user = os.environ.get('DB_USER', '')
    password = os.environ.get('DB_PASSWORD', '')
    database = os.environ.get('DB_NAME', '')
    
    print(f'  Intentando conectar a {host}:{port} como {user}...')
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, connect_timeout=5)
    conn.close()
    print('  Conexión exitosa.')
    sys.exit(0)
except Exception as e:
    print(f'  Error: {e}')
    sys.exit(1)
"
}

until check_mysql; do
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
        echo "ERROR: MySQL no disponible después de $MAX_ATTEMPTS intentos."
        echo "Revisa que la base de datos esté en el mismo proyecto de Railway y que las variables de entorno sean correctas."
        exit 1
    fi
    sleep 3
done

echo "Aplicando migraciones..."
for i in 1 2 3; do
    if python manage.py migrate --noinput 2>&1; then
        echo "Migraciones aplicadas correctamente."
        break
    else
        echo "Intento $i de migraciones falló, reintentando en 3s..."
        sleep 3
    fi
done

echo "Iniciando Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --log-level debug
