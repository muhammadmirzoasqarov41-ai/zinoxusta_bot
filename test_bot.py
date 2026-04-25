import asyncio
from aiogram import Bot
from config import load_config

async def test_bot():
    try:
        config = load_config()
        bot = Bot(token=config.bot_token)
        info = await bot.get_me()
        print(f'✅ Bot info: {info.full_name} @{info.username}')
        return True
    except Exception as e:
        print(f'❌ Bot error: {e}')
        return False

if __name__ == "__main__":
    asyncio.run(test_bot())
