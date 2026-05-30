from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db_factory import get_database
from keyboards import contact_kb, main_menu_kb, profession_kb, regions_kb, role_select_kb
from states import Onboarding
from utils import friendly

router = Router()

WELCOME_TEXT = (
    "Assalomu alaykum, hurmatli foydalanuvchi! 🛠 USTA QIDIR botiga xush kelibsiz. "
    "Biz sizga eng malakali ustalarni topishda yoki mijozlar topishda bajonidil yordam beramiz! "
    "Ro'yxatdan o'tish uchun quyidagi ma'lumotlarni kiriting:"
)


def _user_is_complete(user: dict | None) -> bool:
    if not user:
        return False
    required = ("full_name", "phone", "region", "purpose", "role")
    return all(str(user.get(field) or "").strip() for field in required)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    db = get_database()
    await state.clear()
    user = await db.get_user(message.from_user.id)
    if user:
        if user.get("is_blocked") == 1:
            await message.answer(
                friendly("Kechirasiz, akkauntingiz vaqtincha bloklangan. Admin bilan bog'laning.")
            )
            return

        if _user_is_complete(user):
            await message.answer(
                friendly(
                    "Assalomu alaykum! Sizni yana ko'rib turganimizdan xursandmiz. "
                    "Bot sizning xizmatingizda. Sizga qanday yordam bera olamiz?"
                ),
                reply_markup=main_menu_kb(),
            )
            await state.clear()
            return

        await state.update_data(
            full_name=user.get("full_name") or message.from_user.full_name or "Unknown",
            phone=user.get("phone"),
            region=user.get("region"),
            role=user.get("role"),
            profession=user.get("profession"),
            bio=user.get("bio"),
            photo_id=user.get("photo_id"),
            ref_code=user.get("ref_code"),
        )
        if not str(user.get("phone") or "").strip():
            await message.answer(WELCOME_TEXT)
            await message.answer(
                friendly(
                    "Telefon raqamingizni yuboring. Iltimos, 'Raqamni yuborish' tugmasidan foydalaning."
                ),
                reply_markup=contact_kb(),
            )
            await state.set_state(Onboarding.phone)
            return
        if not str(user.get("region") or "").strip():
            await message.answer(WELCOME_TEXT)
            await message.answer(friendly("Yashash hududingizni tanlang:"), reply_markup=regions_kb())
            await state.set_state(Onboarding.region)
            return
        if not str(user.get("role") or "").strip():
            await message.answer(WELCOME_TEXT)
            await message.answer(
                friendly("Iltimos, o'zingizni tanlang: usta yoki mijoz?"),
                reply_markup=role_select_kb(),
            )
            await state.set_state(Onboarding.role)
            return
        if user.get("role") == "usta" and not str(user.get("profession") or "").strip():
            await message.answer(WELCOME_TEXT)
            await message.answer(
                friendly("Kasbingizni tanlang:"),
                reply_markup=profession_kb(),
            )
            await state.set_state(Onboarding.profession)
            return
        if user.get("role") == "usta" and not str(user.get("bio") or "").strip():
            await message.answer(WELCOME_TEXT)
            await message.answer(friendly("O'zingiz haqingizda qisqacha bio yozing."))
            await state.set_state(Onboarding.bio)
            return
        if not str(user.get("purpose") or "").strip():
            await message.answer(WELCOME_TEXT)
            await message.answer(
                friendly(
                    "Botimizga qanday maqsadda tashrif buyurdingiz? "
                    "(Masalan: Menga malakali santexnik kerak yoki Men ustaman, mijoz qidiryapman)"
                )
            )
            await state.set_state(Onboarding.purpose)
            return

    # Save referral code from /start if present (e.g. /start ref_xxx)
    if command.args:
        await state.update_data(ref_code=command.args.strip())

    # Create a lightweight user record immediately so /start bosilgani
    # database'da ko'rinadi, keyin onboarding tugaganda to'liq yangilanadi.
    await db.add_user(
        tg_id=message.from_user.id,
        full_name=message.from_user.full_name or "Unknown",
        phone="",
        region="",
        purpose="",
        role="",
        ref_code=f"u{message.from_user.id}",
        diamonds=0,
    )

    await message.answer(WELCOME_TEXT)
    await message.answer(friendly("Iltimos, to'liq ism-sharifingizni kiriting."))
    await state.set_state(Onboarding.full_name)
