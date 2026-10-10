$ErrorActionPreference = "Stop"

# Resolve paths relative to this script, regardless of the current directory.
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$FrontendDist = Join-Path $Frontend "dist"
$Python = Join-Path $Backend ".venv\Scripts\python.exe"

Write-Host "Building System Monitor for Windows..."

# Check prerequisites used only when building, not by end users.
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    throw "Node.js/npm is required to build the frontend."
}

# Create the Python virtual environment if needed.
if (-not (Test-Path $Python)) {
    Write-Host "Creating Python virtual environment..."
    $VenvPath = Join-Path $Backend ".venv"

    if (Get-Command py.exe -ErrorAction SilentlyContinue) {
        & py.exe -3 -m venv $VenvPath
    }
    elseif (Get-Command python.exe -ErrorAction SilentlyContinue) {
        & python.exe -m venv $VenvPath
    }
    else {
        throw "Python 3.10+ is required to build the application."
    }

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create the Python virtual environment."
    }
}

# Install the Python application and packaging tool.
Write-Host "Installing backend build dependencies..."
& $Python -m pip install -e $Backend pyinstaller
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install backend dependencies or PyInstaller."
}

# Compile the React frontend and bundle the generated static files.
Write-Host "Building React frontend..."
Push-Location $Frontend
try {
    & npm.cmd ci
    if ($LASTEXITCODE -ne 0) {
        throw "npm ci failed."
    }

    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed."
    }
}
finally {
    Pop-Location
}

if (-not (Test-Path (Join-Path $FrontendDist "index.html"))) {
    throw "React build did not produce frontend/dist/index.html."
}

# Package the launcher, Python runtime, API, and built React frontend.
Write-Host "Packaging System Monitor..."
Push-Location $Backend
try {
    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --name SystemMonitor `
        --specpath (Join-Path $Backend "build") `
        --distpath (Join-Path $Backend "dist") `
        --collect-submodules uvicorn `
        --add-data "${FrontendDist}:frontend/dist" `
        launcher.py

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed."
    }
}
finally {
    Pop-Location
}

$Executable = Join-Path $Backend "dist\SystemMonitor.exe"
if (-not (Test-Path $Executable)) {
    throw "Build finished but SystemMonitor.exe was not found."
}

Write-Host ""
Write-Host "Build successful!"
Write-Host "Executable: $Executable"
