from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import Config
from db import Database
from keyboards import admin_menu_kb, main_menu_kb
from states import (
    AdminAddDiamonds,
    AdminRemoveDiamonds,
    AdminBroadcast,
    AdminAdBroadcast,
    AdminSendById,
    AdminBlockUser,
    AdminUnblockUser,
    AdminGiveAllDiamonds,
)
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
    try:
        await message.bot.send_message(
            user_id,
            friendly(
                f"Tabriklaymiz! Sizning hisobingizga {amount} 💎 Olmos qo'shildi. "
                "Botimiz sizga doimo xizmat qilishdan mamnun."
            ),
        )
    except Exception:
        pass


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
    user_ids = await db.list_user_ids()
    for tg_id in user_ids:
        try:
            await bot.send_message(tg_id, text)
            sent += 1
        except Exception:
            pass

    await message.answer(friendly(f"Xabar {sent} ta foydalanuvchiga yuborildi."))


@router.message(lambda m: m.text == "📢 Reklama yuborish")
async def admin_ad_start(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    await message.answer(
        friendly("Reklama postini yuboring (matn, rasm yoki video bo'lishi mumkin).")
    )
    await state.set_state(AdminAdBroadcast.message)


@router.message(AdminAdBroadcast.message)
async def admin_ad_send(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    await state.clear()

    bot = message.bot
    sent = 0
    user_ids = await db.list_user_ids()

    for tg_id in user_ids:
        try:
            await message.copy_to(chat_id=tg_id)
            sent += 1
        except Exception:
            pass

    await message.answer(friendly(f"Reklama {sent} ta foydalanuvchiga yuborildi."))


@router.message(lambda m: m.text == "👤 ID orqali xabar")
async def admin_send_by_id_start(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    await message.answer(friendly("Foydalanuvchi ID sini kiriting."))
    await state.set_state(AdminSendById.user_id)


@router.message(AdminSendById.user_id)
async def admin_send_by_id_user(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    if not (message.text or "").isdigit():
        await message.answer(friendly("Iltimos, to'g'ri foydalanuvchi ID kiriting."))
        return
    await state.update_data(user_id=int(message.text))
    await message.answer(friendly("Yuboriladigan xabarni kiriting (matn/rasm/video)."))
    await state.set_state(AdminSendById.message)


@router.message(AdminSendById.message)
async def admin_send_by_id_send(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    data = await state.get_data()
    user_id = data.get("user_id")
    await state.clear()
    try:
        await message.copy_to(chat_id=user_id)
        await message.answer(friendly("Xabar foydalanuvchiga yuborildi."))
    except Exception:
        await message.answer(friendly("Xabar yuborishda xatolik yuz berdi."))


@router.message(lambda m: m.text == "🚫 User bloklash")
async def admin_block_start(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    await message.answer(friendly("Bloklanadigan foydalanuvchi ID sini kiriting."))
    await state.set_state(AdminBlockUser.user_id)


@router.message(AdminBlockUser.user_id)
async def admin_block_user(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    if not (message.text or "").isdigit():
        await message.answer(friendly("Iltimos, to'g'ri foydalanuvchi ID kiriting."))
        return
    user_id = int(message.text)
    await db.set_blocked(user_id, True)
    await state.clear()
    await message.answer(friendly("Foydalanuvchi bloklandi."))


@router.message(lambda m: m.text == "✅ User blokdan olish")
async def admin_unblock_start(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    await message.answer(friendly("Blokdan olinadigan foydalanuvchi ID sini kiriting."))
    await state.set_state(AdminUnblockUser.user_id)


@router.message(AdminUnblockUser.user_id)
async def admin_unblock_user(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    if not (message.text or "").isdigit():
        await message.answer(friendly("Iltimos, to'g'ri foydalanuvchi ID kiriting."))
        return
    user_id = int(message.text)
    await db.set_blocked(user_id, False)
    await state.clear()
    await message.answer(friendly("Foydalanuvchi blokdan olindi."))


@router.message(lambda m: m.text == "💎 Barcha userlarga olmos")
async def admin_give_all_start(message: Message, state: FSMContext, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    await message.answer(friendly("Barcha foydalanuvchilarga beriladigan olmos miqdorini kiriting."))
    await state.set_state(AdminGiveAllDiamonds.amount)


@router.message(AdminGiveAllDiamonds.amount)
async def admin_give_all_send(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    if not (message.text or "").isdigit():
        await message.answer(friendly("Iltimos, to'g'ri miqdor kiriting."))
        return
    amount = int(message.text)
    await state.clear()
    count = await db.add_diamonds_all(amount)
    user_ids = await db.list_user_ids()
    sent = 0
    for tg_id in user_ids:
        try:
            await message.bot.send_message(
                tg_id,
                friendly(
                    f"Tabriklaymiz! Sizning hisobingizga {amount} 💎 Olmos qo'shildi. "
                    "Bu botimizdan sizga kichik sovg'a."
                ),
            )
            sent += 1
        except Exception:
            pass
    await message.answer(
        friendly(
            f"{count} ta foydalanuvchining balansiga {amount} 💎 Olmos qo'shildi. "
            f"Bildirishnoma {sent} ta foydalanuvchiga yuborildi."
        )
    )


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
