from datetime import datetime

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db import Database, ISO_FMT
from keyboards import main_menu_kb, usta_services_kb, edit_profile_kb, urgent_confirm_kb
from utils import friendly
from states import ProfileEdit, RateMaster, SearchProfession, SearchRegion

router = Router()

BUY_DIAMONDS_TEXT = (
    "Hurmatli mijoz, hisobingizni to'ldirish va 💎 Olmoslar xarid qilish uchun "
    "to'g'ridan-to'g'ri adminimiz bilan bog'laning. To'lovni karta orqali amalga oshirganingizdan so'ng, "
    "admin hisobingizni tezda to'ldirib beradi!\n"
    "👨‍💻 Telegram: @zinox_1M\n"
    "📞 Telefon: +998880741015\n"
    "📧 Email: luxaidevs@gmail.com\n"
    "📸 Instagram: @luxaidevs"
)


@router.message(lambda m: m.text == "💎 Olmos sotib olish")
async def buy_diamonds(message: Message):
    await message.answer(BUY_DIAMONDS_TEXT)


@router.message(lambda m: m.text == "💎 Olmos balansim")
async def balance(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer(friendly("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting."))
        return
    if user.get("is_blocked") == 1:
        await message.answer(
            friendly("Kechirasiz, akkauntingiz vaqtincha bloklangan. Admin bilan bog'laning.")
        )
        return
    await message.answer(friendly(f"Sizning balansingiz: {user['diamonds']} 💎 Olmos."))


@router.message(lambda m: m.text == "🧑‍🔧 Ustalar ro'yxati")
async def masters_list(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer(friendly("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting."))
        return
    if user.get("is_blocked") == 1:
        await message.answer(
            friendly("Kechirasiz, akkauntingiz vaqtincha bloklangan. Admin bilan bog'laning.")
        )
        return
    masters = await db.list_masters(limit=2, offset=0)
    if not masters:
        await message.answer(friendly("Hozircha ustalar ro'yxati bo'sh. Keyinroq urinib ko'ring."))
        return
    await message.answer(friendly("Quyida ustalar ro'yxati taqdim etiladi:"))
    now = datetime.utcnow().strftime(ISO_FMT)
    master = masters[0]
    is_top = master.get("top_until") and master["top_until"] > now
    is_vip = master.get("vip_until") and master["vip_until"] > now
    badges = []
    if is_top:
        badges.append("TOP")
    if is_vip:
        badges.append("VIP")
    badge_text = ", ".join(badges) if badges else "Oddiy"
    bio = master.get("bio") or "Ko'rsatilmagan"
    avg, cnt = await db.get_master_rating(master["tg_id"])
    text = (
        f"Ism-sharif: {master['full_name']}\n"
        f"Hudud: {master['region']}\n"
        f"Maqom: {badge_text}\n"
        f"Bio: {bio}\n"
        f"Reyting: {avg:.1f} ⭐️ ({cnt})\n"
        f"Kontakt: Yopiq (ochish uchun 10 💎)"
    )
    from keyboards import master_card_nav_kb

    await message.answer(
        friendly(text),
        reply_markup=master_card_nav_kb(
            master["tg_id"], offset=0, has_next=len(masters) > 1, has_prev=False
        ),
    )


@router.message(lambda m: m.text == "🚨 Shoshilinch chaqiruv")
async def urgent_call(message: Message, db: Database, bot: Bot):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer(friendly("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting."))
        return
    if user.get("is_blocked") == 1:
        await message.answer(
            friendly("Kechirasiz, akkauntingiz vaqtincha bloklangan. Admin bilan bog'laning.")
        )
        return

    if user["diamonds"] < 30:
        await message.answer(
            friendly("Kechirasiz, shoshilinch chaqiruv uchun 30 💎 Olmos kerak bo'ladi.")
        )
        return

    await message.answer(
        friendly("Shoshilinch chaqiruv uchun 30 💎 yechiladi. Tasdiqlaysizmi?"),
        reply_markup=urgent_confirm_kb(),
    )


@router.message(lambda m: m.text == "🛠 Usta xizmatlari")
async def usta_services_menu(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer(friendly("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting."))
        return
    if user.get("is_blocked") == 1:
        await message.answer(
            friendly("Kechirasiz, akkauntingiz vaqtincha bloklangan. Admin bilan bog'laning.")
        )
        return
    if user["role"] != "usta":
        await message.answer(
            friendly(
                "Bu bo'lim asosan ustalar uchun mo'ljallangan. Agar siz usta bo'lsangiz, "
                "profil maqsadingizni yangilashingiz mumkin."
            ),
            reply_markup=usta_services_kb(),
        )
        return
    await message.answer(friendly("Ustalar uchun xizmatlar:"), reply_markup=usta_services_kb())


@router.message(lambda m: m.text == "⭐️ TOP ga chiqish (50💎)")
async def buy_top(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer(friendly("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting."))
        return
    if user.get("is_blocked") == 1:
        await message.answer(
            friendly("Kechirasiz, akkauntingiz vaqtincha bloklangan. Admin bilan bog'laning.")
        )
        return
    if user["diamonds"] < 50:
        await message.answer(friendly("TOP uchun 50 💎 Olmos kerak bo'ladi."))
        return
    ok = await db.deduct_diamonds(user["tg_id"], 50)
    if not ok:
        await message.answer(friendly("Balansingiz yetarli emas."))
        return
    await db.set_top(user["tg_id"], days=3)
    await message.answer(friendly("Profilingiz 3 kun uchun TOP ro'yxatiga chiqarildi."))


@router.message(lambda m: m.text == "👑 VIP maqomi (100💎)")
async def buy_vip(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer(friendly("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting."))
        return
    if user.get("is_blocked") == 1:
        await message.answer(
            friendly("Kechirasiz, akkauntingiz vaqtincha bloklangan. Admin bilan bog'laning.")
        )
        return
    if user["diamonds"] < 100:
        await message.answer(friendly("VIP maqomi uchun 100 💎 Olmos kerak bo'ladi."))
        return
    ok = await db.deduct_diamonds(user["tg_id"], 100)
    if not ok:
        await message.answer(friendly("Balansingiz yetarli emas."))
        return
    await db.set_vip(user["tg_id"], days=3650)
    await message.answer(friendly("Profilingizga VIP maqomi berildi."))


@router.message(lambda m: m.text == "⬅️ Orqaga")
async def back_to_main(message: Message):
    await message.answer(friendly("Asosiy menyuga qaytdik."), reply_markup=main_menu_kb())


@router.message(lambda m: m.text == "❓ Yordam")
async def help_message(message: Message):
    await message.answer(
        friendly(
            "Yordam kerak bo'lsa, admin bilan bog'laning: @zinox_1M"
        )
    )


@router.message(lambda m: m.text == "ℹ️ Bot haqida")
async def about_bot(message: Message):
    await message.answer(
        friendly(
            "USTA QIDIR — malakali ustalarni tez topish va mijozlarga xizmat ko'rsatishni osonlashtiruvchi bot.\n"
            "✅ Ichki olmos tizimi\n"
            "✅ Shoshilinch chaqiruv\n"
            "✅ TOP va VIP ustalar\n"
            "✅ Qulay va tezkor muloqot"
        )
    )


@router.message(lambda m: m.text == "✏️ Profilni tahrirlash")
async def edit_profile_start(message: Message, state: FSMContext, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer(friendly("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting."))
        return
    if user.get("is_blocked") == 1:
        await message.answer(
            friendly("Kechirasiz, akkauntingiz vaqtincha bloklangan. Admin bilan bog'laning.")
        )
        return
    await message.answer(friendly("Qaysi ma'lumotni tahrirlaysiz?"), reply_markup=edit_profile_kb())
    await state.set_state(ProfileEdit.field)


@router.message(ProfileEdit.field)
async def edit_profile_field(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    mapping = {
        "Ism-sharif": "full_name",
        "Telefon": "phone",
        "Hudud": "region",
        "Bio": "bio",
        "📷 Profil rasmi": "photo_id",
    }
    if text not in mapping:
        await message.answer(friendly("Iltimos, tugmalardan birini tanlang."), reply_markup=edit_profile_kb())
        return
    await state.update_data(field=mapping[text])
    if mapping[text] == "photo_id":
        await message.answer(friendly("Yangi profil rasmini yuboring."))
    else:
        await message.answer(friendly("Yangi qiymatni kiriting."))
    await state.set_state(ProfileEdit.value)


@router.message(ProfileEdit.value)
async def edit_profile_value(message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    field = data.get("field")
    if field == "photo_id":
        if not message.photo:
            await message.answer(friendly("Iltimos, rasm yuboring."))
            return
        value = message.photo[-1].file_id
    else:
        value = (message.text or "").strip()
        if len(value) < 2:
            await message.answer(friendly("Qiymat juda qisqa. Iltimos, qaytadan kiriting."))
            return
    if not field:
        await state.clear()
        await message.answer(friendly("Noma'lum xatolik. Qaytadan urinib ko'ring."))
        return
    await db.update_user_field(message.from_user.id, field, value)
    await state.clear()
    await message.answer(friendly("Ma'lumot yangilandi."), reply_markup=main_menu_kb())


@router.message(lambda m: m.text == "🔎 Usta qidirish")
async def search_master_start(message: Message, state: FSMContext):
    await message.answer(friendly("Kasb bo'yicha qidirish uchun kasb nomini yozing (masalan: santexnik)."))
    await state.set_state(SearchProfession.profession)


@router.message(SearchProfession.profession)
async def search_by_profession(message: Message, state: FSMContext, db: Database):
    profession = (message.text or "").strip()
    if len(profession) < 2:
        await message.answer(friendly("Iltimos, kasbni aniqroq yozing."))
        return
    masters = await db.list_masters_by_profession(profession, limit=2, offset=0)
    if not masters:
        await message.answer(friendly("Bu kasb bo'yicha usta topilmadi."))
        await state.clear()
        return
    await state.update_data(last_profession=profession)
    await state.clear()
    now = datetime.utcnow().strftime(ISO_FMT)
    master = masters[0]
    is_top = master.get("top_until") and master["top_until"] > now
    is_vip = master.get("vip_until") and master["vip_until"] > now
    badges = []
    if is_top:
        badges.append("TOP")
    if is_vip:
        badges.append("VIP")
    badge_text = ", ".join(badges) if badges else "Oddiy"
    bio = master.get("bio") or "Ko'rsatilmagan"
    text = (
        f"Ism-sharif: {master['full_name']}\n"
        f"Hudud: {master['region']}\n"
        f"Maqom: {badge_text}\n"
        f"Bio: {bio}\n"
        f"Kontakt: Yopiq (ochish uchun 10 💎)"
    )
    from keyboards import master_card_nav_kb

    await message.answer(
        friendly(text),
        reply_markup=master_card_nav_kb(
            master["tg_id"], offset=0, has_next=len(masters) > 1, has_prev=False
        ),
    )


@router.message(lambda m: m.text == "⭐️ Ustani baholash")
async def rate_start(message: Message, state: FSMContext):
    await message.answer(friendly("Iltimos, usta Telegram ID sini kiriting."))
    await state.set_state(RateMaster.master_id)


@router.message(RateMaster.master_id)
async def rate_master_id(message: Message, state: FSMContext):
    if not (message.text or "").isdigit():
        await message.answer(friendly("Iltimos, to'g'ri ID kiriting."))
        return
    await state.update_data(master_id=int(message.text))
    await message.answer(friendly("Bahoni kiriting (1-5)."))
    await state.set_state(RateMaster.rating)


@router.message(RateMaster.rating)
async def rate_master_rating(message: Message, state: FSMContext):
    if not (message.text or "").isdigit():
        await message.answer(friendly("1-5 oralig'ida baho kiriting."))
        return
    rating = int(message.text)
    if rating < 1 or rating > 5:
        await message.answer(friendly("1-5 oralig'ida baho kiriting."))
        return
    await state.update_data(rating=rating)
    await message.answer(friendly("Izoh yozing (ixtiyoriy). Agar yo'q bo'lsa 'yo'q' deb yozing."))
    await state.set_state(RateMaster.comment)


@router.message(RateMaster.comment)
async def rate_master_comment(message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    master_id = data.get("master_id")
    rating = data.get("rating")
    comment = (message.text or "").strip()
    if comment.lower() == "yo'q":
        comment = None
    await db.add_rating(master_id, message.from_user.id, rating, comment)
    await state.clear()
    await message.answer(friendly("Rahmat! Bahongiz qabul qilindi."), reply_markup=main_menu_kb())


@router.message(lambda m: m.text == "📜 Tarixim")
async def my_history(message: Message, db: Database):
    orders = await db.list_orders_for_user(message.from_user.id, limit=10)
    if not orders:
        await message.answer(friendly("Hozircha tarix bo'sh."))
        return
    text = "So'rovlar tarixi:\n"
    for o in orders:
        text += f"- {o['order_type']} | {o['created_at']}\n"
    await message.answer(friendly(text))


@router.message(lambda m: m.text == "📥 So'rovlar")
async def my_requests(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer(friendly("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting."))
        return
    if user.get("role") != "usta":
        await message.answer(friendly("Bu bo'lim faqat ustalar uchun."))
        return
    orders = await db.list_orders_for_master(message.from_user.id, limit=10)
    if not orders:
        await message.answer(friendly("Hozircha so'rovlar yo'q."))
        return
    text = "Kelgan so'rovlar:\n"
    for o in orders:
        text += f"- {o['order_type']} | {o['created_at']}\n"
    await message.answer(friendly(text))
