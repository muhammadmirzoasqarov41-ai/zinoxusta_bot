import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
# from aiogram.filters import Text
from config import load_config
from ai_agent import get_ai_agent
from keyboards import main_menu_kb

async def debug_live_bot():
    config = load_config()
    bot = Bot(token=config.bot_token)
    
    print("🔍 Debugging live bot AI functionality...")
    
    # Test AI agent directly
    try:
        ai_agent = await get_ai_agent()
        print("✅ AI Agent initialized")
        
        # Test conversation
        await ai_agent.start_conversation(99999)
        response = await ai_agent.get_response(99999, "Test message")
        print(f"✅ AI Response: {response[:100]}...")
        
        await ai_agent.clear_conversation(99999)
        print("✅ Conversation cleared")
        
    except Exception as e:
        print(f"❌ AI Agent error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_live_bot())
