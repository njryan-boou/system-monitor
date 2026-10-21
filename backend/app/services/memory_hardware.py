"""Read-only installed RAM module details from Linux SMBIOS Type 17.

DMI often requires root; do not elevate the running monitoring server.
When unreadable, optionally use a one-time, sanitized local snapshot created
by scripts/capture-memory-hardware.py. Serial/asset tags are never exposed.
"""

import json
from functools import lru_cache
from pathlib import Path

DMI_ROOT = Path("/sys/firmware/dmi/entries")
SNAPSHOT_PATH = Path(__file__).resolve().parents[2] / ".memory-hardware.json"
# SMBIOS memory type identifiers, not CPU generation or memory clock frequency.
MEMORY_TYPES = {
    0x12: "DDR", 0x13: "DDR2", 0x18: "DDR3", 0x1A: "DDR4",
    0x1B: "LPDDR", 0x1C: "LPDDR2", 0x1D: "LPDDR3",
    0x1E: "LPDDR4", 0x1F: "LPDDR4X", 0x22: "DDR5",
    0x23: "LPDDR5",
}


def _u16(raw: bytes, offset: int, limit: int) -> int | None:
    if offset + 2 > limit:
        return None
    return int.from_bytes(raw[offset:offset + 2], "little")


def _u32(raw: bytes, offset: int, limit: int) -> int | None:
    if offset + 4 > limit:
        return None
    return int.from_bytes(raw[offset:offset + 4], "little")


def _smbios_string(raw: bytes, start: int, index: int) -> str | None:
    if not index or start >= len(raw):
        return None
    # The strings are NUL-separated and terminated by an extra NUL.
    strings = raw[start:].split(b"\x00")
    if index > len(strings):
        return None
    value = strings[index - 1].decode("utf-8", errors="replace").strip()
    if not value or value.lower() in ("unknown", "not specified", "not provided", "none", "to be filled by o.e.m."):
        return None
    return value[:100]


def parse_memory_device(raw: bytes) -> dict | None:
    """Parse the populated part of a SMBIOS type-17 record.

    Capacity uses MiB unless high bit denotes KiB; 0x7fff references the
    extended MiB size. SMBIOS transfer speeds are MT/s, not MHz.
    """
    if len(raw) < 0x17 or raw[0] != 17:
        return None
    length = raw[1]
    if length < 0x17 or length > len(raw):
        return None
    size = _u16(raw, 0x0C, length)
    if size in (None, 0, 0xFFFF):  # Empty slot or unspecified size.
        return None
    if size == 0x7FFF:
        size_mb = _u32(raw, 0x1C, length)
        if size_mb in (None, 0, 0xFFFFFFFF):
            return None
        capacity_bytes = size_mb * 1024 ** 2
    elif size & 0x8000:
        capacity_bytes = (size & 0x7FFF) * 1024
    else:
        capacity_bytes = size * 1024 ** 2

    # 0x20 is configured memory speed (SMBIOS 3.1); 0x15 is max rated speed.
    configured_speed = _u16(raw, 0x20, length)
    rated_speed = _u16(raw, 0x15, length)
    speed = next((n for n in (configured_speed, rated_speed) if n not in (None, 0, 0xFFFF)), None)
    type_code = raw[0x12] if length > 0x12 else 0
    return {
        "slot": _smbios_string(raw, length, raw[0x10] if length > 0x10 else 0),
        "capacity_bytes": capacity_bytes,
        "memory_type": MEMORY_TYPES.get(type_code),
        "speed_mtps": speed,
        "manufacturer": _smbios_string(raw, length, raw[0x17] if length > 0x17 else 0),
    }


def read_dmi_memory_modules(root: Path = DMI_ROOT) -> list[dict] | None:
    """None means inaccessible, [] means records exist but no populated slots."""
    try:
        entries = sorted(root.glob("17-*/raw"))
    except OSError:
        return None
    if not entries:
        return None
    modules = []
    readable = False
    for entry in entries:
        try:
            raw = entry.read_bytes()
        except OSError:
            continue
        readable = True
        module = parse_memory_device(raw)
        if module is not None:
            modules.append(module)
    return modules if readable else None


def summarize_modules(modules: list[dict], source: str) -> dict:
    types = {item["memory_type"] for item in modules if item.get("memory_type")}
    speeds = {item["speed_mtps"] for item in modules if item.get("speed_mtps") is not None}
    return {
        "memory_type": next(iter(types)) if len(types) == 1 else "Mixed" if types else None,
        "memory_speed_mtps": next(iter(speeds)) if len(speeds) == 1 else None,
        "memory_module_count": len(modules),
        "memory_modules": modules,
        "memory_hardware_source": source,
    }


def unavailable() -> dict:
    return {
        "memory_type": None, "memory_speed_mtps": None,
        "memory_module_count": None, "memory_modules": [],
        "memory_hardware_source": None,
    }


@lru_cache(maxsize=1)
def get_memory_hardware() -> dict:
    # Read live SMBIOS first if Linux exposes it to the unprivileged process.
    modules = read_dmi_memory_modules()
    if modules is not None:
        return summarize_modules(modules, "smbios")

    # A local, sanitized snapshot may be created once via an optional script.
    # This file contains no serials, asset tags, or raw DMI bytes.
    try:
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return unavailable()
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("memory_modules"), list):
        return unavailable()
    modules = snapshot["memory_modules"]
    if not all(
        isinstance(m, dict) and isinstance(m.get("capacity_bytes"), int)
        and m["capacity_bytes"] > 0 and
        all(m.get(key) is None or isinstance(m.get(key), str) for key in ("slot", "memory_type", "manufacturer"))
        and (m.get("speed_mtps") is None or isinstance(m.get("speed_mtps"), int))
        for m in modules
    ):
        return unavailable()
    # Only project the allowlisted fields; ignore unknown keys in the file.
    safe_modules = [
        {key: m.get(key) for key in ("slot", "capacity_bytes", "memory_type", "speed_mtps", "manufacturer")}
        for m in modules
    ]
    return summarize_modules(safe_modules, "snapshot")
