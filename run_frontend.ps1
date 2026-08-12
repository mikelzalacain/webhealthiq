$ErrorActionPreference = "Stop"

Write-Host "Starting WebHealthIQ Frontend..."
cd frontend
# Webpack evita fallos de Turbopack en rutas de red (UNC)
npx next dev --webpack -p 3000
