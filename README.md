# WebHealthIQ

**WebHealthIQ** es una plataforma freemium de auditoría web automatizada: introduce una URL y obtienes una puntuación 0–100 con checks y recomendaciones en SEO, rendimiento, accesibilidad, seguridad y RGPD. El frontend muestra el informe, insights priorizados y exportación PDF; el backend ejecuta los analizadores (Playwright, Axe, HTTP/HTML) detrás de autenticación JWT y cuotas por plan.

## Demo y enlaces

| Recurso | URL |
|--------|-----|
| Web (producción) | [https://webhealthiq.com](https://webhealthiq.com) |
| API | [https://webhealthiq-api.onrender.com](https://webhealthiq-api.onrender.com) |
| Repositorio | [https://github.com/mikelzalacain/webhealthiq](https://github.com/mikelzalacain/webhealthiq) |
| Contacto | [hello@webhealthiq.com](mailto:hello@webhealthiq.com) |

Health check de la API: `GET /health` → `{ "status": "ok" }`.

---

## Stack

### Frontend (`frontend/`)

| Tecnología | Versión (aprox.) | Uso |
|------------|------------------|-----|
| [Next.js](https://nextjs.org/) | **16.3.0** (App Router) | UI, rutas, SEO metadata |
| [React](https://react.dev/) / React DOM | **19.2.8** | Componentes |
| [TypeScript](https://www.typescriptlang.org/) | ^5 | Tipado |
| [Tailwind CSS](https://tailwindcss.com/) | **4** (`@tailwindcss/postcss`) | Estilos |
| [jsPDF](https://github.com/parallax/jsPDF) | **^4.2.1** | Exportación de informes PDF en el cliente |
| next/font (Syne, Figtree, IBM Plex Mono) | — | Tipografía |
| ESLint + `eslint-config-next` | 16.3.0 | Lint |

i18n propio (ES / EN / EU) en `frontend/src/lib/i18n/`.

### Backend (`backend/`)

| Tecnología | Uso |
|------------|-----|
| **FastAPI** + **Uvicorn** | API REST |
| **Playwright** `1.50.0` | Navegador headless (HTML fallback, performance, a11y) |
| **axe-playwright-python** | Accesibilidad (reglas Axe) |
| **BeautifulSoup4** + **httpx** | SEO / RGPD / fetch HTTP |
| **SQLAlchemy** + **psycopg2-binary** | ORM; Postgres en prod, SQLite en local sin `DATABASE_URL` |
| **passlib** + **bcrypt** `4.0.1` | Hash de contraseñas |
| **python-jose** | JWT (Bearer) |
| **Pydantic** `[email]` | Validación de requests |
| **pytest** / **pytest-asyncio** | Tests |

Imagen Docker basada en `mcr.microsoft.com/playwright/python:v1.50.0-jammy`.

### Infraestructura

- **Frontend:** [Vercel](https://vercel.com) — root directory `frontend`, headers de seguridad en `frontend/vercel.json` y `next.config.ts`.
- **Backend:** [Render](https://render.com) — servicio Docker (`render.yaml`), región Frankfurt, health check `/health`.
- **Base de datos:** Postgres vía `DATABASE_URL` (p. ej. [Neon](https://neon.tech) u otro proveedor). Sin variable → SQLite en `backend/data/`.
- **DNS / dominio:** producción en `webhealthiq.com` apuntando al frontend en Vercel; API en `*.onrender.com`.

> **Pagos:** Stripe Billing implementado (Checkout + Customer Portal + webhooks). Sin keys Stripe en local, los endpoints `/api/billing/*` responden **503** y la app sigue funcionando.

---

## Estructura del monorepo

```
webhealthiq/
├── README.md                 # Esta documentación
├── render.yaml               # Blueprint Render (API Docker)
├── .gitignore
├── frontend/                 # Next.js 16 (Vercel)
│   ├── package.json
│   ├── vercel.json
│   ├── .env.example
│   ├── next.config.ts
│   └── src/
│       ├── app/              # Rutas: /, results, login, account, history, legales…
│       ├── components/       # Navbar, Footer, AuthForm, ScoreRing…
│       └── lib/              # auth, i18n, exportReportPdf
└── backend/                  # FastAPI (Render Docker)
    ├── Dockerfile
    ├── requirements.txt
    ├── .env.example
    ├── main.py               # Endpoints
    ├── auth.py / db.py / emailer.py / insights.py / i18n.py / browser.py
    ├── billing.py            # Stripe Checkout / Portal / webhooks
    ├── ssrf.py / ratelimit.py  # Anti-SSRF y rate limit in-memory
    ├── analyzers/            # seo, performance, accessibility, security, gdpr
    └── tests/
```

---

## Funcionalidades

### Auditoría multi-módulo

`POST /api/audit` (auth requerida) analiza la URL en paralelo conceptual (módulos independientes):

| Módulo | Qué hace (resumen) |
|--------|--------------------|
| **SEO** | Title, meta description, H1, alt de imágenes, canonical, Open Graph, Schema.org, robots.txt, sitemap |
| **Performance** | Métricas locales con Playwright (sin APIs de pago de terceros) |
| **Accessibility** | Violaciones Axe vía Playwright |
| **Security** | HTTPS, certificado, cabeceras, cookies, CORS (enfoque defensivo) |
| **GDPR / RGPD** | Scripts de tracking, cookies/consentimiento orientativo sobre el HTML |

Respuesta: `overall_score`, `modules`, `insights` (plan de acción priorizado, motor `rules-v1`) e id de historial.

### Auth freemium y planes

- Registro / login con JWT (Bearer), perfil en `/api/auth/me`.
- Contador mensual de auditorías por plan (`usage_months`).
- Límites en código (`backend/db.py`):

| Plan | Auditorías / mes | Historial (últimas N) |
|------|------------------|------------------------|
| `free` | 5 | 10 |
| `pro` | 50 | 100 |
| `agency` | 200 | 500 |

Al superar la cuota, la API responde **402**. Precios: Pro **4,99 €/mes**, Agencia **14,99 €/mes** (Checkout Stripe).

### Billing (Stripe)

Suscripciones mensuales vía [Stripe Checkout](https://stripe.com/docs/payments/checkout) y gestión con [Customer Portal](https://stripe.com/docs/billing/subscriptions/integrating-customer-portal). Contacto: [hello@webhealthiq.com](mailto:hello@webhealthiq.com).

#### Configurar en Stripe Dashboard

1. Crear dos productos (o precios) de suscripción **mensual** en EUR:
   - **Pro** — `4.99` EUR / month → copiar el `price_…` a `STRIPE_PRICE_PRO`
   - **Agency** — `14.99` EUR / month → copiar el `price_…` a `STRIPE_PRICE_AGENCY`
2. En **Developers → API keys**, copiar la secret key (`sk_test_…` o `sk_live_…`) → `STRIPE_SECRET_KEY`.
3. En **Developers → Webhooks**, añadir endpoint:
   - URL: `https://webhealthiq-api.onrender.com/api/billing/webhook`
   - Eventos: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
   - Copiar el signing secret (`whsec_…`) → `STRIPE_WEBHOOK_SECRET`
4. Activar el Customer Portal (Settings → Billing → Customer portal) para que el usuario pueda cancelar/actualizar método de pago.
5. En Render (y local si pruebas), definir también `APP_URL=https://webhealthiq.com` (success/cancel por defecto: `/account?billing=success` y `/#pricing`). Opcional: `STRIPE_SUCCESS_URL` / `STRIPE_CANCEL_URL`.

Variables documentadas en `backend/.env.example` (placeholders; **nunca** subas secretos reales).

#### Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/api/billing/checkout` | Sí | Body `{ "plan": "pro" \| "agency" }` → `{ "url" }` Checkout Session |
| `POST` | `/api/billing/portal` | Sí | → `{ "url" }` Customer Portal (requiere `stripe_customer_id`) |
| `POST` | `/api/billing/webhook` | No (firma Stripe) | Actualiza `user.plan` y `stripe_*` |

Sin configuración Stripe completa → **503**. Checkout lleva rate limit (~8/min IP, ~10/h por usuario).

### Historial

- Listado `GET /api/audits` y detalle `GET /api/audits/{id}` (solo del usuario autenticado).
- UI: `/history` y `/history/[id]`.

### PDF e insights

- PDF en el navegador con **jsPDF** (`exportReportPdf.ts`), desde resultados e historial.
- Insights: resumen + hasta 8 acciones priorizadas (`fail` / `warning`) generadas en backend (`insights.py`). No es un LLM; la copy de “Insights IA” en pricing indica roadmap.

### Marca blanca (plan Agency)

- Cuenta Agency puede guardar `brand_name` y `brand_primary` (`PATCH /api/account/branding`).
- El **nombre de marca** se usa en la cabecera del PDF. El color primario se persiste; su uso visual completo en el PDF puede ampliarse después.

### i18n

- UI y mensajes de auditoría: **español**, **inglés**, **euskera** (`es` / `en` / `eu`).
- El cliente envía `lang` en la auditoría; el backend normaliza el idioma.

### Reset de contraseña

- `POST /api/auth/forgot-password` y `POST /api/auth/reset-password`.
- Token de un solo uso (~1 h). Si hay SMTP configurado, envía el enlace; si no, el correo se registra en logs (útil en desarrollo).
- Páginas: `/forgot-password`, `/reset-password`.

### Legales y SEO del sitio

- Páginas `/privacy`, `/terms`, `/cookies`.
- `sitemap.ts`, `robots.ts`, Open Graph (`/og.png`), cabeceras de seguridad (HSTS, CSP, etc.).

---

## Variables de entorno

No subas secretos reales al repositorio. Copia los ejemplos y rellena en local / en el panel de Vercel o Render.

### Frontend — `frontend/.env.example`

| Variable | Descripción |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Base de la API **sin barra final**. Local: `http://127.0.0.1:8000`. Prod: `https://webhealthiq-api.onrender.com` |

### Backend — `backend/.env.example`

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `DATABASE_URL` | En prod | Postgres (`postgresql://…`). Sin ella → SQLite en `backend/data/`. URLs `postgres://` se normalizan a `postgresql://`. |
| `JWT_SECRET` | **Sí en prod** | Secreto para firmar JWT. En producción (`RENDER` / `ENV=production` / no `DEBUG`) el arranque **falla** si falta o es el default débil. Solo en local se admite un default de desarrollo. |
| `JWT_EXPIRE_DAYS` | No | Días de validez del JWT (default `14`). |
| `CORS_ORIGINS` | No | Orígenes permitidos, separados por coma. Default: `https://webhealthiq.com,https://www.webhealthiq.com,http://localhost:3000`. **Nunca** `*`. |
| `ENV` | No | `production` fuerza modo prod (JWT estricto, errores genéricos). Render también detecta `RENDER=true`. |
| `DEBUG` | No | `true`/`1` fuerza modo desarrollo aunque haya `RENDER`. |
| `SMTP_HOST` | No | Host SMTP. Sin host/usuario, el reset solo se loguea. |
| `SMTP_PORT` | No | Default `587` (STARTTLS). |
| `SMTP_USER` / `SMTP_PASSWORD` | No | Credenciales SMTP. |
| `SMTP_FROM` | No | Remitente (default `hello@webhealthiq.com` o el usuario SMTP). |
| `APP_URL` | No | Origen del frontend para el enlace de reset (default `https://webhealthiq.com`). |
| `PYTHONUNBUFFERED` | Render | `1` en el blueprint. |
| `PORT` | PaaS | Puerto de Uvicorn (Render lo inyecta; default `8000`). |

#### Seguridad (MVP)

- **Anti-SSRF** en `POST /api/audit`: solo `http`/`https`, DNS con bloqueo de IPs privadas/loopback/link-local/metadata, hosts tipo `localhost` / `.local`, y límite de redirects (`backend/ssrf.py`).
- **Rate limiting** in-memory (1 instancia): login ~10/min IP, register ~5/min IP, forgot-password ~5/min IP + ~3/h por email, reset ~10/min IP, audit ~20/min IP (además de cuota de plan). Respuesta **429**.
- **JWT**: obligatorio y fuerte en prod; caducidad por defecto 14 días.
- **CORS** allowlist vía `CORS_ORIGINS`.
- **Reset de contraseña**: se guarda **hash SHA-256** del token en DB; el email lleva el token en claro.
- **Política de contraseña**: mínimo 8 caracteres, al menos una letra y un número.
- **Errores**: en producción no se expone `str(e)` al cliente (mensaje genérico + log).
- **Cabeceras API**: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`.
- **Pendiente (no en este MVP):** migrar JWT de `localStorage` a cookies HttpOnly.

---

## Cómo correr en local

### Requisitos

- Node.js 20+ recomendado
- Python 3.11+ recomendado
- Para Playwright: tras instalar deps, `playwright install chromium` (en Docker de prod ya viene el browser)

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium

# Opcional: copiar y editar .env
# copy .env.example .env   (Windows)
# cp .env.example .env     (Unix)

uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API: [http://127.0.0.1:8000](http://127.0.0.1:8000) · docs interactivas: `/docs`.

### 2. Frontend

```bash
cd frontend
npm install
# Asegura NEXT_PUBLIC_API_URL=http://127.0.0.1:8000 en .env.local (ver .env.example)
npm run dev
```

App: [http://localhost:3000](http://localhost:3000).

### Tests backend (opcional)

```bash
cd backend
pytest
```

---

## Deploy

### Frontend → Vercel

1. Importar el repo en Vercel.
2. **Root Directory:** `frontend`.
3. Build: `npm run build` (ya definido en `package.json` / `vercel.json`).
4. Variable: `NEXT_PUBLIC_API_URL=https://webhealthiq-api.onrender.com`.
5. Dominio: `webhealthiq.com` (DNS hacia Vercel).

### Backend → Render (Docker)

Blueprint en `render.yaml`:

- Servicio `webhealthiq-api`, runtime Docker.
- `dockerfilePath: ./backend/Dockerfile`, context `./backend`.
- Plan free, región `frankfurt`, `healthCheckPath: /health`.
- Configurar en el dashboard: `DATABASE_URL`, `JWT_SECRET` (generado en el blueprint), `CORS_ORIGINS` si el frontend usa otro origen, SMTP/`APP_URL` si quieres emails de reset, y las variables Stripe (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_AGENCY`) para billing.
- En Render, `JWT_SECRET` debe ser un valor aleatorio fuerte (el blueprint puede generarlo). Si arranca con el default débil, el proceso aborta.

Imagen: Playwright Jammy + `uvicorn main:app --host 0.0.0.0 --port $PORT`.

---

## API principal

Base: `https://webhealthiq-api.onrender.com` (o `http://127.0.0.1:8000` en local).

Autenticación: header `Authorization: Bearer <access_token>` en rutas protegidas.

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `GET` | `/` | No | Ping / mensaje de estado |
| `GET` | `/health` | No | Health check |
| `POST` | `/api/auth/register` | No | Alta (plan `free`). Body: email, password, password_confirm, full_name, company?, accept_terms |
| `POST` | `/api/auth/login` | No | Login → `access_token` + user |
| `GET` | `/api/auth/me` | Sí | Perfil, plan y uso del mes |
| `POST` | `/api/auth/forgot-password` | No | Solicitud de reset (respuesta genérica) |
| `POST` | `/api/auth/reset-password` | No | Body: token, password, password_confirm |
| `PATCH` | `/api/account/branding` | Sí (agency) | `brand_name`, `brand_primary` |
| `POST` | `/api/billing/checkout` | Sí | Stripe Checkout (`pro` / `agency`) |
| `POST` | `/api/billing/portal` | Sí | Stripe Customer Portal |
| `POST` | `/api/billing/webhook` | Firma Stripe | Sync plan / ids |
| `POST` | `/api/audit` | Sí | Body: `{ "url": "…", "lang": "es" }` |
| `GET` | `/api/audits` | Sí | Historial (limitado por plan) |
| `GET` | `/api/audits/{id}` | Sí | Detalle + result/insights |

Códigos útiles: **401** sin token válido, **402** cuota agotada, **403** branding sin plan agency, **404** auditoría ajena o inexistente, **429** rate limit.

OpenAPI: `/docs` y `/redoc` (FastAPI).

---

## Roadmap / fuera de alcance actual

- Insights con LLM (“IA”) — hoy el motor es por reglas (`rules-v1`).
- Ampliar marca blanca (p. ej. aplicar `brand_primary` de forma completa en PDF/UI).
- JWT en cookies HttpOnly (hoy el token vive en `localStorage` del frontend).
- WAF / reglas Cloudflare.

---

## Licencia y contacto

Uso y términos según las páginas legales del sitio. Soporte y contacto comercial: **[hello@webhealthiq.com](mailto:hello@webhealthiq.com)**.
