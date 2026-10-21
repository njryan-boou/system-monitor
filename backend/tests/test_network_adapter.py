"""Network Adapter view: sysfs driver/bus, duplex, and fallback semantics."""

from types import SimpleNamespace

import psutil

from app.schemas.system import NetworkInterfaceResponse
from app.services import network_interfaces as service


def test_hardware_driver_bus_and_operating_state(tmp_path):
    net = tmp_path / "net"
    iface = net / "enp8s0"
    iface.mkdir(parents=True)
    (iface / "operstate").write_text("up\n")
    device = tmp_path / "0000:08:00.0"
    device.mkdir()
    driver = tmp_path / "r8169"
    driver.mkdir()
    (device / "driver").symlink_to(driver, target_is_directory=True)
    (iface / "device").symlink_to(device, target_is_directory=True)

    stat = SimpleNamespace(duplex=psutil.NIC_DUPLEX_FULL)
    assert service.adapter_properties("enp8s0", stat, net) == {
        "driver": "r8169",
        "hardware_path": "0000:08:00.0",
        "operstate": "up",
        "duplex": "Full",
    }


def test_wifi_half_duplex_and_no_hardware_driver(tmp_path):
    iface = tmp_path / "wlp1s0"
    iface.mkdir()
    (iface / "operstate").write_text("dormant\n")
    assert service.adapter_properties(
        "wlp1s0", SimpleNamespace(duplex=psutil.NIC_DUPLEX_HALF), tmp_path
    ) == {
        "driver": None, "hardware_path": None,
        "operstate": "dormant", "duplex": "Half",
    }


def test_virtual_and_missing_adapter_fields_are_optional(tmp_path):
    iface = tmp_path / "veth0"
    iface.mkdir()
    (iface / "operstate").write_text("not a valid state")
    props = service.adapter_properties("veth0", SimpleNamespace(duplex=255), tmp_path)
    assert props == {
        "driver": None, "hardware_path": None,
        "operstate": None, "duplex": None,
    }
    missing = service.adapter_properties("absent", None, tmp_path)
    assert all(value is None for value in missing.values())


def _counters():
    return SimpleNamespace(
        bytes_recv=1024, bytes_sent=2048,
        packets_recv=10, packets_sent=20,
        errin=0, errout=0, dropin=0, dropout=0
    )


def test_metadata_in_existing_api_without_changing_aggregate(monkeypatch):
    service._SAMPLES.clear()
    monkeypatch.setattr(service.psutil, "net_io_counters", lambda pernic=False: {
        "lo": _counters(), "enp8s0": _counters()
    })
    monkeypatch.setattr(service.psutil, "net_if_stats", lambda: {
        "enp8s0": SimpleNamespace(
            isup=True, speed=1000, mtu=1500, duplex=psutil.NIC_DUPLEX_FULL,
        )
    })
    monkeypatch.setattr(service, "adapter_properties", lambda name, stat: {
        "driver": "r8169", "hardware_path": "0000:08:00.0",
        "operstate": "up", "duplex": "Full",
    })
    interfaces = [
        NetworkInterfaceResponse(**item)
        for item in service.get_network_interfaces()
    ]
    assert [x.id for x in interfaces] == ["all", "enp8s0"]
    assert interfaces[0].driver is None
    assert interfaces[0].operstate is None
    assert interfaces[1].driver == "r8169"
    assert interfaces[1].duplex == "Full"
    assert interfaces[1].mtu == 1500
    assert interfaces[1].is_up is True
    assert interfaces[1].bytes_recv == 1024
    service._SAMPLES.clear()
