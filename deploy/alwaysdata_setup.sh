#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/muhammadmirzoasqarov41-ai/zinoxusta_bot.git}"
APP_DIR="${APP_DIR:-$HOME/ustaqidir}"
AD_DOMAIN="${AD_DOMAIN:-$USER.alwaysdata.net}"

echo "1) Clone or update repo"
if [[ -d "${APP_DIR}/.git" ]]; then
  (cd "${APP_DIR}" && git pull --ff-only)
else
  git clone "${REPO_URL}" "${APP_DIR}"
fi

cd "${APP_DIR}"

echo "2) Create virtualenv and install dependencies"
if [[ ! -d ".venv" ]]; then
  python -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt >/dev/null

echo "3) Write .env"
read -r -p "BOT_TOKEN: " BOT_TOKEN
if [[ -z "${BOT_TOKEN}" ]]; then
  echo "BOT_TOKEN is required"
  exit 1
fi

read -r -p "ADMIN_ID (optional): " ADMIN_ID
read -r -p "ADMIN_USERNAME (optional, without @): " ADMIN_USERNAME
read -r -p "WEB_USER [admin]: " WEB_USER
read -r -s -p "WEB_PASS [admin12345]: " WEB_PASS
echo
read -r -p "FIREBASE_CREDENTIALS_JSON path or paste directly: " FIREBASE_CREDENTIALS_JSON
read -r -p "WEBHOOK_PATH [/tg/webhook-secret]: " WEBHOOK_PATH

WEB_USER="${WEB_USER:-admin}"
WEB_PASS="${WEB_PASS:-admin12345}"
WEBHOOK_PATH="${WEBHOOK_PATH:-/tg/webhook-secret}"
if [[ "${WEBHOOK_PATH:0:1}" != "/" ]]; then
  echo "WEBHOOK_PATH must start with '/'"
  exit 1
fi

FIREBASE_CREDENTIALS_FILE="${APP_DIR}/firebase_credentials.json"
if [[ -f "${FIREBASE_CREDENTIALS_JSON}" ]]; then
  cp "${FIREBASE_CREDENTIALS_JSON}" "${FIREBASE_CREDENTIALS_FILE}"
else
  cat > "${FIREBASE_CREDENTIALS_FILE}" <<EOF
${FIREBASE_CREDENTIALS_JSON}
EOF
fi

cat > .env <<EOF
BOT_TOKEN=${BOT_TOKEN}
ADMIN_ID=${ADMIN_ID}
ADMIN_USERNAME=${ADMIN_USERNAME}
DB_TYPE=firebase
WEB_ENABLED=true
WEBHOOK_ENABLED=true
WEBHOOK_BASE_URL=https://${AD_DOMAIN}
WEBHOOK_PATH=${WEBHOOK_PATH}
WEB_USER=${WEB_USER}
WEB_PASS=${WEB_PASS}
FIREBASE_CREDENTIALS_FILE=${FIREBASE_CREDENTIALS_FILE}
EOF

echo "4) Done"
echo
echo "Alwaysdata site command:"
echo "  ${APP_DIR}/.venv/bin/uvicorn --app-dir ${APP_DIR} asgi_app:app --host \$IP --port \$PORT"
echo
echo "Set in alwaysdata Web > Sites:"
echo "  Type: User program"
echo "  Command: the line above"
echo "  Working directory: ${APP_DIR}"
echo "  Python version: 3.12+"
echo
echo "Scheduled task keepalive suggestion (optional):"
echo "  curl --fail --silent --show-error https://${AD_DOMAIN}/health"
