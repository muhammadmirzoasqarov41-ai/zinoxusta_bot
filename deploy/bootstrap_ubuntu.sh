#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/ustaqidir}"
REPO_URL="${REPO_URL:-}"

BOT_TOKEN="${BOT_TOKEN:-}"
ADMIN_ID="${ADMIN_ID:-}"
ADMIN_USERNAME="${ADMIN_USERNAME:-}"

WEB_ENABLED="${WEB_ENABLED:-false}"
WEB_HOST="${WEB_HOST:-0.0.0.0}"
WEB_PORT="${WEB_PORT:-8000}"
WEB_USER="${WEB_USER:-admin}"
WEB_PASS="${WEB_PASS:-admin}"

if [[ -z "${REPO_URL}" ]]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    REPO_URL="$(git config --get remote.origin.url || true)"
  fi
fi

if [[ -z "${REPO_URL}" ]]; then
  echo "REPO_URL is required (or run this script inside a git repo with remote 'origin')"
  echo "Example:"
  echo "  git clone https://github.com/<you>/<repo>.git && cd <repo>"
  echo "  BOT_TOKEN=... bash deploy/bootstrap_ubuntu.sh"
  exit 1
fi

if [[ -z "${BOT_TOKEN}" ]]; then
  echo "BOT_TOKEN is required"
  exit 1
fi

sudo apt-get update -y
sudo apt-get install -y ca-certificates curl git

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sudo sh
fi

sudo mkdir -p "${APP_DIR}"
sudo chown -R "$USER:$USER" "${APP_DIR}"

if [[ ! -d "${APP_DIR}/.git" ]]; then
  git clone "${REPO_URL}" "${APP_DIR}"
else
  (cd "${APP_DIR}" && git pull --ff-only)
fi

cd "${APP_DIR}"
mkdir -p data

cat > .env <<EOF
BOT_TOKEN=${BOT_TOKEN}
ADMIN_ID=${ADMIN_ID}
ADMIN_USERNAME=${ADMIN_USERNAME}
WEB_ENABLED=${WEB_ENABLED}
WEB_HOST=${WEB_HOST}
WEB_PORT=${WEB_PORT}
WEB_USER=${WEB_USER}
WEB_PASS=${WEB_PASS}
EOF

sudo docker compose up -d --build

echo "OK: running. Logs:"
echo "  sudo docker compose logs -f"
