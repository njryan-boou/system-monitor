from fastapi import APIRouter

from typing import Literal

from app.services.monitor import (
    get_cpu_info,
    get_memory_usage,
    get_storage_info,
    get_system_info,
    get_network_info
)

from app.services.gpu import get_gpu_info, get_gpu_infos

from app.schemas.system import (
    CPUResponse,
    MemoryResponse,
    StorageResponse,
    SystemResponse,
    NetworkResponse,
    GPUResponse,
    GPUDeviceResponse
)


router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/cpu", response_model=CPUResponse)
def cpu_info():
    return get_cpu_info()


@router.get("/memory", response_model=MemoryResponse)
def memory_usage():
    return get_memory_usage()


@router.get("/storage", response_model=StorageResponse)
def storage_info():
    return get_storage_info()


@router.get("/info", response_model=SystemResponse)
def system_info():
    return get_system_info()


@router.get("/network", response_model=NetworkResponse)
def network_info():
    return get_network_info()


@router.get("/gpu", response_model=GPUResponse)
def gpu_info(
    vendor: Literal["nvidia", "amd", "intel"] | None = None
):
    return get_gpu_info(vendor)

@router.get("/gpus", response_model=list[GPUDeviceResponse])
def gpu_devices():
    return get_gpu_infos()
