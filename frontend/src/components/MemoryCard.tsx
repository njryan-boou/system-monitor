import type { MemoryResponse } from "../services/api";
import { MemoryStick } from "lucide-react";
import { memo, useState } from "react";

interface MemoryCardProps {
    memory: MemoryResponse | null;
}
type MemoryView = "overview" | "performance" | "hardware";

const toGiB = (bytes: number | null | undefined) =>
    bytes == null ? "N/A" : `${(bytes / 1024 ** 3).toFixed(1)} GiB`;
const transferRate = (mtps: number | null | undefined) =>
    mtps == null ? "N/A" : `${mtps.toLocaleString()} MT/s`;

function MemoryCard({ memory }: MemoryCardProps) {
    const [view, setView] = useState<MemoryView>("overview");
    const overview = view === "overview";
    const performance = view === "performance";
    const swapTotal = memory?.swap_total ?? 0;
    const swapPercent = memory?.swap_percent ?? null;
    const modules = memory?.memory_modules ?? [];

    return (
        <section className="metric-card memory-card">
            <h2 className="card-title"><MemoryStick size={22} />Memory</h2>

            {memory === null ? (
                <p className="metric-empty">Loading memory...</p>
            ) : (
                <>
                    <div className="memory-card-content">
                        <div className="memory-device-name">
                            <p className="metric-lead">{overview ? "RAM Utilization" : performance ? "Swap Utilization" : "Installed RAM Hardware"}</p>
                        </div>
                        <div className="memory-primary-stat">
                            <p className="metric-primary">
                                {overview ? `${memory.percent.toFixed(1)}%` :
                                    performance ? (
                                        swapTotal === 0 ? "Not configured" :
                                        swapPercent == null ? "N/A" : `${swapPercent.toFixed(1)}%`
                                    ) :
                                    memory.memory_type ?? "N/A"}
                            </p>
                            <p className="metric-lead">
                                {overview ? "Physical Memory" : performance ? "Virtual Memory Swap" : "Memory Generation"}
                            </p>
                            <div className="memory-progress-slot">
                                {(overview || (performance && swapPercent !== null)) && (
                                    <progress
                                        className="usage-progress"
                                        value={overview ? memory.percent : swapPercent ?? 0}
                                        max={100}
                                        aria-label={overview ? "RAM utilization" : "Swap utilization"}
                                    />
                                )}
                            </div>
                        </div>

                        <dl className="metric-details memory-metric-details">
                            {overview ? (
                                <>
                                    <div className="detail-row"><dt>Used</dt><dd>{toGiB(memory.used)}</dd></div>
                                    <div className="detail-row"><dt>Available</dt><dd>{toGiB(memory.available)}</dd></div>
                                    <div className="detail-row"><dt>Total</dt><dd>{toGiB(memory.total)}</dd></div>
                                </>
                            ) : performance ? (
                                <>
                                    <div className="detail-row"><dt>Cached RAM</dt><dd>{toGiB(memory.cached)}</dd></div>
                                    <div className="detail-row"><dt>Swap Used</dt><dd>{toGiB(memory.swap_used)}</dd></div>
                                    <div className="detail-row"><dt>Swap Total</dt><dd>{toGiB(memory.swap_total)}</dd></div>
                                </>
                            ) : (
                                <>
                                    <div className="detail-row"><dt>Installed Modules</dt>
                                        <dd>{memory.memory_module_count ?? "N/A"}</dd>
                                    </div>
                                    <div className="detail-row"><dt>Configured Speed</dt>
                                        <dd>{transferRate(memory.memory_speed_mtps)}</dd>
                                    </div>
                                    {modules.map((module, index) => (
                                        <div className="detail-row" key={index}>
                                            <dt title={module.slot ?? undefined}>{module.slot ?? `Module ${index + 1}`}</dt>
                                            <dd className="memory-module-spec">
                                                <span>{toGiB(module.capacity_bytes)}{module.memory_type && memory.memory_type === "Mixed" ? ` · ${module.memory_type}` : ""}</span>
                                                <span>{transferRate(module.speed_mtps)}</span>
                                                <span title={module.manufacturer ?? undefined}>{module.manufacturer ?? "Manufacturer N/A"}</span>
                                            </dd>
                                        </div>
                                    ))}
                                    {modules.length === 0 && (
                                        <div className="detail-row">
                                            <dt>Module details</dt><dd>Unavailable (SMBIOS access)</dd>
                                        </div>
                                    )}
                                    {memory.memory_hardware_source === "snapshot" && (
                                        <div className="detail-row"><dt>Source</dt><dd>Local snapshot</dd></div>
                                    )}
                                </>
                            )}
                        </dl>
                    </div>
                    <div className="memory-view-switch" role="group" aria-label="Memory metrics view">
                        <button type="button" className={overview ? "memory-view-button is-active" : "memory-view-button"}
                            aria-pressed={overview} onClick={() => setView("overview")}>Overview</button>
                        <button type="button" className={performance ? "memory-view-button is-active" : "memory-view-button"}
                            aria-pressed={performance} onClick={() => setView("performance")}>Performance</button>
                        <button type="button" className={view === "hardware" ? "memory-view-button is-active" : "memory-view-button"}
                            aria-pressed={view === "hardware"} onClick={() => setView("hardware")}>Hardware</button>
                    </div>
                </>
            )}
        </section>
    );
}

export default memo(MemoryCard);
