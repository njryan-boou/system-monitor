import CPUCard from "../components/CPUCard";
import MemoryCard from "../components/MemoryCard";
import DiskCard from "../components/DiskCard";
import SystemCard from "../components/SystemCard";

import usePolling from "../hooks/usePolling";

import {
    getCPUInfo,
    getMemoryUsage,
    getStorageInfo,
    getSystemInfo
} from "../services/api";


export default function Dashboard() {
    const { data: cpu, error: cpuError } =
        usePolling(getCPUInfo, 1000);

    const { data: memory, error: memoryError } =
        usePolling(getMemoryUsage, 1000);

    const { data: storage, error: storageError } =
        usePolling(getStorageInfo, 10000);

    const { data: system, error: systemError } =
        usePolling(getSystemInfo, 5000);

    const errors = [
        cpuError ? "CPU" : null,
        memoryError ? "Memory" : null,
        storageError ? "Storage" : null,
        systemError ? "System" : null
    ].filter(Boolean);

    return (
        <main className="dashboard">
            <header className="dashboard-header">
                <h1>System Monitor</h1>

                <p className="dashboard-subtitle">
                    Real-time hardware monitoring dashboard
                </p>
            </header>

            {errors.length > 0 && (
                <p className="dashboard-error" role="status">
                    Unable to update: {errors.join(", ")}.
                    Showing previous measurements where available.
                </p>
            )}

            <div className="metric-grid">
                <CPUCard cpu={cpu} />
                <MemoryCard memory={memory} />
                <DiskCard storage={storage} />
                <SystemCard system={system} />
            </div>
        </main>
    );
}