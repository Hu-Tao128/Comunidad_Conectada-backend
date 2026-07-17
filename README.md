# Comunidad Conectada Backend

Backend base de Comunidad Conectada con Django 5, Django REST Framework y MySQL 8.

## Puesta en marcha

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

La configuración usa SQLite como fallback local. Para MySQL 8 define en `.env`:

```text
DB_ENGINE=django.db.backends.mysql
DB_NAME=comunidad_conectada
DB_USER=...
DB_PASSWORD=...
DB_HOST=127.0.0.1
DB_PORT=3306
SECRET_KEY=...
```

La API de consulta está disponible bajo `/api/` y requiere autenticación. JWT se obtiene en `/api/auth/token/` y se renueva en `/api/auth/token/refresh/`. Los ViewSets son de solo lectura (`GET` de lista y detalle); la lógica de negocio queda preparada en `services.py`.

La estructura de dominio separa `accounts`, `communities` (`Privada`, `Modulo`, `Casa`), `audit`, `notifications` y los módulos del DER. El ORM de Django actúa como repositorio; no se mantienen capas `repositories.py` artificiales.
