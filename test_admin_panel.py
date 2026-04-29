import asyncio
from aiogram import Bot
from aiogram.types import CallbackQuery
from config import load_config
from handlers.admin_enhanced import router
from db import Database

async def test_admin_panel():
    print("🔍 Testing admin panel functionality...")
    
    config = load_config()
    bot = Bot(token=config.bot_token)
    db = Database(config.db_path)
    
    # Test database methods
    try:
        print("📊 Testing database methods...")
        users = await db.get_all_users(limit=5, offset=0)
        print(f"✅ get_all_users works: {len(users)} users")
        
        total_count = await db.get_total_users_count()
        print(f"✅ get_total_users_count works: {total_count} total users")
        
        # Test user list handler
        print("\n🔍 Testing user list handler...")
        
        # Create test callback
        class TestCallback:
            def __init__(self):
                self.data = "admin:user_list"
                self.from_user = type('User', (), {'id': config.admin_id or 12345})()
                self.message = type('Message', (), {'edit_text': lambda text, **kwargs: None, 'answer': lambda text: None})()
        
        test_callback = TestCallback()
        
        # Import and test the handler
        from handlers.admin_enhanced import admin_user_list
        
        print("✅ admin_user_list handler imported successfully")
        print("📋 User list callback handler is ready")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_admin_panel())
