"""Linux block-drive monitoring.

Capacity is the physical drive size; mounted filesystem usage belongs to a
specific volume, not the entire drive. I/O counters are for whole devices.
Unresolvable dm/LVM/RAID mappings are not guessed to be a single drive.
"""

import os
import re
import stat
from pathlib import Path
from threading import Lock
from time import monotonic

import psutil

SYS_BLOCK_ROOT = Path("/sys/block")
SYS_DEV_BLOCK_ROOT = Path("/sys/dev/block")
DRIVE_NAME = re.compile(r"^(?:nvme[0-9]+n[0-9]+|sd[a-z]+|vd[a-z]+|xvd[a-z]+|mmcblk[0-9]+|hd[a-z]+)$")

_io_lock = Lock()
_previous_io: dict[str, tuple[int, int, int | None, float]] = {}


def read_int(path: Path) -> int | None:
    try:
        return int(path.read_text().strip())
    except (OSError, ValueError):
        return None


def read_text(path: Path) -> str | None:
    try:
        return path.read_text().strip() or None
    except (OSError, UnicodeError):
        return None


def physical_disks(sys_block_root: Path = SYS_BLOCK_ROOT) -> dict[str, Path]:
    """Return only real disk-class blocks, not loop, zram, dm or partitions."""
    result: dict[str, Path] = {}
    for disk in sorted(sys_block_root.iterdir()) if sys_block_root.is_dir() else []:
        if DRIVE_NAME.fullmatch(disk.name) and read_int(disk / "size") is not None:
            result[disk.name] = disk.resolve()
    return result


def backing_disks(sysfs_path: Path, disk_paths: dict[str, Path], visited: set[Path] | None = None) -> set[str]:
    """Follow partitions and device-mapper slaves to physical disk nodes."""
    try:
        path = sysfs_path.resolve(strict=True)
    except (OSError, RuntimeError):
        return set()
    visited = visited if visited is not None else set()
    if path in visited:
        return set()
    visited.add(path)

    for name, root in disk_paths.items():
        if path == root or root in path.parents:
            return {name}

    owners: set[str] = set()
    try:
        slaves = list((path / "slaves").iterdir())
    except OSError:
        slaves = []
    for slave in slaves:
        owners.update(backing_disks(slave, disk_paths, visited))
    return owners


def mounted_volumes(disk_paths: dict[str, Path]) -> dict[str, dict]:
    """Choose a representative mounted filesystem for each physical disk.

    A volume spanning multiple physical disks must not be assigned to any
    individual drive. A drive with multiple filesystems shows the largest
    mounted one; mountpoint is explicitly returned with those metrics.
    """
    volumes: dict[str, list[dict]] = {}
    try:
        partitions = psutil.disk_partitions(all=False)
    except (OSError, RuntimeError):
        return {}
    for partition in partitions:
        if not partition.device.startswith("/dev/"):
            continue
        try:
            device_stat = os.stat(partition.device)
            if not stat.S_ISBLK(device_stat.st_mode):
                continue
            device_number = device_stat.st_rdev
            path = SYS_DEV_BLOCK_ROOT / f"{os.major(device_number)}:{os.minor(device_number)}"
            physical = backing_disks(path, disk_paths)
            if len(physical) != 1:
                continue
            usage = psutil.disk_usage(partition.mountpoint)
        except (OSError, RuntimeError):
            continue
        name = next(iter(physical))
        volumes.setdefault(name, []).append({
            "mountpoint": partition.mountpoint,
            "volume_total": usage.total,
            "volume_used": usage.used,
            "volume_free": usage.free,
            "volume_percent": usage.percent,
        })

    return {
        name: max(items, key=lambda v: (v["volume_total"], v["mountpoint"] == "/", -len(v["mountpoint"])))
        for name, items in volumes.items()
    }


def device_io_rates(counters: dict, timestamp: float) -> dict[str, dict]:
    """Delta of cumulative per-drive counters, never lifetime bytes/sec."""
    result = {}
    with _io_lock:
        for name, counters_for_disk in counters.items():
            read_bytes = getattr(counters_for_disk, "read_bytes", None)
            write_bytes = getattr(counters_for_disk, "write_bytes", None)
            busy_time = getattr(counters_for_disk, "busy_time", None)
            if read_bytes is None or write_bytes is None:
                continue

            previous = _previous_io.get(name)
            _previous_io[name] = (read_bytes, write_bytes, busy_time, timestamp)
            rate_read = rate_write = busy = None
            if previous is not None:
                last_read, last_write, last_busy, last_time = previous
                elapsed = timestamp - last_time
                delta_read = read_bytes - last_read
                delta_write = write_bytes - last_write
                if elapsed > 0 and delta_read >= 0 and delta_write >= 0:
                    rate_read = round(delta_read / elapsed, 1)
                    rate_write = round(delta_write / elapsed, 1)
                    if busy_time is not None and last_busy is not None:
                        busy_ms = busy_time - last_busy
                        if busy_ms >= 0:
                            busy = round(min(100.0, 100.0 * busy_ms / (elapsed * 1000)), 1)

            result[name] = {
                "read_bytes_per_sec": rate_read,
                "write_bytes_per_sec": rate_write,
                "busy_percent": busy,
            }
        # Avoid unbounded sample accumulation after removable disk hot-unplug.
        _previous_io_keys = set(counters)
        for name in list(_previous_io):
            if name not in _previous_io_keys:
                del _previous_io[name]
    return result


def get_storage_devices() -> list[dict]:
    disks = physical_disks()
    if not disks:
        return []
    volumes = mounted_volumes(disks)
    try:
        counters = psutil.disk_io_counters(perdisk=True) or {}
    except (OSError, RuntimeError):
        counters = {}
    rates = device_io_rates({name: item for name, item in counters.items() if name in disks}, monotonic())
    devices = []
    for name, disk in disks.items():
        sectors = read_int(disk / "size")
        model = read_text(disk / "device/model")
        rotational = read_int(disk / "queue/rotational")
        devices.append({
            "id": name,
            "name": model or name,
            "device": f"/dev/{name}",
            "media_type": "HDD" if rotational == 1 else "SSD" if rotational == 0 else None,
            "capacity_bytes": sectors * 512 if sectors is not None else None,
            **{
                "mountpoint": None,
                "volume_total": None,
                "volume_used": None,
                "volume_free": None,
                "volume_percent": None,
            },
            **volumes.get(name, {}),
            **rates.get(name, {
                "read_bytes_per_sec": None,
                "write_bytes_per_sec": None,
                "busy_percent": None,
            }),
        })
    return devices
