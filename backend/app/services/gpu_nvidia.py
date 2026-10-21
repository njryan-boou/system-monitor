"""NVIDIA GPU telemetry through NVML."""

from functools import lru_cache

import pynvml


@lru_cache(maxsize=1)
def get_nvidia_gpu_count() -> int:
    try:
        pynvml.nvmlInit()
        return pynvml.nvmlDeviceGetCount()
    except pynvml.NVMLError:
        return 0


@lru_cache(maxsize=None)
def get_nvidia_gpu(index: int = 0) -> dict | None:
    if not 0 <= index < get_nvidia_gpu_count():
        return None

    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(index)
        name = pynvml.nvmlDeviceGetName(handle)
        if isinstance(name, bytes):
            name = name.decode("utf-8")

        return {"handle": handle, "name": name}
    except pynvml.NVMLError:
        return None


def unavailable_gpu_info() -> dict:
    return {
        "available": False,
        "name": None,
        "usage": None,
        "memory_used": None,
        "memory_total": None,
        "temperature_c": None,
    }


def get_nvidia_gpu_info(index: int = 0) -> dict:
    gpu = get_nvidia_gpu(index)
    if gpu is None:
        return unavailable_gpu_info()

    try:
        handle = gpu["handle"]
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        memory = pynvml.nvmlDeviceGetMemoryInfo(handle)

        try:
            temperature = pynvml.nvmlDeviceGetTemperature(
                handle, pynvml.NVML_TEMPERATURE_GPU
            )
        except pynvml.NVMLError:
            temperature = None

        def optional_nvml(call):
            try:
                return call()
            except (pynvml.NVMLError, AttributeError):
                return None

        clock = optional_nvml(lambda: pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS))
        max_clock = optional_nvml(lambda: pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS))
        power_mw = optional_nvml(lambda: pynvml.nvmlDeviceGetPowerUsage(handle))

        return {
            "clock_mhz": clock,
            "max_clock_mhz": max_clock,
            "power_watts": round(power_mw / 1000, 2) if power_mw is not None else None,
            "available": True,
            "name": gpu["name"],
            "gpu_type": "dedicated" if gpu["name"].lower().startswith(("nvidia geforce rtx 5060", "nvidia geforce")) else None,
            "usage": utilization.gpu,
            "memory_used": memory.used,
            "memory_total": memory.total,
            "temperature_c": temperature,
        }
    except pynvml.NVMLError:
        return unavailable_gpu_info()


def get_nvidia_gpu_infos() -> list[tuple[str, dict]]:
    """Enumerate all NVIDIA adapters, keeping indices stable."""
    devices = []
    for index in range(get_nvidia_gpu_count()):
        info = get_nvidia_gpu_info(index)
        if info["available"]:
            devices.append((f"nvidia:{index}", info))
    return devices
