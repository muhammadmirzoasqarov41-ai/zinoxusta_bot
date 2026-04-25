import asyncio
from aiogram import Bot
from aiogram.types import Message
from config import load_config
from keyboards import main_menu_kb

async def test_start_simple():
    print("🔍 Testing start command...")
    
    config = load_config()
    bot = Bot(token=config.bot_token)
    
    # Test main menu keyboard directly
    try:
        kb = main_menu_kb()
        print("✅ Main menu keyboard created")
        
        # Check keyboard content
        kb_text = str(kb)
        print(f"📋 Keyboard preview: {kb_text}")
        
        # Look for AI button
        if "🤖 AI Yordamchi" in kb_text:
            print("✅ AI button is in main menu")
        else:
            print("❌ AI button is NOT in main menu")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_start_simple())
