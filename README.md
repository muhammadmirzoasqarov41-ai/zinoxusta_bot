# USTA QIDIR bot (Aiogram 3.x)

## Ishga tushirish (lokal)
1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `.env` yarating va `BOT_TOKEN` ni kiriting (namuna: `.env.example`).
5. `python main.py`

## Railway deploy
- Railway projektida `BOT_TOKEN` (va ixtiyoriy `ADMIN_ID`, `ADMIN_USERNAME`, `DB_PATH`) env qiymatlarini kiriting.
- Start command sifatida `python main.py` yoki `Procfile` foydalaning.
 - Web panel uchun `WEB_ENABLED=true`, `WEB_USER`, `WEB_PASS`, `WEB_PORT` qiymatlarini kiriting (default: o'chirilgan).

## Admin panel
- Admin sifatida kirish uchun `ADMIN_ID` yoki `ADMIN_USERNAME` ni sozlang.
- Admin buyruq: `/admin`.

## VPS deploy (Oracle Always Free / boshqa VPS)
1. VPS (Ubuntu) oling, serverga kiring (`ssh`).
2. Docker o'rnating:
   - `sudo apt update && sudo apt -y install ca-certificates curl git`
   - `curl -fsSL https://get.docker.com | sudo sh`
   - `sudo usermod -aG docker $USER` (so'ng `exit` qilib qayta kiring)
3. Repo:
   - `git clone <repo_url> ustaqidir && cd ustaqidir`
4. Environment:
   - `cp .env.example .env`
   - `.env` ichida `BOT_TOKEN` ni kiriting (ixtiyoriy: `ADMIN_ID`, `ADMIN_USERNAME`).
5. Run:
   - `mkdir -p data`
   - `docker compose up -d --build`
6. Log:
   - `docker compose logs -f`

SQLite DB Docker ichida `/data/ustaqidir.db` bo'ladi (hostda `./data/ustaqidir.db`).

Tezkor auto-deploy uchun: `deploy/bootstrap_ubuntu.sh` (VPS ichida `REPO_URL=... BOT_TOKEN=... bash deploy/bootstrap_ubuntu.sh`).

Web panel kerak bo'lsa:
- `.env` da `WEB_ENABLED=true` qiling.
- `docker-compose.yml` dagi `ports:` ni public qilish uchun `127.0.0.1:` qismini olib tashlang.

## PythonAnywhere deploy (karta bo'lmasligi mumkin)
PythonAnywhere free'da polling 24/7 ishlashi qiyin, shuning uchun **webhook** ishlatamiz.
PythonAnywhere'da ASGI (FastAPI/uvicorn) hozircha ko'proq **command-line** orqali sozlanadi.

1. API token yarating:
   - PythonAnywhere → Account → API token → Create
2. Bash console oching va `pa` tool o'rnating:
   - `pip install --upgrade pythonanywhere`
3. Repo:
   - `git clone https://github.com/muhammadmirzoasqarov41-ai/zinoxusta_bot.git`
4. Virtualenv:
   - `mkvirtualenv zinoxusta --python=python3.10`
   - `cd zinoxusta_bot && pip install -r requirements.txt`
5. `.env` yarating (`~/zinoxusta_bot/.env`):
   - `BOT_TOKEN=...`
   - `WEBHOOK_ENABLED=true`
   - `WEBHOOK_BASE_URL=https://<username>.pythonanywhere.com` (EU bo'lsa: `https://<username>.eu.pythonanywhere.com`)
   - `WEBHOOK_PATH=/tg/<secret>`
6. ASGI website yaratish:
   - `pa website create --domain <username>.pythonanywhere.com --command '/home/<username>/.virtualenvs/zinoxusta/bin/uvicorn --app-dir /home/<username>/zinoxusta_bot --uds ${DOMAIN_SOCKET} asgi_app:app'`
7. Reload (kod o'zgarsa):
   - `pa website reload --domain <username>.pythonanywhere.com`
8. Tekshiruv:
   - `https://<username>.pythonanywhere.com/health` → `{"ok": true}`

Tezkor script:
- Bash console ichida: `bash deploy/pythonanywhere_setup.sh`
- (EU bo'lsa) oldindan: `export PA_DOMAIN="<username>.eu.pythonanywhere.com"`

## Eslatma
- Ma'lumotlar bazasi `SQLite` (`DB_PATH`) orqali saqlanadi.
- Yangi foydalanuvchiga ro'yxatdan o'tganda 10 ta olmos beriladi.
 - Web panel HTTP Basic Auth bilan himoyalangan.
