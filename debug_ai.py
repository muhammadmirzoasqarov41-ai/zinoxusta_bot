import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from config import load_config
from ai_agent import get_ai_agent
from keyboards import ai_chat_kb

async def test_ai_in_bot():
    config = load_config()
    bot = Bot(token=config.bot_token)
    
    print("🔍 Testing AI Agent in Bot Context...")
    
    # Test 1: Initialize AI agent
    try:
        ai_agent = await get_ai_agent()
        print("✅ AI Agent initialized successfully")
    except Exception as e:
        print(f"❌ AI Agent initialization failed: {e}")
        return
    
    # Test 2: Start conversation
    try:
        await ai_agent.start_conversation(12345)
        print("✅ Conversation started successfully")
    except Exception as e:
        print(f"❌ Conversation start failed: {e}")
        return
    
    # Test 3: Get AI response
    try:
        response = await ai_agent.get_response(12345, "Assalom alaykum, Usta Top botida yordam bering")
        print(f"✅ AI Response: {response}")
    except Exception as e:
        print(f"❌ AI Response failed: {e}")
        return
    
    # Test 4: Check active conversation
    try:
        is_active = await ai_agent.is_active_conversation(12345)
        print(f"✅ Active conversation check: {is_active}")
    except Exception as e:
        print(f"❌ Active conversation check failed: {e}")
    
    print("🎉 All AI Agent tests completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_in_bot())
