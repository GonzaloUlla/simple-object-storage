"""Dependencies to be injected in the API"""

from typing import AsyncGenerator

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient


async def get_db() -> AsyncGenerator:
    db_client = AsyncIOMotorClient(settings.DB_URL)
    db = db_client[settings.DB_NAME]
    try:
        yield db
    finally:
        db_client.close()
