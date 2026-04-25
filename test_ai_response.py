import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from config import load_config
from ai_agent import get_ai_agent

async def test_ai_response():
    print("🔍 Testing AI response generation...")
    
    try:
        # Initialize AI agent
        ai_agent = await get_ai_agent()
        print("✅ AI Agent initialized")
        
        # Start conversation
        await ai_agent.start_conversation(99999)
        print("✅ Conversation started")
        
        # Test multiple messages
        test_messages = [
            "Assalom alaykum",
            "Toshkentda elektrik usta topish kerak",
            "Usta Top platformasi qanday ishlaydi?",
            "Sog'liq"
        ]
        
        for i, msg in enumerate(test_messages, 1):
            print(f"\n📝 Test {i}: {msg}")
            try:
                response = await ai_agent.get_response(99999, msg)
                print(f"✅ Response {i}: {response[:100]}...")
            except Exception as e:
                print(f"❌ Error {i}: {e}")
                import traceback
                traceback.print_exc()
        
        # Clear conversation
        await ai_agent.clear_conversation(99999)
        print("\n✅ Conversation cleared")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_response())
