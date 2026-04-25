import asyncio
from aiogram import Bot
from aiogram.types import Message
from config import load_config
from handlers.start import router as start_router
from keyboards import main_menu_kb

async def test_complete_flow():
    print("🔍 Testing complete bot flow...")
    
    config = load_config()
    bot = Bot(token=config.bot_token)
    
    # Test 1: Check if start handler has AI button
    class TestMessage:
        def __init__(self, text, from_user_id):
            self.text = text
            self.from_user = type('User', (), {'id': from_user_id})()
            self.bot = bot
            self.answer_calls = []
            
        async def answer(self, text, **kwargs):
            self.answer_calls.append(text)
            print(f"📱 Bot would answer: {text[:50]}...")
    
    # Simulate /start command
    test_msg = TestMessage("/start", 12345)
    
    # Find start handler
    for handler in start_router.message.handlers:
        try:
            if hasattr(handler, 'callback'):
                await handler.callback(test_msg)
                print("✅ Start handler executed")
                break
        except Exception as e:
            print(f"❌ Handler error: {e}")
    
    # Check what was sent to user
    if test_msg.answer_calls:
        for answer in test_msg.answer_calls:
            print(f"📋 Answer content: {answer[:100]}...")
            if "🤖 AI Yordamchi" in answer:
                print("✅ AI button found in start response")
            else:
                print("❌ AI button NOT found in start response")

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
