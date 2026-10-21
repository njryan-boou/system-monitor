"""System endpoint OS identity and optional host metadata."""
from app.services import monitor
from app.schemas.system import SystemResponse


def test_system_info_linux_os_release(monkeypatch):
    monkeypatch.setattr(monitor.platform, "system", lambda: "Linux")
    monkeypatch.setattr(monitor.platform, "release", lambda: "6.17.1-test")
    monkeypatch.setattr(monitor.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(monitor.platform, "node", lambda: "workstation")
    monkeypatch.setattr(monitor.platform, "freedesktop_os_release", lambda: {
        "PRETTY_NAME": "Fedora Linux 43", "VERSION_ID": "43", "ID": "fedora"
    })
    monkeypatch.setattr(monitor.psutil, "boot_time", lambda: 1000.0)
    monkeypatch.setattr(monitor.psutil, "pids", lambda: [1, 2, 3])
    monkeypatch.setattr(monitor.time, "time", lambda: 4600.0)
    result = SystemResponse(**monitor.get_system_info())
    assert result.distro_name == "Fedora Linux 43"
    assert result.distro_version == "43"
    assert result.os_release == "6.17.1-test"
    assert result.uptime == 3600
    assert result.hostname == "workstation"
    assert result.process_count == 3


def test_system_info_missing_os_metadata(monkeypatch):
    monkeypatch.setattr(monitor.platform, "system", lambda: "Linux")
    monkeypatch.setattr(monitor.platform, "freedesktop_os_release",
                        lambda: (_ for _ in ()).throw(OSError("missing os-release")))
    monkeypatch.setattr(monitor.psutil, "pids", lambda: [])
    data = monitor.get_system_info()
    assert data["distro_name"] is None
    assert data["distro_version"] is None
