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

## Render deploy
1. Render’da yangi `Web Service` yarating va `render.yaml` ni bog'lang yoki manual sozlang.
2. Env larni kiriting:
   - `BOT_TOKEN`
   - `ADMIN_ID` va `ADMIN_USERNAME` ixtiyoriy
   - `WEB_USER` va `WEB_PASS`
   - `FIREBASE_CREDENTIALS_JSON` ga yangi Firebase service account JSON ni qo'ying
3. Firebase’da Firestore database yaratilgan bo'lsin.
4. Telegram webhook uchun quyidagilar yoqilgan bo'lsin:
   - `WEB_ENABLED=true`
   - `WEBHOOK_ENABLED=true`
   - `WEBHOOK_PATH=/tg/webhook-secret`
5. `WEBHOOK_BASE_URL` bo'sh qoldirilsa ham bo'ladi, Render avtomatik URL dan foydalaniladi.
6. Start command: `uvicorn asgi_app:app --host 0.0.0.0 --port $PORT`
7. Free Render service 15 daqiqa idle qolsa uyquga ketadi, shuning uchun repo ichida GitHub Actions keepalive workflow qo'shilgan: [`.github/workflows/keepalive.yml`](/home/ibrohim/ustatop/.github/workflows/keepalive.yml).
8. GitHub repo’da Actions yoqilgan bo'lsin, workflow `main` ga tushgach avtomatik `/health` ga ping yuboradi.

## alwaysdata deploy
1. alwaysdata’da `Web > Sites > Add a site` ga kiring.
2. `Type` sifatida `User program` tanlang.
3. Command uchun mana buni qo'ying:
   - `uvicorn asgi_app:app --host $IP --port $PORT`
4. Working directory sifatida repo papkasini ko'rsating.
5. Python version ni `3.12+` yoki mavjud eng yaqin versiyaga qo'ying.
6. `.env` ichida kamida quyidagilar bo'lsin:
   - `BOT_TOKEN`
   - `DB_TYPE=firebase`
   - `WEB_ENABLED=true`
   - `WEBHOOK_ENABLED=true`
   - `WEBHOOK_BASE_URL=https://<sizning-domainingiz>`
   - `WEBHOOK_PATH=/tg/webhook-secret`
   - `WEB_USER`
   - `WEB_PASS`
   - `FIREBASE_CREDENTIALS_FILE=/path/to/firebase_credentials.json`
7. Firebase service account JSON’ni alohida fayl sifatida saqlang, `FIREBASE_CREDENTIALS_FILE` bilan ulang.
8. Agar free plan’da bo‘lsangiz, `Advanced > Scheduled tasks` orqali vaqti-vaqti bilan `/health` ga `curl` yuborib turish mumkin.
9. alwaysdata log’lari `Web > Sites` bo‘limidan ko‘rinadi.
10. Keepalive uchun [`deploy/alwaysdata_keepalive.sh`](/home/ibrohim/ustatop/deploy/alwaysdata_keepalive.sh) skriptidan ham foydalanishingiz mumkin.

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
   - `cd zinoxusta_bot`
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
5. `.env` yarating (`~/zinoxusta_bot/.env`):
   - `BOT_TOKEN=...`
   - `WEBHOOK_ENABLED=true`
   - `WEBHOOK_BASE_URL=https://<username>.pythonanywhere.com` (EU bo'lsa: `https://<username>.eu.pythonanywhere.com`)
   - `WEBHOOK_PATH=/tg/<secret>`
6. ASGI website yaratish:
   - `pa website create --domain <username>.pythonanywhere.com --command '/home/<username>/zinoxusta_bot/.venv/bin/uvicorn --app-dir /home/<username>/zinoxusta_bot --uds ${DOMAIN_SOCKET} asgi_app:app'`
7. Reload (kod o'zgarsa):
   - `pa website reload --domain <username>.pythonanywhere.com`
8. Tekshiruv:
   - `https://<username>.pythonanywhere.com/health` → `{"ok": true}`

Tezkor script:
- Bash console ichida: `bash deploy/pythonanywhere_setup.sh`
- (EU bo'lsa) oldindan: `export PA_DOMAIN="<username>.eu.pythonanywhere.com"`

## Eslatma
- Ma'lumotlar bazasi `Firebase Firestore` orqali saqlanadi.
- `firebase_credentials.json` yoki `FIREBASE_CREDENTIALS_JSON` yangi project service account bilan yangilangan bo'lishi kerak.
- Yangi foydalanuvchiga ro'yxatdan o'tganda 10 ta olmos beriladi.
 - Web panel HTTP Basic Auth bilan himoyalangan.
 - Free Render instance idle bo'lsa uyquga ketishi mumkin; keepalive workflow bu muammoni ancha kamaytiradi.
