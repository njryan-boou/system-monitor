from functools import lru_cache
from pathlib import Path
from threading import Lock


ENGINES = ("rcs", "ccs", "vcs", "vecs", "bcs")

_sample_lock = Lock()
_previous_sample = None


@lru_cache(maxsize=1)
def get_intel_gpu() -> Path | None:
    for card in sorted(Path("/sys/class/drm").glob("card[0-9]*")):
        if not card.name[4:].isdigit():
            continue

        device = card / "device"

        try:
            vendor = (device / "vendor").read_text().strip()
            driver = (device / "driver").resolve().name

            if vendor == "0x8086" and driver == "xe":
                return device.resolve()
        except OSError:
            continue

    return None


def get_gpu_clients(pci_address: str) -> dict:
    clients = {}

    for fd in Path("/proc").glob("[0-9]*/fdinfo/*"):
        try:
            fields = {}

            for line in fd.read_text().splitlines():
                key, separator, value = line.partition(":")

                if separator:
                    fields[key.strip()] = value.strip()

            if fields.get("drm-driver") != "xe":
                continue

            if fields.get("drm-pdev") != pci_address:
                continue

            client_id = fields.get("drm-client-id")

            if client_id is None or client_id in clients:
                continue

            counters = {}

            for engine in ENGINES:
                try:
                    busy = int(fields[f"drm-cycles-{engine}"])
                    total = int(fields[f"drm-total-cycles-{engine}"])
                    counters[engine] = (busy, total)
                except (KeyError, ValueError):
                    continue

            clients[client_id] = counters

        except (OSError, UnicodeError):
            continue

    return clients


def calculate_peak_activity(previous: dict, current: dict):
    peak = None

    for client_id in previous.keys() & current.keys():
        old_client = previous[client_id]
        new_client = current[client_id]

        for engine in ENGINES:
            if engine not in old_client or engine not in new_client:
                continue

            old_busy, old_total = old_client[engine]
            new_busy, new_total = new_client[engine]

            busy_delta = new_busy - old_busy
            total_delta = new_total - old_total

            if busy_delta < 0 or total_delta <= 0:
                continue

            activity = max(
                0.0,
                min(100.0, 100.0 * busy_delta / total_delta)
            )

            if peak is None or activity > peak:
                peak = activity

    return round(peak, 1) if peak is not None else None


def get_intel_gpu_info() -> dict | None:
    global _previous_sample

    device = get_intel_gpu()

    if device is None:
        return None

    try:
        device_id = (device / "device").read_text().strip().lower()
    except OSError:
        device_id = None

    name = (
        "Intel Lunar Lake Graphics"
        if device_id == "0x64a0"
        else "Intel Graphics"
    )

    with _sample_lock:
        current = get_gpu_clients(device.name)

        usage = (
            calculate_peak_activity(_previous_sample, current)
            if _previous_sample is not None
            else None
        )

        _previous_sample = current

    return {
        "available": True,
        "name": name,
        "usage": usage,
        "usage_label": "Peak Client Engine Activity",
        "memory_used": None,
        "memory_total": None,
        "temperature_c": None,
    }
