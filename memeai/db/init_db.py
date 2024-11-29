import asyncio
from memeai.db.db_service import TwitterDBService


async def init_database():
    db_service = TwitterDBService()
    await db_service.init_db()
    print("Database initialized successfully")

if __name__ == "__main__":
    asyncio.run(init_database())
