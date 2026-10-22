"""The GPU list endpoint must enumerate adapters without changing /gpu behavior."""

from fastapi.testclient import TestClient

from app.main import app
from app.services import gpu

client = TestClient(app)


def sample(name):
    return {
        "available": True,
        "name": name,
        "usage": 10.0,
        "memory_used": None,
        "memory_total": None,
        "temperature_c": None,
    }


def test_gpu_list_preserves_nvidia_then_integrated_order(monkeypatch):
    monkeypatch.setattr(gpu, "get_nvidia_gpu_infos", lambda: [
        ("nvidia:0", sample("NVIDIA 1")),
        ("nvidia:1", sample("NVIDIA 2")),
    ])
    monkeypatch.setattr(gpu, "get_nouveau_gpu_infos", lambda: [])
    monkeypatch.setattr(gpu, "get_amd_gpu_info", lambda: sample("AMD iGPU"))
    monkeypatch.setattr(gpu, "get_intel_gpu_info", lambda: None)

    response = client.get("/api/system/gpus")
    assert response.status_code == 200
    devices = response.json()
    assert [item["id"] for item in devices] == [
        "nvidia:0", "nvidia:1", "amd:0"
    ]
    assert [item["vendor"] for item in devices] == [
        "nvidia", "nvidia", "amd"
    ]
    assert devices[2]["name"] == "AMD iGPU"


def test_gpu_list_empty_when_no_adapters(monkeypatch):
    monkeypatch.setattr(gpu, "get_nvidia_gpu_infos", lambda: [])
    monkeypatch.setattr(gpu, "get_nouveau_gpu_infos", lambda: [])
    monkeypatch.setattr(gpu, "get_amd_gpu_info", lambda: None)
    monkeypatch.setattr(gpu, "get_intel_gpu_info", lambda: None)
    response = client.get("/api/system/gpus")
    assert response.status_code == 200
    assert response.json() == []


def test_single_gpu_endpoint_is_unchanged(monkeypatch):
    monkeypatch.setattr(gpu, "get_nvidia_gpu_info", lambda: sample("NVIDIA"))
    response = client.get("/api/system/gpu")
    assert response.status_code == 200
    assert response.json()["name"] == "NVIDIA"


def test_gpu_list_includes_nouveau_even_without_telemetry(monkeypatch):
    nouveau = {
        "available": True,
        "name": "NVIDIA GeForce GT 710",
        "usage": None,
        "memory_used": None,
        "memory_total": None,
        "temperature_c": None,
    }
    monkeypatch.setattr(gpu, "get_nvidia_gpu_infos", lambda: [])
    monkeypatch.setattr(gpu, "get_nouveau_gpu_infos", lambda: [
        ("nvidia:pci:0000:0b:00.0", nouveau),
    ])
    monkeypatch.setattr(gpu, "get_amd_gpu_info", lambda: sample("AMD iGPU"))
    monkeypatch.setattr(gpu, "get_intel_gpu_info", lambda: None)

    response = client.get("/api/system/gpus")
    assert response.status_code == 200
    devices = response.json()
    assert [item["id"] for item in devices] == [
        "nvidia:pci:0000:0b:00.0", "amd:0"
    ]
    assert devices[0]["name"] == "NVIDIA GeForce GT 710"
    assert devices[0]["usage"] is None


def test_legacy_nvidia_endpoint_falls_back_to_nouveau(monkeypatch):
    nouveau = {**sample("NVIDIA GeForce GT 710"), "usage": None}
    monkeypatch.setattr(gpu, "get_nvidia_gpu_info", lambda: {
        "available": False, "name": None,
    })
    monkeypatch.setattr(gpu, "get_nouveau_gpu_infos", lambda: [
        ("nvidia:pci:0000:0b:00.0", nouveau),
    ])

    response = client.get("/api/system/gpu?vendor=nvidia")
    assert response.status_code == 200
    assert response.json()["name"] == "NVIDIA GeForce GT 710"
