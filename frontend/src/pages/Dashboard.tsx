import { useEffect, useState } from "react";

import CPUCard from "../components/CPUCard";
import MemoryCard from "../components/MemoryCard";
import DiskCard from "../components/DiskCard";
import SystemCard from "../components/SystemCard";

import {
    getCPUInfo,
    getMemoryUsage,
    getStorageInfo,
    getSystemInfo
} from "../services/api";

import type {
    CPUResponse,
    MemoryResponse,
    StorageResponse,
    SystemResponse
} from "../services/api";


export default function Dashboard() {
    const [cpu, setCPU] = useState<CPUResponse | null>(null);
    const [memory, setMemory] = useState<MemoryResponse | null>(null);
    const [storage, setStorage] = useState<StorageResponse | null>(null);
    const [system, setSystem] = useState<SystemResponse | null>(null);

    const [errors, setErrors] = useState<string[]>([]);

    useEffect(() => {
        let active = true;
        let timer: ReturnType<typeof setTimeout>;

        async function updateSystem() {
            const results = await Promise.allSettled([
                getCPUInfo(),
                getMemoryUsage(),
                getStorageInfo(),
                getSystemInfo()
            ]);

            if (!active) return;

            const [
                cpuResult,
                memoryResult,
                storageResult,
                systemResult
            ] = results;

            const failures: string[] = [];

            if (cpuResult.status === "fulfilled") {
                setCPU(cpuResult.value);
            } else {
                failures.push("CPU");
            }

            if (memoryResult.status === "fulfilled") {
                setMemory(memoryResult.value);
            } else {
                failures.push("Memory");
            }

            if (storageResult.status === "fulfilled") {
                setStorage(storageResult.value);
            } else {
                failures.push("Storage");
            }

            if (systemResult.status === "fulfilled") {
                setSystem(systemResult.value);
            } else {
                failures.push("System");
            }

            setErrors(failures);

            timer = setTimeout(() => {
                void updateSystem();
            }, 3000);
        }

        void updateSystem();

        return () => {
            active = false;
            clearTimeout(timer);
        };
    }, []);

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