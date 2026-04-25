import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram import F
from config import load_config
from handlers.ai_chat import router, start_ai_chat, handle_ai_message
from keyboards import main_menu_kb

async def test_bot_ai_integration():
    print("🔍 Testing complete bot AI integration...")
    
    config = load_config()
    bot = Bot(token=config.bot_token)
    
    # Create proper test message
    class TestMessage:
        def __init__(self, text, from_user_id, bot_instance):
            self.text = text
            self.from_user = type('User', (), {'id': from_user_id})()
            self.bot = bot_instance
            self.answer_calls = []
            
        async def answer(self, text, **kwargs):
            self.answer_calls.append(text)
            print(f"📱 Bot would answer: {text[:50]}...")
    
    test_user_id = 12345
    test_msg = TestMessage("🤖 AI Yordamchi", test_user_id, bot)
    
    # Test 1: AI button click
    print("\n📱 Test 1: AI button click")
    try:
        await start_ai_chat(test_msg)
        print("✅ AI button handler works")
    except Exception as e:
        print(f"❌ AI button handler failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: AI message after button click
    print("\n📝 Test 2: AI message after conversation start")
    user_msg = TestMessage("Toshkentda elektrik ustasi kerak", test_user_id, bot)
    
    try:
        await handle_ai_message(user_msg)
        print("✅ AI message handler works")
    except Exception as e:
        print(f"❌ AI message handler failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bot_ai_integration())
