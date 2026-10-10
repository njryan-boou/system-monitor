import type { SystemResponse } from "../services/api";
import { Monitor } from "lucide-react";

interface SystemCardProps {
    system: SystemResponse | null;
}

export default function SystemCard({ system }: SystemCardProps) {
    const formatUptime = (seconds: number): string => {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);

        return `${days}d ${hours}h ${minutes}m`;
    };

    return (
        <section className="metric-card">
            <h2 className="card-title">
                <Monitor size={22} />
                System
            </h2>

            {system === null ? (
                <p className="metric-empty">Loading system...</p>
            ) : (
                <>
                    <p className="metric-lead">
                        Operating System
                    </p>

                    <p className="metric-primary">
                        {system.os}
                    </p>

                    <dl className="metric-details">
                        <div className="detail-row">
                            <dt>OS Release</dt>
                            <dd>{system.os_release}</dd>
                        </div>

                        <div className="detail-row">
                            <dt>Architecture</dt>
                            <dd>{system.architecture}</dd>
                        </div>

                        <div className="detail-row">
                            <dt>Uptime</dt>
                            <dd>{formatUptime(system.uptime)}</dd>
                        </div>
                    </dl>
                </>
            )}
        </section>
    );
}