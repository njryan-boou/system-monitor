from pathlib import Path

import pytest

from app.services import gpu_intel


@pytest.fixture(autouse=True)
def reset_intel_sampling_state():
    gpu_intel.get_intel_gpu_path.cache_clear()
    gpu_intel._previous_sample = None
    yield
    gpu_intel.get_intel_gpu_path.cache_clear()
    gpu_intel._previous_sample = None


def test_detects_intel_xe_device(tmp_path, monkeypatch):
    card = tmp_path / "card0" / "device"
    card.mkdir(parents=True)
    (card / "vendor").write_text("0x8086\n")
    (card / "device").write_text("0x64a0\n")
    drivers = tmp_path / "drivers"
    (drivers / "xe").mkdir(parents=True)
    (card / "driver").symlink_to(drivers / "xe", target_is_directory=True)
    monkeypatch.setattr(gpu_intel, "DRM_ROOT", tmp_path)

    assert gpu_intel.get_intel_gpu_path() == card.resolve()


def test_reads_unique_clients_and_ignores_other_devices(tmp_path):
    def add_fd(pid, fd, body):
        file = tmp_path / str(pid) / "fdinfo" / str(fd)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(body)

    valid = (
        "drm-driver: xe\n"
        "drm-pdev: 0000:00:02.0\n"
        "drm-client-id: 33\n"
        "drm-cycles-rcs: 10\n"
        "drm-total-cycles-rcs: 100\n"
    )
    add_fd(10, 5, valid)
    add_fd(10, 6, valid)
    add_fd(11, 3, valid.replace("0000:00:02.0", "0000:00:03.0"))
    add_fd(12, 4, valid.replace("33", "34").replace("10\n", "30\n"))

    clients = gpu_intel.get_gpu_clients("0000:00:02.0", tmp_path)
    assert set(clients) == {"33", "34"}
    assert clients["33"]["rcs"] == (10, 100)


def test_peak_activity_uses_deltas_and_clamps():
    previous = {
        "1": {"rcs": (100, 1000), "ccs": (30, 1000)},
        "2": {"rcs": (20, 1000)},
    }
    current = {
        "1": {"rcs": (105, 1100), "ccs": (60, 1100)},
        "2": {"rcs": (26, 1100)},
    }
    assert gpu_intel.calculate_peak_activity(previous, current) == 30.0
    assert gpu_intel.calculate_peak_activity(previous, previous) is None
    assert gpu_intel.calculate_peak_activity(previous, {"3": {}}) is None
    assert gpu_intel.calculate_peak_activity(
        {"1": {"rcs": (0, 100)}}, {"1": {"rcs": (1000, 200)}}
    ) == 100.0


def test_temperature_only_from_attached_sensor(tmp_path):
    assert gpu_intel.read_temperature(tmp_path) is None
    hwmon = tmp_path / "hwmon" / "hwmon0"
    hwmon.mkdir(parents=True)
    (hwmon / "temp1_input").write_text("42000\n")
    assert gpu_intel.read_temperature(tmp_path) == 42


def test_service_warms_up_then_returns_activity(tmp_path, monkeypatch):
    (tmp_path / "device").write_text("0x64a0\n")
    monkeypatch.setattr(gpu_intel, "get_intel_gpu_path", lambda: tmp_path)
    samples = iter([
        {"33": {"rcs": (100, 1000)}},
        {"33": {"rcs": (101, 1200)}},
        {},
    ])
    monkeypatch.setattr(gpu_intel, "get_gpu_clients", lambda _: next(samples))
    first = gpu_intel.get_intel_gpu_info()
    second = gpu_intel.get_intel_gpu_info()
    third = gpu_intel.get_intel_gpu_info()
    assert first["name"] == "Intel Lunar Lake Graphics"
    assert first["usage"] is None
    assert second["usage"] == 0.5
    assert second["usage_label"] == "Peak Client Engine Activity"
    assert third["usage"] is None
    assert third["memory_total"] is None
