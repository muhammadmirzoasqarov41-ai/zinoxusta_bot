from keyboards import main_menu_kb
import asyncio

async def test_menu():
    print("🔍 Testing main menu keyboard...")
    
    try:
        # Get the keyboard
        kb = main_menu_kb()
        
        # Print keyboard structure
        print("✅ Main menu keyboard created successfully")
        
        # Check if AI button is in keyboard
        kb_text = str(kb)
        if "🤖 AI Yordamchi" in kb_text:
            print("✅ AI button found in main menu")
        else:
            print("❌ AI button NOT found in main menu")
            print(f"Keyboard content: {kb_text}")
            
    except Exception as e:
        print(f"❌ Error testing menu: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_menu())
