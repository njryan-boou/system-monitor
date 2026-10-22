"""Discover NVIDIA GPUs driven by Nouveau without relying on NVML.

PCI/DRM device presence is independent from availability of GPU telemetry.
Unsupported metrics must remain None, never a fabricated zero.
"""

from functools import lru_cache
from pathlib import Path
import re
import shlex
import subprocess


DRM_ROOT = Path("/sys/class/drm")


@lru_cache(maxsize=128)
def _pci_gpu_name(pci_address: str) -> str | None:
    """Resolve a marketing name via pciutils, without running it every poll."""
    try:
        result = subprocess.run(
            ["lspci", "-mm", "-s", pci_address],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        fields = shlex.split(result.stdout.splitlines()[0])
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired, ValueError):
        return None

    if len(fields) < 4:
        return None

    description = fields[3]
    match = re.search(r"\[([^\]]+)\]", description)
    model = match.group(1) if match else description
    if not model:
        return None
    return model if model.lower().startswith("nvidia ") else f"NVIDIA {model}"


def _temperature_c(device: Path) -> int | None:
    """Read only sensors belonging to this GPU, when Nouveau exposes them."""
    for sensor in sorted(device.glob("hwmon/hwmon*/temp*_input")):
        try:
            millidegrees = int(sensor.read_text().strip())
        except (OSError, ValueError):
            continue
        if -40000 <= millidegrees <= 150000:
            return round(millidegrees / 1000)
    return None


def get_nouveau_gpu_infos(drm_root: Path = DRM_ROOT) -> list[tuple[str, dict]]:
    """List each Nouveau-backed PCI NVIDIA adapter once, with stable PCI IDs."""
    devices = []
    seen_addresses: set[str] = set()

    for card in sorted(drm_root.glob("card[0-9]*")):
        if not card.name[4:].isdigit():
            continue

        device = card / "device"
        try:
            if (device / "vendor").read_text().strip().lower() != "0x10de":
                continue
            if (device / "driver").resolve().name != "nouveau":
                continue
            pci_address = device.resolve().name
        except OSError:
            continue

        if pci_address in seen_addresses:
            continue
        seen_addresses.add(pci_address)

        name = _pci_gpu_name(pci_address) or f"NVIDIA GPU ({pci_address})"
        devices.append((
            f"nvidia:pci:{pci_address}",
            {
                "available": True,
                "name": name,
                "gpu_type": "dedicated" if "GeForce" in name else None,
                "usage": None,
                "memory_used": None,
                "memory_total": None,
                "temperature_c": _temperature_c(device),
                "clock_mhz": None,
                "max_clock_mhz": None,
                "memory_clock_mhz": None,
                "power_watts": None,
            },
        ))

    return devices
