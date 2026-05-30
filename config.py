import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
    load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)
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
    webhook_enabled: bool
    webhook_base_url: str
    webhook_path: str
    groq_api_key: str | None
    groq_model: str
    db_type: str
    firebase_project_id: str | None
    firebase_private_key: str | None
    firebase_client_email: str | None


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
    web_port_raw = os.getenv("WEB_PORT", os.getenv("PORT", "8000")).strip()
    web_port = int(web_port_raw) if web_port_raw.isdigit() else 8000
    web_enabled = os.getenv("WEB_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}

    webhook_enabled = os.getenv("WEBHOOK_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
    webhook_base_url = os.getenv(
        "WEBHOOK_BASE_URL",
        os.getenv("RENDER_EXTERNAL_URL", ""),
    ).strip().rstrip("/")
    webhook_path = os.getenv("WEBHOOK_PATH", "").strip()
    if webhook_enabled:
        if not webhook_base_url:
            raise RuntimeError("WEBHOOK_BASE_URL is required when WEBHOOK_ENABLED=true")
        if not webhook_path:
            raise RuntimeError("WEBHOOK_PATH is required when WEBHOOK_ENABLED=true")
        if not webhook_path.startswith("/"):
            raise RuntimeError("WEBHOOK_PATH must start with '/'")

    groq_api_key = os.getenv("GROQ_API_KEY", "").strip() or None
    groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()

    # Firebase configuration
    db_type = os.getenv("DB_TYPE", "sqlite").strip()
    firebase_project_id = os.getenv("FIREBASE_PROJECT_ID", "").strip() or None
    firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").strip() or None
    firebase_client_email = os.getenv("FIREBASE_CLIENT_EMAIL", "").strip() or None

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
        webhook_enabled=webhook_enabled,
        webhook_base_url=webhook_base_url,
        webhook_path=webhook_path,
        groq_api_key=groq_api_key,
        groq_model=groq_model,
        db_type=db_type,
        firebase_project_id=firebase_project_id,
        firebase_private_key=firebase_private_key,
        firebase_client_email=firebase_client_email,
    )
