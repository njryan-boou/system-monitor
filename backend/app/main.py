import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.system import router as system_router


app = FastAPI(
    title="System Monitor",
    version="0.1.0"
)

# Register API endpoints
app.include_router(system_router)


@app.get("/api/health")
def health():
    return {"message": "System Monitor API is running"}


# Locate the React production build
if getattr(sys, "frozen", False):
    # Running as a PyInstaller executable
    FRONTEND_DIST = Path(sys._MEIPASS) / "frontend" / "dist"
else:
    # Running from the source repository
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


# Serve the frontend when available
if (FRONTEND_DIST / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIST, html=True),
        name="frontend"
    )
else:
    @app.get("/")
    def root():
        return {"message": "Frontend not built. API is running."}