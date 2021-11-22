"""Dependencies to be injected in the API"""
from typing import Generator

from motor.motor_asyncio import AsyncIOMotorClient

from config import settings


async def get_db() -> Generator:
    db_client = AsyncIOMotorClient(settings.DB_URL)
    db = db_client[settings.DB_NAME]
    try:
        yield db
    finally:
        db_client.close()
