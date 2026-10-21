import { memo, useState } from "react";
import { Network, ChevronLeft, ChevronRight } from "lucide-react";
import type { NetworkInterfaceResponse, NetworkResponse } from "../services/api";

interface NetworkCardProps {
    network: NetworkResponse | null;
    interfaces: NetworkInterfaceResponse[] | null;
}
type View = "overview" | "performance" | "adapter";
const speed = (bytes: number | null) =>
    bytes == null ? "Sampling..." : `${(bytes / 1024 ** 2).toFixed(2)} MiB/s`;
const bytesGiB = (bytes: number) => `${(bytes / 1024 ** 3).toFixed(2)} GiB`;
const count = (value: number) => value.toLocaleString();

function NetworkCard({ network, interfaces }: NetworkCardProps) {
    const [selectedId, setSelectedId] = useState("all");
    const [view, setView] = useState<View>("overview");
    const items = interfaces ?? [];
    const index = Math.max(0, items.findIndex(item => item.id === selectedId));
    const adapter = items[index];
    const overview = view === "overview";
    const performance = view === "performance";
    const individualAdapter = adapter?.id !== "all";
    const change = (step: number) => {
        if (items.length) setSelectedId(items[(index + step + items.length) % items.length].id);
    };
    const down = adapter?.ready ? adapter.download_bytes_per_sec : null;
    const up = adapter?.ready ? adapter.upload_bytes_per_sec : null;

    return (
        <section className="metric-card network-card">
            <div className="network-card-header">
                {items.length > 1 && (
                    <nav className="gpu-navigation" aria-label="Select network interface">
                        <button type="button" aria-label="Previous network interface" onClick={() => change(-1)}><ChevronLeft size={18}/></button>
                        <span aria-live="polite">{index + 1} / {items.length}</span>
                        <button type="button" aria-label="Next network interface" onClick={() => change(1)}><ChevronRight size={18}/></button>
                    </nav>
                )}
                <h2 className="card-title"><Network size={22}/>Network</h2>
            </div>
            {interfaces === null || network === null ? (
                <p className="metric-empty">Loading network...</p>
            ) : !adapter ? (
                <p className="metric-empty">No network interfaces detected</p>
            ) : (
                <>
                    <div className="network-card-content">
                        <div className="network-identity">
                            <p className="metric-lead" title={adapter.name}>{adapter.name}</p>
                            <p className="gpu-type-label">{adapter.interface_type}
                                {adapter.is_up != null ? (adapter.is_up ? " · Connected" : " · Down") : ""}
                            </p>
                        </div>
                        <div className="network-primary-stat">
                            <p className="metric-primary">
                                {overview ? speed(down) : performance ?
                                    (adapter.speed_mbps != null ? `${adapter.speed_mbps} Mb/s` : "N/A") :
                                    !individualAdapter || adapter.is_up == null ? "N/A" :
                                    adapter.is_up ? "Connected" : "Down"}
                            </p>
                            <p className="metric-lead">{overview ? "Download Speed" : performance ? "Reported Link Speed" : "Adapter Link Status"}</p>
                        </div>
                        <dl className="metric-details network-metric-details">
                            {overview ? (
                                <>
                                    <div className="detail-row"><dt>Upload Speed</dt><dd>{speed(up)}</dd></div>
                                    <div className="detail-row"><dt>Total Received</dt><dd>{bytesGiB(adapter.bytes_recv)}</dd></div>
                                    <div className="detail-row"><dt>Total Sent</dt><dd>{bytesGiB(adapter.bytes_sent)}</dd></div>
                                </>
                            ) : performance ? (
                                <>
                                    <div className="detail-row"><dt>Received Packets</dt><dd>{count(adapter.packets_recv)}</dd></div>
                                    <div className="detail-row"><dt>Sent Packets</dt><dd>{count(adapter.packets_sent)}</dd></div>
                                    <div className="detail-row"><dt>Errors (Rx / Tx)</dt><dd>{count(adapter.errors_recv)} / {count(adapter.errors_sent)}</dd></div>
                                    <div className="detail-row"><dt>Dropped (Rx / Tx)</dt><dd>{count(adapter.drops_recv)} / {count(adapter.drops_sent)}</dd></div>
                                </>
                            ) : !individualAdapter ? (
                                <div className="detail-row"><dt>Adapter</dt><dd>Select an interface using the arrows above</dd></div>
                            ) : (
                                <>
                                    <div className="detail-row"><dt>Interface Type</dt><dd>{adapter.interface_type}</dd></div>
                                    <div className="detail-row"><dt>Driver</dt><dd>{adapter.driver ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>Duplex</dt><dd>{adapter.duplex ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>MTU</dt><dd>{adapter.mtu == null ? "N/A" : `${adapter.mtu} bytes`}</dd></div>
                                    <div className="detail-row"><dt>Operating State</dt><dd>{adapter.operstate ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>Bus Device</dt><dd>{adapter.hardware_path ?? "N/A"}</dd></div>
                                </>
                            )}
                        </dl>
                    </div>
                    <div className="network-view-switch" role="group" aria-label="Network metrics view">
                        <button type="button" className={overview ? "network-view-button is-active" : "network-view-button"}
                            aria-pressed={overview} onClick={() => setView("overview")}>Overview</button>
                        <button type="button" className={performance ? "network-view-button is-active" : "network-view-button"}
                            aria-pressed={performance} onClick={() => setView("performance")}>Performance</button>
                        <button type="button" className={view === "adapter" ? "network-view-button is-active" : "network-view-button"}
                            aria-pressed={view === "adapter"} onClick={() => setView("adapter")}>Adapter</button>
                    </div>
                </>
            )}
        </section>
    );
}

export default memo(NetworkCard);
