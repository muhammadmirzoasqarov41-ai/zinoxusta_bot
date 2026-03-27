from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db import Database
from keyboards import contact_kb, main_menu_kb, role_select_kb
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
    await message.answer(friendly("Elektron pochtangizni (email) kiriting."))
    await state.set_state(Onboarding.email)


@router.message(Onboarding.email)
async def onboarding_email(message: Message, state: FSMContext):
    email = (message.text or "").strip()
    if "@" not in email or "." not in email:
        await message.answer(friendly("Iltimos, to'g'ri email kiriting."))
        return
    await state.update_data(email=email)
    await message.answer(
        friendly(
            "Yashash hududingizni yozing (Masalan: Andijon viloyati, Qo'rg'ontepa tumani)."
        )
    )
    await state.set_state(Onboarding.region)


@router.message(Onboarding.region)
async def onboarding_region(message: Message, state: FSMContext):
    region = (message.text or "").strip()
    if len(region) < 3:
        await message.answer(friendly("Iltimos, yashash hududingizni to'liqroq yozing."))
        return
    await state.update_data(region=region)
    await message.answer(
        friendly("Iltimos, o'zingizni tanlang: usta yoki mijoz?"),
        reply_markup=role_select_kb(),
    )
    await state.set_state(Onboarding.role)


@router.message(Onboarding.role)
async def onboarding_role(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "🧑‍🔧 Men ustaman":
        role = "usta"
    elif text == "🙋‍♂️ Men mijozman":
        role = "mijoz"
    else:
        await message.answer(
            friendly("Iltimos, quyidagi tugmalardan birini tanlang."),
            reply_markup=role_select_kb(),
        )
        return
    await state.update_data(role=role)
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
    email = data.get("email")
    region = data.get("region")
    role = data.get("role") or "mijoz"

    await db.add_user(
        tg_id=message.from_user.id,
        full_name=full_name,
        phone=phone,
        email=email,
        region=region,
        purpose=purpose,
        role=role,
        diamonds=10,
    )

    await state.clear()

    await message.answer(
        "Ro'yxatdan o'tganingiz uchun rahmat! 🎁 Sizga sovg'a sifatida 10 ta 💎 Olmos taqdim etildi. "
        "Botimiz doimo xizmatingizda. 😊\nYordam berishga tayyorman."
    )
    await message.answer(
        friendly("Quyidagi menyudan kerakli bo'limni tanlashingiz mumkin."),
        reply_markup=main_menu_kb(),
    )
