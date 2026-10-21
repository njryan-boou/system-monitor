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
