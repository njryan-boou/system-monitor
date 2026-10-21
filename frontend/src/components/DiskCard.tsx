import type { StorageDeviceResponse, StorageResponse } from "../services/api";
import { HardDrive, ChevronLeft, ChevronRight } from "lucide-react";
import { memo, useState } from "react";

interface DiskCardProps {
    storage: StorageResponse | null;
    devices: StorageDeviceResponse[] | null;
}
type View = "overview" | "performance";
const size = (bytes: number | null | undefined) =>
    bytes == null ? "N/A" : `${(bytes / 1024 ** 3).toFixed(1)} GiB`;
const rate = (bytes: number | null | undefined) =>
    bytes == null ? "N/A" : `${(bytes / 1024 ** 2).toFixed(1)} MiB/s`;

function DiskCard({ storage, devices }: DiskCardProps) {
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [view, setView] = useState<View>("overview");
    const list = devices ?? [];
    const index = Math.max(0, list.findIndex(disk => disk.id === selectedId));
    const disk = list[index];
    const overview = view === "overview";
    const select = (offset: number) => {
        if (!list.length) return;
        setSelectedId(list[(index + offset + list.length) % list.length].id);
    };
    const title = disk ? `${disk.name} (${disk.device})` : "Root filesystem";

    return (
        <section className="metric-card storage-card">
            <div className="storage-card-header">
                {list.length > 1 && (
                    <nav className="gpu-navigation" aria-label="Choose storage drive">
                        <button type="button" aria-label="Previous drive" onClick={() => select(-1)}><ChevronLeft size={18}/></button>
                        <span aria-live="polite">{index + 1} / {list.length}</span>
                        <button type="button" aria-label="Next drive" onClick={() => select(1)}><ChevronRight size={18}/></button>
                    </nav>
                )}
                <h2 className="card-title"><HardDrive size={22}/>Storage</h2>
            </div>
            {storage === null || devices === null ? <p className="metric-empty">Loading storage...</p> : (
                <>
                    <div className="storage-card-content">
                        <div className="storage-device-name">
                            <p className="metric-lead" title={title}>{title}</p>
                            {disk?.media_type && <p className="gpu-type-label">{disk.media_type}</p>}
                        </div>
                        <div className="storage-primary-stat">
                            <p className="metric-primary">
                                {overview
                                    ? disk ? size(disk.capacity_bytes) : `${storage.percent.toFixed(1)}%`
                                    : disk?.busy_percent == null ? "N/A" : `${disk.busy_percent.toFixed(1)}%`}
                            </p>
                            <p className="metric-lead">{overview ? (disk ? "Physical Drive Capacity" : "Root Filesystem Usage") : "Drive Busy Time"}</p>
                            <div className="storage-progress-slot">
                                {overview && !disk && <progress className="usage-progress" value={storage.percent} max={100} aria-label="Root filesystem utilization"/>}
                                {!overview && disk?.busy_percent != null &&
                                    <progress className="usage-progress" value={disk.busy_percent} max={100} aria-label="Drive busy time"/>}
                            </div>
                        </div>
                        <dl className="metric-details storage-metric-details">
                            {overview ? (
                                <>
                                    <div className="detail-row"><dt>Mounted Volume</dt><dd title={disk ? (disk.mountpoint ?? "N/A") : storage.volume}>{disk ? (disk.mountpoint ?? "N/A") : storage.volume}</dd></div>
                                    <div className="detail-row"><dt>Volume Used</dt><dd>{size(disk ? disk.volume_used : storage.used)}</dd></div>
                                    <div className="detail-row"><dt>Volume Available</dt><dd>{size(disk ? disk.volume_free : storage.free)}</dd></div>
                                    <div className="detail-row"><dt>Volume Total</dt><dd>{size(disk ? disk.volume_total : storage.total)}</dd></div>
                                </>
                            ) : (
                                <>
                                    <div className="detail-row"><dt>Read Speed</dt><dd>{rate(disk?.read_bytes_per_sec)}</dd></div>
                                    <div className="detail-row"><dt>Write Speed</dt><dd>{rate(disk?.write_bytes_per_sec)}</dd></div>
                                    <div className="detail-row"><dt>Device</dt><dd>{disk?.device ?? "N/A"}</dd></div>
                                </>
                            )}
                        </dl>
                    </div>
                    <div className="storage-view-switch" role="group" aria-label="Storage metrics view">
                        <button type="button" className={overview ? "storage-view-button is-active" : "storage-view-button"}
                            aria-pressed={overview} onClick={() => setView("overview")}>Overview</button>
                        <button type="button" className={!overview ? "storage-view-button is-active" : "storage-view-button"}
                            aria-pressed={!overview} onClick={() => setView("performance")}>Performance</button>
                    </div>
                </>
            )}
        </section>
    );
}
export default memo(DiskCard);
