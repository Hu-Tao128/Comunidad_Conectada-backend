# Arquitectura del Backend — Comunidad Conectada

## Stack tecnológico

| Componente    | Tecnología                        |
|---------------|-----------------------------------|
| Framework     | Django 6.x + Django REST Framework |
| Base de datos | MySQL / SQLite (desarrollo)       |
| Autenticación | JWT (SimpleJWT)                   |
| Hash de claves| bcrypt_sha256                     |

---

## Estructura del proyecto

```
Comunidad_Conectada-backend/
├── config/                  # Configuración de Django
│   ├── settings.py          # Settings globales (DB, CORS, JWT, paginación)
│   └── urls.py              # Raíz de rutas (/api/)
├── apps/
│   ├── accounts/            # Usuarios, perfiles, registro, admins
│   ├── auth/                # Login JWT (SimpleJWT)
│   ├── communities/         # Privadas, módulos, miembros
│   ├── areas/               # Áreas comunes (privada)
│   ├── directorio/          # Directorio telefónico
│   ├── anuncios/            # Anuncios
│   ├── reportes/            # Reportes e incidentes
│   ├── reservas/            # Reservaciones de áreas
│   ├── pagos/               # Cuotas y pagos
│   ├── proyectos/           # Proyectos comunitarios
│   ├── objetos_perdidos/    # Objetos perdidos
│   ├── auditoria/           # Auditoría de acciones
│   └── notificaciones/      # Sistema de notificaciones
├── common/                  # Mixins, modelos base, permisos
│   ├── models.py            # BaseModel (timestamps, status, soft-delete)
│   ├── mixins.py            # ReadOnlyViewSet, PrivateScopedViewSet
│   └── permissions.py       # ReadOnlyAuthenticated
└── docs/
    └── ARQUITECTURA.md      # Este documento
```

---

## Capas por aplicación

Cada app sigue el mismo patrón Django REST:

```
models.py      → Define los modelos (entidades)
serializers.py → Transforman modelos ↔ JSON (validación incluida)
views.py       → Lógica de las vistas (ViewSets, APIViews)
filters.py     → Filtros por campos (django-filters)
urls.py        → Rutas específicas
permissions.py → Permisos personalizados
```

---

## Modelo base (`common/models.py`)

`BaseModel` es la clase abstracta que usan casi todos los modelos:

```python
class BaseModel(models.Model):
    created_at  = DateTimeField(auto_now_add=True)
    updated_at  = DateTimeField(auto_now=True)
    deleted_at  = DateTimeField(null=True, blank=True)
    created_by  = ForeignKey(Usuario)
    updated_by  = ForeignKey(Usuario, null=True)
    status      = CharField(default="activo")
```

Esto proporciona **soft-delete** (`deleted_at`) y trazabilidad de quién creó/modificó cada registro.

---

## Mixins de vistas (`common/mixins.py`)

### `ReadOnlyViewSet`
ViewSet base de solo lectura (GET lista + detalle). Todos los módulos lo usan como base.

### `PrivateScopedViewSet`
Extiende `ReadOnlyViewSet` y filtra automáticamente los datos según las privadas a las que pertenece el usuario autenticado:

- Si el usuario es `is_staff` (admin global), ve todo.
- Si es moderador/habitante, solo ve datos de sus privadas.
- El campo de lookup se configura con `private_lookup` (default: `"privada_id"`).

---

## Autenticación y roles

### JWT (SimpleJWT)
- Login vía `POST /api/auth/token/` con email + password
- Refresh vía `POST /api/auth/token/refresh/`
- Header: `Authorization: Bearer <token>`

### Roles del sistema

| Rol        | Descripción                                      |
|------------|--------------------------------------------------|
| `admin`    | Administrador global de Comunidad Conectada      |
| `moderador`| Moderador de una privada (panel de administración)|
| `habitante`| Residente de una privada (sin acceso a admin)    |

### Cómo se determina el rol
- `is_staff = True` → rol `"admin"` (accede a `/admin-comunidad/`)
- Miembro con `rol = "moderador"` → accede al panel de moderación (`/admin/*`)
- Si no es staff ni moderador → `"habitante"` (solo lobby)

---

## Módulos del sistema

### Catálogo (`ModuloSistema`)
Funcionalidades contratables que aparecen en el sidebar.

### Contratación (`PrivadaModulo`)
Relación many-to-many entre privadas y módulos del sistema.

### Flujo
1. Admin global crea un `ModuloSistema` (catálogo).
2. Al crear una privada, se seleccionan los módulos contratados vía checklist.
3. El sidebar filtra las rutas visibles según `modulos_contratados`.

---

## Permisos

| Permiso               | App/files         | Qué permite                                   |
|-----------------------|-------------------|-----------------------------------------------|
| `IsAuthenticated`     | DRF global        | Cualquier usuario autenticado                 |
| `IsAdminUser`         | DRF               | Solo `is_staff=True`                          |
| `ModeratorPermission` | accounts          | Admin global o moderador de alguna privada    |
| `ReadOnlyAuthenticated`| common           | Lectura si autenticado                        |

---

## Endpoints principales

### Públicos
| Método | Ruta                     | Descripción              |
|--------|--------------------------|--------------------------|
| POST   | `/api/auth/token/`       | Login (JWT)              |
| POST   | `/api/auth/register/`    | Registro de habitante    |

### Privadas
| Método | Ruta                                      | Descripción                     |
|--------|-------------------------------------------|---------------------------------|
| GET    | `/api/privadas/`                          | Listar privadas                 |
| GET    | `/api/privadas/mias/`                     | Mis membresías                  |
| POST   | `/api/privadas/crear/`                    | Crear privada                   |
| POST   | `/api/privadas/unirse/`                   | Unirse con código               |
| POST   | `/api/privadas/{id}/miembros/{id}/promover/` | Promover a moderador        |

### Admin global
| Método | Ruta                                         | Descripción                    |
|--------|----------------------------------------------|--------------------------------|
| GET    | `/api/admin/privadas/`                       | Todas las privadas             |
| GET    | `/api/admin/modulos/`                        | Catálogo de módulos            |
| POST   | `/api/admin/modulos/`                        | Crear módulo en catálogo       |
| PATCH  | `/api/admin/privadas/{id}/modulos/`          | Asignar módulos a privada      |
| GET    | `/api/admin/usuarios/`                       | Listar admins                  |
| POST   | `/api/admin/usuarios/`                      | Crear admin                    |

### Módulos (filtrados por privada)
| Método | Ruta                          | Descripción              |
|--------|-------------------------------|--------------------------|
| GET    | `/api/usuarios/`              | Usuarios de la privada   |
| GET    | `/api/reportes/`              | Reportes                 |
| GET    | `/api/reservaciones/`         | Reservaciones            |
| GET    | `/api/directorio/`            | Directorio               |
| GET    | `/api/eventos/`               | Eventos                  |
| GET    | `/api/objetos-perdidos/`      | Objetos perdidos         |
| GET    | `/api/modulos-sistema/`       | Catálogo de módulos      |

---

## Paginación

DRF tiene paginación global activa (`PAGE_SIZE=20`). Las vistas de administración (`AdminPrivadasView`, `AdminModulosView`, `ModuloSistemaViewSet`, `MisPrivadasView`) la deshabilitan con `pagination_class = None` porque el frontend espera arreglos planos.
