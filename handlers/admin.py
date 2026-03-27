from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import aiosqlite

from config import Config
from db import Database
from keyboards import admin_menu_kb, main_menu_kb
from states import AdminAddDiamonds, AdminRemoveDiamonds, AdminBroadcast
from utils import friendly, is_admin

router = Router()


@router.message(Command("admin"))
async def admin_start(message: Message, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        await message.answer(friendly("Kechirasiz, bu bo'lim faqat admin uchun."))
        return
    await message.answer(friendly("Admin paneliga xush kelibsiz."), reply_markup=admin_menu_kb())


@router.message(lambda m: m.text == "➕ Olmos qo'shish")
async def admin_add_start(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    await message.answer(friendly("Foydalanuvchi ID sini kiriting."))
    await state.set_state(AdminAddDiamonds.user_id)


@router.message(AdminAddDiamonds.user_id)
async def admin_add_user_id(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    if not (message.text or "").isdigit():
        await message.answer(friendly("Iltimos, to'g'ri foydalanuvchi ID kiriting."))
        return
    await state.update_data(user_id=int(message.text))
    await message.answer(friendly("Qo'shiladigan olmos miqdorini kiriting."))
    await state.set_state(AdminAddDiamonds.amount)


@router.message(AdminAddDiamonds.amount)
async def admin_add_amount(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    if not (message.text or "").isdigit():
        await message.answer(friendly("Iltimos, to'g'ri miqdor kiriting."))
        return
    amount = int(message.text)
    data = await state.get_data()
    user_id = data.get("user_id")
    await db.add_diamonds(user_id, amount)
    await state.clear()
    await message.answer(friendly("Olmoslar muvaffaqiyatli qo'shildi."))


@router.message(lambda m: m.text == "➖ Olmos ayirish")
async def admin_remove_start(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    await message.answer(friendly("Foydalanuvchi ID sini kiriting."))
    await state.set_state(AdminRemoveDiamonds.user_id)


@router.message(AdminRemoveDiamonds.user_id)
async def admin_remove_user_id(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    if not (message.text or "").isdigit():
        await message.answer(friendly("Iltimos, to'g'ri foydalanuvchi ID kiriting."))
        return
    await state.update_data(user_id=int(message.text))
    await message.answer(friendly("Ayiriladigan olmos miqdorini kiriting."))
    await state.set_state(AdminRemoveDiamonds.amount)


@router.message(AdminRemoveDiamonds.amount)
async def admin_remove_amount(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    if not (message.text or "").isdigit():
        await message.answer(friendly("Iltimos, to'g'ri miqdor kiriting."))
        return
    amount = int(message.text)
    data = await state.get_data()
    user_id = data.get("user_id")
    ok = await db.deduct_diamonds(user_id, amount)
    await state.clear()
    if not ok:
        await message.answer(friendly("Balans yetarli emas yoki foydalanuvchi topilmadi."))
        return
    await message.answer(friendly("Olmoslar muvaffaqiyatli ayirildi."))


@router.message(lambda m: m.text == "📣 Xabar yuborish")
async def admin_broadcast_start(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    await message.answer(friendly("Yuboriladigan xabar matnini kiriting."))
    await state.set_state(AdminBroadcast.message)


@router.message(AdminBroadcast.message)
async def admin_broadcast_send(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    text = message.text or ""
    await state.clear()

    from aiogram import Bot

    bot: Bot = message.bot
    sent = 0

    async with aiosqlite.connect(db.db_path) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT tg_id FROM users") as cur:
            rows = await cur.fetchall()
            for row in rows:
                try:
                    await bot.send_message(row["tg_id"], text)
                    sent += 1
                except Exception:
                    pass

    await message.answer(friendly(f"Xabar {sent} ta foydalanuvchiga yuborildi."))


@router.message(lambda m: m.text == "📊 Statistika")
async def admin_stats(message: Message, db: Database, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    stats = await db.stats()
    await message.answer(
        friendly(
            "Baza statistikasi:\n"
            f"Foydalanuvchilar: {stats['total_users']}\n"
            f"Umumiy sarflangan olmos: {stats['total_spent']}\n"
            f"Umumiy balans: {stats['total_balance']}"
        )
    )


@router.message(lambda m: m.text == "⬅️ Orqaga")
async def admin_back(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    await state.clear()
    await message.answer(friendly("Asosiy menyu."), reply_markup=main_menu_kb())
