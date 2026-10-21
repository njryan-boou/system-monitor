import type { StorageDeviceResponse, StorageResponse, StoragePartitionsResponse } from "../services/api";
import { HardDrive, ChevronLeft, ChevronRight } from "lucide-react";
import { memo, useState } from "react";

interface DiskCardProps {
    storage: StorageResponse | null;
    devices: StorageDeviceResponse[] | null;
    partitions: StoragePartitionsResponse | null;
}
type View = "overview" | "performance" | "partitions";
const size = (bytes: number | null | undefined) =>
    bytes == null ? "N/A" : `${(bytes / 1024 ** 3).toFixed(1)} GiB`;
const rate = (bytes: number | null | undefined) =>
    bytes == null ? "N/A" : `${(bytes / 1024 ** 2).toFixed(1)} MiB/s`;

function DiskCard({ storage, devices, partitions }: DiskCardProps) {
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [view, setView] = useState<View>("overview");
    const list = devices ?? [];
    // Prefer root filesystem on initial load; remember manual drive selection.
    const selectedIndex = list.findIndex(disk => disk.id === selectedId);
    const rootIndex = list.findIndex(disk => disk.mountpoint === "/");
    const mountedIndex = list.findIndex(disk => disk.volume_percent != null);
    const defaultIndex = rootIndex >= 0 ? rootIndex : mountedIndex >= 0 ? mountedIndex : 0;
    const index = selectedIndex >= 0 ? selectedIndex : defaultIndex;
    const disk = list[index];
    const overview = view === "overview";
    const performance = view === "performance";
    // Utilization is a selected mounted filesystem's usage, not physical drive usage.
    const volumePercent = disk ? disk.volume_percent : storage?.percent;
    const hasVolumeUsage = volumePercent != null && Number.isFinite(volumePercent);
    const partitionList = partitions?.drives.find(drive => drive.disk_id === disk?.id)?.partitions ?? [];
    const partitionReady = partitions !== null && partitions.available;

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
                                    ? hasVolumeUsage ? `${volumePercent.toFixed(1)}%` : "N/A"
                                    : performance
                                        ? disk?.busy_percent == null ? "N/A" : `${disk.busy_percent.toFixed(1)}%`
                                        : partitions === null ? "..." : !partitionReady || !disk ? "N/A" : partitionList.length}
                            </p>
                            <p className="metric-lead" title={overview && disk && hasVolumeUsage ? "Usage of the mounted filesystem, not of the entire physical drive." : undefined}>
                                {overview
                                    ? hasVolumeUsage ? (disk ? "Mounted Volume Usage" : "Root Filesystem Usage") : "Filesystem Usage Unavailable"
                                    : performance ? "Drive Busy Time" : "Partitions on Selected Drive"}
                            </p>
                            <div className="storage-progress-slot">
                                {overview && hasVolumeUsage && <progress
                                    className="usage-progress"
                                    value={Math.max(0, Math.min(100, volumePercent))}
                                    max={100}
                                    aria-label={disk ? "Selected mounted filesystem utilization" : "Root filesystem utilization"}
                                />}
                                {performance && disk?.busy_percent != null &&
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
                                    {disk && <div className="detail-row"><dt>Drive Capacity</dt><dd>{size(disk.capacity_bytes)}</dd></div>}
                                </>
                            ) : performance ? (
                                <>
                                    <div className="detail-row"><dt>Read Speed</dt><dd>{rate(disk?.read_bytes_per_sec)}</dd></div>
                                    <div className="detail-row"><dt>Write Speed</dt><dd>{rate(disk?.write_bytes_per_sec)}</dd></div>
                                    <div className="detail-row"><dt>Device</dt><dd>{disk?.device ?? "N/A"}</dd></div>
                                </>
                            ) : !partitionReady ? (
                                <div className="detail-row"><dt>Partition data</dt><dd>{partitions === null ? "Loading..." : "Unavailable on this system"}</dd></div>
                            ) : partitionList.length === 0 ? (
                                <div className="detail-row"><dt>Partitions</dt><dd>No partitions detected</dd></div>
                            ) : (
                                partitionList.map(partition => (
                                    <div className="detail-row storage-partition-row" key={partition.device}>
                                        <dt title={partition.device}>{partition.name}</dt>
                                        <dd className="storage-partition-info">
                                            <span>{size(partition.size_bytes)} · {partition.filesystem ?? "Unknown filesystem"}</span>
                                            <span title={partition.mountpoints.join(", ")}>
                                                {partition.mountpoints.length
                                                    ? partition.mountpoints.join(", ")
                                                    : "Not mounted"}
                                            </span>
                                        </dd>
                                    </div>
                                ))
                            )}
                        </dl>
                    </div>
                    <div className="storage-view-switch" role="group" aria-label="Storage metrics view">
                        <button type="button" className={overview ? "storage-view-button is-active" : "storage-view-button"}
                            aria-pressed={overview} onClick={() => setView("overview")}>Overview</button>
                        <button type="button" className={performance ? "storage-view-button is-active" : "storage-view-button"}
                            aria-pressed={performance} onClick={() => setView("performance")}>Performance</button>
                        <button type="button" className={view === "partitions" ? "storage-view-button is-active" : "storage-view-button"}
                            aria-pressed={view === "partitions"} onClick={() => setView("partitions")}>Partitions</button>
                    </div>
                </>
            )}
        </section>
    );
}
export default memo(DiskCard);
