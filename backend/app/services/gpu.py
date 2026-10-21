from typing import Literal

from app.services.gpu_nvidia import get_nvidia_gpu_info, get_nvidia_gpu_infos, unavailable_gpu_info
from app.services.gpu_amd import get_amd_gpu_info
from app.services.gpu_intel import get_intel_gpu_info


def get_gpu_info(vendor: Literal["nvidia", "amd", "intel"] | None = None) -> dict:
    if vendor == "nvidia":
        return get_nvidia_gpu_info()
    if vendor == "amd":
        return get_amd_gpu_info() or unavailable_gpu_info()
    if vendor == "intel":
        return get_intel_gpu_info() or unavailable_gpu_info()

    nvidia = get_nvidia_gpu_info()
    if nvidia["available"]:
        return nvidia
    return get_amd_gpu_info() or get_intel_gpu_info() or unavailable_gpu_info()


def get_gpu_infos() -> list[dict]:
    """All detected GPU adapters with stable IDs for the UI."""
    found = []
    for device_id, info in get_nvidia_gpu_infos():
        found.append({"id": device_id, "vendor": "nvidia", **info})

    amd = get_amd_gpu_info()
    if amd is not None:
        found.append({"id": "amd:0", "vendor": "amd", **amd})

    intel = get_intel_gpu_info()
    if intel is not None:
        found.append({"id": "intel:0", "vendor": "intel", **intel})

    return found
