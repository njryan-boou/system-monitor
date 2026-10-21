"""RAM Hardware view: sanitized SMBIOS parsing and privilege-safe fallback."""

import json
import struct

from app.schemas.system import MemoryResponse
from app.services import memory_hardware as hardware
from app.services import monitor


def dmi_record(
    size_mb=16_384, memory_type=0x22, rated_mtps=6000,
    configured_mtps=5600, manufacturer="Corsair", slot="DIMM_A1",
):
    raw = bytearray(0x22)
    raw[0] = 17
    raw[1] = len(raw)
    struct.pack_into("<H", raw, 0x0C, size_mb)
    raw[0x10] = 1
    raw[0x12] = memory_type
    raw[0x17] = 2
    struct.pack_into("<H", raw, 0x15, rated_mtps)
    struct.pack_into("<H", raw, 0x20, configured_mtps)
    return bytes(raw) + slot.encode() + b"\0" + manufacturer.encode() + b"\0\0"


def test_parse_ddr5_capacity_slot_manufacturer_and_configured_speed():
    module = hardware.parse_memory_device(dmi_record())
    assert module == {
        "slot": "DIMM_A1", "capacity_bytes": 16 * 1024 ** 3,
        "memory_type": "DDR5", "speed_mtps": 5600, "manufacturer": "Corsair"
    }


def test_speed_falls_back_to_rated_and_empty_slot_ignored():
    module = hardware.parse_memory_device(dmi_record(configured_mtps=0))
    assert module["speed_mtps"] == 6000
    assert hardware.parse_memory_device(dmi_record(size_mb=0)) is None
    assert hardware.parse_memory_device(dmi_record(size_mb=0xFFFF)) is None
    assert hardware.parse_memory_device(b"") is None


def test_extended_capacity_and_lpddr_type():
    raw = bytearray(dmi_record(size_mb=0x7FFF, memory_type=0x23))
    struct.pack_into("<I", raw, 0x1C, 65_536)
    module = hardware.parse_memory_device(bytes(raw))
    assert module["capacity_bytes"] == 64 * 1024 ** 3
    assert module["memory_type"] == "LPDDR5"


def test_scan_deduplicates_no_slots_and_summary_handles_mixed(tmp_path):
    first = tmp_path / "17-0"
    second = tmp_path / "17-1"
    first.mkdir()
    second.mkdir()
    (first / "raw").write_bytes(dmi_record())
    (second / "raw").write_bytes(dmi_record(size_mb=32_768, slot="DIMM_B1", configured_mtps=5200))
    modules = hardware.read_dmi_memory_modules(tmp_path)
    assert len(modules) == 2
    summary = hardware.summarize_modules(modules, "smbios")
    assert summary["memory_module_count"] == 2
    assert summary["memory_type"] == "DDR5"
    assert summary["memory_speed_mtps"] is None  # Mixed configured speeds.


def test_no_readable_firmware_gracefully_returns_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr(hardware, "DMI_ROOT", tmp_path / "missing")
    monkeypatch.setattr(hardware, "SNAPSHOT_PATH", tmp_path / "missing.json")
    monkeypatch.setattr(hardware, "read_dmi_memory_modules", lambda: None)
    hardware.get_memory_hardware.cache_clear()
    assert hardware.get_memory_hardware() == hardware.unavailable()
    hardware.get_memory_hardware.cache_clear()


def test_snapshot_is_sanitized_and_validated(tmp_path, monkeypatch):
    snapshot = tmp_path / "memory.json"
    monkeypatch.setattr(hardware, "SNAPSHOT_PATH", snapshot)
    monkeypatch.setattr(hardware, "read_dmi_memory_modules", lambda: None)
    snapshot.write_text(json.dumps({
        "memory_modules": [{
            "slot": "A1", "capacity_bytes": 8 * 1024 ** 3,
            "memory_type": "DDR4", "speed_mtps": 3200,
            "manufacturer": "Samsung",
            "serial": "MUST_NOT_BE_EXPOSED",
        }]
    }))
    hardware.get_memory_hardware.cache_clear()
    result = hardware.get_memory_hardware()
    assert result["memory_hardware_source"] == "snapshot"
    assert result["memory_type"] == "DDR4"
    assert "serial" not in result["memory_modules"][0]
    assert result["memory_module_count"] == 1
    hardware.get_memory_hardware.cache_clear()


def test_memory_api_remains_compatible(monkeypatch):
    from types import SimpleNamespace

    monkeypatch.setattr(monitor.psutil, "virtual_memory", lambda: SimpleNamespace(
        total=32 * 1024 ** 3, used=8 * 1024 ** 3,
        available=24 * 1024 ** 3, percent=25.0, cached=0
    ))
    monkeypatch.setattr(monitor.psutil, "swap_memory", lambda: SimpleNamespace(
        total=0, used=0, percent=0
    ))
    monkeypatch.setattr(monitor, "get_memory_hardware", lambda: hardware.summarize_modules([
        {"slot": "A1", "capacity_bytes": 16 * 1024 ** 3,
         "memory_type": "DDR5", "speed_mtps": 5600, "manufacturer": "Corsair"}
    ], "smbios"))
    response = MemoryResponse(**monitor.get_memory_usage())
    assert response.percent == 25.0
    assert response.memory_module_count == 1
    assert response.memory_modules[0].manufacturer == "Corsair"


def test_rejects_invalid_snapshot(tmp_path, monkeypatch):
    snapshot = tmp_path / "memory.json"
    monkeypatch.setattr(hardware, "SNAPSHOT_PATH", snapshot)
    monkeypatch.setattr(hardware, "read_dmi_memory_modules", lambda: None)
    snapshot.write_text(json.dumps({"memory_modules": [
        {"slot": "A1", "capacity_bytes": -1, "memory_type": "DDR5"}
    ]}))
    hardware.get_memory_hardware.cache_clear()
    assert hardware.get_memory_hardware() == hardware.unavailable()
    hardware.get_memory_hardware.cache_clear()
