from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🧑‍🔧 Ustalar ro'yxati"), KeyboardButton(text="🚨 Shoshilinch chaqiruv"))
    kb.row(KeyboardButton(text="🔎 Usta qidirish"), KeyboardButton(text="⭐️ Ustani baholash"))
    kb.row(KeyboardButton(text="📜 Tarixim"), KeyboardButton(text="📥 So'rovlar"))
    kb.row(KeyboardButton(text="🚪 Chatni yakunlash"))
    kb.row(KeyboardButton(text="🛠 Usta xizmatlari"), KeyboardButton(text="💎 Olmos balansim"))
    kb.row(KeyboardButton(text="✏️ Profilni tahrirlash"), KeyboardButton(text="💎 Olmos sotib olish"))
    kb.row(KeyboardButton(text="ℹ️ Bot haqida"), KeyboardButton(text="❓ Yordam"))
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


def role_select_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🧑‍🔧 Men ustaman"))
    kb.row(KeyboardButton(text="🙋‍♂️ Men mijozman"))
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def profession_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="Santexnik"), KeyboardButton(text="Elektrik"))
    kb.row(KeyboardButton(text="Slesar"), KeyboardButton(text="Payvandchi"))
    kb.row(KeyboardButton(text="Usta (umumiy)"), KeyboardButton(text="Mebelchi"))
    kb.row(KeyboardButton(text="Quruvchi"), KeyboardButton(text="Konditsioner ustasi"))
    kb.row(KeyboardButton(text="🚫 Hech qaysi"))
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


REGIONS: dict[str, list[str]] = {
    "Toshkent shahar": [
        "Bektemir", "Chilonzor", "Hamza", "Mirobod", "Mirzo Ulug'bek", "Sergeli",
        "Shayxontohur", "Uchtepa", "Yakkasaroy", "Yangihayot", "Yunusobod"
    ],
    "Toshkent viloyati": [
        "Angren", "Bekobod", "Bo'ka", "Bo'stonliq", "Chinoz", "Qibray", "Ohangaron",
        "Olmaliq", "Oqqo'rg'on", "Piskent", "Quyi Chirchiq", "Yangiyo'l",
        "Yuqori Chirchiq", "Zangiota"
    ],
    "Andijon": ["Andijon shahar", "Asaka", "Baliqchi", "Bo'ston", "Buloqboshi", "Izboskan", "Jalaquduq", "Marhamat", "Oltinko'l", "Paxtaobod", "Shahrixon", "Ulug'nor", "Xo'jaobod"],
    "Buxoro": ["Buxoro shahar", "Buxoro", "G'ijduvon", "Jondor", "Kogon", "Olot", "Peshku", "Qorako'l", "Qorovulbozor", "Romitan", "Shofirkon", "Vobkent"],
    "Farg'ona": ["Farg'ona shahar", "Beshariq", "Bog'dod", "Buvayda", "Dang'ara", "Furqat", "Qo'shtepa", "Quva", "Quvasoy", "Rishton", "So'x", "Toshloq", "Uchko'prik", "Yozyovon"],
    "Jizzax": ["Jizzax shahar", "Arnasoy", "Baxmal", "Do'stlik", "Forish", "G'allaorol", "Mirzacho'l", "Paxtakor", "Yangiobod", "Zafarobod", "Zarbdor"],
    "Xorazm": ["Urganch", "Bog'ot", "Gurlan", "Hazorasp", "Khiva", "Qo'shko'pir", "Shovot", "Urganch tuman", "Xonqa", "Yangibozor", "Yangiariq"],
    "Namangan": ["Namangan shahar", "Chortoq", "Chust", "Kosonsoy", "Mingbuloq", "Norin", "Pop", "To'raqo'rg'on", "Uchqo'rg'on", "Uychi", "Yangiqo'rg'on"],
    "Navoiy": ["Navoiy shahar", "Karmana", "Konimex", "Navbahor", "Nurota", "Qiziltepa", "Tomdi", "Uchquduq", "Xatirchi", "Zarafshon"],
    "Qashqadaryo": ["Qarshi", "Chiroqchi", "Dehqonobod", "G'uzor", "Kasbi", "Kitob", "Koson", "Mirishkor", "Muborak", "Nishon", "Shahrisabz", "Yakkabog'"],
    "Qoraqalpog'iston": ["Nukus", "Amudaryo", "Beruniy", "Chimboy", "Ellikqal'a", "Kegeyli", "Mo'ynoq", "Qonliko'l", "Qorao'zak", "Shumanay", "Taxtako'pir", "To'rtko'l", "Xo'jayli"],
    "Samarqand": ["Samarqand shahar", "Bulung'ur", "Ishtixon", "Jomboy", "Kattaqo'rg'on", "Kattaqo'rg'on shahar", "Narpay", "Nurobod", "Oqdaryo", "Paxtachi", "Payariq", "Pastdarg'om", "Qo'shrabot", "Tayloq", "Urgut"],
    "Sirdaryo": ["Guliston", "Boyovut", "Mirzaobod", "Oqoltin", "Sardoba", "Sayxunobod", "Sirdaryo", "Xovos", "Yangiyer"],
    "Surxondaryo": ["Termiz", "Angor", "Bandixon", "Boysun", "Denov", "Jarqo'rg'on", "Muzrabot", "Oltinsoy", "Qiziriq", "Qumqo'rg'on", "Sariosiyo", "Sherobod", "Sho'rchi", "Uzun"],
    "Buxoro shahar": ["Buxoro shahar"],
}


