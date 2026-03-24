# dev.ps1 — inicia backend (FastAPI) e frontend (Vite) em janelas separadas
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Start-Process powershell -ArgumentList "-NoExit", "-Command",
  "Set-Location '$root\backend'; uvicorn app.main:app --reload" `
  -WindowStyle Normal

Start-Process powershell -ArgumentList "-NoExit", "-Command",
  "Set-Location '$root\frontend'; npm run dev" `
  -WindowStyle Normal

Write-Host "Backend:  http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
