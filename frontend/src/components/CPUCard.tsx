import type { CPUResponse } from "../services/api";
import { Cpu } from "lucide-react";
import { memo, useState } from "react";

interface CPUCardProps { cpu: CPUResponse | null; }
type View = "overview" | "performance";

function CPUCard({ cpu }: CPUCardProps) {
    const [view, setView] = useState<View>("overview");
    const overview = view === "overview";
    const samples = cpu?.per_logical_cpu_usage ?? [];
    const peak = samples.length ? Math.max(...samples) : null;
    const average = samples.length ? samples.reduce((sum, value) => sum + value, 0) / samples.length : null;

    return (
        <section className="metric-card cpu-card">
            <h2 className="card-title"><Cpu size={22} />CPU</h2>
            {cpu === null ? <p className="metric-empty">Loading CPU...</p> : (
                <>
                    <div className="cpu-card-content">
                        <div className="cpu-device-name">
                            <p className="metric-lead">{cpu.name ?? "Unknown Processor"}</p>
                        </div>
                        <div className="cpu-primary-stat">
                            <p className="metric-primary">
                                {overview ? `${cpu.usage.toFixed(1)}%` : peak === null ? "N/A" : `${peak.toFixed(1)}%`}
                            </p>
                            <p className="metric-lead">
                                {overview ? "Total CPU Utilization" : "Busiest Logical CPU"}
                            </p>
                            <div className="cpu-progress-slot">
                                {(overview || peak !== null) && (
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
                            ) : (
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
                            )}
                        </dl>
                    </div>
                    <div className="cpu-view-switch" role="group" aria-label="CPU metrics view">
                        <button type="button" className={overview ? "cpu-view-button is-active" : "cpu-view-button"}
                            aria-pressed={overview} onClick={() => setView("overview")}>Overview</button>
                        <button type="button" className={!overview ? "cpu-view-button is-active" : "cpu-view-button"}
                            aria-pressed={!overview} onClick={() => setView("performance")}>Performance</button>
                    </div>
                </>
            )}
        </section>
    );
}

export default memo(CPUCard);
