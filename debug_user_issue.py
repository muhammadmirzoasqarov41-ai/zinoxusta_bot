import asyncio
from aiogram import Bot
from aiogram.types import Message
from config import load_config
from handlers.start import router as start_router
from keyboards import main_menu_kb

async def debug_user_issue():
    print("🔍 Debugging user's specific AI button issue...")
    
    config = load_config()
    bot = Bot(token=config.bot_token)
    
    # Test what keyboard is actually sent to user
    class TestMessage:
        def __init__(self, text, from_user_id):
            self.text = text
            self.from_user = type('User', (), {'id': from_user_id})()
            self.bot = bot
            self.answer_calls = []
            
        async def answer(self, text, **kwargs):
            self.answer_calls.append(text)
            print(f"📱 Bot would send: {text[:100]}...")
            # Show keyboard structure
            if 'reply_markup' in kwargs:
                kb = kwargs['reply_markup']
                print(f"⌨️ Keyboard: {str(kb)[:200]}...")
    
    # Simulate /start command for user
    test_user_id = 12345
    test_msg = TestMessage("/start", test_user_id)
    
    print(f"\n👤 Simulating /start for user {test_user_id}")
    
    # Find and execute start handler
    for handler in start_router.message.handlers:
        try:
            if hasattr(handler, 'callback'):
                await handler.callback(test_msg, db=None, state=None, command=None)
                print("✅ Start handler executed")
                break
        except Exception as e:
            print(f"❌ Handler error: {e}")
            import traceback
            traceback.print_exc()
    
    # Check what was sent
    if test_msg.answer_calls:
        for i, answer in enumerate(test_msg.answer_calls, 1):
            print(f"\n📋 Answer {i}: {answer}")
            if "🤖 AI Yordamchi" in answer:
                print("✅ AI button FOUND in response")
            else:
                print("❌ AI button NOT found in response")
    else:
        print("❌ No answers sent")

if __name__ == "__main__":
    asyncio.run(debug_user_issue())
