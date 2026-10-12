import type { CPUResponse } from "../services/api";
import { Cpu } from "lucide-react";
import { memo } from "react";

interface CPUCardProps {
    cpu: CPUResponse | null;
}

function CPUCard({ cpu }: CPUCardProps) {
    return (
        <section className="metric-card">
            <h2 className="card-title">
                <Cpu size={22} />
                CPU
            </h2>

            {cpu === null ? (
                <p className="metric-empty">Loading CPU...</p>
            ) : (
                <>
                    <p className="metric-lead">
                        {cpu.name ?? "Unknown Processor"}
                    </p>

                    <p className="metric-primary">
                        {cpu.usage.toFixed(1)}%
                    </p>

                    <progress
                        className="usage-progress"
                        value={cpu.usage}
                        max={100}
                        aria-label="CPU utilization"
                    />

                    <dl className="metric-details">
                        <div className="detail-row">
                            <dt>Physical Cores</dt>
                            <dd>{cpu.physical_cores ?? "N/A"}</dd>
                        </div>

                        <div className="detail-row">
                            <dt>Logical Cores</dt>
                            <dd>{cpu.logical_cores ?? "N/A"}</dd>
                        </div>

                        <div className="detail-row">
                            <dt>Frequency</dt>
                            <dd>
                                {cpu.frequency_mhz === null
                                    ? "N/A"
                                    : `${(cpu.frequency_mhz / 1000).toFixed(2)} GHz`}
                            </dd>
                        </div>
                    </dl>
                </>
            )}
        </section>
    );
}

export default memo(CPUCard);