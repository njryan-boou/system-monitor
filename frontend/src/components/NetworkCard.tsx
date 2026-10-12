import { memo } from "react";
import { Network } from "lucide-react";

import type { NetworkResponse } from "../services/api";

interface NetworkCardProps {
    network: NetworkResponse | null;
}

function NetworkCard({ network }: NetworkCardProps) {
    const toMiB = (bytes: number): string => {
        return (bytes / (1024 ** 2)).toFixed(2);
    };

    const toGiB = (bytes: number): string => {
        return (bytes / (1024 ** 3)).toFixed(2);
    };

    return (
        <section className="metric-card">
            <h2 className="card-title">
                <Network size={22} />
                Network
            </h2>

            {network === null ? (
                <p className="metric-empty">
                    Loading network...
                </p>
            ) : (
                <>
                    <p className="metric-lead">
                        Network Activity (All Interfaces)
                    </p>

                    <p className="metric-primary">
                        {network.ready
                            ? `${toMiB(network.download_bytes_per_sec)} MiB/s`
                            : "Sampling..."}
                    </p>

                    <p className="metric-lead">
                        Download Speed
                    </p>

                    <dl className="metric-details">
                        <div className="detail-row">
                            <dt>Upload Speed</dt>
                            <dd>
                                {network.ready
                                    ? `${toMiB(network.upload_bytes_per_sec)} MiB/s`
                                    : "Sampling..."}
                            </dd>
                        </div>

                        <div className="detail-row">
                            <dt>Total Received</dt>
                            <dd>
                                {toGiB(network.bytes_recv)} GiB
                            </dd>
                        </div>

                        <div className="detail-row">
                            <dt>Total Sent</dt>
                            <dd>
                                {toGiB(network.bytes_sent)} GiB
                            </dd>
                        </div>
                    </dl>
                </>
            )}
        </section>
    );
}

export default memo(NetworkCard);