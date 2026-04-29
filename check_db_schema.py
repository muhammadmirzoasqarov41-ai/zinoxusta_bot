import aiosqlite
from config import load_config

async def check_db_schema():
    config = load_config()
    async with aiosqlite.connect(config.db_path) as db:
        cursor = await db.execute('PRAGMA table_info(users)')
        columns = await cursor.fetchall()
        print('📋 Users table schema:')
        for col in columns:
            print(f'  - {col[1]} ({col[2]})')

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_db_schema())
