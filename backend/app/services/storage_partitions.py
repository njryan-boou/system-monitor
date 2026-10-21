"""Read-only physical-drive partition inventory via Linux util-linux lsblk.

Unlike filesystem utilization, partition layout is visible for unmounted disks.
A separate slow-polled API avoids spawning lsblk every second alongside I/O.
No elevated permissions, partition changes, or shell interpretation are used.
"""

import json
import subprocess

from app.services.storage_devices import physical_disks


LSBLK = [
    "lsblk", "--json", "--bytes",
    "--output", "NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS",
]


def _text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return value.strip() or None


def _size(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _mountpoints(node: dict) -> list[str]:
    points = node.get("mountpoints")
    if not isinstance(points, list):
        points = [node.get("mountpoint")]
    return list(dict.fromkeys(
        point for value in points if (point := _text(value)) is not None
    ))


def _partition_nodes(node: dict) -> list[dict]:
    """Find partition entries in a device tree, including nested layouts."""
    partitions = []
    for child in node.get("children", []) if isinstance(node.get("children"), list) else []:
        if not isinstance(child, dict):
            continue
        if child.get("type") == "part":
            partitions.append(child)
        partitions.extend(_partition_nodes(child))
    return partitions


def parse_lsblk(data: object, disk_names: set[str]) -> dict:
    """Normalize lsblk JSON; never associate partitions with another disk."""
    if not isinstance(data, dict) or not isinstance(data.get("blockdevices"), list):
        return {"available": False, "drives": []}

    by_disk: dict[str, list[dict]] = {name: [] for name in disk_names}
    for node in data["blockdevices"]:
        if not isinstance(node, dict) or node.get("type") != "disk":
            continue
        name = _text(node.get("name"))
        if name not in by_disk:
            continue
        seen: set[str] = set()
        for child in _partition_nodes(node):
            part_name = _text(child.get("name"))
            if part_name is None or part_name in seen:
                continue
            seen.add(part_name)
            by_disk[name].append({
                "name": part_name,
                "device": f"/dev/{part_name}",
                "size_bytes": _size(child.get("size")),
                "filesystem": _text(child.get("fstype")),
                "mountpoints": _mountpoints(child),
            })

    return {
        "available": True,
        "drives": [
            {"disk_id": name, "partitions": by_disk[name]}
            for name in sorted(by_disk)
        ],
    }


def get_storage_partitions() -> dict:
    disks = physical_disks()
    if not disks:
        return {"available": True, "drives": []}
    try:
        result = subprocess.run(
            LSBLK, capture_output=True, text=True, check=False, timeout=3,
        )
        if result.returncode != 0:
            return {"available": False, "drives": []}
        data = json.loads(result.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {"available": False, "drives": []}
    return parse_lsblk(data, set(disks))
