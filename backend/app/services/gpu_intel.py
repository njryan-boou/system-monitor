from functools import lru_cache
from pathlib import Path
from threading import Lock
from time import monotonic


_sample_lock = Lock()
_previous_sample = None


@lru_cache(maxsize=1)
def get_intel_gpu() -> tuple[Path, Path] | None:
    drm = Path("/sys/class/drm")

    for card in sorted(drm.glob("card[0-9]*")):
        if not card.name[4:].isdigit():
            continue

        device = card / "device"

        try:
            vendor = (device / "vendor").read_text().strip()
            driver = (device / "driver").resolve().name

            if vendor != "0x8086" or driver != "xe":
                continue

            # Prefer the render GT (gt0).
            counters = sorted(
                device.glob("tile*/gt0/gtidle/idle_residency_ms")
            )

            if not counters:
                continue

            return device, counters[0]

        except OSError:
            continue

    return None


def read_int(path: Path) -> int | None:
    try:
        return int(path.read_text().strip())
    except (OSError, ValueError):
        return None


def get_intel_gpu_info() -> dict | None:
    global _previous_sample

    gpu = get_intel_gpu()

    if gpu is None:
        return None

    device, counter = gpu

    try:
        device_id = (device / "device").read_text().strip().lower()
    except OSError:
        device_id = None

    name = (
        "Intel Lunar Lake Graphics"
        if device_id == "0x64a0"
        else "Intel Graphics"
    )

    usage = None

    with _sample_lock:
        idle_ms = read_int(counter)
        now = monotonic()

        if idle_ms is not None:
            if _previous_sample is not None:
                previous_time, previous_idle = _previous_sample

                elapsed_ms = (now - previous_time) * 1000
                idle_delta = idle_ms - previous_idle

                if (
                    elapsed_ms >= 250
                    and 0 <= idle_delta <= elapsed_ms * 1.1
                ):
                    usage = round(
                        max(
                            0.0,
                            min(
                                100.0,
                                100.0 * (
                                    1 - idle_delta / elapsed_ms
                                )
                            )
                        ),
                        1
                    )

            _previous_sample = (now, idle_ms)

    return {
        "available": True,
        "name": name,
        "usage": usage,
        "usage_label": "Render GT non-idle (estimate)",
        "memory_used": None,
        "memory_total": None,
        "temperature_c": None
    }
