from typing import Literal

from app.services.gpu_nvidia import (
    get_nvidia_gpu_info,
    unavailable_gpu_info
)

from app.services.gpu_amd import get_amd_gpu_info
from app.services.gpu_intel import get_intel_gpu_info


def get_gpu_info(
    vendor: Literal["nvidia", "amd", "intel"] | None = None
) -> dict:

    if vendor == "nvidia":
        return get_nvidia_gpu_info()

    if vendor == "amd":
        return get_amd_gpu_info() or unavailable_gpu_info()

    if vendor == "intel":
        return get_intel_gpu_info() or unavailable_gpu_info()

    # Automatic GPU selection
    nvidia = get_nvidia_gpu_info()

    if nvidia["available"]:
        return nvidia

    amd = get_amd_gpu_info()

    if amd is not None:
        return amd

    intel = get_intel_gpu_info()

    if intel is not None:
        return intel

    return unavailable_gpu_info()
