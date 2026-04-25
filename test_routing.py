import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram import F
from config import load_config
from handlers.ai_chat import router as ai_router

async def test_routing():
    print("🔍 Testing message routing...")
    
    # Create test message
    class TestMessage:
        def __init__(self, text, from_user_id):
            self.text = text
            self.from_user = type('User', (), {'id': from_user_id})()
            self.bot = None
    
    test_msg = TestMessage("🤖 AI Yordamchi", 12345)
    
    # Check if any handler matches
    for handler in ai_router.message.handlers:
        try:
            # Check filters
            if hasattr(handler, 'filters'):
                for filter_obj in handler.filters:
                    if hasattr(filter_obj, 'callback'):
                        result = filter_obj.callback(test_msg)
                        print(f"Filter result: {result}")
                        if result:
                            print(f"✅ Handler would match: {handler.callback}")
        except Exception as e:
            print(f"❌ Filter error: {e}")

if __name__ == "__main__":
    asyncio.run(test_routing())
