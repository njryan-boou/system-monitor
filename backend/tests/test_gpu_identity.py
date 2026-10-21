from pathlib import Path
from app.services import gpu_identity


def test_known_amd_gpu_model_and_type(tmp_path):
    (tmp_path / "device").write_text("0x13c0")
    assert gpu_identity.identify_gpu("amd", tmp_path) == ("AMD Radeon 610M", "integrated")


def test_known_intel_gpu_model_and_type(tmp_path):
    (tmp_path / "device").write_text("0x64a0")
    assert gpu_identity.identify_gpu("intel", tmp_path) == ("Intel Lunar Lake Graphics", "integrated")


def test_unknown_device_does_not_guess_type(tmp_path, monkeypatch):
    (tmp_path / "device").write_text("0xffff")
    monkeypatch.setattr(gpu_identity, "pci_marketing_name", lambda address, vendor: None)
    assert gpu_identity.identify_gpu("amd", tmp_path) == ("AMD Radeon Graphics", None)


def test_pci_model_metadata_is_optional(tmp_path, monkeypatch):
    (tmp_path / "device").write_text("0xffff")
    monkeypatch.setattr(gpu_identity, "pci_marketing_name", lambda address, vendor: "AMD Radeon RX 7900 XTX")
    assert gpu_identity.identify_gpu("amd", tmp_path) == ("AMD Radeon RX 7900 XTX", None)
