"""System firmware: actual DMI fields, boot-mode detection, missing metadata."""

from app.schemas.system import SystemResponse
from app.services import system_firmware as firmware


def _put(root, name, value):
    root.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(value, encoding="utf-8")


def test_fedora_uefi_motherboard_and_bios_fields(tmp_path):
    dmi = tmp_path / "dmi"
    sys_firmware = tmp_path / "firmware"
    (sys_firmware / "efi").mkdir(parents=True)
    _put(dmi, "board_vendor", "ASUSTeK COMPUTER INC.\n")
    _put(dmi, "board_name", "ROG STRIX X870E-E GAMING WIFI\n")
    _put(dmi, "board_version", "Rev 1.xx")
    _put(dmi, "bios_vendor", "American Megatrends International, LLC.")
    _put(dmi, "bios_version", "1801")
    _put(dmi, "bios_date", "08/16/2025")

    result = firmware.read_system_firmware(dmi, sys_firmware, "Linux", containerized=False)
    assert result == {
        "motherboard_manufacturer": "ASUSTeK COMPUTER INC.",
        "motherboard_model": "ROG STRIX X870E-E GAMING WIFI",
        "motherboard_version": "Rev 1.xx",
        "bios_vendor": "American Megatrends International, LLC.",
        "bios_version": "1801",
        "bios_release_date": "08/16/2025",
        "boot_mode": "UEFI",
    }
    system = SystemResponse(
        os="Linux", os_release="6.17", architecture="x86_64", uptime=60,
        **result,
    )
    assert system.boot_mode == "UEFI"
    assert system.bios_version == "1801"


def test_legacy_detected_only_with_accessible_sysfs_outside_container(tmp_path):
    firmware_root = tmp_path / "firmware"
    firmware_root.mkdir()
    result = firmware.read_system_firmware(
        tmp_path / "missing-dmi", firmware_root, "Linux", containerized=False
    )
    assert result["boot_mode"] == "Legacy"
    assert result["motherboard_model"] is None


def test_container_without_efi_does_not_assume_legacy(tmp_path):
    root = tmp_path / "firmware"
    root.mkdir()
    data = firmware.read_system_firmware(tmp_path / "dmi", root, "Linux", containerized=True)
    assert data["boot_mode"] is None


def test_missing_sysfs_is_not_mislabeled(tmp_path):
    data = firmware.read_system_firmware(
        tmp_path / "dmi", tmp_path / "missing", "Linux", containerized=False
    )
    assert all(value is None for value in data.values())


def test_non_linux_reports_unavailable(tmp_path):
    _put(tmp_path / "dmi", "board_name", "EXAMPLE")
    (tmp_path / "firmware" / "efi").mkdir(parents=True)
    result = firmware.read_system_firmware(
        tmp_path / "dmi", tmp_path / "firmware", "Windows", containerized=False
    )
    assert all(value is None for value in result.values())


def test_sanitize_placeholder_values_and_permission_denied(tmp_path, monkeypatch):
    dmi = tmp_path / "dmi"
    _put(dmi, "board_vendor", "To Be Filled By O.E.M.")
    _put(dmi, "board_name", "Unknown")
    _put(dmi, "bios_vendor", "  Valid Firmware Corp  ")
    original = firmware.Path.read_text

    def reader(self, *args, **kwargs):
        if self.name == "bios_date":
            raise PermissionError("restricted")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(firmware.Path, "read_text", reader)
    data = firmware.read_system_firmware(dmi, tmp_path / "missing", "Linux", containerized=False)
    assert data["motherboard_manufacturer"] is None
    assert data["motherboard_model"] is None
    assert data["bios_vendor"] == "Valid Firmware Corp"
    assert data["bios_release_date"] is None
    assert not any(key in data for key in ("serial", "uuid", "asset_tag"))


def test_cache_method_returns_static_dictionary(monkeypatch):
    firmware.get_system_firmware.cache_clear()
    calls = []
    monkeypatch.setattr(firmware, "read_system_firmware", lambda: calls.append(1) or
                        {"bios_version": "TEST"})
    assert firmware.get_system_firmware()["bios_version"] == "TEST"
    assert firmware.get_system_firmware()["bios_version"] == "TEST"
    assert len(calls) == 1
    firmware.get_system_firmware.cache_clear()
