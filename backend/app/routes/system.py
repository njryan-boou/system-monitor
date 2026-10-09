from fastapi import APIRouter
from app.services.monitor import get_cpu_usage, get_memory_usage

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/cpu")
def cpu_usage():
    return {"usage": get_cpu_usage()}


@router.get("/memory")
def memory_usage():
    return get_memory_usage()