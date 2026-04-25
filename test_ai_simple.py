import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from config import load_config
from handlers.ai_chat import router
from keyboards import main_menu_kb

async def test_ai_button():
    config = load_config()
    bot = Bot(token=config.bot_token)
    
    print("🔍 Testing AI button click simulation...")
    
    # Create a test message object
    class TestMessage:
        def __init__(self, text, from_user_id):
            self.text = text
            self.from_user = type('User', (), {'id': from_user_id})()
            self.bot = bot
    
    # Test 1: AI button click
    test_msg = TestMessage("🤖 AI Yordamchi", 12345)
    
    try:
        # Find the AI chat handler
        for handler in router.message.handlers:
            if hasattr(handler, 'callback'):
                result = handler.callback(test_msg)
                print(f"✅ Handler called: {handler}")
                break
        else:
            print("❌ No handler found for AI button")
            
    except Exception as e:
        print(f"❌ Handler execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_button())
