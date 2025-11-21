#!/bin/bash

set -e

VERSION="1.0.0"
IDENTIFIER="uk.co.bing-bong.macmocker"
PACKAGE_NAME="MacMocker-${VERSION}.pkg"

echo "Building MacMocker package ${VERSION}..."

# Create staging directory
BUILD_DIR="$(mktemp -d)"
PAYLOAD_DIR="${BUILD_DIR}/payload"
SCRIPTS_DIR="${BUILD_DIR}/scripts"

mkdir -p "${PAYLOAD_DIR}/usr/local/macmocker"
mkdir -p "${SCRIPTS_DIR}"

# Copy project files
echo "Copying files..."
cd ..
cp -R core tests config main.py pyproject.toml "${PAYLOAD_DIR}/usr/local/macmocker/"

# Create postinstall script
cat > "${SCRIPTS_DIR}/postinstall" << 'EOF'
#!/bin/bash

export PATH="/usr/local/bin:$PATH"

# Install uv if needed
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Install dependencies
cd /usr/local/macmocker
uv pip install --system -e .

# Create artifacts directory
mkdir -p /Users/Shared/macmocker_artifacts

# Set permissions
chmod -R 755 /usr/local/macmocker
chmod +x /usr/local/macmocker/main.py

exit 0
EOF

chmod +x "${SCRIPTS_DIR}/postinstall"

# Build package
echo "Building package..."
pkgbuild \
    --root "${PAYLOAD_DIR}" \
    --scripts "${SCRIPTS_DIR}" \
    --identifier "${IDENTIFIER}" \
    --version "${VERSION}" \
    --install-location "/" \
    "${PACKAGE_NAME}"

# Cleanup
rm -rf "${BUILD_DIR}"

echo "Package created: ${PACKAGE_NAME}"
echo "Upload this to Jamf Pro for deployment"
