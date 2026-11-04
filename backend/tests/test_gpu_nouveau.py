"""Nouveau discovery must not depend on NVIDIA's proprietary driver."""

from types import SimpleNamespace

from app.services import gpu_nouveau


def _make_card(root, name, vendor, driver, address):
    drm = root / "drm"
    drm.mkdir(exist_ok=True)
    pci = root / address
    pci.mkdir(exist_ok=True)
    (pci / "vendor").write_text(vendor)
    driver_dir = root / driver
    driver_dir.mkdir(exist_ok=True)
    (pci / "driver").symlink_to(driver_dir, target_is_directory=True)

    card = drm / name
    card.mkdir()
    (card / "device").symlink_to(pci, target_is_directory=True)
    return drm, pci


def test_discovers_gt_710_with_no_nvml_or_telemetry(tmp_path, monkeypatch):
    drm, pci = _make_card(
        tmp_path, "card0", "0x10de", "nouveau", "0000:0b:00.0"
    )
    monkeypatch.setattr(gpu_nouveau.subprocess, "run", lambda *a, **kw: SimpleNamespace(
        returncode=0,
        stdout='0000:0b:00.0 "VGA compatible controller" '
               '"NVIDIA Corporation" "GK208B [GeForce GT 710]"\n',
    ))
    gpu_nouveau._pci_gpu_name.cache_clear()

    result = gpu_nouveau.get_nouveau_gpu_infos(drm)
    assert len(result) == 1
    device_id, info = result[0]
    assert device_id == "nvidia:pci:0000:0b:00.0"
    assert info["name"] == "NVIDIA GeForce GT 710"
    assert info["available"] is True
    assert info["usage"] is None
    assert info["memory_total"] is None
    assert info["temperature_c"] is None

    hwmon = pci / "hwmon" / "hwmon0"
    hwmon.mkdir(parents=True)
    (hwmon / "temp1_input").write_text("57000\n")
    assert gpu_nouveau.get_nouveau_gpu_infos(drm)[0][1]["temperature_c"] == 57
    gpu_nouveau._pci_gpu_name.cache_clear()


def test_ignores_other_vendors_and_non_nouveau_drivers(tmp_path):
    drm, _ = _make_card(
        tmp_path, "card0", "0x1002", "amdgpu", "0000:72:00.0"
    )
    assert gpu_nouveau.get_nouveau_gpu_infos(drm) == []


def test_falls_back_to_pci_identity_when_pciutils_is_missing(tmp_path, monkeypatch):
    drm, _ = _make_card(
        tmp_path, "card0", "0x10de", "nouveau", "0000:0b:00.0"
    )
    def no_lspci(*args, **kwargs):
        raise FileNotFoundError("lspci")

    monkeypatch.setattr(gpu_nouveau.subprocess, "run", no_lspci)
    gpu_nouveau._pci_gpu_name.cache_clear()
    result = gpu_nouveau.get_nouveau_gpu_infos(drm)
    assert result[0][1]["name"] == "NVIDIA GPU (0000:0b:00.0)"
    gpu_nouveau._pci_gpu_name.cache_clear()
