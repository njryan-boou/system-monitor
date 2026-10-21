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



def get_cpu_temperature() -> float | None:
    """A CPU/package thermal sensor only; never use GPU or ACPI zone temps."""
    reader = getattr(psutil, "sensors_temperatures", None)
    if reader is None:
        return None
    try:
        chips = reader()
    except (OSError, RuntimeError, NotImplementedError):
        return None

    for chip_name, labels in (
        ("k10temp", ("Tdie", "Tctl")),
        ("coretemp", ("Package id 0",)),
    ):
        sensors = chips.get(chip_name, [])
        for label in labels:
            for sensor in sensors:
                if (sensor.label or "").strip().lower() != label.lower():
                    continue
                value = sensor.current
                if value is not None and -40 <= value <= 150:
                    return round(float(value), 1)
    return None


def get_cpu_load_average() -> float | None:
    """One-minute Linux run-queue load; not a CPU-utilization percentage."""
    try:
        one_min, _, _ = psutil.getloadavg()
    except (OSError, AttributeError, NotImplementedError):
        return None
    return round(float(one_min), 2) if one_min >= 0 else None


def get_cpu_info() -> dict:
    frequency = psutil.cpu_freq()

    return {
        "name": get_cpu_name(),
        "usage": psutil.cpu_percent(interval=None),
        "physical_cores": get_cpu_phys_cores(),
        "logical_cores": get_cpu_log_cores(),
        "frequency_mhz": frequency.current if frequency else None,
        "per_logical_cpu_usage": psutil.cpu_percent(interval=None, percpu=True),
        "temperature_c": get_cpu_temperature(),
        "load_average_1m": get_cpu_load_average(),
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