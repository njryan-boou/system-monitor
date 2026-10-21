"""Physical-drive enumeration and sampled I/O semantics."""
from types import SimpleNamespace

from app.services import storage_devices as service


def test_lists_supported_drive_types_only(tmp_path):
    for name in ("nvme0n1", "sda", "loop0", "dm-0", "zram0"):
        p = tmp_path / name
        p.mkdir()
        (p / "size").write_text("2048")
    assert list(service.physical_disks(tmp_path)) == ["nvme0n1", "sda"]


def test_rates_require_two_valid_samples():
    service._previous_io.clear()
    sample = lambda read, write, busy: {
        "sda": SimpleNamespace(read_bytes=read, write_bytes=write, busy_time=busy)
    }
    first = service.device_io_rates(sample(1024, 200, 10), 10.0)["sda"]
    assert first["read_bytes_per_sec"] is None
    second = service.device_io_rates(sample(3072, 1224, 210), 11.0)["sda"]
    assert second == {
        "read_bytes_per_sec": 2048.0,
        "write_bytes_per_sec": 1024.0,
        "busy_percent": 20.0,
    }
    service._previous_io.clear()


def test_counters_do_not_report_negative_rates():
    service._previous_io.clear()
    counter = lambda count: {"sda": SimpleNamespace(
        read_bytes=count, write_bytes=count, busy_time=count)}
    service.device_io_rates(counter(500), 10.0)
    result = service.device_io_rates(counter(100), 11.0)["sda"]
    assert result["read_bytes_per_sec"] is None
    assert result["busy_percent"] is None
    service._previous_io.clear()
