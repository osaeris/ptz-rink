#!/usr/bin/env bash
set -e

APP_NAME="ptz-rink"

echo "Stopping any container using port 5001..."

docker ps --filter publish=5001 --format "{{.ID}}" | while read id
do
    docker stop "$id"
    docker rm "$id"
done

echo "Building image..."
docker build -t "$APP_NAME" .

echo "Starting..."
docker run -d \
    --name "$APP_NAME" \
    -p 5001:5001 \
    -v "$(pwd)/config:/app/config" \
    --restart unless-stopped \
    "$APP_NAME"

echo "Done."

