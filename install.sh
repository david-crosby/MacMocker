#!/bin/bash

set -e

INSTALL_DIR="/usr/local/macmocker"
LOG_FILE="/var/log/macmocker-install.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_message "Starting MacMocker installation"

if [[ $EUID -ne 0 ]]; then
   log_message "ERROR: This script must be run as root"
   exit 1
fi

log_message "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

log_message "Checking for Python 3"
if ! command -v python3 &> /dev/null; then
    log_message "ERROR: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
log_message "Found Python version: $PYTHON_VERSION"

log_message "Checking for uv package manager"
if ! command -v uv &> /dev/null; then
    log_message "Installing uv package manager"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

UV_VERSION=$(uv --version 2>&1 || echo "unknown")
log_message "Using uv version: $UV_VERSION"

log_message "Copying test suite files to $INSTALL_DIR"
rsync -av --exclude='*.pyc' --exclude='__pycache__' --exclude='.git' \
    /tmp/macmocker/ "$INSTALL_DIR/"

cd "$INSTALL_DIR"

log_message "Installing Python dependencies with uv"
uv pip install --system -e .

log_message "Setting permissions"
chmod +x "$INSTALL_DIR/main.py"
chmod -R 755 "$INSTALL_DIR"

log_message "Creating artifacts directory"
mkdir -p /var/log/macmocker/artifacts
chmod 777 /var/log/macmocker/artifacts

log_message "Creating symlink in /usr/local/bin"
ln -sf "$INSTALL_DIR/main.py" /usr/local/bin/macmocker

log_message "Installation complete!"
log_message "Run 'macmocker --help' for usage information"

log_message "Verifying installation"
if "$INSTALL_DIR/main.py" --version > /dev/null 2>&1; then
    log_message "Installation verified successfully"
else
    log_message "WARNING: Installation verification failed"
    exit 1
fi

exit 0
