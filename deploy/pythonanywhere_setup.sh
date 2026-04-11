#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/muhammadmirzoasqarov41-ai/zinoxusta_bot.git}"
APP_DIR="${APP_DIR:-$HOME/zinoxusta_bot}"
VENV_NAME="${VENV_NAME:-zinoxusta}"

# Set this if you're on the EU system, for example:
#   PA_DOMAIN="<username>.eu.pythonanywhere.com"
PA_DOMAIN="${PA_DOMAIN:-$USER.pythonanywhere.com}"

echo "1) Install/upgrade PythonAnywhere CLI (pa)"
python3 -m pip install --upgrade --user pythonanywhere >/dev/null

echo "2) Clone/pull repo"
if [[ -d "${APP_DIR}/.git" ]]; then
  (cd "${APP_DIR}" && git pull --ff-only)
else
  git clone "${REPO_URL}" "${APP_DIR}"
fi

cd "${APP_DIR}"

echo "3) Create virtualenv (if needed)"
if ! command -v mkvirtualenv >/dev/null 2>&1; then
  echo "mkvirtualenv not found. Install virtualenvwrapper first (PythonAnywhere docs), then re-run."
  exit 1
fi

if ! ls "$HOME/.virtualenvs" 2>/dev/null | rg -q "^${VENV_NAME}\$"; then
  mkvirtualenv "${VENV_NAME}" --python=python3.10
fi

echo "4) Install dependencies"
workon "${VENV_NAME}"
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

echo "6) Create ASGI website (if it already exists, delete/recreate or use reload)"
pa website create --domain "${PA_DOMAIN}" --command "/home/${USER}/.virtualenvs/${VENV_NAME}/bin/uvicorn --app-dir /home/${USER}/$(basename "${APP_DIR}") --uds \${DOMAIN_SOCKET} asgi_app:app"

echo "OK. Open:"
echo "  https://${PA_DOMAIN}/health"
