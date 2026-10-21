import { memo, useState } from "react";
import { ChevronLeft, ChevronRight, CircuitBoard } from "lucide-react";
import type { GPUDeviceResponse } from "../services/api";

interface GPUCardProps { gpus: GPUDeviceResponse[] | null; }

function GPUCard({ gpus }: GPUCardProps) {
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const devices = gpus ?? [];
    const index = Math.max(0, devices.findIndex((gpu) => gpu.id === selectedId));
    const gpu = devices[index];

    const select = (offset: number) => {
        if (!devices.length) return;
        setSelectedId(devices[(index + offset + devices.length) % devices.length].id);
    };

    const toGiB = (bytes: number | null) => bytes === null ? "N/A" : `${(bytes / 1024 ** 3).toFixed(1)} GiB`;

    return (
        <section className="metric-card">
            <div className="gpu-card-header">
                <h2 className="card-title"><CircuitBoard size={22} />GPU</h2>
                {devices.length > 1 && (
                    <div className="gpu-navigation">
                        <button type="button" aria-label="Previous GPU" onClick={() => select(-1)}><ChevronLeft size={18} /></button>
                        <span aria-live="polite">{index + 1} / {devices.length}</span>
                        <button type="button" aria-label="Next GPU" onClick={() => select(1)}><ChevronRight size={18} /></button>
                    </div>
                )}
            </div>
            {gpus === null ? <p className="metric-empty">Loading GPU...</p> : !gpu ? (
                <p className="metric-empty">GPU monitoring unavailable</p>
            ) : (
                <>
                    <p className="metric-lead">{gpu.name ?? "Graphics Processor"}</p>
                    {gpu.gpu_type && <p className="gpu-type-label">{gpu.gpu_type === "integrated" ? "Integrated GPU" : "Dedicated GPU"}</p>}
                    <p className="metric-primary">{gpu.usage === null ? "N/A" : `${gpu.usage.toFixed(1)}%`}</p>
                    <p className="metric-lead">{gpu.usage_label ?? "GPU Utilization"}</p>
                    {gpu.usage !== null && <progress className="usage-progress" value={gpu.usage} max={100} aria-label={gpu.usage_label ?? "GPU utilization"} />}
                    <dl className="metric-details">
                        <div className="detail-row"><dt>VRAM Used</dt><dd>{toGiB(gpu.memory_used)}</dd></div>
                        <div className="detail-row"><dt>VRAM Total</dt><dd>{toGiB(gpu.memory_total)}</dd></div>
                        <div className="detail-row"><dt>Temperature</dt><dd>{gpu.temperature_c === null ? "N/A" : `${gpu.temperature_c}°C`}</dd></div>
                    </dl>
                </>
            )}
        </section>
    );
}

export default memo(GPUCard);
