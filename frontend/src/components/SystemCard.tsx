import type { SystemResponse } from "../services/api";
import { Monitor } from "lucide-react";
import { memo, useState } from "react";

interface SystemCardProps { system: SystemResponse | null; }
type View = "overview" | "details" | "firmware";

const uptimeText = (seconds: number | null): string => {
    if (seconds == null) return "N/A";
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
};

function SystemCard({ system }: SystemCardProps) {
    const [view, setView] = useState<View>("overview");
    const overview = view === "overview";
    const details = view === "details";
    const bootDate = system?.boot_time == null ? null : new Date(system.boot_time * 1000);
    const bootText = bootDate && !Number.isNaN(bootDate.valueOf()) ? bootDate.toLocaleString() : "N/A";
    const primary = system === null ? "" :
        overview ? (system.distro_name ?? system.os) :
        details ? (system.hostname ?? "N/A") :
        (system.motherboard_model ?? system.bios_version ?? "N/A");

    return (
        <section className="metric-card system-card">
            <h2 className="card-title"><Monitor size={22} />System</h2>
            {system === null ? <p className="metric-empty">Loading system...</p> : (
                <>
                    <div className="system-card-content">
                        <div className="system-identity">
                            <p className="metric-lead">
                                {overview ? "Operating System" : details ? "Machine Information" : "Motherboard & Firmware"}
                            </p>
                        </div>
                        <div className="system-primary-stat">
                            <p className="metric-primary" title={primary}>
                                {primary}
                            </p>
                            <p className="metric-lead">
                                {overview ? "Installed OS" : details ? "Hostname" :
                                    system.motherboard_model ? "Motherboard Model" : "Firmware Version"}
                            </p>
                        </div>
                        <dl className="metric-details system-metric-details">
                            {overview ? (
                                <>
                                    <div className="detail-row"><dt>OS Release</dt><dd>{system.distro_version ?? system.os_release}</dd></div>
                                    <div className="detail-row"><dt>Architecture</dt><dd>{system.architecture}</dd></div>
                                    <div className="detail-row"><dt>Uptime</dt><dd>{uptimeText(system.uptime)}</dd></div>
                                </>
                            ) : details ? (
                                <>
                                    <div className="detail-row"><dt>Kernel</dt><dd>{system.os_release}</dd></div>
                                    <div className="detail-row"><dt>Boot Time</dt><dd>{bootText}</dd></div>
                                    <div className="detail-row"><dt>Processes</dt><dd>{system.process_count ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>OS Family</dt><dd>{system.os}</dd></div>
                                </>
                            ) : (
                                <>
                                    <div className="detail-row"><dt>Board Manufacturer</dt><dd>{system.motherboard_manufacturer ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>Board Model</dt><dd>{system.motherboard_model ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>Board Version</dt><dd>{system.motherboard_version ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>BIOS Vendor</dt><dd>{system.bios_vendor ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>BIOS / UEFI Version</dt><dd>{system.bios_version ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>BIOS Release Date</dt><dd>{system.bios_release_date ?? "N/A"}</dd></div>
                                    <div className="detail-row"><dt>Boot Mode</dt><dd>{system.boot_mode ?? "N/A"}</dd></div>
                                </>
                            )}
                        </dl>
                    </div>
                    <div className="system-view-switch" role="group" aria-label="System information view">
                        <button type="button" className={overview ? "system-view-button is-active" : "system-view-button"}
                            aria-pressed={overview} onClick={() => setView("overview")}>Overview</button>
                        <button type="button" className={details ? "system-view-button is-active" : "system-view-button"}
                            aria-pressed={details} onClick={() => setView("details")}>Details</button>
                        <button type="button" className={view === "firmware" ? "system-view-button is-active" : "system-view-button"}
                            aria-pressed={view === "firmware"} onClick={() => setView("firmware")}>Firmware</button>
                    </div>
                </>
            )}
        </section>
    );
}

export default memo(SystemCard);
