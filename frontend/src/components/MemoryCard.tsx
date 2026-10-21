import type { MemoryResponse } from "../services/api";
import { MemoryStick } from "lucide-react";
import { memo, useState } from "react";

interface MemoryCardProps {
    memory: MemoryResponse | null;
}
type MemoryView = "overview" | "performance";

function MemoryCard({ memory }: MemoryCardProps) {
    const [view, setView] = useState<MemoryView>("overview");
    const overview = view === "overview";
    const toGiB = (bytes: number | null | undefined) =>
        bytes == null ? "N/A" : `${(bytes / 1024 ** 3).toFixed(1)} GiB`;
    const swapTotal = memory?.swap_total ?? 0;
    const swapPercent = memory?.swap_percent ?? null;

    return (
        <section className="metric-card memory-card">
            <h2 className="card-title"><MemoryStick size={22} />Memory</h2>

            {memory === null ? (
                <p className="metric-empty">Loading memory...</p>
            ) : (
                <>
                    <div className="memory-card-content">
                        <div className="memory-device-name">
                            <p className="metric-lead">{overview ? "RAM Utilization" : "Swap Utilization"}</p>
                        </div>
                        <div className="memory-primary-stat">
                            <p className="metric-primary">
                                {overview ? `${memory.percent.toFixed(1)}%` :
                                    swapTotal === 0 ? "Not configured" :
                                    swapPercent == null ? "N/A" : `${swapPercent.toFixed(1)}%`}
                            </p>
                            <p className="metric-lead">
                                {overview ? "Physical Memory" : "Virtual Memory Swap"}
                            </p>
                            <div className="memory-progress-slot">
                                {(overview || swapPercent !== null) && (
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
                            ) : (
                                <>
                                    <div className="detail-row"><dt>Cached RAM</dt><dd>{toGiB(memory.cached)}</dd></div>
                                    <div className="detail-row"><dt>Swap Used</dt><dd>{toGiB(memory.swap_used)}</dd></div>
                                    <div className="detail-row"><dt>Swap Total</dt><dd>{toGiB(memory.swap_total)}</dd></div>
                                </>
                            )}
                        </dl>
                    </div>
                    <div className="memory-view-switch" role="group" aria-label="Memory metrics view">
                        <button type="button" className={overview ? "memory-view-button is-active" : "memory-view-button"}
                            aria-pressed={overview} onClick={() => setView("overview")}>Overview</button>
                        <button type="button" className={!overview ? "memory-view-button is-active" : "memory-view-button"}
                            aria-pressed={!overview} onClick={() => setView("performance")}>Performance</button>
                    </div>
                </>
            )}
        </section>
    );
}

export default memo(MemoryCard);
