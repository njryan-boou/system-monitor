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

export interface NetworkCountersResponse {
    bytes_sent: number;
    bytes_recv: number;
}

export interface NetworkResponse extends NetworkCountersResponse {
    download_bytes_per_sec: number;
    upload_bytes_per_sec: number;
    ready: boolean;
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

let previousNetworkSample: (
    NetworkCountersResponse & { timestamp: number }
) | null = null;

export async function getNetworkInfo(): Promise<NetworkResponse> {
    const response = await fetch("/api/system/network");

    if (!response.ok) {
        throw new Error("Failed to fetch network information");
    }

    const counters: NetworkCountersResponse = await response.json();
    const timestamp = performance.now();

    let download = 0;
    let upload = 0;
    let ready = false;

    if (previousNetworkSample !== null) {
        const elapsed =
            (timestamp - previousNetworkSample.timestamp) / 1000;

        if (elapsed > 0) {
            download = Math.max(
                0,
                counters.bytes_recv - previousNetworkSample.bytes_recv
            ) / elapsed;

            upload = Math.max(
                0,
                counters.bytes_sent - previousNetworkSample.bytes_sent
            ) / elapsed;

            ready = true;
        }
    }

    previousNetworkSample = {
        ...counters,
        timestamp
    };

    return {
        ...counters,
        download_bytes_per_sec: download,
        upload_bytes_per_sec: upload,
        ready
    };
}