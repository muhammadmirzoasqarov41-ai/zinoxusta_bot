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
 - Web panel uchun `WEB_ENABLED=true`, `WEB_USER`, `WEB_PASS`, `WEB_PORT` qiymatlarini kiriting.

## Admin panel
- Admin sifatida kirish uchun `ADMIN_ID` yoki `ADMIN_USERNAME` ni sozlang.
- Admin buyruq: `/admin`.

## Eslatma
- Ma'lumotlar bazasi `SQLite` (`DB_PATH`) orqali saqlanadi.
- Yangi foydalanuvchiga ro'yxatdan o'tganda 10 ta olmos beriladi.
 - Web panel HTTP Basic Auth bilan himoyalangan.
