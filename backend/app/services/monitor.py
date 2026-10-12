from pathlib import Path
import psutil
import platform
import time
from functools import lru_cache
from cpuinfo import get_cpu_info as get_cpu_details


@lru_cache(maxsize=1)
def get_cpu_name() -> str | None:
    return get_cpu_details().get("brand_raw")


@lru_cache(maxsize=1)
def get_cpu_phys_cores() -> int | None:
    return psutil.cpu_count(logical=False)


@lru_cache(maxsize=1)
def get_cpu_log_cores() -> int | None:
    return psutil.cpu_count(logical=True)


def get_cpu_info() -> dict:
    frequency = psutil.cpu_freq()

    return {
        "name": get_cpu_name(),
        "usage": psutil.cpu_percent(interval=None),
        "physical_cores": get_cpu_phys_cores(),
        "logical_cores": get_cpu_log_cores(),
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
    
    
def get_network_info() -> dict:
    network = psutil.net_io_counters()

    if network is None:
        raise RuntimeError("Network statistics unavailable")

    return {
        "bytes_sent": network.bytes_sent,
        "bytes_recv": network.bytes_recv
    }