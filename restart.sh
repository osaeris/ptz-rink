#!/usr/bin/env bash
set -e

APP_NAME="ptz-rink"
PORT="5001"

# Resolve the directory this script lives in
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${SCRIPT_DIR}/config"

echo "Using config directory: ${CONFIG_DIR}"

# Ensure config directory exists on host
mkdir -p "${CONFIG_DIR}"

echo "Stopping container..."
docker stop "${APP_NAME}" 2>/dev/null || true

echo "Removing container..."
docker rm "${APP_NAME}" 2>/dev/null || true

echo "Building image..."
docker build -t "${APP_NAME}" .

echo "Starting container..."
docker run -d \
  --name "${APP_NAME}" \
  -p "${PORT}:${PORT}" \
  -v "${CONFIG_DIR}:/app/config" \
  --restart unless-stopped \
  "${APP_NAME}"

echo "Done. App running on port ${PORT}."

