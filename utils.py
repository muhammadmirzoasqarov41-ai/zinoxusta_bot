from aiogram.types import User


def friendly(text: str) -> str:
    if "😊" in text or "🙂" in text:
        return text
    return f"{text} 😊\nYordam berishga tayyorman."


def detect_role(purpose_text: str) -> str:
    text = purpose_text.lower()
    if "usta" in text and "kerak" not in text:
        return "usta"
    if "mijoz" in text and "qidir" in text:
        return "usta"
    return "mijoz"


def is_admin(user: User, admin_id: int | None, admin_username: str | None) -> bool:
    if admin_id is not None and user.id == admin_id:
        return True
    if admin_username and user.username:
        return user.username.lower() == admin_username.lower()
    return False
