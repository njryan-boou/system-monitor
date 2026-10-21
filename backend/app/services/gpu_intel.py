"""Intel Xe telemetry from per-client DRM file descriptor counters.

The reported value is the *peak accessible client/engine activity*, not
whole-device utilization. Integrated GPU memory is shared with system RAM;
no reliable per-GPU memory totals are exposed through these counters.
"""

from functools import lru_cache
from pathlib import Path
from threading import Lock

from app.services.gpu_identity import identify_gpu


DRM_ROOT = Path("/sys/class/drm")
PROC_ROOT = Path("/proc")
ENGINES = ("rcs", "ccs", "vcs", "vecs", "bcs")

_sample_lock = Lock()
_previous_sample: dict | None = None


@lru_cache(maxsize=1)
def get_intel_gpu_path() -> Path | None:
    for card in sorted(DRM_ROOT.glob("card*")):
        if not card.name.startswith("card") or not card.name[4:].isdigit():
            continue

        device = card / "device"
        try:
            if (device / "vendor").read_text().strip() != "0x8086":
                continue
            if (device / "driver").resolve().name != "xe":
                continue
            return device.resolve()
        except OSError:
            continue

    return None


def get_gpu_clients(pci_address: str, proc_root: Path = PROC_ROOT) -> dict:
    """Read each accessible Xe DRM client once, even if it has many FDs."""
    clients = {}

    for fdinfo in proc_root.glob("[0-9]*/fdinfo/*"):
        try:
            fields = {}
            for line in fdinfo.read_text().splitlines():
                key, separator, value = line.partition(":")
                if separator:
                    fields[key.strip()] = value.strip()

            if fields.get("drm-driver") != "xe":
                continue
            if fields.get("drm-pdev") != pci_address:
                continue

            client_id = fields.get("drm-client-id")
            if not client_id or client_id in clients:
                continue

            counters = {}
            for engine in ENGINES:
                try:
                    busy = int(fields[f"drm-cycles-{engine}"])
                    total = int(fields[f"drm-total-cycles-{engine}"])
                except (KeyError, ValueError):
                    continue
                if busy >= 0 and total >= 0:
                    counters[engine] = (busy, total)

            if counters:
                clients[client_id] = counters
        except (OSError, UnicodeError):
            # Other users' processes and closing FDs may be unreadable.
            continue

    return clients


def calculate_peak_activity(previous: dict, current: dict) -> float | None:
    """Percent busy for the busiest comparable client/engine pair."""
    peak = None

    for client_id in previous.keys() & current.keys():
        for engine in ENGINES:
            old = previous[client_id].get(engine)
            new = current[client_id].get(engine)
            if old is None or new is None:
                continue

            busy_delta = new[0] - old[0]
            total_delta = new[1] - old[1]
            if busy_delta < 0 or total_delta <= 0:
                continue

            # Concurrent contexts can make aggregated cycle counts exceed
            # the reference cycle count; keep the displayed scale 0-100%.
            percent = max(0.0, min(100.0, 100.0 * busy_delta / total_delta))
            peak = percent if peak is None else max(peak, percent)

    return round(peak, 1) if peak is not None else None


def read_temperature(device: Path) -> int | None:
    """Read only sensors attached to the Intel GPU device, if available."""
    for sensor in sorted(device.glob("hwmon/hwmon*/temp*_input")):
        try:
            millidegrees = int(sensor.read_text().strip())
            if -40000 <= millidegrees <= 150000:
                return round(millidegrees / 1000)
        except (OSError, ValueError):
            continue
    return None


def get_intel_gpu_info() -> dict | None:
    global _previous_sample

    device = get_intel_gpu_path()
    if device is None:
        return None

    name, gpu_type = identify_gpu("intel", device)

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
        "gpu_type": gpu_type,
        "usage": usage,
        "usage_label": "Peak Client Engine Activity",
        "memory_used": None,
        "memory_total": None,
        "temperature_c": read_temperature(device),
    }
