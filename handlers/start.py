from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db import Database
from keyboards import main_menu_kb
from states import Onboarding
from utils import friendly

router = Router()

WELCOME_TEXT = (
    "Assalomu alaykum, hurmatli foydalanuvchi! 🛠 USTA QIDIR botiga xush kelibsiz. "
    "Biz sizga eng malakali ustalarni topishda yoki mijozlar topishda bajonidil yordam beramiz! "
    "Ro'yxatdan o'tish uchun quyidagi ma'lumotlarni kiriting:"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database):
    user = await db.get_user(message.from_user.id)
    if user:
        await message.answer(
            friendly(
                "Assalomu alaykum! Sizni yana ko'rib turganimizdan xursandmiz. "
                "Bot sizning xizmatingizda. Sizga qanday yordam bera olamiz?"
            ),
            reply_markup=main_menu_kb(),
        )
        await state.clear()
        return

    await message.answer(WELCOME_TEXT)
    await message.answer(friendly("Iltimos, to'liq ism-sharifingizni kiriting."))
    await state.set_state(Onboarding.full_name)
