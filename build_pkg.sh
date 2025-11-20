#!/bin/bash

set -e

VERSION="0.1.0"
PKG_NAME="macmocker-${VERSION}.pkg"
BUILD_DIR="$(pwd)/build"
PAYLOAD_DIR="${BUILD_DIR}/payload"
SCRIPTS_DIR="${BUILD_DIR}/scripts"
PKG_ROOT="${PAYLOAD_DIR}/usr/local/macmocker"

echo "Building MacMocker Package v${VERSION}"

echo "Cleaning previous build artifacts"
rm -rf "${BUILD_DIR}"
mkdir -p "${PAYLOAD_DIR}"
mkdir -p "${SCRIPTS_DIR}"
mkdir -p "${PKG_ROOT}"

echo "Copying test suite files"
rsync -av --exclude='*.pyc' --exclude='__pycache__' --exclude='.git' \
    --exclude='build' --exclude='deployment' \
    ./ "${PKG_ROOT}/"

echo "Setting permissions"
chmod +x "${PKG_ROOT}/main.py"
chmod -R 755 "${PKG_ROOT}"

echo "Creating postinstall script"
cat > "${SCRIPTS_DIR}/postinstall" << 'EOF'
#!/bin/bash

INSTALL_DIR="/usr/local/macmocker"
LOG_FILE="/var/log/macmocker-install.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_message "Running postinstall script"

if ! command -v python3 &> /dev/null; then
    log_message "ERROR: Python 3 is required but not installed"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    log_message "Installing uv package manager"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

cd "$INSTALL_DIR"

log_message "Installing Python dependencies"
uv pip install --system -e . >> "$LOG_FILE" 2>&1

log_message "Creating artifacts directory"
mkdir -p /var/log/macmocker/artifacts
chmod 777 /var/log/macmocker/artifacts

log_message "Creating symlink"
ln -sf "$INSTALL_DIR/main.py" /usr/local/bin/macmocker

log_message "Postinstall complete"
exit 0
EOF

chmod +x "${SCRIPTS_DIR}/postinstall"

echo "Building package"
pkgbuild --root "${PAYLOAD_DIR}" \
    --scripts "${SCRIPTS_DIR}" \
    --identifier "uk.co.bing-bong.macmocker" \
    --version "${VERSION}" \
    --install-location "/" \
    "${BUILD_DIR}/${PKG_NAME}"

echo "Package built successfully: ${BUILD_DIR}/${PKG_NAME}"
echo ""
echo "To install: sudo installer -pkg ${BUILD_DIR}/${PKG_NAME} -target /"
echo "To deploy via Jamf: Upload ${BUILD_DIR}/${PKG_NAME} to Jamf Pro"

exit 0
