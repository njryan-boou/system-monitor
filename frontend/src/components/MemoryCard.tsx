import type { MemoryResponse } from "../services/api";
import { MemoryStick } from "lucide-react";

interface MemoryCardProps {
    memory: MemoryResponse | null;
}

export default function MemoryCard({ memory }: MemoryCardProps) {
    const toGiB = (bytes: number): string => {
        return (bytes / (1024 ** 3)).toFixed(1);
    };

    return (
        <section className="metric-card">
            <h2 className="card-title">
                <MemoryStick size={22} />
                Memory
            </h2>

            {memory === null ? (
                <p className="metric-empty">Loading memory...</p>
            ) : (
                <>
                    <p className="metric-lead">
                        RAM Utilization
                    </p>

                    <p className="metric-primary">
                        {memory.percent.toFixed(1)}%
                    </p>

                    <progress
                        className="usage-progress"
                        value={memory.percent}
                        max={100}
                        aria-label="Memory utilization"
                    />

                    <dl className="metric-details">
                        <div className="detail-row">
                            <dt>Used</dt>
                            <dd>{toGiB(memory.used)} GiB</dd>
                        </div>

                        <div className="detail-row">
                            <dt>Available</dt>
                            <dd>{toGiB(memory.available)} GiB</dd>
                        </div>

                        <div className="detail-row">
                            <dt>Total</dt>
                            <dd>{toGiB(memory.total)} GiB</dd>
                        </div>
                    </dl>
                </>
            )}
        </section>
    );
}