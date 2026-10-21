import { memo, useState } from "react";
import { ChevronLeft, ChevronRight, CircuitBoard } from "lucide-react";
import type { GPUDeviceResponse } from "../services/api";

interface GPUCardProps {
    gpus: GPUDeviceResponse[] | null;
}

type MetricView = "overview" | "performance";

function GPUCard({ gpus }: GPUCardProps) {
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [view, setView] = useState<MetricView>("overview");
    const devices = gpus ?? [];
    const index = Math.max(0, devices.findIndex((gpu) => gpu.id === selectedId));
    const gpu = devices[index];

    const select = (offset: number) => {
        if (!devices.length) return;
        setSelectedId(devices[(index + offset + devices.length) % devices.length].id);
    };

    const toGiB = (bytes: number | null) =>
        bytes === null ? "N/A" : `${(bytes / 1024 ** 3).toFixed(1)} GiB`;

    const toResidentMemory = (bytes: number | null) => {
        if (bytes === null) return "N/A";
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KiB`;
        if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MiB`;
        return toGiB(bytes);
    };

    const overview = view === "overview";
    const activeClock = gpu?.clock_mhz;
    const maxClock = gpu?.max_clock_mhz;
    const clockPercent = activeClock != null && maxClock != null && maxClock > 0
        ? Math.max(0, Math.min(100, activeClock / maxClock * 100))
        : null;

    return (
        <section className="metric-card gpu-card">
            <div className="gpu-card-header">
                {devices.length > 1 && (
                    <nav className="gpu-navigation" aria-label="Choose GPU">
                        <button type="button" aria-label="Previous GPU" onClick={() => select(-1)}>
                            <ChevronLeft size={18} />
                        </button>
                        <span aria-live="polite">{index + 1} / {devices.length}</span>
                        <button type="button" aria-label="Next GPU" onClick={() => select(1)}>
                            <ChevronRight size={18} />
                        </button>
                    </nav>
                )}
                <h2 className="card-title"><CircuitBoard size={22} />GPU</h2>
            </div>

            {gpus === null ? (
                <p className="metric-empty">Loading GPU...</p>
            ) : !gpu ? (
                <p className="metric-empty">GPU monitoring unavailable</p>
            ) : (
                <>
                    <div className="gpu-card-content">
                        <div className="gpu-device-identity">
                            <p className="metric-lead">{gpu.name ?? "Graphics Processor"}</p>
                            {gpu.gpu_type && (
                                <p className="gpu-type-label">
                                    {gpu.gpu_type === "integrated" ? "Integrated GPU" : "Dedicated GPU"}
                                </p>
                            )}
                        </div>

                        <div className="gpu-primary-stat">
                            <p className="metric-primary">
                                {overview
                                    ? gpu.usage === null ? "N/A" : `${gpu.usage.toFixed(1)}%`
                                    : activeClock == null ? "N/A" : `${activeClock.toFixed(0)} MHz`}
                            </p>
                            <p className="metric-lead">
                                {overview ? (gpu.usage_label ?? "GPU Utilization") : "Current GPU Clock"}
                            </p>
                            <div className="gpu-progress-slot">
                                {overview && gpu.usage !== null && (
                                    <progress
                                        className="usage-progress"
                                        value={gpu.usage}
                                        max={100}
                                        aria-label={gpu.usage_label ?? "GPU utilization"}
                                    />
                                )}
                                {!overview && clockPercent !== null && (
                                    <progress
                                        className="usage-progress"
                                        value={clockPercent}
                                        max={100}
                                        aria-label="Current GPU clock as a percentage of maximum clock"
                                    />
                                )}
                            </div>
                        </div>

                        <dl className="metric-details gpu-metric-details">
                            {overview ? (
                                <>
                                    <div className="detail-row">
                                        <dt title={gpu.memory_label ? "Largest accessible GPU client resident memory, not total device memory." : undefined}>
                                            {gpu.memory_label ? "Client Memory Used" : "VRAM Used"}
                                        </dt>
                                        <dd>{gpu.memory_label ? toResidentMemory(gpu.memory_used) : toGiB(gpu.memory_used)}</dd>
                                    </div>
                                    <div className="detail-row">
                                        <dt>{gpu.memory_label ? "GPU Memory Total" : "VRAM Total"}</dt>
                                        <dd>{toGiB(gpu.memory_total)}</dd>
                                    </div>
                                    <div className="detail-row">
                                        <dt>Temperature</dt>
                                        <dd>{gpu.temperature_c == null ? "N/A" : `${gpu.temperature_c}°C`}</dd>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="detail-row">
                                        <dt>Maximum Clock</dt>
                                        <dd>{maxClock == null ? "N/A" : `${maxClock.toFixed(0)} MHz`}</dd>
                                    </div>
                                    <div className="detail-row">
                                        <dt>GPU Power</dt>
                                        <dd>{gpu.power_watts == null ? "N/A" : `${gpu.power_watts.toFixed(2)} W`}</dd>
                                    </div>
                                    <div className="detail-row">
                                        <dt>Temperature</dt>
                                        <dd>{gpu.temperature_c == null ? "N/A" : `${gpu.temperature_c}°C`}</dd>
                                    </div>
                                </>
                            )}
                        </dl>
                    </div>

                    <div className="gpu-view-switch" role="group" aria-label="GPU metrics view">
                        <button
                            type="button"
                            className={overview ? "gpu-view-button is-active" : "gpu-view-button"}
                            aria-pressed={overview}
                            onClick={() => setView("overview")}
                        >
                            Overview
                        </button>
                        <button
                            type="button"
                            className={!overview ? "gpu-view-button is-active" : "gpu-view-button"}
                            aria-pressed={!overview}
                            onClick={() => setView("performance")}
                        >
                            Performance
                        </button>
                    </div>
                </>
            )}
        </section>
    );
}

export default memo(GPUCard);
