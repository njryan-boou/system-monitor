from app.services.gpu_intel import read_client_resident_memory


def add_fd(root, pid, fd, client, memory, device="0000:00:02.0"):
    file = root / str(pid) / "fdinfo" / str(fd)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(
        f"drm-driver: xe\ndrm-pdev: {device}\n"
        f"drm-client-id: {client}\n{memory}"
    )


def test_peak_client_memory_deduplicates_fd_and_clients(tmp_path):
    add_fd(tmp_path, 1, 3, 11,
           "drm-resident-system: 4096 KiB\ndrm-resident-vram0: 1024 KiB\n")
    add_fd(tmp_path, 1, 4, 11,
           "drm-resident-system: 4096 KiB\ndrm-resident-vram0: 1024 KiB\n")
    add_fd(tmp_path, 2, 3, 12, "drm-resident-system: 2048 KiB\n")
    add_fd(tmp_path, 3, 3, 13, "drm-resident-system: 6000 KiB\n",
           device="0000:00:03.0")
    assert read_client_resident_memory("0000:00:02.0", tmp_path) == 5 * 1024 ** 2


def test_no_supported_fields_is_unavailable(tmp_path):
    add_fd(tmp_path, 1, 3, 11, "drm-cycles-rcs: 10\n")
    assert read_client_resident_memory("0000:00:02.0", tmp_path) is None


def test_invalid_and_explicit_byte_units(tmp_path):
    add_fd(tmp_path, 1, 3, 11,
           "drm-resident-system: 1048576 B\n"
           "drm-resident-vram0: invalid\n")
    assert read_client_resident_memory("0000:00:02.0", tmp_path) == 1048576

def test_lunar_lake_gtt_and_stolen_regions(tmp_path):
    """Real Xe fdinfo samples on the HP Lunar Lake laptop."""
    add_fd(tmp_path, 29, 3, 29,
           "drm-shared-system: 0\\n"
           "drm-resident-system: 3040 KiB\\n"
           "drm-shared-gtt: 0\\n"
           "drm-resident-gtt: 128 KiB\\n"
           "drm-resident-stolen: 0\\n")
    add_fd(tmp_path, 23, 3, 23,
           "drm-shared-gtt: 72 MiB\\n"
           "drm-resident-gtt: 281860 KiB\\n"
           "drm-resident-stolen: 0\\n")
    # Shared bytes are not extra resident bytes, and the largest client's
    # residency is reported rather than adding different clients together.
    assert read_client_resident_memory("0000:00:02.0", tmp_path) == 281860 * 1024


def test_sums_independent_resident_regions(tmp_path):
    add_fd(tmp_path, 5, 4, 5,
           "drm-resident-system: 2 MiB\\n"
           "drm-resident-gtt: 3 MiB\\n"
           "drm-resident-stolen: 512 KiB\\n"
           "drm-resident-vram0: 1 MiB\\n"
           "drm-shared-gtt: 8 MiB\\n")
    assert read_client_resident_memory("0000:00:02.0", tmp_path) == 6815744
