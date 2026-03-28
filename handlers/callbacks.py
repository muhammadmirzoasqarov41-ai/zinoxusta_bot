from aiogram import Router
from aiogram.types import CallbackQuery

from datetime import datetime

from db import Database, ISO_FMT
from utils import friendly
from keyboards import master_card_nav_kb

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
    if user.get("is_blocked") == 1:
        await callback.answer(
            "Kechirasiz, akkauntingiz vaqtincha bloklangan. 😊", show_alert=True
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
    await db.add_order(user["tg_id"], target_tg_id, "open_contact")
    await callback.message.answer(friendly(text))
    await callback.answer("Kontakt ochildi. 😊")


@router.callback_query(lambda c: c.data and c.data.startswith("masters_page:"))
async def masters_page(callback: CallbackQuery, db: Database):
    if not callback.data:
        return
    offset_raw = callback.data.split(":", 1)[1]
    if not offset_raw.isdigit():
        await callback.answer("Noto'g'ri so'rov. 😊", show_alert=True)
        return
    offset = int(offset_raw)
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting. 😊", show_alert=True)
        return
    if user.get("is_blocked") == 1:
        await callback.answer("Kechirasiz, akkauntingiz vaqtincha bloklangan. 😊", show_alert=True)
        return
    masters = await db.list_masters(limit=2, offset=offset)
    if not masters:
        await callback.answer("Boshqa usta yo'q. 😊", show_alert=True)
        return
    master = masters[0]
    now = datetime.utcnow().strftime(ISO_FMT)
    is_top = master.get("top_until") and master["top_until"] > now
    is_vip = master.get("vip_until") and master["vip_until"] > now
    badges = []
    if is_top:
        badges.append("TOP")
    if is_vip:
        badges.append("VIP")
    badge_text = ", ".join(badges) if badges else "Oddiy"
    bio = master.get("bio") or "Ko'rsatilmagan"
    avg, cnt = await db.get_master_rating(master["tg_id"])
    text = (
        f"Ism-sharif: {master['full_name']}\n"
        f"Hudud: {master['region']}\n"
        f"Maqom: {badge_text}\n"
        f"Bio: {bio}\n"
        f"Reyting: {avg:.1f} ⭐️ ({cnt})\n"
        f"Kontakt: Yopiq (ochish uchun 10 💎)"
    )
    await callback.message.edit_text(
        friendly(text),
        reply_markup=master_card_nav_kb(
            master["tg_id"],
            offset=offset,
            has_next=len(masters) > 1,
            has_prev=offset > 0,
        ),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "urgent_cancel")
async def urgent_cancel(callback: CallbackQuery):
    await callback.message.answer(friendly("Shoshilinch chaqiruv bekor qilindi."))
    await callback.answer()


@router.callback_query(lambda c: c.data == "urgent_confirm")
async def urgent_confirm(callback: CallbackQuery, db: Database):
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting. 😊", show_alert=True)
        return
    if user.get("is_blocked") == 1:
        await callback.answer("Kechirasiz, akkauntingiz vaqtincha bloklangan. 😊", show_alert=True)
        return
    if user["diamonds"] < 30:
        await callback.answer("Balansingiz yetarli emas (30 💎 kerak). 😊", show_alert=True)
        return

    masters = await db.list_masters_by_region(user["region"])
    if not masters:
        masters = await db.list_masters(limit=500, offset=0)
        if not masters:
            await callback.message.answer(
                friendly("Afsuski, hozircha ustalar topilmadi. Hozircha olmos yechilmadi.")
            )
            await callback.answer()
            return

    ok = await db.deduct_diamonds(user["tg_id"], 30)
    if not ok:
        await callback.answer("Balansingiz yetarli emas. 😊", show_alert=True)
        return

    sent = 0
    for master in masters:
        try:
            await callback.bot.send_message(
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
            await db.add_order(user["tg_id"], master["tg_id"], "urgent_call")
            sent += 1
        except Exception:
            pass

    await callback.message.answer(
        friendly(
            f"Shoshilinch chaqiruv {sent} ta ustaga yuborildi. Sizdan 30 💎 Olmos yechildi."
        )
    )
    await callback.answer()
