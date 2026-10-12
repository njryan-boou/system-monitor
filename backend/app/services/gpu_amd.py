from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def get_amd_gpu_path() -> Path | None:
    drm = Path("/sys/class/drm")

    for card in sorted(drm.glob("card[0-9]*")):
        if not card.name[4:].isdigit():
            continue

        device = card / "device"

        try:
            vendor = (device / "vendor").read_text().strip()

            if vendor != "0x1002":
                continue

            driver = (device / "driver").resolve().name

            if driver != "amdgpu":
                continue

            return device

        except OSError:
            continue

    return None


def read_int(path: Path) -> int | None:
    try:
        return int(path.read_text().strip())
    except (OSError, ValueError):
        return None


def get_amd_gpu_info() -> dict | None:
    device = get_amd_gpu_path()

    if device is None:
        return None

    usage = read_int(device / "gpu_busy_percent")

    memory_used = read_int(
        device / "mem_info_vram_used"
    )

    memory_total = read_int(
        device / "mem_info_vram_total"
    )

    temperature = None

    sensors = sorted(
        device.glob("hwmon/hwmon*/temp*_input")
    )

    for sensor in sensors:
        value = read_int(sensor)

        if value is not None:
            temperature = round(value / 1000)
            break

    return {
        "available": True,
        "name": "AMD Radeon Graphics",
        "usage": usage,
        "memory_used": memory_used,
        "memory_total": memory_total,
        "temperature_c": temperature
    }