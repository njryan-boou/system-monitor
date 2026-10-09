export interface CPUResponse {
    usage: number;
}

export interface MemoryResponse {
    total: number;
    used: number;
    available: number;
    percent: number;
}

export async function getCPUUsage(): Promise<CPUResponse> {
    const response = await fetch("/api/system/cpu");

    if (!response.ok) {
        throw new Error("Failed to fetch CPU usage");
    }

    return await response.json();
}

export async function getMemoryUsage(): Promise<MemoryResponse> {
    const response = await fetch("/api/system/memory");

    if (!response.ok) {
        throw new Error("Failed to fetch memory usage");
    }

    return await response.json();
}