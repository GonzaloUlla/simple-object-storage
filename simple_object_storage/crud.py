from uuid import UUID

from fastapi.encoders import jsonable_encoder
from models import ObjectModel

# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_objects_by_bucket(db: AsyncIOMotorDatabase, bucket: str):
    return await db[bucket].find().to_list(1000)


async def get_object_by_id(
    db: AsyncIOMotorDatabase, bucket: str, object_id: UUID
):
    return await db[bucket].find_one({"_id": jsonable_encoder(object_id)})


async def insert_object(
    db: AsyncIOMotorDatabase, bucket: str, obj: ObjectModel
):
    return await db[bucket].insert_one(jsonable_encoder(obj))


async def update_object_data(
    db: AsyncIOMotorDatabase, bucket: str, object_id: UUID, object_data: str
):
    return await db[bucket].update_one(
        {"_id": jsonable_encoder(object_id)},
        {"$set": {"data": jsonable_encoder(object_data)}},
    )


async def delete_object_by_id(
    db: AsyncIOMotorDatabase, bucket: str, object_id: UUID
):
    return await db[bucket].delete_one({"_id": jsonable_encoder(object_id)})
