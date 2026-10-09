import psutil


def get_cpu_usage() -> float:
    return psutil.cpu_percent(interval=1)


def get_memory_usage() -> dict:
    memory = psutil.virtual_memory()

    return {
        "total": memory.total,
        "used": memory.used,
        "available": memory.available,
        "percent": memory.percent
    }