import { memo } from "react";
import { CircuitBoard } from "lucide-react";

import type { GPUResponse } from "../services/api";

interface GPUCardProps {
    gpu: GPUResponse | null;
}

function GPUCard({ gpu }: GPUCardProps) {
    const toGiB = (bytes: number | null): string => {
        if (bytes === null) return "N/A";

        return `${(bytes / (1024 ** 3)).toFixed(1)} GiB`;
    };

    return (
        <section className="metric-card">
            <h2 className="card-title">
                <CircuitBoard size={22} />
                GPU
            </h2>

            {gpu === null ? (
                <p className="metric-empty">Loading GPU...</p>
            ) : !gpu.available ? (
                <p className="metric-empty">
                    GPU monitoring unavailable
                </p>
            ) : (
                <>
                    <p className="metric-lead">
                        {gpu.name ?? "Graphics Processor"}
                    </p>

                    <p className="metric-primary">
                        {gpu.usage !== null
                            ? `${gpu.usage.toFixed(1)}%`
                            : "N/A"}
                    </p>

                    <p className="metric-lead">
                        {gpu.usage_label ?? "GPU Utilization"}
                    </p>

                    <progress
                        className="usage-progress"
                        value={gpu.usage ?? 0}
                        max={100}
                        aria-label="GPU utilization"
                    />

                    <dl className="metric-details">
                        <div className="detail-row">
                            <dt>VRAM Used</dt>
                            <dd>{toGiB(gpu.memory_used)}</dd>
                        </div>

                        <div className="detail-row">
                            <dt>VRAM Total</dt>
                            <dd>{toGiB(gpu.memory_total)}</dd>
                        </div>

                        <div className="detail-row">
                            <dt>Temperature</dt>
                            <dd>
                                {gpu.temperature_c !== null
                                    ? `${gpu.temperature_c}°C`
                                    : "N/A"}
                            </dd>
                        </div>
                    </dl>
                </>
            )}
        </section>
    );
}

export default memo(GPUCard);