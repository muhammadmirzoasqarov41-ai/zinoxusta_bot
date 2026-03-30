from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db import Database
from aiogram import F
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

from keyboards import (
    contact_kb,
    main_menu_kb,
    role_select_kb,
    role_inline_kb,
    profession_kb,
    regions_kb,
    districts_kb,
    skip_kb,
)
from states import Onboarding
from utils import friendly

router = Router()


@router.message(Onboarding.full_name)
async def onboarding_full_name(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if len(text) < 3:
        await message.answer(friendly("Iltimos, to'liq ism-sharifingizni kiriting."))
        return
    await state.update_data(full_name=text)
    await message.answer(
        friendly(
            "Telefon raqamingizni yuboring. Iltimos, 'Raqamni yuborish' tugmasidan foydalaning."
        ),
        reply_markup=contact_kb(),
    )
    await state.set_state(Onboarding.phone)


@router.message(Onboarding.phone)
async def onboarding_phone(message: Message, state: FSMContext):
    if not message.contact or not message.contact.phone_number:
        await message.answer(
            friendly("Iltimos, telefon raqamingizni aynan tugma orqali yuboring."),
            reply_markup=contact_kb(),
        )
        return
    await state.update_data(phone=message.contact.phone_number)
    await message.answer(
        friendly("Yashash hududingizni tanlang:"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        friendly("Hududni tanlash tugmalari pastda chiqadi."),
        reply_markup=regions_kb(),
    )
    await state.set_state(Onboarding.region)


@router.message(Onboarding.region)
async def onboarding_region(message: Message, state: FSMContext):
    # Fallback: if user typed region manually, allow continuing to role selection
    text = (message.text or "").strip()
    if len(text) >= 3:
        await state.update_data(region=text)
        await message.answer(
            friendly("Iltimos, o'zingizni tanlang: usta yoki mijoz?"),
            reply_markup=role_select_kb(),
        )
        await state.set_state(Onboarding.role)
        return
    await message.answer(friendly("Iltimos, hududni tugmalar orqali tanlang."))


@router.callback_query(F.data == "region_back")
async def region_back(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(friendly("Yashash hududingizni tanlang:"))
    await callback.message.edit_reply_markup(reply_markup=regions_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("region:"))
async def pick_region(callback: CallbackQuery, state: FSMContext):
    region = callback.data.split("region:", 1)[1]
    await state.update_data(region=region)
    await callback.message.edit_text(friendly(f"{region} tanlandi. Endi tumanni tanlang:"))
    await callback.message.edit_reply_markup(reply_markup=districts_kb(region))
    await state.set_state(Onboarding.district)
    await callback.answer()


@router.callback_query(F.data.startswith("district:"))
async def pick_district(callback: CallbackQuery, state: FSMContext):
    _, region, district = callback.data.split(":", 2)
    await state.update_data(region=f"{region}, {district}")
    await callback.message.edit_text(
        friendly(f"Hududingiz: {region}, {district}. Endi o'zingizni tanlang:")
    )
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer(
        friendly(""),
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.message.answer(
        friendly("Iltimos, o'zingizni tanlang:"),
        reply_markup=role_inline_kb(),
    )
    await state.set_state(Onboarding.role)
    await callback.answer()


@router.callback_query(F.data.startswith("role:"))
async def pick_role_inline(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split(":", 1)[1]
    if role not in {"usta", "mijoz"}:
        await callback.answer("Noto'g'ri tanlov. 😊", show_alert=True)
        return
    await state.update_data(role=role)
    if role == "usta":
        await callback.message.answer(
            friendly("Kasbingizni tanlang:"),
            reply_markup=profession_kb(),
        )
        await state.set_state(Onboarding.profession)
    else:
        await callback.message.answer(
            friendly(
                "Botimizga qanday maqsadda tashrif buyurdingiz? "
                "(Masalan: Menga malakali santexnik kerak yoki Men ustaman, mijoz qidiryapman)"
            )
        )
        await state.set_state(Onboarding.purpose)
    await callback.answer()


@router.message(Onboarding.role)
async def onboarding_role(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "🧑‍🔧 Men ustaman" or "usta" in text.lower():
        role = "usta"
    elif text == "🙋‍♂️ Men mijozman" or "mijoz" in text.lower():
        role = "mijoz"
    else:
        await message.answer(
            friendly("Iltimos, quyidagi tugmalardan birini tanlang."),
            reply_markup=role_select_kb(),
        )
        return
    await state.update_data(role=role)
    if role == "usta":
        await message.answer(
            friendly("Kasbingizni tanlang:"),
            reply_markup=profession_kb(),
        )
        await state.set_state(Onboarding.profession)
        return
    await message.answer(
        friendly(
            "Botimizga qanday maqsadda tashrif buyurdingiz? "
            "(Masalan: Menga malakali santexnik kerak yoki Men ustaman, mijoz qidiryapman)"
        )
    )
    await state.set_state(Onboarding.purpose)


@router.message(Onboarding.profession)
async def onboarding_profession(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "🚫 Hech qaysi":
        await message.answer(friendly("Kasbingizni yozing (masalan: santexnik)."))
        await state.set_state(Onboarding.profession_custom)
        return
    if len(text) < 2:
        await message.answer(friendly("Iltimos, kasbingizni tanlang."))
        return
    await state.update_data(profession=text)
    await message.answer(friendly("O'zingiz haqingizda qisqacha bio yozing."))
    await state.set_state(Onboarding.bio)


@router.message(Onboarding.profession_custom)
async def onboarding_profession_custom(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if len(text) < 2:
        await message.answer(friendly("Iltimos, kasbingizni aniqroq yozing."))
        return
    await state.update_data(profession=text)
    await message.answer(friendly("O'zingiz haqingizda qisqacha bio yozing."))
    await state.set_state(Onboarding.bio)


@router.message(Onboarding.bio)
async def onboarding_bio(message: Message, state: FSMContext):
    bio = (message.text or "").strip()
    if len(bio) < 3:
        await message.answer(friendly("Bio juda qisqa. Iltimos, biroz batafsil yozing."))
        return
    await state.update_data(bio=bio)
    await message.answer(
        friendly("Profil uchun rasmingizni yuboring (ixtiyoriy)."),
        reply_markup=skip_kb(),
    )
    await state.set_state(Onboarding.photo)


@router.message(Onboarding.photo)
async def onboarding_photo(message: Message, state: FSMContext):
    if message.text and "O'tkazib yuborish" in message.text:
        await state.update_data(photo_id=None)
    elif message.photo:
        await state.update_data(photo_id=message.photo[-1].file_id)
    else:
        await message.answer(friendly("Iltimos, rasm yuboring yoki o'tkazib yuboring."), reply_markup=skip_kb())
        return
    await message.answer(
        friendly(
            "Botimizga qanday maqsadda tashrif buyurdingiz? "
            "(Masalan: Menga malakali santexnik kerak yoki Men ustaman, mijoz qidiryapman)"
        )
    )
    await state.set_state(Onboarding.purpose)


@router.message(Onboarding.purpose)
async def onboarding_purpose(message: Message, state: FSMContext, db: Database):
    purpose = (message.text or "").strip()
    if len(purpose) < 3:
        await message.answer(friendly("Iltimos, maqsadingizni qisqacha yozing."))
        return

    data = await state.get_data()
    full_name = data.get("full_name")
    phone = data.get("phone")
    region = data.get("region")
    role = data.get("role") or "mijoz"
    profession = data.get("profession")
    bio = data.get("bio")
    photo_id = data.get("photo_id")
    ref_code_raw = data.get("ref_code")
    referrer_id = None
    if ref_code_raw and ref_code_raw.startswith("ref_"):
        ref_key = ref_code_raw.replace("ref_", "", 1)
        ref_user = await db.get_by_ref_code(ref_key)
        if ref_user and ref_user.get("tg_id") != message.from_user.id:
            referrer_id = int(ref_user["tg_id"])

    await db.add_user(
        tg_id=message.from_user.id,
        full_name=full_name,
        phone=phone,
        region=region,
        purpose=purpose,
        role=role,
        profession=profession,
        bio=bio,
        photo_id=photo_id,
        ref_code=f"u{message.from_user.id}",
        referred_by=referrer_id,
        diamonds=10,
    )

    await state.clear()

    await message.answer(
        "Ro'yxatdan o'tganingiz uchun rahmat! 🎁 Sizga sovg'a sifatida 10 ta 💎 Olmos taqdim etildi. "
        "Botimiz doimo xizmatingizda. 😊\nYordam berishga tayyorman."
    )
    if referrer_id:
        await db.add_diamonds(referrer_id, 3)
        try:
            await message.bot.send_message(
                referrer_id,
                friendly("Tabriklaymiz! Taklifingiz orqali yangi foydalanuvchi ro'yxatdan o'tdi va sizga 3 💎 Olmos berildi."),
            )
        except Exception:
            pass
    await message.answer(
        friendly("Quyidagi menyudan kerakli bo'limni tanlashingiz mumkin."),
        reply_markup=main_menu_kb(),
    )
