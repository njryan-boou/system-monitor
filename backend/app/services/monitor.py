from pathlib import Path
import psutil
import platform
import time
from functools import lru_cache
from cpuinfo import get_cpu_info as get_cpu_details


@lru_cache(maxsize=1)
def get_cpu_name() -> str | None:
    return get_cpu_details().get("brand_raw")


def get_cpu_info() -> dict:
    frequency = psutil.cpu_freq()
    cpu = get_cpu_details()

    return {
        "name": get_cpu_name(),
        "usage": psutil.cpu_percent(interval=1),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "frequency_mhz": frequency.current if frequency else None
    }


def get_memory_usage() -> dict:
    memory = psutil.virtual_memory()

    return {
        "total": memory.total,
        "used": memory.used,
        "available": memory.available,
        "percent": memory.percent
    }


def get_storage_info() -> dict:
    path = Path.home().anchor
    storage = psutil.disk_usage(path)

    return {
        "volume": path,
        "total": storage.total,
        "used": storage.used,
        "free": storage.free,
        "percent": storage.percent
    }


def get_system_info() -> dict:
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "uptime": int(time.time() - psutil.boot_time())
    }