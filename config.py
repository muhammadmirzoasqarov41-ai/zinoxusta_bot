import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_id: int | None
    admin_username: str | None
    db_path: str
    web_user: str
    web_pass: str
    web_host: str
    web_port: int
    web_enabled: bool


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set")

    admin_id_raw = os.getenv("ADMIN_ID", "").strip()
    admin_id = int(admin_id_raw) if admin_id_raw.isdigit() else None

    admin_username = os.getenv("ADMIN_USERNAME", "").strip()
    if admin_username.startswith("@"):
        admin_username = admin_username[1:]
    if admin_username == "":
        admin_username = None

    db_path = os.getenv("DB_PATH", "ustaqidir.db").strip()
    web_user = os.getenv("WEB_USER", "admin").strip()
    web_pass = os.getenv("WEB_PASS", "admin").strip()
    web_host = os.getenv("WEB_HOST", "0.0.0.0").strip()
    web_port_raw = os.getenv("WEB_PORT", "8000").strip()
    web_port = int(web_port_raw) if web_port_raw.isdigit() else 8000
    web_enabled = os.getenv("WEB_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}

    return Config(
        bot_token=bot_token,
        admin_id=admin_id,
        admin_username=admin_username,
        db_path=db_path,
        web_user=web_user,
        web_pass=web_pass,
        web_host=web_host,
        web_port=web_port,
        web_enabled=web_enabled,
    )
