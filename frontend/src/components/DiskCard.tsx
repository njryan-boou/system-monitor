import type { StorageResponse } from "../services/api";
import { HardDrive } from "lucide-react";
import { memo } from "react";

interface DiskCardProps {
    storage: StorageResponse | null;
}

function DiskCard({ storage }: DiskCardProps) {
    const toGiB = (bytes: number): string => {
        return (bytes / (1024 ** 3)).toFixed(1);
    };

    return (
        <section className="metric-card">
            <h2 className="card-title">
                <HardDrive size={22} />
                Storage
            </h2>

            {storage === null ? (
                <p className="metric-empty">Loading storage...</p>
            ) : (
                <>
                    <p className="metric-lead">
                        Volume: {storage.volume}
                    </p>

                    <p className="metric-primary">
                        {storage.percent.toFixed(1)}%
                    </p>

                    <progress
                        className="usage-progress"
                        value={storage.percent}
                        max={100}
                        aria-label="Storage utilization"
                    />

                    <dl className="metric-details">
                        <div className="detail-row">
                            <dt>Used</dt>
                            <dd>{toGiB(storage.used)} GiB</dd>
                        </div>

                        <div className="detail-row">
                            <dt>Available</dt>
                            <dd>{toGiB(storage.free)} GiB</dd>
                        </div>

                        <div className="detail-row">
                            <dt>Total</dt>
                            <dd>{toGiB(storage.total)} GiB</dd>
                        </div>
                    </dl>
                </>
            )}
        </section>
    );
}

export default memo(DiskCard);