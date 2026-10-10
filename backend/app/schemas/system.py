from pydantic import BaseModel


class CPUResponse(BaseModel):
    name: str | None
    usage: float
    physical_cores: int | None
    logical_cores: int | None
    frequency_mhz: float | None


class MemoryResponse(BaseModel):
    total: int
    used: int
    available: int
    percent: float


class StorageResponse(BaseModel):
    volume: str
    total: int
    used: int
    free: int
    percent: float


class SystemResponse(BaseModel):
    os: str
    os_release: str
    architecture: str
    uptime: int