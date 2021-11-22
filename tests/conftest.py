from typing import Generator

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from simple_object_storage.config import settings
from simple_object_storage.main import app
from simple_object_storage.models import ObjectModel
from simple_object_storage.routers import get_db
from .utils import get_uuid

FAKE_OBJECTS = {
    "a": [
        {"_id": get_uuid("a", 1), "data": "a1 data"},
        {"_id": get_uuid("a", 2), "data": "a2 data"},
    ],
    "b": [
        {"_id": get_uuid("b", 1), "data": "b1 data"},
    ],
}

TEST_MONGO_DATABASE = "test_simple_object_storage"
TEST_MONGO_URL = f"""
    mongodb://{settings.MONGO_USERNAME}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}
    :{settings.MONGO_PORT}/{TEST_MONGO_DATABASE}?authSource=admin&retryWrites=true&w=majority
""".replace(
    "\n", ""
).replace(
    " ", ""
)


async def override_get_db() -> Generator:
    db_client = AsyncIOMotorClient(TEST_MONGO_URL)
    db = db_client[TEST_MONGO_DATABASE]
    try:
        yield db
    finally:
        db_client.close()


@pytest.fixture()
def api_client():
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_mongo(mocker):
    mocker.patch.object(settings, "MONGO_DATABASE", autospec=True)
    mocker.patch.object(settings, "DB_NAME", autospec=True)
    settings.MONGO_DATABASE = settings.DB_NAME = TEST_MONGO_DATABASE

    mocker.patch.object(settings, "MONGO_URL", autospec=True)
    mocker.patch.object(settings, "DB_URL", autospec=True)
    settings.MONGO_URL = settings.DB_URL = TEST_MONGO_URL


@pytest.fixture(scope="session", autouse=True)
def reset_db(request):
    _populate_db()
    request.addfinalizer(_remove_db)


def _remove_db():
    db_client = AsyncIOMotorClient(TEST_MONGO_URL)
    try:
        db_client.drop_database(TEST_MONGO_DATABASE)
    finally:
        db_client.close()


def _populate_db():
    db_client = AsyncIOMotorClient(TEST_MONGO_URL)
    db = db_client[TEST_MONGO_DATABASE]
    for k, v in FAKE_OBJECTS.items():
        for obj in v:
            obj = ObjectModel(id=obj["_id"], data=obj["data"])
            db[k].insert_one(jsonable_encoder(obj))
