#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/muhammadmirzoasqarov41-ai/zinoxusta_bot.git}"
APP_DIR="${APP_DIR:-$HOME/zinoxusta_bot}"

# Set this if you're on the EU system, for example:
#   PA_DOMAIN="<username>.eu.pythonanywhere.com"
PA_DOMAIN="${PA_DOMAIN:-$USER.pythonanywhere.com}"

echo "1) Install/upgrade PythonAnywhere CLI (pa)"
python3 -m pip install --upgrade --user pythonanywhere >/dev/null
export PATH="$HOME/.local/bin:$PATH"

echo "2) Clone/pull repo"
if [[ -d "${APP_DIR}/.git" ]]; then
  (cd "${APP_DIR}" && git pull --ff-only)
else
  git clone "${REPO_URL}" "${APP_DIR}"
fi

cd "${APP_DIR}"

echo "3) Create venv + install deps"
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

echo "5) Write .env (only stored on your account)"
read -r -p "WEBHOOK_PATH (example: /tg/abc123xyz): " WEBHOOK_PATH
if [[ -z "${WEBHOOK_PATH}" || "${WEBHOOK_PATH:0:1}" != "/" ]]; then
  echo "WEBHOOK_PATH must start with '/'"
  exit 1
fi

read -r -s -p "BOT_TOKEN (hidden): " BOT_TOKEN
echo
if [[ -z "${BOT_TOKEN}" ]]; then
  echo "BOT_TOKEN is required"
  exit 1
fi

cat > .env <<EOF
BOT_TOKEN=${BOT_TOKEN}
WEBHOOK_ENABLED=true
WEBHOOK_BASE_URL=https://${PA_DOMAIN}
WEBHOOK_PATH=${WEBHOOK_PATH}
EOF

echo "6) Create/reload ASGI website"
UVICORN_CMD="${APP_DIR}/.venv/bin/uvicorn --app-dir ${APP_DIR} --uds \${DOMAIN_SOCKET} asgi_app:app"
pa website create --domain "${PA_DOMAIN}" --command "${UVICORN_CMD}" || pa website reload --domain "${PA_DOMAIN}"

echo "OK. Open:"
echo "  https://${PA_DOMAIN}/health"
