"""Memory endpoint should preserve RAM statistics and distinguish swap."""
from types import SimpleNamespace

from app.services import monitor
from app.schemas.system import MemoryResponse


def test_memory_with_swap(monkeypatch):
    monkeypatch.setattr(monitor.psutil, "virtual_memory", lambda: SimpleNamespace(
        total=16_000, used=8_000, available=8_000, percent=50.0, cached=3_000))
    monkeypatch.setattr(monitor.psutil, "swap_memory", lambda: SimpleNamespace(
        total=4_000, used=1_000, percent=25.0))
    result = MemoryResponse(**monitor.get_memory_usage())
    assert result.percent == 50.0
    assert result.cached == 3_000
    assert result.swap_total == 4_000
    assert result.swap_used == 1_000
    assert result.swap_percent == 25.0


def test_memory_without_swap(monkeypatch):
    monkeypatch.setattr(monitor.psutil, "virtual_memory", lambda: SimpleNamespace(
        total=16_000, used=4_000, available=12_000, percent=25.0))
    monkeypatch.setattr(monitor.psutil, "swap_memory", lambda: SimpleNamespace(
        total=0, used=0, percent=0.0))
    result = MemoryResponse(**monitor.get_memory_usage())
    assert result.cached is None
    assert result.swap_total == 0
    assert result.swap_percent is None
