"""CPU-specific sensor selection and optional performance metrics."""
from types import SimpleNamespace

from app.services import monitor


def test_cpu_temperature_prefers_amd_tdie(monkeypatch):
    monkeypatch.setattr(monitor.psutil, "sensors_temperatures", lambda: {
        "k10temp": [
            SimpleNamespace(label="Tctl", current=61.0),
            SimpleNamespace(label="Tdie", current=58.25),
        ],
        "acpitz": [SimpleNamespace(label="", current=99)],
    })
    assert monitor.get_cpu_temperature() == 58.2


def test_cpu_temperature_does_not_use_unrelated_sensor(monkeypatch):
    monkeypatch.setattr(monitor.psutil, "sensors_temperatures", lambda: {
        "acpitz": [SimpleNamespace(label="", current=80)],
        "nvme": [SimpleNamespace(label="Composite", current=45)],
    })
    assert monitor.get_cpu_temperature() is None


def test_cpu_temperature_selects_intel_package(monkeypatch):
    monkeypatch.setattr(monitor.psutil, "sensors_temperatures", lambda: {
        "coretemp": [
            SimpleNamespace(label="Core 0", current=40),
            SimpleNamespace(label="Package id 0", current=51),
        ]
    })
    assert monitor.get_cpu_temperature() == 51.0


def test_cpu_load_average(monkeypatch):
    monkeypatch.setattr(monitor.psutil, "getloadavg", lambda: (1.2345, 2.0, 3.0))
    assert monitor.get_cpu_load_average() == 1.23
