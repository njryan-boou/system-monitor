from functools import lru_cache
from typing import Literal

import pynvml

from app.services.gpu_amd import get_amd_gpu_info


# -----------------------------
# NVIDIA GPU Initialization
# -----------------------------

@lru_cache(maxsize=1)
def get_nvidia_gpu() -> dict | None:
    try:
        pynvml.nvmlInit()

        if pynvml.nvmlDeviceGetCount() == 0:
            return None

        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        name = pynvml.nvmlDeviceGetName(handle)

        if isinstance(name, bytes):
            name = name.decode("utf-8")

        return {
            "handle": handle,
            "name": name
        }

    except pynvml.NVMLError:
        return None


# -----------------------------
# Unavailable GPU Response
# -----------------------------

def unavailable_gpu_info() -> dict:
    return {
        "available": False,
        "name": None,
        "usage": None,
        "memory_used": None,
        "memory_total": None,
        "temperature_c": None
    }


# -----------------------------
# NVIDIA GPU Monitoring
# -----------------------------

def get_nvidia_gpu_info() -> dict:
    gpu = get_nvidia_gpu()

    if gpu is None:
        return unavailable_gpu_info()

    handle = gpu["handle"]

    try:
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        memory = pynvml.nvmlDeviceGetMemoryInfo(handle)

        try:
            temperature = pynvml.nvmlDeviceGetTemperature(
                handle,
                pynvml.NVML_TEMPERATURE_GPU
            )

        except pynvml.NVMLError:
            temperature = None

        return {
            "available": True,
            "name": gpu["name"],
            "usage": utilization.gpu,
            "memory_used": memory.used,
            "memory_total": memory.total,
            "temperature_c": temperature
        }

    except pynvml.NVMLError:
        return unavailable_gpu_info()


# -----------------------------
# GPU Selection
# -----------------------------

def get_gpu_info(
    vendor: Literal["nvidia", "amd"] | None = None
) -> dict:

    # Explicit AMD selection
    if vendor == "amd":
        return get_amd_gpu_info() or unavailable_gpu_info()

    # Check NVIDIA
    nvidia = get_nvidia_gpu_info()

    if vendor == "nvidia":
        return nvidia

    # Prefer NVIDIA when available
    if nvidia["available"]:
        return nvidia

    # Otherwise check AMD
    return get_amd_gpu_info() or unavailable_gpu_info()