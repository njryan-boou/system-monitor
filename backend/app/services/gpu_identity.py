"""Best-effort, non-misleading identification of Linux PCI graphics devices.

Known PCI IDs identify architectures where the marketed GPU is established.
Other cards may expose a model through pciutils; absence of that utility is
not fatal. Never derive integrated/dedicated from PCI bus placement or VRAM.
"""

from functools import lru_cache
from pathlib import Path
import re
import shlex
import subprocess
from typing import Literal

GPUType = Literal["integrated", "dedicated"]

# Verified for the supported machines. PCI IDs do not identify every SKU.
KNOWN_AMD = {
    "0x13c0": ("AMD Radeon 610M", "integrated"),
}
KNOWN_INTEL = {
    "0x64a0": ("Intel Lunar Lake Graphics", "integrated"),
}


def read_device_id(device: Path) -> str | None:
    try:
        return device.joinpath("device").read_text().strip().lower()
    except OSError:
        return None


@lru_cache(maxsize=128)
def pci_marketing_name(pci_address: str, vendor: Literal["amd", "intel"]) -> str | None:
    """Look up the chipset description once, without spawning processes per poll."""
    try:
        result = subprocess.run(
            ["lspci", "-mm", "-s", pci_address],
            capture_output=True, text=True, timeout=2, check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        parts = shlex.split(result.stdout.splitlines()[0])
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired, ValueError):
        return None

    if len(parts) < 4:
        return None

    description = parts[3]
    if vendor == "amd":
        # E.g. 'Navi 31 [Radeon RX 7900 XTX]'
        match = re.search(r"\[(Radeon[^\]]+)\]", description, flags=re.I)
        if match:
            return f"AMD {match.group(1)}"
        if description.lower().startswith("radeon"):
            return f"AMD {description}"
    else:
        # E.g. 'Raptor Lake-P [Iris Xe Graphics]'
        match = re.search(r"\[((?:Intel )?(?:Arc|Iris)[^\]]+)\]", description, flags=re.I)
        if match:
            model = match.group(1)
            return model if model.lower().startswith("intel ") else f"Intel {model}"
    return None


def identify_gpu(
    vendor: Literal["amd", "intel"], device: Path
) -> tuple[str, GPUType | None]:
    """Return a display name and type, or None when type is unproven."""
    device_id = read_device_id(device)
    known = KNOWN_AMD if vendor == "amd" else KNOWN_INTEL
    if device_id in known:
        name, gpu_type = known[device_id]
        return name, gpu_type

    model = pci_marketing_name(device.resolve().name, vendor)
    if model:
        return model, None

    return ("AMD Radeon Graphics" if vendor == "amd" else "Intel Graphics"), None
