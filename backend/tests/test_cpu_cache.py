"""Cache hierarchy must count shared instances only once."""

from app.schemas.system import CPUResponse
from app.services import cpu_cache


def entry(root, cpu, index, level, kind, size, shared):
    path = root / f"cpu{cpu}" / "cache" / f"index{index}"
    path.mkdir(parents=True, exist_ok=True)
    for filename, value in {
        "level": str(level),
        "type": kind,
        "size": size,
        "shared_cpu_list": shared,
    }.items():
        (path / filename).write_text(value)


def test_cache_size_and_cpu_set_parsing():
    assert cpu_cache.parse_cache_size("32K") == 32768
    assert cpu_cache.parse_cache_size("1M") == 1024 ** 2
    assert cpu_cache.parse_cache_size("64MiB") == 64 * 1024 ** 2
    assert cpu_cache.parse_cache_size("unknown") is None
    assert cpu_cache.parse_cpu_set("0-3,8,10-11") == frozenset({0, 1, 2, 3, 8, 10, 11})
    assert cpu_cache.parse_cpu_set("3-0") is None


def test_cache_shared_across_threads_is_not_double_counted(tmp_path):
    cpu_cache.get_cpu_cache_info.cache_clear()
    for cpu in (0, 1):
        entry(tmp_path, cpu, 0, 1, "Data", "32K", "0-1")
        entry(tmp_path, cpu, 1, 1, "Instruction", "32K", "0-1")
        entry(tmp_path, cpu, 2, 2, "Unified", "1M", "0-1")
    for cpu in (0, 1, 2, 3):
        entry(tmp_path, cpu, 3, 3, "Unified", "16M", "0-3")
    entry(tmp_path, 4, 0, 1, "Data", "48K", "4")
    entry(tmp_path, 4, 3, 3, "Unified", "8M", "4-7")

    result = cpu_cache.get_cpu_cache_info(tmp_path)
    assert result["cache_l1_data_bytes"] == 80 * 1024
    assert result["cache_l1_instruction_bytes"] == 32 * 1024
    assert result["cache_l2_bytes"] == 1024 ** 2
    assert result["cache_l3_bytes"] == 24 * 1024 ** 2
    assert result["cache_l3_groups"] == 2
    assert result["cache_l1_unified_bytes"] is None

    # Distinct cache groups are counted once even across repeated polls.
    assert cpu_cache.get_cpu_cache_info(tmp_path) == result
    cpu_cache.get_cpu_cache_info.cache_clear()


def test_unavailable_cache_is_not_invented(tmp_path):
    entry(tmp_path, 0, 0, 1, "Data", "32K", "invalid")
    entry(tmp_path, 0, 1, 3, "Unified", "unknown", "0")
    data = cpu_cache.get_cpu_cache_info(tmp_path)
    assert all(value is None for value in data.values())
    validated = CPUResponse(
        name="Test CPU", usage=10.0, physical_cores=1, logical_cores=2,
        frequency_mhz=None, **data,
    )
    assert validated.cache_l3_bytes is None
    cpu_cache.get_cpu_cache_info.cache_clear()


def test_l1_unified_and_l2_data(tmp_path):
    entry(tmp_path, 0, 0, 1, "Unified", "64K", "0")
    entry(tmp_path, 0, 1, 2, "Data", "512K", "0")
    entry(tmp_path, 0, 2, 2, "Instruction", "512K", "0")
    data = cpu_cache.get_cpu_cache_info(tmp_path)
    assert data["cache_l1_unified_bytes"] == 65536
    assert data["cache_l2_bytes"] == 1024 ** 2
    cpu_cache.get_cpu_cache_info.cache_clear()
