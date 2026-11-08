# ClassroomHub

ClassroomHub es un proyecto de aprendizaje con **Django**. Evolución por laboratorios:

- **Laboratorio 06:** rutas, vistas y plantillas (`/`, `/resources/`, `/about/`).
- **Laboratorio 07:** catálogo persistente en **MariaDB/MySQL** (modelos `Category` y `Resource`, migraciones, ORM y Django Admin).
- **Laboratorio 08:** **cuentas de usuario, autenticación, sesiones y permisos** con las herramientas integradas de Django.

## Funcionalidades

- Páginas públicas: inicio, catálogo (`/resources/`) y About, sin necesidad de iniciar sesión.
- Registro de cuentas comunes (`UserCreationForm`, sin privilegios administrativos), inicio y cierre de sesión (`LoginView` y un `LogoutView` que solo acepta POST).
- Panel privado `/dashboard/` (`@login_required`) con un contador de visitas guardado en `request.session`.
- Revisión de recursos `/resources/review/`, solo para usuarios con el permiso `pages.view_resource` (grupo **Catalog reviewers**).
- Navegación que cambia según el estado de autenticación y los permisos (solo presentación; la seguridad la aplica el servidor).
- 28 pruebas automatizadas en `pages/tests.py`.

## Rutas

| Ruta | Nombre | Acceso |
|---|---|---|
| `/` | `pages:home` | Público |
| `/resources/` | `pages:resources` | Público |
| `/about/` | `pages:about` | Público |
| `/accounts/signup/` | `pages:signup` | Público (si ya hay sesión, redirige al dashboard) |
| `/accounts/login/` | `pages:login` | Público |
| `/accounts/logout/` | `pages:logout` | Solo **POST** con token CSRF (GET responde 405) |
| `/dashboard/` | `pages:dashboard` | Requiere iniciar sesión |
| `/resources/review/` | `pages:resource-review` | Requiere sesión **y** permiso `pages.view_resource` |
| `/admin/` | — | Administradores (`is_staff`) |

Respuestas de `/resources/review/`: anónimo → redirige al login (302); autenticado sin permiso → **403**; con permiso → 200.

## Requisitos

- Python 3.12
- MySQL 8.0+ o MariaDB 10.4+ (desarrollado con MariaDB 10.4.32)
- Django 4.2.11, `mysqlclient` y `python-dotenv` (en `requirements.txt`)

## 1. Entorno virtual (Windows)

Desde la carpeta `classroom-hub/` (donde está `manage.py`):

```bash
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

En Linux/macOS: `python3 -m venv venv` y `source venv/bin/activate`.

## 2. Base de datos

Con una cuenta administrativa, solo para este paso (`mysql -u root -p`):

```sql
CREATE DATABASE classroom_hub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'classroomhub_user'@'localhost' IDENTIFIED BY 'cambia_esta_contrasena';
GRANT ALL PRIVILEGES ON classroom_hub.* TO 'classroomhub_user'@'localhost';
GRANT ALL PRIVILEGES ON test_classroom_hub.* TO 'classroomhub_user'@'localhost';
FLUSH PRIVILEGES;
```

La aplicación usa solo `classroomhub_user`. El segundo `GRANT` permite que Django cree la base de pruebas `test_classroom_hub`.

## 3. Variables de entorno

```bash
copy .env.example .env
```

(Linux/macOS: `cp .env.example .env`). Completa tus valores:

```
DB_NAME=classroom_hub
DB_USER=classroomhub_user
DB_PASSWORD=replace_with_a_private_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

> `.env` contiene credenciales y no se sube a GitHub (está en `.gitignore`). Solo se publica `.env.example`.

## 4. Migraciones

```bash
python manage.py check
python manage.py migrate
python manage.py showmigrations
```

Además de las de `pages`, se aplican las de `auth` (usuarios, grupos y permisos), `sessions`, `admin` y `contenttypes`.

## 5. Crear usuarios

**Cuenta común:** desde el navegador, en <http://127.0.0.1:8000/accounts/signup/>. El formulario solo pide nombre de usuario y contraseña (con validación de seguridad); la cuenta se crea sin privilegios administrativos.

**Administrador** (para entrar a `/admin/`):

```bash
python manage.py createsuperuser
```

## 6. Crear el grupo y asignar el permiso

El grupo **Catalog reviewers** debe tener el permiso `pages.view_resource` ("Can view resource"), que Django crea automáticamente para el modelo `Resource`.

**Opción A: Django Admin** (`/admin/`)
1. *Groups* > *Add group*: nombre `Catalog reviewers`.
2. En *Available permissions*, elegir `pages | resource | Can view resource` y pasarlo a *Chosen permissions*. Guardar.
3. *Users* > abrir la cuenta de prueba > en *Groups* elegir `Catalog reviewers`. **No** marcar *Staff status* ni *Superuser status*.

**Opción B: Django Shell** (`python manage.py shell`)

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()
permission = Permission.objects.get(
    content_type__app_label="pages", codename="view_resource"
)
group, _ = Group.objects.get_or_create(name="Catalog reviewers")
group.permissions.add(permission)

user = User.objects.get(username="nombre_de_la_cuenta")
user.groups.add(group)
```

## 7. Iniciar el servidor y probar los permisos

```bash
python manage.py runserver
```

| Usuario | `/dashboard/` | `/resources/review/` |
|---|---|---|
| Anónimo | Redirige al login | Redirige al login |
| Cuenta común (sin grupo) | 200 | **403** |
| Cuenta en `Catalog reviewers` | 200 | 200 |

El enlace "Review" solo aparece en el menú para quien tiene el permiso, pero **la protección real está en la vista**: escribir la URL directamente no permite saltarla.

## 8. Pruebas

```bash
python manage.py test -v 2
```

Resultado esperado: `Ran 28 tests ... OK` (10 del catálogo del Laboratorio 07, 12 de autenticación y 6 de permisos). Django usa la base independiente `test_classroom_hub` y la elimina al terminar; la base `classroom_hub` no se modifica.

## Seguridad

- Las contraseñas se guardan cifradas (hash), nunca en texto plano.
- El cierre de sesión es solo por POST y con protección CSRF.
- El registro no puede otorgar permisos: el formulario no incluye `is_staff` ni `is_superuser`.
- No se publican contraseñas, `.env`, cookies de sesión ni datos de usuarios.

## Estructura

```
classroom-hub/
├── manage.py
├── requirements.txt
├── .env.example
├── config/            # settings.py (MariaDB, auth, sesiones), urls.py
└── pages/
    ├── models.py      # Category y Resource
    ├── admin.py
    ├── views.py       # catálogo, signup, dashboard, resource_review
    ├── urls.py        # rutas públicas y de cuentas
    ├── tests.py       # 28 pruebas
    └── templates/pages/   # base, home, resources, about, signup, login, dashboard, review
```