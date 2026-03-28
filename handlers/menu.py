from datetime import datetime

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db import Database, ISO_FMT
from keyboards import main_menu_kb, usta_services_kb, edit_profile_kb
from utils import friendly
from states import ProfileEdit

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

    masters = await db.list_masters_by_region(user["region"])
    if not masters:
        await message.answer(
            friendly("Afsuski, sizning hududingizda ustalar topilmadi. Hozircha olmos yechilmadi.")
        )
        return

    ok = await db.deduct_diamonds(user["tg_id"], 30)
    if not ok:
        await message.answer(friendly("Balansingiz yetarli emas."))
        return

    sent = 0
    for master in masters:
        try:
            await bot.send_message(
                master["tg_id"],
                friendly(
                    "Sizning hududingizda shoshilinch chaqiruv bor!\n"
                    f"Mijoz: {user['full_name']}\n"
                    f"Telefon: {user['phone']}\n"
                    f"Hudud: {user['region']}\n"
                    f"Maqsad: {user['purpose']}\n"
                    "Iltimos, imkoningiz bo'lsa tezda bog'laning."
                ),
            )
            sent += 1
        except Exception:
            pass

    await message.answer(
        friendly(
            f"Shoshilinch chaqiruv {sent} ta ustaga yuborildi. Sizdan 30 💎 Olmos yechildi."
        )
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
    }
    if text not in mapping:
        await message.answer(friendly("Iltimos, tugmalardan birini tanlang."), reply_markup=edit_profile_kb())
        return
    await state.update_data(field=mapping[text])
    await message.answer(friendly("Yangi qiymatni kiriting."))
    await state.set_state(ProfileEdit.value)


@router.message(ProfileEdit.value)
async def edit_profile_value(message: Message, state: FSMContext, db: Database):
    value = (message.text or "").strip()
    if len(value) < 2:
        await message.answer(friendly("Qiymat juda qisqa. Iltimos, qaytadan kiriting."))
        return
    data = await state.get_data()
    field = data.get("field")
    if not field:
        await state.clear()
        await message.answer(friendly("Noma'lum xatolik. Qaytadan urinib ko'ring."))
        return
    await db.update_user_field(message.from_user.id, field, value)
    await state.clear()
    await message.answer(friendly("Ma'lumot yangilandi."), reply_markup=main_menu_kb())
