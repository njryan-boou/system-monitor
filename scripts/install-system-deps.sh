#!/usr/bin/env bash
# Bootstrap Fedora and Ubuntu/Debian development or build machines for System Monitor.
# Run as a regular user: bash scripts/install-system-deps.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
    echo "Usage: bash scripts/install-system-deps.sh [--with-pyinstaller]"
    echo "Installs system prerequisites, Python packages, npm packages, and builds the frontend."
    echo "--with-pyinstaller also installs PyInstaller for standalone Linux builds."
}

WITH_PYINSTALLER=false
case "$#" in
    0) ;;
    1)
        case "$1" in
            --with-pyinstaller) WITH_PYINSTALLER=true ;;
            -h|--help) usage; exit 0 ;;
            *) usage >&2; exit 2 ;;
        esac
        ;;
    *) usage >&2; exit 2 ;;
esac

if [[ "$(uname -s)" != "Linux" ]] || [[ ! -r /etc/os-release ]]; then
    echo "Error: This installer requires a supported Linux distribution." >&2
    exit 1
fi

# Identify Fedora explicitly; keep Ubuntu/Debian on the original apt path.
# shellcheck source=/etc/os-release
. /etc/os-release
if [[ "${ID:-}" == "fedora" ]] && command -v dnf >/dev/null 2>&1; then
    PACKAGE_MANAGER="dnf"
elif [[ -f /etc/debian_version ]] && command -v apt-get >/dev/null 2>&1; then
    PACKAGE_MANAGER="apt"
else
    echo "Error: Supported systems are Fedora (dnf) and Ubuntu/Debian (apt)." >&2
    echo "Install Python 3.10+, a Vite-compatible Node.js, npm, and Git manually on other systems." >&2
    exit 1
fi

if [[ "$(id -u)" -eq 0 ]]; then
    echo "Error: Run as your normal user, not with sudo." >&2
    echo "The script will request sudo only for system packages." >&2
    exit 1
fi

if ! command -v sudo >/dev/null 2>&1; then
    echo "Error: sudo is required to install system packages." >&2
    exit 1
fi

node_compatible() {
    command -v node >/dev/null 2>&1 || return 1
    command -v npm >/dev/null 2>&1 || return 1

    local version major minor
    version="$(node --version)" || return 1
    [[ "$version" =~ ^v([0-9]+)\.([0-9]+)\. ]] || return 1
    major="${BASH_REMATCH[1]}"
    minor="${BASH_REMATCH[2]}"

    # Vite 8: Node 20.19+, 22.12+, or 24+ (not Node 21 or 23).
    (( major >= 24 || (major == 22 && minor >= 12) ||
       (major == 20 && minor >= 19) ))
}

echo "Installing System Monitor system prerequisites..."
echo "This step may ask for your sudo password and install system packages."
sudo -v
if [[ "$PACKAGE_MANAGER" == "apt" ]]; then
    sudo apt-get update
    sudo apt-get install -y \
        python3 python3-venv python3-pip python3-dev \
        build-essential git curl ca-certificates gnupg
else
    sudo dnf install -y \
        python3 python3-pip python3-devel \
        gcc gcc-c++ make git curl ca-certificates
fi

if ! python3 -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
    echo "Error: System Monitor requires Python 3.10 or newer." >&2
    echo "The distribution's python3 is too old; install a supported Python first." >&2
    exit 1
fi

if node_compatible; then
    echo "Using existing Node.js $(node --version) and npm $(npm --version)."
else
    echo "Node.js/npm missing or too old for Vite 8."
    if [[ "$PACKAGE_MANAGER" == "dnf" ]]; then
        # Fedora's nodejs package includes npm; use its official repository.
        echo "Installing Node.js and npm from Fedora repositories..."
        sudo dnf install -y nodejs
    else
        echo "Installing Node.js 24.x from the NodeSource signed apt repository..."

        arch="$(dpkg --print-architecture)"
    case "$arch" in
        amd64|arm64) ;;
        *)
            echo "Error: NodeSource Node.js 24 packages require amd64 or arm64; found $arch." >&2
            exit 1
            ;;
    esac

    if [[ -f /etc/apt/sources.list.d/nodesource.list ]]; then
        echo "Error: An older NodeSource apt source already exists." >&2
        echo "Please migrate /etc/apt/sources.list.d/nodesource.list before rerunning." >&2
        exit 1
    fi

    temp_dir="$(mktemp -d)"
    trap 'rm -rf "$temp_dir"' EXIT
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        -o "$temp_dir/nodesource.asc"
    gpg --batch --yes --dearmor \
        -o "$temp_dir/nodesource.gpg" "$temp_dir/nodesource.asc"

    sudo install -d -m 0755 /usr/share/keyrings
    sudo install -m 0644 "$temp_dir/nodesource.gpg" /usr/share/keyrings/nodesource.gpg

    printf 'Types: deb\nURIs: https://deb.nodesource.com/node_24.x\nSuites: nodistro\nComponents: main\nArchitectures: %s\nSigned-By: /usr/share/keyrings/nodesource.gpg\n' "$arch" |
        sudo tee /etc/apt/sources.list.d/nodesource.sources >/dev/null

        sudo apt-get update
        sudo apt-get install -y nodejs
    fi
fi

if ! node_compatible; then
    echo "Error: A compatible Node.js and npm installation was not found after setup." >&2
    echo "Check PATH, node --version, and npm --version." >&2
    if [[ "$PACKAGE_MANAGER" == "dnf" ]]; then
        echo "If Fedora's default nodejs is too old, install a supported Fedora Node.js stream (e.g. nodejs24) and select its node/npm binaries." >&2
    fi
    exit 1
fi

echo "Python: $(python3 --version)"
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"

# Keep all language-level installation logic in the existing setup script.
bash "$ROOT/scripts/setup.sh"

if [[ "$WITH_PYINSTALLER" == true ]]; then
    echo "Installing PyInstaller for the standalone Linux build..."
    "$ROOT/backend/.venv/bin/python" -m pip install pyinstaller
fi

echo
echo "Ready! Start System Monitor with: bash scripts/run.sh"
if [[ "$WITH_PYINSTALLER" == true ]]; then
    echo "Build a Linux executable with: bash scripts/build-linux.sh"
fi
