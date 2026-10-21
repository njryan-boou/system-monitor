"""Network rate sampling and aggregate/interface behavior."""
from types import SimpleNamespace

from app.services import network_interfaces as service


def counter(recv, sent, packets_recv=0, packets_sent=0):
    return SimpleNamespace(bytes_recv=recv, bytes_sent=sent,
                           packets_recv=packets_recv, packets_sent=packets_sent,
                           errin=0, errout=0, dropin=0, dropout=0)


def test_network_sample_warmup_and_rates():
    service._SAMPLES.clear()
    assert not service.sample_rates({"eth0": counter(100, 200, 10, 20)}, 10.0)["eth0"]["ready"]
    result = service.sample_rates({"eth0": counter(1100, 700, 30, 35)}, 12.0)["eth0"]
    assert result["ready"]
    assert result["download_bytes_per_sec"] == 500
    assert result["upload_bytes_per_sec"] == 250
    assert result["download_packets_per_sec"] == 10
    assert result["upload_packets_per_sec"] == 7.5
    service._SAMPLES.clear()


def test_counter_reset_and_removed_adapter():
    service._SAMPLES.clear()
    service.sample_rates({"wlan0": counter(100, 200)}, 10)
    assert not service.sample_rates({"wlan0": counter(5, 10)}, 11)["wlan0"]["ready"]
    service.sample_rates({}, 12)
    assert not service.sample_rates({"wlan0": counter(8, 12)}, 13)["wlan0"]["ready"]
    service._SAMPLES.clear()


def test_aggregate_includes_loopback_without_listing_it(monkeypatch):
    service._SAMPLES.clear()
    monkeypatch.setattr(service.psutil, "net_io_counters", lambda perdisk=False, pernic=False: {
        "lo": counter(100, 150, 2, 3),
        "eth0": counter(200, 250, 4, 5),
    })
    monkeypatch.setattr(service.psutil, "net_if_stats", lambda: {
        "eth0": SimpleNamespace(isup=True, speed=1000, mtu=1500),
    })
    result = service.get_network_interfaces()
    assert [x["id"] for x in result] == ["all", "eth0"]
    assert result[0]["bytes_recv"] == 300
    assert result[1]["speed_mbps"] == 1000
    service._SAMPLES.clear()
