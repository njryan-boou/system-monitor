# System Monitor

A lightweight, cross-platform system monitoring dashboard built with
**React, TypeScript, Python, and FastAPI**.

System Monitor provides a web-based interface for viewing CPU, memory,
storage, and operating system information in real time.

The application uses Python to collect hardware metrics and exposes
them through a REST API. A React frontend retrieves these metrics
and displays them in a responsive dashboard.

## Live Demo

**Website:** [System Monitor](https://system-monitor-eta.vercel.app)

**Backend API:** [FastAPI Documentation](https://system-monitor-api-87a9.onrender.com/docs)

The frontend is hosted on Vercel, while the FastAPI backend runs on Render.

> **Note:** The deployed dashboard displays hardware information from
> the environment running the FastAPI backend, not from the device
> accessing the website.
>
> The free hosting service may require additional time to respond
> after periods of inactivity.

## Preview

System Monitor features a dark-themed dashboard with individual
monitoring cards, utilization indicators, and automatically
refreshing measurements.

## Features

### CPU Monitoring

- Processor model and manufacturer information
- Overall CPU utilization
- Physical CPU core count
- Logical processor count
- Current CPU frequency

### Memory Monitoring

- Total system memory
- Used memory
- Available memory
- Memory utilization percentage

### Storage Monitoring

- Filesystem mount point
- Total storage capacity
- Used storage
- Available storage
- Storage utilization percentage

### System Information

- Operating system
- OS/kernel release
- System architecture
- System uptime

### Web Dashboard

- Automatically refreshing hardware metrics
- CPU, memory, and storage utilization bars
- Responsive layout for desktop and mobile devices
- Dark-themed interface
- Hardware-specific icons
- Loading indicators
- API error handling
- Independent metric updates

## Technology Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| React | User interface |
| TypeScript | Type-safe frontend development |
| HTML | Application structure |
| CSS | Styling and responsive layouts |
| Vite | Frontend development and production builds |
| Lucide React | Interface icons |

### Backend

| Technology | Purpose |
|------------|---------|
| Python | Backend programming language |
| FastAPI | REST API framework |
| Uvicorn | ASGI web server |
| Pydantic | API response validation |
| psutil | System and hardware metrics |
| py-cpuinfo | Processor identification |
| Pytest | Automated testing |
| HTTPX-compatible test client | HTTP API testing |

### Infrastructure

| Service | Purpose |
|---------|---------|
| GitHub | Version control |
| Vercel | Frontend hosting |
| Render | Backend hosting |

No database is required for the initial release.

## Project Structure

```text
system-monitor/
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   ├── tests/
│   └── pyproject.toml
│
├── scripts/
│   ├── setup.sh
│   ├── run.sh
│   └── run.ps1
│
├── README.md
└── .gitignore
```

## Architecture

System Monitor follows a client-server architecture.

```text
                  WEB BROWSER
                       |
                       v
              React + TypeScript
                       |
                       | HTTP Requests
                       |
                       v
                  FastAPI
                       |
                       v
              Monitoring Service
                       |
             +---------+---------+
             |                   |
             v                   v
           psutil             py-cpuinfo
             |                   |
             +---------+---------+
                       |
                       v
               Operating System
                       |
             +---------+---------+
             |         |         |
            CPU       RAM      Storage
```

### Backend

The backend is responsible for collecting hardware information
and exposing it through HTTP endpoints.

Responsibilities are separated into three layers:

**Monitoring Service**

`app/services/monitor.py`

Retrieves system information using Python libraries.

**API Routes**

`app/routes/system.py`

Defines the HTTP endpoints used by the frontend.

**Response Schemas**

`app/schemas/system.py`

Uses Pydantic to define and validate API response structures.

### Frontend

The frontend is built with React and TypeScript.

**Components**

Individual monitoring cards display hardware information.

**Dashboard**

Manages application state, retrieves updated information,
and organizes the monitoring cards.

**API Service**

Handles communication between React and FastAPI.

## Installation

### Prerequisites

Ensure the following software is installed:

- Python 3.10 or newer
- Node.js and npm
- Git

The application has been developed and tested primarily on Linux.

Most basic monitoring functionality is designed to work across
Windows, Linux, and macOS.

Some hardware metrics may vary depending on the operating system,
hardware, drivers, and permissions.

### 1. Clone the Repository

```bash
git clone https://github.com/njryan-boou/system-monitor.git

cd system-monitor
```

### 2. Configure the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate the environment on Linux or macOS:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the backend and its dependencies:

```bash
python -m pip install -e .
```

To install development and testing dependencies:

```bash
python -m pip install -e ".[dev]"
```

Dependencies are declared in `backend/pyproject.toml`.

### 3. Configure the Frontend

From the project root, navigate to:

```bash
cd frontend
```

Install the JavaScript dependencies:

```bash
npm install
```

## Running Locally

The frontend and backend run as separate development servers.

Both servers must be running for the dashboard to retrieve
system information.

### Start the Backend

From the `backend/` directory:

```bash
source .venv/bin/activate
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

http://localhost:8000

Interactive API documentation:

http://localhost:8000/docs

The `--reload` option automatically restarts the backend when
Python source files change.

### Start the Frontend

Open a second terminal.

Navigate to the `frontend/` directory:

```bash
npm run dev
```

The application will normally be available at:

http://localhost:5173

Open this address in your browser to view the dashboard.

### Local API Communication

During development, Vite forwards requests beginning with `/api`
to the local FastAPI backend.

For example:

```text
Browser
   |
   v
localhost:5173/api/system/cpu
   |
   v
Vite Development Proxy
   |
   v
localhost:8000/api/system/cpu
   |
   v
FastAPI
```

The development proxy is configured in `frontend/vite.config.ts`.

## Standalone Local Application (v0.2.0 in development)

System Monitor can be packaged with PyInstaller so end users can run it
without installing Python, Node.js, or application dependencies.

The executable starts the local FastAPI server on `127.0.0.1:8000`
and opens the monitoring dashboard in the default browser.
It displays hardware information from the computer running the executable.

**Build on Linux:** From the repository root, after running `./scripts/setup.sh`
and installing PyInstaller into `backend/.venv`:

```bash
backend/.venv/bin/python -m pip install pyinstaller
./scripts/build-linux.sh
./backend/dist/system-monitor-linux
```

**Build on Windows:** From PowerShell in the repository root, with Python 3
and Node.js/npm installed:

```powershell
.\scripts\build-windows.ps1
.\backend\dist\SystemMonitor.exe
```

The build scripts compile the frontend and bundle the application into a
single executable. Building requires development tools, but running the
packaged application does not. Builds must be produced on their target
operating system (Linux for Linux, Windows for Windows).

> Windows packaging has not yet been verified. Linux executable
> compatibility depends on the target system's native libraries; the
> current Linux build has been tested on the development machine,
> including when launched from outside the source repository.
>
> Do not expose the local unauthenticated API to the public internet.

## API Documentation

System Monitor exposes a REST API for retrieving hardware metrics.

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/system/cpu` | CPU information |
| GET | `/api/system/memory` | Memory information |
| GET | `/api/system/storage` | Storage information |
| GET | `/api/system/info` | Operating system information |

All endpoints return JSON.

### CPU Information

**Endpoint**

```http
GET /api/system/cpu
```

Example response:

```json
{
    "name": "AMD Ryzen 9 9950X 16-Core Processor",
    "usage": 15.5,
    "physical_cores": 16,
    "logical_cores": 32,
    "frequency_mhz": 2400.0
}
```

The response contains processor identification, utilization,
core counts, and current reported frequency.

Some fields may be `null` if the operating environment
does not expose the requested information.

### Memory Information

**Endpoint**

```http
GET /api/system/memory
```

Example response:

```json
{
    "total": 68719476736,
    "used": 17179869184,
    "available": 51539607552,
    "percent": 25.0
}
```

Memory capacities are returned in bytes.

The frontend converts these measurements to GiB for display.

### Storage Information

**Endpoint**

```http
GET /api/system/storage
```

Example response:

```json
{
    "volume": "/",
    "total": 1000000000000,
    "used": 400000000000,
    "free": 600000000000,
    "percent": 40.0
}
```

Storage capacities are returned in bytes.

The initial implementation monitors one filesystem.

On Linux, `/` represents the root filesystem.

### System Information

**Endpoint**

```http
GET /api/system/info
```

Example response:

```json
{
    "os": "Linux",
    "os_release": "6.14.0",
    "architecture": "x86_64",
    "uptime": 187200
}
```

Uptime is returned in seconds.

The frontend formats this into days, hours, and minutes.

The OS release field represents the kernel release on Linux.

## Data Collection

System Monitor uses Python libraries to retrieve information
from the operating system.

The dashboard periodically requests updated information
from the backend.

The frontend maintains the latest successful measurements
and updates the monitoring cards as new data arrives.

### Static and Dynamic Information

Some hardware information rarely changes:

- Processor model
- Physical core count
- Logical processor count
- Operating system
- Architecture

Other measurements change continuously:

- CPU utilization
- CPU frequency
- Memory utilization
- Storage utilization
- System uptime

Processor identification is cached to avoid repeatedly
retrieving static CPU information.

### Platform Limitations

Not all hardware information is exposed consistently across
operating systems.

For example:

- CPU frequencies may be reported differently on Windows and Linux.
- Hardware sensors may require platform-specific interfaces.
- Virtualized environments may expose host-level information.
- Some CPU identification fields may be unavailable.

Unsupported measurements should be represented as unavailable
rather than assigned estimated values.

## Testing

The backend uses Pytest and FastAPI's testing utilities.

### Run Backend Tests

From `backend/`:

```bash
python -m pytest -v
```

The initial test suite covers all four API endpoints:

```text
/api/system/cpu
/api/system/memory
/api/system/storage
/api/system/info
```

Tests verify that endpoints return successful HTTP responses
containing the expected fields.

Additional tests for metric validation and error handling
may be introduced in future versions.

### Frontend Production Build

From `frontend/`:

```bash
npm run build
```

This performs the configured TypeScript checks and generates
the production frontend assets.

The output is written to:

```text
frontend/dist/
```

### Frontend Linting

Run:

```bash
npm run lint
```

This checks the frontend source code using the project's
configured linter.

## Deployment

System Monitor is deployed using Vercel and Render.

### Frontend — Vercel

The React application is deployed as a static frontend.

Deployment configuration:

| Setting | Value |
|---------|-------|
| Platform | Vercel |
| Framework | Vite |
| Root directory | `frontend` |
| Build command | `npm run build` |
| Output directory | `dist` |

The production frontend communicates with the backend
through a Vercel rewrite.

### Backend — Render

FastAPI is deployed as a Python web service.

Deployment configuration:

| Setting | Value |
|---------|-------|
| Platform | Render |
| Runtime | Python |
| Root directory | `backend` |
| Build command | `pip install .` |

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Production Architecture

```text
                 Internet
                    |
                    v
              Vercel Hosting
              React Frontend
                    |
                    | HTTPS
                    v
               Vercel Rewrite
                    |
                    | HTTPS
                    v
               Render Hosting
               FastAPI Backend
                    |
                    v
             System Monitoring
                    |
                    v
             Cloud Environment
```

### Production API Routing

The frontend uses relative API paths such as:

```text
/api/system/cpu
```

Vercel forwards these requests to the Render backend.

The production rewrite is configured in:

```text
frontend/vercel.json
```

This allows the frontend to use the same API paths
in development and production.

## Cloud Environment Considerations

When deployed to cloud infrastructure, System Monitor collects
information from the environment running the backend.

This may differ from the resources actually allocated
to the application.

For example:

- The CPU model may describe underlying host hardware.
- Reported logical processors may exceed the allocated CPU quota.
- System memory statistics may reflect host-level memory.
- Filesystem capacity may not represent usable application storage.
- System uptime may reflect the host rather than the container.

These differences are normal in virtualized and containerized
environments.

Container-aware resource monitoring may be added in future versions.

## Security

The initial release is intended for local monitoring and
demonstration purposes.

The API currently does not implement user authentication.

Avoid exposing private information or sensitive system details
through publicly accessible endpoints.

The application does not require elevated permissions for
its basic monitoring functionality.

Additional security features may be introduced in future releases,
particularly if support for remote monitoring agents is added.

## Roadmap

### v0.1.0 — Initial Release

- [x] FastAPI backend
- [x] React + TypeScript frontend
- [x] CPU monitoring
- [x] Memory monitoring
- [x] Storage monitoring
- [x] Operating system information
- [x] Pydantic response models
- [x] Automatic metric refreshing
- [x] Responsive dashboard
- [x] Utilization indicators
- [x] Custom application branding
- [x] Backend API tests
- [x] Frontend production build
- [x] Frontend deployment to Vercel
- [x] Backend deployment to Render

### Planned Features

**Performance Visualization**
- CPU utilization history
- Memory utilization history
- Real-time charts
- Per-core CPU utilization

**Hardware Monitoring**
- CPU temperature
- CPU cache information
- GPU utilization
- GPU memory usage
- GPU temperatures
- Multiple storage devices

**System Monitoring**
- Network upload and download speeds
- Process monitoring
- System resource history
- Additional operating system information

**Application Improvements**
- Expanded automated testing
- Improved platform compatibility
- Container-aware resource measurements
- Historical data collection
- Additional dashboard customization

### Long-Term Possibilities

- Multiple system monitoring
- Remote monitoring agents
- Historical performance comparisons
- Secure user authentication
- Hardware monitoring across different operating systems

These features are potential future additions and are not
part of the initial release.

## Project Status

**Current Version:** v0.1.0

**Status:** Initial deployment

System Monitor is a full-stack development project focused on
hardware monitoring, REST API development, and frontend visualization.

The initial release establishes the core monitoring architecture
and provides a foundation for more advanced features.

Development will continue through incremental improvements
and future releases.