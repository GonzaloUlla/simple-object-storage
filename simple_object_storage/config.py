import os

from pydantic import BaseSettings


class CommonSettings(BaseSettings):
    APP_NAME: str = "Simple Object Storage"
    APP_TITLE: str = "simple_object_storage"
    APP_DESCRIPTION: str = "HTTP service to store objects in buckets"
    DEBUG_MODE: bool = False


class ServerSettings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000


class DatabaseSettings(BaseSettings):
    DB_URL: str
    DB_NAME: str


class MongoSettings(DatabaseSettings):
    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: int = os.getenv("MONGO_PORT", 27017)
    MONGO_USERNAME: str = os.getenv("MONGO_USERNAME", "root")
    MONGO_PASSWORD: str = os.getenv("MONGO_PASSWORD", "rootpassword")
    MONGO_DATABASE: str = os.getenv("MONGO_DATABASE", "simple_object_storage")
    MONGO_URL: str = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}" \
                     "?authSource=admin&retryWrites=true&w=majority"

    DB_NAME = MONGO_DATABASE
    DB_URL = MONGO_URL


class Settings(CommonSettings, ServerSettings, MongoSettings):
    pass


settings = Settings()
