#!/usr/bin/env python3
"""Optional one-time, read-only SMBIOS capture for unprivileged System Monitor.

Run with sudo only if /sys/firmware/dmi/entries/17-*/raw is restricted:
    sudo python3 scripts/capture-memory-hardware.py

The result is a sanitized, local snapshot. The dashboard process itself never
needs root. Re-run after changing RAM and restart System Monitor.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.memory_hardware import (  # noqa: E402
    SNAPSHOT_PATH, read_dmi_memory_modules, summarize_modules,
)


def main() -> int:
    modules = read_dmi_memory_modules()
    if modules is None:
        print("Unable to read SMBIOS memory information. No snapshot written.", file=sys.stderr)
        return 1
    if not modules:
        print("No installed RAM modules found in readable SMBIOS data.", file=sys.stderr)
        return 1

    data = summarize_modules(modules, "snapshot")
    # Snapshot contains only memory generation, configured speed, capacity,
    # manufacturer and module slot. Serial/asset identifiers are excluded.
    temp_path = None
    try:
        # Random exclusive temporary file avoids following user-created symlinks
        # when this optional command is executed with sudo.
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=SNAPSHOT_PATH.parent,
            prefix=".ram-snapshot-", delete=False,
        ) as stream:
            temp_path = Path(stream.name)
            json.dump(data, stream, indent=2)
            stream.write("\n")
        os.chmod(temp_path, 0o644)  # Readable by the ordinary backend user.
        os.replace(temp_path, SNAPSHOT_PATH)
    except OSError as exc:
        print(f"Could not save local RAM snapshot: {exc}", file=sys.stderr)
        return 1
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    print(f"Saved {len(modules)} installed RAM module(s) to {SNAPSHOT_PATH}")
    print("Restart System Monitor to pick up the snapshot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
