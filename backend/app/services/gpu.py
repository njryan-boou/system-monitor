from typing import Literal

from app.services.gpu_nvidia import (
    get_nvidia_gpu_info,
    unavailable_gpu_info
)

from app.services.gpu_amd import get_amd_gpu_info


def get_gpu_info(
    vendor: Literal["nvidia", "amd"] | None = None
) -> dict:

    if vendor == "amd":
        return get_amd_gpu_info() or unavailable_gpu_info()

    nvidia = get_nvidia_gpu_info()

    if vendor == "nvidia" or nvidia["available"]:
        return nvidia

    return get_amd_gpu_info() or unavailable_gpu_info()
