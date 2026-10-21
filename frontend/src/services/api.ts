export interface CPUResponse {
    name: string;
    usage: number;
    physical_cores: number | null;
    logical_cores: number | null;
    frequency_mhz: number | null;
    per_logical_cpu_usage?: number[];
    temperature_c?: number | null;
    load_average_1m?: number | null;
    cache_l1_data_bytes?: number | null;
    cache_l1_instruction_bytes?: number | null;
    cache_l1_unified_bytes?: number | null;
    cache_l2_bytes?: number | null;
    cache_l3_bytes?: number | null;
    cache_l3_groups?: number | null;
}

export interface MemoryResponse {
    total: number;
    used: number;
    available: number;
    percent: number;
    cached?: number | null;
    swap_total?: number;
    swap_used?: number;
    swap_percent?: number | null;
}

export interface StorageResponse {
    volume: string;
    total: number;
    used: number;
    free: number;
    percent: number;
}

export interface StorageDeviceResponse {
    id: string;
    name: string;
    device: string;
    media_type: "SSD" | "HDD" | null;
    capacity_bytes: number | null;
    mountpoint: string | null;
    volume_total: number | null;
    volume_used: number | null;
    volume_free: number | null;
    volume_percent: number | null;
    read_bytes_per_sec: number | null;
    write_bytes_per_sec: number | null;
    busy_percent: number | null;
}

export async function getStorageDevices(): Promise<StorageDeviceResponse[]> {
    const response = await fetch("/api/system/storage/devices");
    if (!response.ok) throw new Error("Failed to fetch storage devices");
    return response.json();
}

export interface SystemResponse {
    os: string;
    os_release: string;
    architecture: string;
    uptime: number | null;
    distro_name?: string | null;
    distro_version?: string | null;
    distro_id?: string | null;
    hostname?: string | null;
    boot_time?: number | null;
    process_count?: number | null;
}

export interface NetworkCountersResponse {
    bytes_sent: number;
    bytes_recv: number;
}

export interface NetworkInterfaceResponse {
    id: string;
    name: string;
    interface_type: string;
    is_up: boolean | null;
    speed_mbps: number | null;
    mtu: number | null;
    bytes_recv: number;
    bytes_sent: number;
    packets_recv: number;
    packets_sent: number;
    errors_recv: number;
    errors_sent: number;
    drops_recv: number;
    drops_sent: number;
    ready: boolean;
    download_bytes_per_sec: number | null;
    upload_bytes_per_sec: number | null;
    download_packets_per_sec: number | null;
    upload_packets_per_sec: number | null;
}

export async function getNetworkInterfaces(): Promise<NetworkInterfaceResponse[]> {
    const response = await fetch("/api/system/network/interfaces");
    if (!response.ok) throw new Error("Failed to fetch network interfaces");
    return response.json();
}

export interface GPUResponse {
    available: boolean;
    name: string | null;
    usage: number | null;
    memory_used: number | null;
    memory_total: number | null;
    temperature_c: number | null;
    usage_label?: string | null;
    memory_label?: string | null;
    clock_mhz?: number | null;
    max_clock_mhz?: number | null;
    memory_clock_mhz?: number | null;
    power_watts?: number | null;
    gpu_type?: "integrated" | "dedicated" | null;
}

export interface GPUDeviceResponse extends GPUResponse {
    id: string;
    vendor: "nvidia" | "amd" | "intel";
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

export async function getGPUDevices(): Promise<GPUDeviceResponse[]> {
    const response = await fetch("/api/system/gpus");
    if (!response.ok) throw new Error("Failed to fetch GPU devices");
    return await response.json();
}

export async function getGPUInfo(): Promise<GPUResponse> {
    const response = await fetch("/api/system/gpu");

    if (!response.ok) {
        throw new Error("Failed to fetch GPU information");
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