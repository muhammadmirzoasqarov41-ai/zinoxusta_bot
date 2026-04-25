import asyncio
from ai_agent import get_ai_agent

async def test_enhanced_ai():
    print("🔍 Testing enhanced AI assistant...")
    
    try:
        ai_agent = await get_ai_agent()
        print("✅ Enhanced AI Agent initialized")
        
        # Test comprehensive questions
        test_questions = [
            "Usta Top bot qanday ishlaydi?",
            "Toshkentda yaxshi elektrik ustasi topish uchun nima qilish kerak?",
            "Plumber uchun qanday hujjatlar kerak?",
            "Olmos qanday ishlaydi?",
            "Shoshilinch chaqiruv qanday ishlaydi?",
            "Usta profilini qanday yaratish kerak?",
            "Mijoz usta bilan qanday bog'lanadi?"
        ]
        
        await ai_agent.start_conversation(99999)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 Test {i}: {question}")
            response = await ai_agent.get_response(99999, question)
            print(f"✅ AI Response {i}: {response[:150]}...")
            print("-" * 50)
        
        await ai_agent.clear_conversation(99999)
        print("\n✅ Enhanced AI test completed successfully!")
        
    except Exception as e:
        print(f"❌ Enhanced AI test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_ai())
