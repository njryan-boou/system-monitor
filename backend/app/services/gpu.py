from functools import lru_cache
import pynvml


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


def get_gpu_info() -> dict:
    gpu = get_nvidia_gpu()

    if gpu is None:
        return {
            "available": False,
            "name": None,
            "usage": None,
            "memory_used": None,
            "memory_total": None,
            "temperature_c": None
        }

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
        return {
            "available": False,
            "name": None,
            "usage": None,
            "memory_used": None,
            "memory_total": None,
            "temperature_c": None
        }