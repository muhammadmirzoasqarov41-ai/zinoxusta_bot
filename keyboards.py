from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🧑‍🔧 Ustalar ro'yxati"), KeyboardButton(text="🚨 Shoshilinch chaqiruv"))
    kb.row(KeyboardButton(text="🛠 Usta xizmatlari"), KeyboardButton(text="💎 Olmos balansim"))
    kb.row(KeyboardButton(text="💎 Olmos sotib olish"))
    kb.row(KeyboardButton(text="❓ Yordam"))
    return kb.as_markup(resize_keyboard=True)


def contact_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Raqamni yuborish", request_contact=True))
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def usta_services_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="⭐️ TOP ga chiqish (50💎)"))
    kb.row(KeyboardButton(text="👑 VIP maqomi (100💎)"))
    kb.row(KeyboardButton(text="⬅️ Orqaga"))
    return kb.as_markup(resize_keyboard=True)


def back_to_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="⬅️ Orqaga"))
    return kb.as_markup(resize_keyboard=True)


def master_card_kb(tg_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📞 Raqamini ochish (10💎)", callback_data=f"open_contact:{tg_id}")
    return builder.as_markup()


def admin_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="➕ Olmos qo'shish"), KeyboardButton(text="➖ Olmos ayirish"))
    kb.row(KeyboardButton(text="📣 Xabar yuborish"), KeyboardButton(text="📊 Statistika"))
    kb.row(KeyboardButton(text="⬅️ Orqaga"))
    return kb.as_markup(resize_keyboard=True)
