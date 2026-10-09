from fastapi import FastAPI
from app.routes.system import router as system_router

app = FastAPI(
    title="System Monitor",
    version="0.1.0"
)

app.include_router(system_router)


@app.get("/")
def root():
    return {"message": "System Monitor API is running"}