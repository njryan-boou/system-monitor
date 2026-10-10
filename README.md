# System Monitor

A lightweight, browser-based hardware monitoring application built with React, TypeScript, Python, and FastAPI.

System Monitor provides a dashboard for viewing real-time CPU, memory, storage, and operating system information.

The application uses Python to collect system metrics and exposes them through a REST API, which a React frontend uses to display hardware information.

## Features

### CPU Monitoring
- Processor model
- CPU utilization
- Physical core count
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

### Dashboard
- Automatically refreshing hardware information
- CPU, RAM, and storage utilization bars
- Responsive layout
- Dark-themed interface

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | React, TypeScript |
| Styling | CSS |
| Build Tool | Vite |
| Backend | Python, FastAPI |
| Web Server | Uvicorn |
| Data Validation | Pydantic |
| Hardware Monitoring | psutil, py-cpuinfo |

## Project Structure

```text
system-monitor/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CPUCard.tsx
│   │   │   ├── MemoryCard.tsx
│   │   │   ├── DiskCard.tsx
│   │   │   └── SystemCard.tsx
│   │   │
│   │   ├── pages/
│   │   │   └── Dashboard.tsx
│   │   │
│   │   ├── services/
│   │   │   └── api.ts
│   │   │
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── system.py
│   │   │
│   │   ├── schemas/
│   │   │   └── system.py
│   │   │
│   │   ├── services/
│   │   │   └── monitor.py
│   │   │
│   │   └── main.py
│   │
│   └── pyproject.toml
│
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.10 or newer
- Node.js and npm
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd system-monitor
```

Replace `<repository-url>` with the GitHub repository URL.

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

Install the required dependencies:

```bash
python -m pip install -e .
```

### 3. Frontend Setup

From the project root, navigate to the frontend:

```bash
cd frontend
```

Install the dependencies:

```bash
npm install
```

## Running the Application

The frontend and backend run as separate development servers.

### Start the Backend

From the `backend/` directory:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

The API will be available at:

http://localhost:8000

Interactive API documentation:

http://localhost:8000/docs

### Start the Frontend

Open another terminal and navigate to `frontend/`:

```bash
npm run dev
```

Open the application at:

http://localhost:5173

The Vite development server forwards `/api` requests to the FastAPI backend.

Both servers must be running for the dashboard to retrieve system information.

## API Endpoints

The backend exposes the following REST endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/system/cpu` | CPU information |
| GET | `/api/system/memory` | Memory information |
| GET | `/api/system/storage` | Storage information |
| GET | `/api/system/info` | Operating system information |

### Example Response

Request:

```http
GET /api/system/cpu
```

Example JSON response:

```json
{
    "name": "AMD Ryzen 9 9950X 16-Core Processor",
    "usage": 15.5,
    "physical_cores": 16,
    "logical_cores": 32,
    "frequency_mhz": 2400.0
}
```

Values depend on the system being monitored.

## How It Works

System Monitor uses a client-server architecture.

```text
Operating System
       |
       v
Python Monitoring Service
       |
       | psutil / py-cpuinfo
       v
FastAPI Backend
       |
       | HTTP / JSON
       v
React Frontend
       |
       v
Web Dashboard
```

The Python backend collects information from the operating system.

FastAPI exposes the collected metrics through HTTP endpoints.

The React frontend periodically requests updated information and displays the results in the dashboard.

### Monitoring Behavior

The application monitors the computer running the Python backend.

For example, if FastAPI runs on an Ubuntu desktop, the dashboard displays that desktop's hardware information regardless of which device opens the website.

Some metrics may be unavailable depending on operating system, hardware, permissions, or virtualization.

## Development

### Frontend Production Build

From `frontend/`:

```bash
npm run build
```

The generated production files are placed in:

```text
frontend/dist/
```

### API Documentation

FastAPI automatically generates interactive API documentation using OpenAPI.

While the backend is running, visit:

http://localhost:8000/docs

## Roadmap

### v0.1.0 — Initial Release
- [x] CPU monitoring
- [x] Memory monitoring
- [x] Storage monitoring
- [x] System information
- [x] FastAPI REST endpoints
- [x] React dashboard
- [x] Utilization indicators
- [ ] Final testing
- [ ] Initial deployment

### Future Development
- CPU and RAM usage history graphs
- Network monitoring
- GPU monitoring
- CPU temperature monitoring
- Per-core utilization
- Advanced hardware information
- Multiple storage device support
- Improved error handling

## Platform Compatibility

The application uses cross-platform Python libraries to support different operating systems.

Primary development environment: Linux.

The monitoring backend is designed to support Windows, Linux, and macOS where the required hardware metrics are available.

Not all hardware information is exposed consistently across operating systems.

## Security

System Monitor is intended for local development and monitoring.

The application does not currently provide authentication.

Avoid exposing the monitoring API directly to the public internet without implementing appropriate access controls.

## Project Status

**Version:** 0.1.0 (in development)

The initial implementation focuses on basic system monitoring and establishing a functional full-stack architecture.

Additional monitoring capabilities and improvements are planned for future releases.