import type { CPUResponse } from "../services/api";
import { Cpu } from "lucide-react";
import { memo, useState } from "react";

interface CPUCardProps { cpu: CPUResponse | null; }
type View = "overview" | "performance" | "cache";

function formatCache(bytes: number | null | undefined): string {
    if (bytes == null) return "N/A";
    const units = ["B", "KiB", "MiB", "GiB"];
    let value = bytes;
    let index = 0;
    while (value >= 1024 && index < units.length - 1) {
        value /= 1024;
        index += 1;
    }
    return `${value.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${units[index]}`;
}

function CPUCard({ cpu }: CPUCardProps) {
    const [view, setView] = useState<View>("overview");
    const overview = view === "overview";
    const performance = view === "performance";
    const samples = cpu?.per_logical_cpu_usage ?? [];
    const peak = samples.length ? Math.max(...samples) : null;
    const average = samples.length
        ? samples.reduce((sum, value) => sum + value, 0) / samples.length
        : null;

    return (
        <section className="metric-card cpu-card">
            <h2 className="card-title"><Cpu size={22} />CPU</h2>
            {cpu === null ? <p className="metric-empty">Loading CPU...</p> : (
                <>
                    <div className="cpu-card-content">
                        <div className="cpu-device-name">
                            <p className="metric-lead" title={cpu.name ?? undefined}>{cpu.name ?? "Unknown Processor"}</p>
                        </div>
                        <div className="cpu-primary-stat">
                            <p className="metric-primary">
                                {overview ? `${cpu.usage.toFixed(1)}%` :
                                    performance ? (peak === null ? "N/A" : `${peak.toFixed(1)}%`) :
                                    formatCache(cpu.cache_l3_bytes)}
                            </p>
                            <p className="metric-lead">
                                {overview ? "Total CPU Utilization" :
                                    performance ? "Busiest Logical CPU" : "Total L3 Cache"}
                            </p>
                            <div className="cpu-progress-slot">
                                {(overview || (performance && peak !== null)) && (
                                    <progress className="usage-progress"
                                        value={overview ? cpu.usage : peak ?? 0}
                                        max={100}
                                        aria-label={overview ? "Total CPU utilization" : "Busiest logical CPU utilization"}
                                    />
                                )}
                            </div>
                        </div>
                        <dl className="metric-details cpu-metric-details">
                            {overview ? (
                                <>
                                    <div className="detail-row"><dt>Physical Cores</dt><dd>{cpu.physical_cores ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>Logical Cores</dt><dd>{cpu.logical_cores ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>Frequency</dt>
                                        <dd>{cpu.frequency_mhz == null ? "N/A" : `${(cpu.frequency_mhz / 1000).toFixed(2)} GHz`}</dd>
                                    </div>
                                </>
                            ) : performance ? (
                                <>
                                    <div className="detail-row"><dt>CPU Temperature</dt>
                                        <dd>{cpu.temperature_c == null ? "N/A" : `${cpu.temperature_c.toFixed(1)}°C`}</dd>
                                    </div>
                                    <div className="detail-row"><dt>Average Thread Usage</dt>
                                        <dd>{average === null ? "N/A" : `${average.toFixed(1)}%`}</dd>
                                    </div>
                                    <div className="detail-row"><dt>Load Average (1m)</dt>
                                        <dd>{cpu.load_average_1m == null ? "N/A" : cpu.load_average_1m.toFixed(2)}</dd>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="detail-row"><dt>L1 Data</dt><dd>{formatCache(cpu.cache_l1_data_bytes)}</dd></div>
                                    <div className="detail-row"><dt>L1 Instruction</dt><dd>{formatCache(cpu.cache_l1_instruction_bytes)}</dd></div>
                                    {cpu.cache_l1_unified_bytes != null && (
                                        <div className="detail-row"><dt>L1 Unified</dt><dd>{formatCache(cpu.cache_l1_unified_bytes)}</dd></div>
                                    )}
                                    <div className="detail-row"><dt>L2 Cache</dt><dd>{formatCache(cpu.cache_l2_bytes)}</dd></div>
                                    <div className="detail-row"><dt>L3 Groups</dt><dd>{cpu.cache_l3_groups ?? "N/A"}</dd></div>
                                </>
                            )}
                        </dl>
                    </div>
                    <div className="cpu-view-switch" role="group" aria-label="CPU metrics view">
                        <button type="button" className={overview ? "cpu-view-button is-active" : "cpu-view-button"}
                            aria-pressed={overview} onClick={() => setView("overview")}>Overview</button>
                        <button type="button" className={performance ? "cpu-view-button is-active" : "cpu-view-button"}
                            aria-pressed={performance} onClick={() => setView("performance")}>Performance</button>
                        <button type="button" className={view === "cache" ? "cpu-view-button is-active" : "cpu-view-button"}
                            aria-pressed={view === "cache"} onClick={() => setView("cache")}>Cache</button>
                    </div>
                </>
            )}
        </section>
    );
}

export default memo(CPUCard);
