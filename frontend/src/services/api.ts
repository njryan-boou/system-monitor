export interface CPUResponse {
    name: string;
    usage: number;
    physical_cores: number | null;
    logical_cores: number | null;
    frequency_mhz: number | null;
}

export interface MemoryResponse {
    total: number;
    used: number;
    available: number;
    percent: number;
}

export interface StorageResponse {
    volume: string;
    total: number;
    used: number;
    free: number;
    percent: number;
}

export interface SystemResponse {
    os: string;
    os_release: string;
    architecture: string;
    uptime: number;
}

export async function getCPUInfo(): Promise<CPUResponse> {
    const response = await fetch("/api/system/cpu");

    if (!response.ok) {
        throw new Error("Failed to fetch CPU information");
    }

    return await response.json();
}

export async function getMemoryUsage(): Promise<MemoryResponse> {
    const response = await fetch("/api/system/memory");

    if (!response.ok) {
        throw new Error("Failed to fetch memory information");
    }

    return await response.json();
}

export async function getStorageInfo(): Promise<StorageResponse> {
    const response = await fetch("/api/system/storage");

    if (!response.ok) {
        throw new Error("Failed to fetch storage information");
    }

    return await response.json();
}

export async function getSystemInfo(): Promise<SystemResponse> {
    const response = await fetch("/api/system/info");

    if (!response.ok) {
        throw new Error("Failed to fetch system information");
    }

    return await response.json();
}