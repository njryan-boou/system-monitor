import { memo, useState } from "react";
import { ChevronLeft, ChevronRight, CircuitBoard } from "lucide-react";
import type { GPUDeviceResponse } from "../services/api";

interface GPUCardProps {
    gpus: GPUDeviceResponse[] | null;
}

type MetricView = "overview" | "performance" | "memory";

const validBytes = (value: number | null | undefined): value is number =>
    value != null && Number.isFinite(value) && value >= 0;

const toGiB = (bytes: number | null | undefined): string =>
    validBytes(bytes) ? `${(bytes / 1024 ** 3).toFixed(1)} GiB` : "N/A";

const toResidentMemory = (bytes: number | null | undefined): string => {
    if (!validBytes(bytes)) return "N/A";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KiB`;
    if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MiB`;
    return toGiB(bytes);
};

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

    const overview = view === "overview";
    const performance = view === "performance";
    const memory = view === "memory";
    const activeClock = gpu?.clock_mhz;
    const maxClock = gpu?.max_clock_mhz;
    const clockPercent = activeClock != null && maxClock != null && maxClock > 0
        ? Math.max(0, Math.min(100, activeClock / maxClock * 100))
        : null;

    // Intel Xe's memory_used is the *largest accessible DRM client's* resident
    // memory, not whole-device memory. Never derive VRAM capacity or utilization
    // from such samples (nor from a missing/invalid memory_total).
    const clientResident = Boolean(gpu?.memory_label);
    const memoryUsed = gpu?.memory_used;
    const memoryTotal = gpu?.memory_total;
    const hasDeviceMemory = !clientResident &&
        validBytes(memoryUsed) && validBytes(memoryTotal) &&
        memoryTotal > 0 && memoryUsed <= memoryTotal;
    const memoryPercent = hasDeviceMemory
        ? 100 * (memoryUsed! / memoryTotal!)
        : null;
    const memoryFree = hasDeviceMemory
        ? memoryTotal! - memoryUsed!
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
                            <p className="metric-lead" title={gpu.name ?? undefined}>{gpu.name ?? "Graphics Processor"}</p>
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
                                    : performance
                                        ? activeClock == null ? "N/A" : `${activeClock.toFixed(0)} MHz`
                                        : memoryPercent !== null
                                            ? `${memoryPercent.toFixed(1)}%`
                                            : toResidentMemory(gpu.memory_used)}
                            </p>
                            <p className="metric-lead">
                                {overview
                                    ? (gpu.usage_label ?? "GPU Utilization")
                                    : performance ? "Current GPU Clock"
                                        : memoryPercent !== null ? "Reported VRAM Utilization"
                                            : clientResident ? "Largest Accessible Client Resident Memory"
                                                : "Reported GPU Memory Used"}
                            </p>
                            <div className="gpu-progress-slot">
                                {overview && gpu.usage !== null && (
                                    <progress className="usage-progress" value={gpu.usage} max={100}
                                        aria-label={gpu.usage_label ?? "GPU utilization"} />
                                )}
                                {performance && clockPercent !== null && (
                                    <progress className="usage-progress" value={clockPercent} max={100}
                                        aria-label="Current GPU clock as a percentage of maximum clock" />
                                )}
                                {memory && memoryPercent !== null && (
                                    <progress className="usage-progress" value={memoryPercent} max={100}
                                        aria-label="Reported VRAM utilization" />
                                )}
                            </div>
                        </div>

                        <dl className="metric-details gpu-metric-details">
                            {overview ? (
                                <>
                                    <div className="detail-row">
                                        <dt>Temperature</dt>
                                        <dd>{gpu.temperature_c == null ? "N/A" : `${gpu.temperature_c}°C`}</dd>
                                    </div>
                                    <div className="detail-row">
                                        <dt>GPU Power</dt>
                                        <dd>{gpu.power_watts == null ? "N/A" : `${gpu.power_watts.toFixed(2)} W`}</dd>
                                    </div>
                                    <div className="detail-row">
                                        <dt>GPU Type</dt>
                                        <dd>{gpu.gpu_type === "integrated" ? "Integrated" : gpu.gpu_type === "dedicated" ? "Dedicated" : "N/A"}</dd>
                                    </div>
                                </>
                            ) : performance ? (
                                <>
                                    <div className="detail-row">
                                        <dt>Maximum Clock</dt>
                                        <dd>{maxClock == null ? "N/A" : `${maxClock.toFixed(0)} MHz`}</dd>
                                    </div>
                                    <div className="detail-row">
                                        <dt>Memory Clock</dt>
                                        <dd>{gpu.memory_clock_mhz == null ? "N/A" : `${gpu.memory_clock_mhz.toFixed(0)} MHz`}</dd>
                                    </div>
                                    <div className="detail-row">
                                        <dt>Clock vs Max</dt>
                                        <dd>{clockPercent == null ? "N/A" : `${clockPercent.toFixed(1)}%`}</dd>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="detail-row">
                                        <dt>{clientResident ? "Client Resident" : "VRAM Used"}</dt>
                                        <dd>{toResidentMemory(gpu.memory_used)}</dd>
                                    </div>
                                    <div className="detail-row">
                                        <dt>VRAM Available</dt>
                                        <dd>{toResidentMemory(memoryFree)}</dd>
                                    </div>
                                    <div className="detail-row">
                                        <dt>VRAM Capacity</dt>
                                        <dd>{clientResident ? "N/A" : toResidentMemory(gpu.memory_total)}</dd>
                                    </div>
                                    {clientResident && (
                                        <div className="detail-row">
                                            <dt>Measurement</dt>
                                            <dd>Largest accessible client, not total GPU memory</dd>
                                        </div>
                                    )}
                                    {!clientResident && gpu.gpu_type === "integrated" && (
                                        <div className="detail-row">
                                            <dt>Measurement</dt>
                                            <dd>Driver-reported VRAM region, not all shared RAM</dd>
                                        </div>
                                    )}
                                </>
                            )}
                        </dl>
                    </div>

                    <div className="gpu-view-switch" role="group" aria-label="GPU metrics view">
                        <button type="button" className={overview ? "gpu-view-button is-active" : "gpu-view-button"}
                            aria-pressed={overview} onClick={() => setView("overview")}>Overview</button>
                        <button type="button" className={performance ? "gpu-view-button is-active" : "gpu-view-button"}
                            aria-pressed={performance} onClick={() => setView("performance")}>Performance</button>
                        <button type="button" className={memory ? "gpu-view-button is-active" : "gpu-view-button"}
                            aria-pressed={memory} onClick={() => setView("memory")}>Memory</button>
                    </div>
                </>
            )}
        </section>
    );
}

export default memo(GPUCard);
