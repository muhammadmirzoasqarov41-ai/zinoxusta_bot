from aiogram import Router
from aiogram.types import CallbackQuery

from db import Database
from utils import friendly

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("open_contact:"))
async def open_contact(callback: CallbackQuery, db: Database):
    if not callback.data:
        return
    parts = callback.data.split(":", 1)
    if len(parts) != 2 or not parts[1].isdigit():
        await callback.answer("Noto'g'ri so'rov. 😊", show_alert=True)
        return

    target_tg_id = int(parts[1])
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer(
            "Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting. 😊", show_alert=True
        )
        return

    if user["diamonds"] < 10:
        await callback.answer("Balansingiz yetarli emas (10 💎 kerak). 😊", show_alert=True)
        return

    target = await db.get_user(target_tg_id)
    if not target:
        await callback.answer("Usta topilmadi. 😊", show_alert=True)
        return

    ok = await db.deduct_diamonds(user["tg_id"], 10)
    if not ok:
        await callback.answer("Balansingiz yetarli emas. 😊", show_alert=True)
        return

    text = (
        "Usta kontakti ochildi:\n"
        f"Ism-sharif: {target['full_name']}\n"
        f"Telefon: {target['phone']}\n"
        f"Hudud: {target['region']}\n"
        "Rahmat!"
    )
    await callback.message.answer(friendly(text))
    await callback.answer("Kontakt ochildi. 😊")
