"""CPU cache hierarchy from Linux sysfs.

Cache entries are exposed once per logical CPU. A shared cache instance must
be counted only once, identified by cache level, type and shared CPU set.
Missing or malformed topology information is not guessed.
"""

import re
from functools import lru_cache
from pathlib import Path

CPU_SYSFS = Path("/sys/devices/system/cpu")
CACHE_SIZE = re.compile(r"^([0-9]+)\s*([KMG]?)\s*(?:i?B)?$", re.IGNORECASE)
CPU_NAME = re.compile(r"^cpu[0-9]+$")
INDEX_NAME = re.compile(r"^index[0-9]+$")


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None


def parse_cache_size(value: str | None) -> int | None:
    """Parse Linux sizes like 32K, 1M, 64M; return exact byte counts."""
    if value is None:
        return None
    match = CACHE_SIZE.fullmatch(value.strip())
    if match is None:
        return None
    number, unit = match.groups()
    return int(number) * 1024 ** {"": 0, "K": 1, "M": 2, "G": 3}[unit.upper()]


def parse_cpu_set(value: str | None) -> frozenset[int] | None:
    """Normalize '0-3,8,10-11' so duplicated sysfs entries are recognized."""
    if not value:
        return None
    cpus: set[int] = set()
    try:
        for item in value.strip().split(","):
            parts = item.strip().split("-")
            if len(parts) == 1:
                if not parts[0].isdigit():
                    return None
                cpus.add(int(parts[0]))
            elif len(parts) == 2 and all(p.isdigit() for p in parts):
                start, end = (int(p) for p in parts)
                if end < start or end - start > 16384:
                    return None
                cpus.update(range(start, end + 1))
            else:
                return None
    except ValueError:
        return None
    return frozenset(cpus) if cpus else None


def _list_dir(path: Path) -> list[Path]:
    try:
        return list(path.iterdir())
    except OSError:
        return []


@lru_cache(maxsize=8)
def get_cpu_cache_info(cpu_root: Path = CPU_SYSFS) -> dict:
    """Summed capacity across distinct instances, not per-thread multiplication.

    Cache capacities are static under normal operation, so this is cached
    instead of walking sysfs for every 1-second CPU poll.
    """
    groups: dict[tuple[int, str, frozenset[int]], int] = {}
    for cpu_path in _list_dir(cpu_root):
        if not CPU_NAME.fullmatch(cpu_path.name):
            continue
        for cache in _list_dir(cpu_path / "cache"):
            if not INDEX_NAME.fullmatch(cache.name):
                continue
            level_raw = _read(cache / "level")
            kind = _read(cache / "type")
            size = parse_cache_size(_read(cache / "size"))
            shared = parse_cpu_set(_read(cache / "shared_cpu_list"))
            if not level_raw or not level_raw.isdigit() or kind is None or not size or not shared:
                continue
            level = int(level_raw)
            if level not in (1, 2, 3):
                continue
            kind = kind.title()
            if kind not in ("Data", "Instruction", "Unified"):
                continue
            key = (level, kind, shared)
            # Inconsistent duplicate entries must never silently increase a total.
            groups.setdefault(key, size)

    def total(predicate) -> int | None:
        matching = [size for (level, kind, _), size in groups.items() if predicate(level, kind)]
        return sum(matching) if matching else None

    # One record per distinct cache size/type, with the physical instance
    # count. Hybrid processors may have differently-sized L2/L3 groups.
    by_instance: dict[tuple[int, str, int], int] = {}
    for (level, kind, _), size in groups.items():
        key = (level, kind, size)
        by_instance[key] = by_instance.get(key, 0) + 1
    instance_sizes = [
        {"level": level, "kind": kind, "size_bytes": size, "count": count}
        for (level, kind, size), count in sorted(
            by_instance.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])
        )
    ]

    return {
        "cache_instances": instance_sizes,
        "cache_l1_data_bytes": total(lambda level, kind: level == 1 and kind == "Data"),
        "cache_l1_instruction_bytes": total(lambda level, kind: level == 1 and kind == "Instruction"),
        "cache_l1_unified_bytes": total(lambda level, kind: level == 1 and kind == "Unified"),
        "cache_l2_bytes": total(lambda level, kind: level == 2),
        "cache_l3_bytes": total(lambda level, kind: level == 3),
        "cache_l3_groups": sum(1 for level, _, _ in groups if level == 3) or None,
    }
