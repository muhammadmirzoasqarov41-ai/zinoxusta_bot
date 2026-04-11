#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/ustaqidir}"

cd "${APP_DIR}"
git pull --ff-only
sudo docker compose up -d --build
sudo docker image prune -f >/dev/null 2>&1 || true

echo "Updated. Logs:"
echo "  sudo docker compose logs -f"
