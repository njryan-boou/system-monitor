"""Partition inventory: unmounted drives, Btrfs subvolumes, errors."""

import json
import subprocess
from types import SimpleNamespace

from app.schemas.system import StoragePartitionsResponse
from app.services import storage_partitions as service


def test_mounted_and_unmounted_nvme_partitions():
    data = {"blockdevices": [
        {"name": "nvme0n1", "type": "disk", "size": 4096805658624,
         "children": [
            {"name": "nvme0n1p1", "type": "part", "size": 4096800000000,
             "fstype": "ext4", "mountpoints": [None]},
         ]},
        {"name": "nvme2n1", "type": "disk", "size": 2000398934016,
         "children": [
            {"name": "nvme2n1p1", "type": "part", "size": 629145600,
             "fstype": "vfat", "mountpoints": ["/boot/efi"]},
            {"name": "nvme2n1p2", "type": "part", "size": 2147483648,
             "fstype": "ext4", "mountpoints": ["/boot"]},
            {"name": "nvme2n1p3", "type": "part", "size": "1997621166080",
             "fstype": "btrfs", "mountpoints": ["/home", "/", None, "/home"]},
         ]},
        {"name": "zram0", "type": "disk",
         "children": [{"name": "zram0p1", "type": "part", "size": 100,
                       "fstype": "swap", "mountpoints": [None]}]},
    ]}
    result = service.parse_lsblk(data, {"nvme0n1", "nvme1n1", "nvme2n1"})
    schema = StoragePartitionsResponse(**result)
    assert schema.available
    by_disk = {drive.disk_id: drive.partitions for drive in schema.drives}
    assert len(by_disk["nvme0n1"]) == 1
    assert by_disk["nvme0n1"][0].mountpoints == []
    assert by_disk["nvme0n1"][0].filesystem == "ext4"
    assert by_disk["nvme1n1"] == []
    assert len(by_disk["nvme2n1"]) == 3
    assert by_disk["nvme2n1"][2].mountpoints == ["/home", "/"]
    assert by_disk["nvme2n1"][2].size_bytes == 1997621166080
    assert "zram0" not in by_disk


def test_nested_partitions_and_legacy_mountpoint():
    data = {"blockdevices": [
        {"name": "sda", "type": "disk", "children": [
            {"name": "dm-0", "type": "crypt", "children": [
                {"name": "sda1", "type": "part", "size": 1024,
                 "fstype": None, "mountpoint": "/mnt/data"},
            ]},
        ]},
    ]}
    result = service.parse_lsblk(data, {"sda"})
    assert result["drives"][0]["partitions"][0]["mountpoints"] == ["/mnt/data"]


def test_malformed_json_shape_is_unavailable():
    assert service.parse_lsblk(None, {"sda"}) == {"available": False, "drives": []}
    assert service.parse_lsblk({"blockdevices": {}}, {"sda"}) == {
        "available": False, "drives": []
    }


def test_lsblk_command_is_readonly_and_cannot_invent_data(monkeypatch):
    monkeypatch.setattr(service, "physical_disks", lambda: {"sda": "unused"})
    called = {}

    def fake_run(args, **kwargs):
        called["args"] = args
        called["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout=json.dumps({
            "blockdevices": [{"name": "sda", "type": "disk", "children": [
                {"name": "sda1", "type": "part", "size": "1048576",
                 "fstype": "ntfs", "mountpoints": []},
            ]}]
        }))

    monkeypatch.setattr(service.subprocess, "run", fake_run)
    data = service.get_storage_partitions()
    assert data["drives"][0]["partitions"][0]["size_bytes"] == 1048576
    assert called["args"][0] == "lsblk"
    assert called["kwargs"]["timeout"] == 3
    assert "shell" not in called["kwargs"]


def test_lsblk_unavailable_or_timeout(monkeypatch):
    monkeypatch.setattr(service, "physical_disks", lambda: {"sda": "unused"})
    monkeypatch.setattr(service.subprocess, "run", lambda *a, **kw:
                        (_ for _ in ()).throw(FileNotFoundError()))
    assert service.get_storage_partitions()["available"] is False
    monkeypatch.setattr(service.subprocess, "run", lambda *a, **kw:
                        (_ for _ in ()).throw(subprocess.TimeoutExpired("lsblk", 3)))
    assert service.get_storage_partitions()["available"] is False
    monkeypatch.setattr(service.subprocess, "run", lambda *a, **kw:
                        SimpleNamespace(returncode=0, stdout="{not-json"))
    assert service.get_storage_partitions()["available"] is False


def test_no_disk_does_not_launch_lsblk(monkeypatch):
    monkeypatch.setattr(service, "physical_disks", lambda: {})
    monkeypatch.setattr(service.subprocess, "run", lambda *a, **kw:
                        (_ for _ in ()).throw(AssertionError("should not call")))
    assert service.get_storage_partitions() == {"available": True, "drives": []}
