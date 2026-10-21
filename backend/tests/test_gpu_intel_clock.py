"""Xe GT sysfs clock and GPU-attached power sensor tests."""
from app.services import gpu_intel


def test_gt_clock_prefers_actual_frequency(tmp_path):
    frequency = tmp_path / "tile0/gt0/freq0"
    frequency.mkdir(parents=True)
    (frequency / "act_freq").write_text("850\n")
    (frequency / "rp0_freq").write_text("2000\n")
    assert gpu_intel.read_gt_clock_mhz(tmp_path) == 850.0
    assert gpu_intel.read_gt_clock_mhz(tmp_path, "rp0_freq") == 2000.0


def test_missing_gt_clock_stays_unavailable(tmp_path):
    assert gpu_intel.read_gt_clock_mhz(tmp_path) is None


def test_invalid_gt_clock_stays_unavailable(tmp_path):
    frequency = tmp_path / "tile0/gt0/freq0"
    frequency.mkdir(parents=True)
    (frequency / "act_freq").write_text("unavailable\n")
    assert gpu_intel.read_gt_clock_mhz(tmp_path) is None


def test_gpu_attached_power_only(tmp_path):
    assert gpu_intel.read_gpu_power_watts(tmp_path) is None
    sensor = tmp_path / "hwmon/hwmon0"
    sensor.mkdir(parents=True)
    (sensor / "power1_input").write_text("3150000\n")
    assert gpu_intel.read_gpu_power_watts(tmp_path) == 3.15


def test_energy_counter_warmup_and_delta(tmp_path, monkeypatch):
    sensor = tmp_path / "hwmon/hwmon0"
    sensor.mkdir(parents=True)
    (sensor / "energy1_input").write_text("1000000\n")
    gpu_intel._previous_energy.clear()
    times = iter([10.0, 11.0])
    monkeypatch.setattr(gpu_intel, "monotonic", lambda: next(times))
    assert gpu_intel.read_gpu_power_watts(tmp_path) is None
    (sensor / "energy1_input").write_text("3000000\n")
    assert gpu_intel.read_gpu_power_watts(tmp_path) == 2.0
    gpu_intel._previous_energy.clear()
