# FamilyProgressWeb

[![Tests](https://github.com/andresmarinabad/familyprogressweb/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/andresmarinabad/familyprogressweb/actions/workflows/ci-tests.yml)

App familiar que muestra barras de progreso hasta el próximo cumpleaños de cada niño, con soporte para embarazos. Disponible en castellano y catalán.

🔗 **[resacadecumples.com](https://resacadecumples.com)**

## Stack

| Capa | Tecnología |
|---|---|
| App | Python · Flask (serverless) |
| Deploy | Vercel |
| Base de datos | Supabase (PostgreSQL) |
| Imágenes | Supabase Storage (bucket `images`, público) |
| Infra como código | OpenTofu (Terraform) |

## Estructura

```
├── app.py                          # Flask app
├── templates/                      # Jinja2 templates
├── static/
│   ├── kids.css / kids.js
│   └── images/placeholder/         # Placeholders locales (missing, embarazo)
├── translations/
│   ├── es.json
│   └── ca.json
├── scripts/
│   └── migrate_to_supabase.py      # Script de migración inicial
├── infra/
│   ├── vercel/                     # Terraform: proyecto Vercel + env vars
│   └── supabase/
│       ├── main.tf                 # Terraform: proyecto Supabase + bucket
│       ├── kids.sql                # Schema de la tabla + datos iniciales
│       └── migrate_to_supabase.py  # (ver scripts/)
├── tests/
└── requirements.txt
```

## Variables de entorno

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Flask session key (generada por Terraform) |
| `APP_PASSWORD` | Contraseña del login (generada por Terraform) |
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | JWT secret de Supabase (Settings → API → service_role) |

## Desarrollo local

```bash
# Rellenar .envrc con SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY
direnv allow
flask --app app run --debug
```

La app apunta directamente a Supabase en producción — no hay base de datos local.

## Infraestructura (OpenTofu)

Hay dos módulos independientes. Cada uno necesita su propio `tofu init` + `tofu apply`.

```bash
# 1. Crear proyecto Supabase + bucket de imágenes
cd infra/supabase
tofu init && tofu apply

# 2. Crear proyecto Vercel + env vars
cd infra/vercel
# Rellenar terraform.tfvars con github_token, supabase_url, supabase_service_role_key
tofu init && tofu apply
```

## Añadir un niño nuevo

Ejecutar en el **SQL Editor** de Supabase:

```sql
INSERT INTO kids (nombre, fecha, clan)
VALUES ('Nombre', 'DD/MM/YYYY', 'clan');
```

Para embarazos:
```sql
INSERT INTO kids (nombre, fecha, clan, embarazo)
VALUES ('Nombre', 'DD/MM/YYYY', 'clan', true);
```

Clanes disponibles: `mc`, `cm`, `cf`, `cc`, `mtc`.

## Subir una foto

Accede a `/upload` desde la app (requiere login). La imagen se recorta a cuadrado, se sube al bucket `images` de Supabase y se actualiza el campo `image_url` en la tabla `kids`.

## Migración inicial (primera vez)

Si ya tienes la tabla creada con `kids.sql` y las imágenes subidas manualmente al bucket, ejecuta el script para enlazar las imágenes con sus filas en la tabla:

```bash
SUPABASE_URL=https://xxx.supabase.co \
SUPABASE_SERVICE_ROLE_KEY=eyJ... \
python scripts/migrate_to_supabase.py
```

El script lista los ficheros del bucket `images`, busca el kid con nombre normalizado equivalente y actualiza `image_url`.

## Schema de la tabla `kids`

```sql
CREATE TABLE kids (
  id        SERIAL PRIMARY KEY,
  nombre    TEXT    NOT NULL,
  fecha     TEXT    NOT NULL,  -- formato DD/MM/YYYY
  clan      TEXT    NOT NULL,
  embarazo  BOOLEAN NOT NULL DEFAULT FALSE,
  image_url TEXT                -- URL pública de Supabase Storage
);
```

El SQL completo con los datos iniciales está en `infra/supabase/kids.sql`.

## Tests

```bash
direnv exec . pytest tests/ -v
```
