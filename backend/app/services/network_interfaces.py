"""Linux network interface telemetry with per-interface rate sampling.

Cumulative counters are not speeds; speeds and packets/s require two samples.
The aggregate intentionally includes loopback, like the existing /network API.
"""

from pathlib import Path
from threading import Lock
from time import monotonic
from types import SimpleNamespace

import psutil

SYS_NET = Path("/sys/class/net")
_FIELDS = ("bytes_recv", "bytes_sent", "packets_recv", "packets_sent")
_SAMPLES: dict[str, tuple[tuple[int, ...], float]] = {}
_SAMPLE_LOCK = Lock()


def interface_type(name: str, sys_net: Path = SYS_NET) -> str:
    """Classify with sysfs where possible; avoid guessing by device name."""
    path = sys_net / name
    if (path / "wireless").exists() or (path / "phy80211").exists():
        return "Wi-Fi"
    if (path / "device").exists():
        return "Ethernet"
    if path.exists():
        return "Virtual"
    return "Other"


def sample_rates(counters: dict, timestamp: float) -> dict[str, dict]:
    """Compute nonnegative deltas against the preceding successful sample."""
    rates = {}
    with _SAMPLE_LOCK:
        for name, item in counters.items():
            values = tuple(int(getattr(item, field, 0)) for field in _FIELDS)
            previous = _SAMPLES.get(name)
            _SAMPLES[name] = (values, timestamp)
            result = {
                "ready": False,
                "download_bytes_per_sec": None,
                "upload_bytes_per_sec": None,
                "download_packets_per_sec": None,
                "upload_packets_per_sec": None,
            }
            if previous is not None:
                last_values, last_time = previous
                elapsed = timestamp - last_time
                differences = [now - last for now, last in zip(values, last_values)]
                if elapsed > 0 and all(d >= 0 for d in differences):
                    result.update({
                        "ready": True,
                        "download_bytes_per_sec": round(differences[0] / elapsed, 2),
                        "upload_bytes_per_sec": round(differences[1] / elapsed, 2),
                        "download_packets_per_sec": round(differences[2] / elapsed, 2),
                        "upload_packets_per_sec": round(differences[3] / elapsed, 2),
                    })
            rates[name] = result

        # A reconnected interface must warm up again if it was absent.
        for name in list(_SAMPLES):
            if name not in counters:
                del _SAMPLES[name]
    return rates


def _totals(counter) -> dict:
    return {
        "bytes_recv": counter.bytes_recv,
        "bytes_sent": counter.bytes_sent,
        "packets_recv": counter.packets_recv,
        "packets_sent": counter.packets_sent,
        "errors_recv": counter.errin,
        "errors_sent": counter.errout,
        "drops_recv": counter.dropin,
        "drops_sent": counter.dropout,
    }


def get_network_interfaces() -> list[dict]:
    try:
        counters = psutil.net_io_counters(pernic=True) or {}
    except (OSError, RuntimeError):
        return []
    if not counters:
        return []

    try:
        statuses = psutil.net_if_stats()
    except (OSError, RuntimeError):
        statuses = {}

    # The aggregate uses all NIC counters (including loopback) for compatibility.
    total = SimpleNamespace(**{
        key: sum(getattr(value, key, 0) for value in counters.values())
        for key in (*_FIELDS, "errin", "errout", "dropin", "dropout")
    })
    all_counters = {"all": total, **{name: value for name, value in counters.items() if name != "lo" and name != "all"}}
    rates = sample_rates(all_counters, monotonic())
    devices = [{
        "id": "all",
        "name": "All Interfaces",
        "interface_type": "Aggregate",
        "is_up": None,
        "speed_mbps": None,
        "mtu": None,
        **_totals(total),
        **rates["all"],
    }]

    # List active hardware links first, then other interfaces (VPNs, bridges).
    names = [name for name in counters if name not in ("lo", "all")]
    names.sort(key=lambda name: (
        not bool(getattr(statuses.get(name), "isup", False)),
        interface_type(name) in ("Virtual", "Other"),
        name,
    ))
    for name in names:
        stat = statuses.get(name)
        speed = getattr(stat, "speed", None)
        devices.append({
            "id": name,
            "name": name,
            "interface_type": interface_type(name),
            "is_up": getattr(stat, "isup", None),
            "speed_mbps": speed if speed is not None and speed > 0 else None,
            "mtu": getattr(stat, "mtu", None),
            **_totals(counters[name]),
            **rates[name],
        })
    return devices
