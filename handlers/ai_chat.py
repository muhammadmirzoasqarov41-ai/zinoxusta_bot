from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from db import Database
from keyboards import main_menu_kb, ai_chat_kb
from utils import friendly
from ai_agent import get_ai_agent
import asyncio

router = Router()

# Simple state management for AI conversations
active_ai_users = set()


@router.message(F.text == "🤖 AI Yordamchi")
async def start_ai_chat(message: Message):
    """AI yordamchi bilan suhbatni boshlash"""
    user_id = message.from_user.id
    
    print(f"🔍 AI Chat requested by user {user_id}")
    
    # AI agentni olish
    try:
        ai_agent = await get_ai_agent()
        await ai_agent.start_conversation(user_id)
        active_ai_users.add(user_id)  # Add to active users
        print(f"✅ AI conversation started for user {user_id}")
        
        await message.answer(
            friendly("🤖 **AI Yordamchi**\n\n"
                    "Salom! Men Usta Top platformasining aqlli yordamchisiman. "
                    "Sizga quyidagi masalalarda yordam bera olaman:\n\n"
                    "🔧 Usta va xizmatlar topish\n"
                    "💡 Texnik maslahatlar\n"
                    "📋 Platformadan foydalanish bo'yicha ko'rsatmalar\n"
                    "🔍 Savollaringizga javob berish\n\n"
                    "O'z savolingizni yuboring!"),
            reply_markup=ai_chat_kb()
        )
        
    except Exception as e:
        await message.answer(
            friendly(f"AI yordamchi hozirda mavjud emas. Iltimos, keyinroq urinib ko'ring.\n"
                    f"Xatolik: {str(e)}"),
            reply_markup=main_menu_kb()
        )


@router.message(F.text == "🔄 AI Suhbatini tozalash")
async def clear_ai_chat(message: Message):
    """AI suhbatini tozalash"""
    user_id = message.from_user.id
    
    try:
        ai_agent = await get_ai_agent()
        await ai_agent.clear_conversation(user_id)
        active_ai_users.discard(user_id)  # Remove from active users
        
        await message.answer(
            friendly("🔄 AI suhbat muvaffaqiyatli tozalandi. Yangi suhbat boshlash uchun "
                    "\"🤖 AI Yordamchi\" tugmasini bosing."),
            reply_markup=main_menu_kb()
        )
        
    except Exception as e:
        await message.answer(
            friendly(f"Xatolik yuz berdi: {str(e)}"),
            reply_markup=main_menu_kb()
        )


@router.message(F.text == "🚪 AI Chatdan chiqish")
async def exit_ai_chat(message: Message):
    """AI chatdan chiqish"""
    await message.answer(
        friendly("🚪 AI yordamchi chatidan chiqdingiz. Asosiy menuga qaytdingiz."),
        reply_markup=main_menu_kb()
    )


@router.message(F.text)
async def handle_ai_message(message: Message):
    """AI ga yuborilgan xabarlarni qayta ishlash"""
    user_id = message.from_user.id
    user_message = message.text
    
    print(f"🔍 Message received from user {user_id}: {user_message}")
    
    # Asosiy menyuni tekshirish - agar asosiy menyudagi tugmalar bo'lsa, AI emas
    main_menu_buttons = [
        "🧑‍🔧 Ustalar ro'yxati", "🚨 Shoshilinch chaqiruv", "🔎 Usta qidirish", 
        "⭐️ Ustani baholash", "📜 Tarixim", "📥 So'rovlar", "🚪 Chatni yakunlash",
        "🎁 Olmos ishlash", "🛠 Usta xizmatlari", "💎 Olmos balansim",
        "✏️ Profilni tahrirlash", "💎 Olmos sotib olish", "ℹ️ Bot haqida", "❓ Yordam",
        "🤖 AI Yordamchi"  # AI button ni ham qo'shish
    ]
    
    # AI chat tugmalarini tekshirish
    ai_chat_buttons = ["🔄 AI Suhbatini tozalash", "🚪 AI Chatdan chiqish"]
    
    # Agar asosiy menyu yoki AI chat tugmalari bo'lsa, AI ga yubormaslik
    if user_message in main_menu_buttons or user_message in ai_chat_buttons:
        print(f"🚫 Message filtered: {user_message}")
        return
    
    # Faqat AI chat rejimida ishlash
    try:
        ai_agent = await get_ai_agent()
        
        # Faol suhbat borligini tekshirish - local state dan foydalanamiz
        is_active = user_id in active_ai_users
        print(f"🔍 Active conversation for user {user_id}: {is_active}")
        
        if not is_active:
            print(f"🚫 No active conversation for user {user_id}")
            return
            
        # Typing indicator yuborish
        await message.bot.send_chat_action(chat_id=user_id, action="typing")
        
        # AI dan javob olish
        print(f"🤖 Getting AI response for user {user_id}")
        response = await ai_agent.get_response(user_id, user_message)
        print(f"✅ AI response for user {user_id}: {response[:50]}...")
        
        await message.answer(
            friendly(f"🤖 **AI Yordamchi:**\n\n{response}"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=ai_chat_kb()
        )
        
    except asyncio.TimeoutError:
        await message.answer(
            friendly("⏰ AI javob berishda uzoq vaqt oldi. Iltimos, birozdan so'ng urinib ko'ring."),
            reply_markup=ai_chat_kb()
        )
    except Exception as e:
        await message.answer(
            friendly(f"❌ AI xizmatida xatolik: {str(e)}\n\n"
                    "Iltimos, keyinroq urinib ko'ring yoki admin bilan bog'laning."),
            reply_markup=ai_chat_kb()
        )


@router.callback_query(F.data.startswith("ai_help_"))
async def ai_help_callback(callback: CallbackQuery):
    """AI yordamchi uchun tezkor yordam"""
    help_type = callback.data.split("_")[2]
    
    help_messages = {
        "usta": "🔧 **Usta topish uchun:**\n\n"
                "Qanday usta kerakligini aniqliang, masalan:\n"
                "\"Samarqandda elektrik topib ber\"\n"
                "\"Toshkentda plumber kerak\"\n"
                "\"Konditsioner ustasi chaqirish\"",
                
        "xizmat": "📋 **Xizmatlar haqida:**\n\n"
                "Qanday xizmatlar mavjudligini so'rashingiz mumkin:\n"
                "\"Qanday xizmatlar bor?\"\n"
                "\"Elektr ishlari qancha turadi?\"\n"
                "\"Konditsioner tozlash qanday amalga oshiriladi?\"",
                
        "platform": "📱 **Platforma foydalanishi:**\n\n"
                  "\"Platformadan qanday foydalanaman?\"\n"
                  "\"Usta qanday ro'yxatdan o'tadi?\"\n"
                  "\"Baholash qanday ishlaydi?\"\n"
                  "\"Olmoslar nima uchun kerak?\""
    }
    
    help_text = help_messages.get(help_type, "Yordam topilmadi")
    
    await callback.message.answer(
        friendly(help_text),
        reply_markup=ai_chat_kb()
    )
    await callback.answer()
