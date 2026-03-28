from aiogram import Router
from aiogram.types import Message

from db import Database
from keyboards import main_menu_kb
from utils import friendly

router = Router()


@router.message(lambda m: m.text == "🚪 Chatni yakunlash")
async def end_chat(message: Message, db: Database):
    ok = await db.end_chat(message.from_user.id)
    if ok:
        await message.answer(friendly("Chat yakunlandi."), reply_markup=main_menu_kb())
    else:
        await message.answer(friendly("Hozirda faol chat yo'q."), reply_markup=main_menu_kb())


@router.message()
async def relay_chat(message: Message, db: Database):
    # Only relay plain text/photos/voice etc. If no active chat, do nothing.
    partner_id = await db.get_chat_partner(message.from_user.id)
    if not partner_id:
        return

    try:
        await message.copy_to(chat_id=partner_id)
    except Exception:
        await message.answer(friendly("Xabarni yetkazishda xatolik yuz berdi."))
