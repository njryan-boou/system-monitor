import CPUCard from "../components/CPUCard";
import MemoryCard from "../components/MemoryCard";
import DiskCard from "../components/DiskCard";
import SystemCard from "../components/SystemCard";
import NetworkCard from "../components/NetworkCard";
import GPUCard from "../components/GPUCard";

import usePolling from "../hooks/usePolling";

import packageInfo from "../../package.json";

import {
    getCPUInfo,
    getMemoryUsage,
    getStorageInfo,
    getSystemInfo,
    getNetworkInfo,
    getGPUInfo
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

    const { data: network, error: networkError } =
        usePolling(getNetworkInfo, 1000);

    const { data: gpu, error: gpuError } =
        usePolling(getGPUInfo, 1000);

    const errors = [
        cpuError ? "CPU" : null,
        memoryError ? "Memory" : null,
        storageError ? "Storage" : null,
        systemError ? "System" : null,
        networkError ? "Network" : null,
        gpuError ? "GPU" : null
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
                <NetworkCard network={network} />
                <GPUCard gpu={gpu} />
            </div>

            <footer className="dashboard-footer">
                <span>System Monitor v{packageInfo.version}</span>
                <span>•</span>
                <span>React + FastAPI</span>
                <span>•</span>
                <a
                    href="https://github.com/njryan-boou/system-monitor"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    GitHub
                </a>
            </footer>
        </main>
    );
}