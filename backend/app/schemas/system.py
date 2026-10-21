from typing import Literal

from pydantic import BaseModel


class CPUResponse(BaseModel):
    name: str | None
    usage: float
    physical_cores: int | None
    logical_cores: int | None
    frequency_mhz: float | None
    per_logical_cpu_usage: list[float] = []
    temperature_c: float | None = None
    load_average_1m: float | None = None


class MemoryResponse(BaseModel):
    total: int
    used: int
    available: int
    percent: float
    cached: int | None = None
    swap_total: int = 0
    swap_used: int = 0
    swap_percent: float | None = None


class StorageResponse(BaseModel):
    volume: str
    total: int
    used: int
    free: int
    percent: float


class StorageDeviceResponse(BaseModel):
    id: str
    name: str
    device: str
    media_type: Literal["SSD", "HDD"] | None = None
    capacity_bytes: int | None = None
    mountpoint: str | None = None
    volume_total: int | None = None
    volume_used: int | None = None
    volume_free: int | None = None
    volume_percent: float | None = None
    read_bytes_per_sec: float | None = None
    write_bytes_per_sec: float | None = None
    busy_percent: float | None = None


class SystemResponse(BaseModel):
    os: str
    os_release: str
    architecture: str
    uptime: int
    
    
class NetworkResponse(BaseModel):
    bytes_sent: int
    bytes_recv: int
    
    
class NetworkInterfaceResponse(BaseModel):
    id: str
    name: str
    interface_type: str
    is_up: bool | None = None
    speed_mbps: int | None = None
    mtu: int | None = None
    bytes_recv: int
    bytes_sent: int
    packets_recv: int
    packets_sent: int
    errors_recv: int
    errors_sent: int
    drops_recv: int
    drops_sent: int
    ready: bool
    download_bytes_per_sec: float | None = None
    upload_bytes_per_sec: float | None = None
    download_packets_per_sec: float | None = None
    upload_packets_per_sec: float | None = None


class GPUResponse(BaseModel):
    available: bool
    name: str | None
    usage: float | None
    memory_used: int | None
    memory_total: int | None
    temperature_c: int | None
    usage_label: str | None = None
    memory_label: str | None = None
    clock_mhz: float | None = None
    max_clock_mhz: float | None = None
    memory_clock_mhz: float | None = None
    power_watts: float | None = None
    gpu_type: Literal["integrated", "dedicated"] | None = None

class GPUDeviceResponse(GPUResponse):
    id: str
    vendor: Literal["nvidia", "amd", "intel"]
