import { useEffect, useState } from "react";

import CPUCard from "../components/CPUCard";
import MemoryCard from "../components/MemoryCard";

import {
    getCPUUsage,
    getMemoryUsage
} from "../services/api";

import type { MemoryResponse } from "../services/api";

export default function Dashboard() {
    const [cpuUsage, setCPUUsage] = useState<number | null>(null);
    const [memory, setMemory] = useState<MemoryResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let active = true;

        async function updateSystem() {
            try {
                const [cpuData, memoryData] = await Promise.all([
                    getCPUUsage(),
                    getMemoryUsage()
                ]);

                if (active) {
                    setCPUUsage(cpuData.usage);
                    setMemory(memoryData);
                    setError(null);
                }
            } catch {
                if (active) {
                    setError("Failed to retrieve system information");
                }
            }
        }

        void updateSystem();

        const interval = setInterval(() => {
            void updateSystem();
        }, 3000);

        return () => {
            active = false;
            clearInterval(interval);
        };
    }, []);

    return (
        <main>
            <h1>System Monitor</h1>

            {error && <p role="alert">{error}</p>}

            <div className="metric-grid">
                <CPUCard usage={cpuUsage} />
                <MemoryCard memory={memory} />
            </div>
        </main>
    );
}