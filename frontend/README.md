# WebHealthIQ — Frontend

Next.js 16 (App Router) + React 19 + Tailwind 4.

La documentación completa del monorepo (stack, API, env, deploy) está en el **[README raíz](../README.md)**.

## Desarrollo

```bash
npm install
# Copia .env.example → .env.local si hace falta
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000). La API debe estar en `NEXT_PUBLIC_API_URL` (por defecto `http://127.0.0.1:8000`).

## Scripts

| Comando | Descripción |
|---------|-------------|
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Build de producción |
| `npm start` | Sirve el build |
| `npm run lint` | ESLint |
