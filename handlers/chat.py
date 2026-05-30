from aiogram import Router
from aiogram.types import Message

from db_factory import get_database
from keyboards import main_menu_kb
from utils import friendly

router = Router()


@router.message(lambda m: m.text == "🚪 Chatni yakunlash")
async def end_chat(message: Message):
    ok = await get_database().end_chat(message.from_user.id)
    if ok:
        await message.answer(friendly("Chat yakunlandi."), reply_markup=main_menu_kb())
    else:
        await message.answer(friendly("Hozirda faol chat yo'q."), reply_markup=main_menu_kb())


@router.message()
async def relay_chat(message: Message):
    # Only relay plain text/photos/voice etc. If no active chat, do nothing.
    partner_id = await get_database().get_chat_partner(message.from_user.id)
    if not partner_id:
        return

    try:
        await message.copy_to(chat_id=partner_id)
    except Exception:
        await message.answer(friendly("Xabarni yetkazishda xatolik yuz berdi."))
