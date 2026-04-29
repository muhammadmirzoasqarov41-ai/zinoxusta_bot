import asyncio
from config import load_config
from db import Database

async def test_user_list():
    print("🔍 Testing user list functionality...")
    
    config = load_config()
    db = Database(config.db_path)
    
    try:
        # Test get_all_users
        print("📊 Testing get_all_users...")
        users = await db.get_all_users(limit=3, offset=0)
        print(f"✅ get_all_users works: {len(users)} users")
        
        if users:
            print("📋 First user data:")
            for key, value in users[0].items():
                print(f"  - {key}: {value}")
        
        # Test get_total_users_count
        print("\n📊 Testing get_total_users_count...")
        total_count = await db.get_total_users_count()
        print(f"✅ get_total_users_count works: {total_count} total users")
        
        print("\n✅ All database methods working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_list())
