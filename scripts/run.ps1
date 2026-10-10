$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"

$Python = Join-Path $Backend ".venv\Scripts\python.exe"
$Index = Join-Path $Frontend "dist\index.html"

if (!(Test-Path $Python)) {
    Write-Error "Python virtual environment not found."
    exit 1
}

if (!(Test-Path $Index)) {
    Write-Error "Frontend has not been built."
    exit 1
}

Set-Location $Backend

Write-Host "Starting System Monitor..."
Write-Host "Open http://localhost:8000"

& $Python -m uvicorn app.main:app --host 127.0.0.1 --port 8000