def regions_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for name in REGIONS.keys():
        builder.button(text=name, callback_data=f"region:{name}")
    builder.adjust(2)
    return builder.as_markup()


def districts_kb(region: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for name in REGIONS.get(region, []):
        builder.button(text=name, callback_data=f"district:{region}:{name}")
    builder.button(text="⬅️ Orqaga", callback_data="region_back")
    builder.adjust(2)
    return builder.as_markup()


def edit_profile_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="Ism-sharif"), KeyboardButton(text="Telefon"))
    kb.row(KeyboardButton(text="Hudud"), KeyboardButton(text="Bio"))
    kb.row(KeyboardButton(text="📷 Profil rasmi"))
    kb.row(KeyboardButton(text="⬅️ Orqaga"))
    return kb.as_markup(resize_keyboard=True)


def skip_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="⏭️ O'tkazib yuborish"))
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def master_card_kb(tg_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔔 Jalb qilish (10💎)", callback_data=f"open_contact:{tg_id}")
    builder.button(text="💬 Chat boshlash", callback_data=f"start_chat:{tg_id}")
    builder.adjust(1)
    return builder.as_markup()


def master_card_nav_kb(tg_id: int, offset: int, has_next: bool, has_prev: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔔 Jalb qilish (10💎)", callback_data=f"open_contact:{tg_id}")
    builder.button(text="💬 Chat boshlash", callback_data=f"start_chat:{tg_id}")
    if has_prev:
        builder.button(text="⬅️ Oldingi", callback_data=f"masters_page:{max(offset-1,0)}")
    if has_next:
        builder.button(text="➡️ Keyingi", callback_data=f"masters_page:{offset+1}")
    builder.adjust(1, 2, 2)
    return builder.as_markup()


def urgent_confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data="urgent_confirm")
    builder.button(text="❌ Bekor qilish", callback_data="urgent_cancel")
    builder.adjust(2)
    return builder.as_markup()


def admin_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="➕ Olmos qo'shish"), KeyboardButton(text="➖ Olmos ayirish"))
    kb.row(KeyboardButton(text="💎 Barcha userlarga olmos"))
    kb.row(KeyboardButton(text="👤 ID orqali xabar"))
    kb.row(KeyboardButton(text="📣 Xabar yuborish"), KeyboardButton(text="📢 Reklama yuborish"))
    kb.row(KeyboardButton(text="🚫 User bloklash"), KeyboardButton(text="✅ User blokdan olish"))
    kb.row(KeyboardButton(text="📊 Statistika"))
    kb.row(KeyboardButton(text="⬅️ Orqaga"))
    return kb.as_markup(resize_keyboard=True)
