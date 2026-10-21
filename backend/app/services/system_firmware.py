"""Read-only Linux motherboard and BIOS/UEFI metadata from DMI sysfs.

Only non-unique firmware identity fields are read. Do not expose DMI serial
numbers, UUIDs, asset tags, or run the monitoring process as root.
"""

import os
import platform
from functools import lru_cache
from pathlib import Path

DMI_ROOT = Path("/sys/class/dmi/id")
FIRMWARE_ROOT = Path("/sys/firmware")
IGNORED_VALUES = {
    "unknown",
    "none",
    "not specified",
    "not available",
    "not applicable",
    "default string",
    "to be filled by o.e.m.",
    "to be filled by oem",
    "system product name",
    "base board product name",
    "invalid",
}


def read_dmi_field(path: Path) -> str | None:
    """Read public DMI fields; fail closed when restricted or meaningless."""
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError, ValueError):
        return None
    if not value or value.casefold() in IGNORED_VALUES:
        return None
    return value[:160]


def _inside_container() -> bool:
    """Sysfs may hide EFI in containers; don't mislabel them Legacy."""
    return bool(
        os.environ.get("container")
        or Path("/.dockerenv").exists()
        or Path("/run/.containerenv").exists()
    )


def read_system_firmware(
    dmi_root: Path = DMI_ROOT,
    firmware_root: Path = FIRMWARE_ROOT,
    os_name: str | None = None,
    containerized: bool | None = None,
) -> dict:
    """Discover actual firmware fields; missing values stay unavailable."""
    result = {
        "motherboard_manufacturer": None,
        "motherboard_model": None,
        "motherboard_version": None,
        "bios_vendor": None,
        "bios_version": None,
        "bios_release_date": None,
        "boot_mode": None,
    }
    if (os_name if os_name is not None else platform.system()) != "Linux":
        return result

    fields = {
        "motherboard_manufacturer": "board_vendor",
        "motherboard_model": "board_name",
        "motherboard_version": "board_version",
        "bios_vendor": "bios_vendor",
        "bios_version": "bios_version",
        "bios_release_date": "bios_date",
    }
    for key, name in fields.items():
        result[key] = read_dmi_field(dmi_root / name)

    # The EFI sysfs directory is positive evidence of UEFI boot.
    # Its absence can mean a legacy boot OR masked sysfs, particularly in
    # containers; only call it Legacy on a non-containerized Linux host.
    if (firmware_root / "efi").is_dir():
        result["boot_mode"] = "UEFI"
    elif firmware_root.is_dir() and not (
        containerized if containerized is not None else _inside_container()
    ):
        result["boot_mode"] = "Legacy"
    return result


@lru_cache(maxsize=1)
def get_system_firmware() -> dict:
    """Static host metadata: do not reread sysfs on each five-second poll."""
    return read_system_firmware()
