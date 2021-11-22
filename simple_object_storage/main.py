"""Main API module with server settings and routers"""

from config import settings
from fastapi import FastAPI
from routers import router
from uvicorn import run

app = FastAPI(title=settings.APP_TITLE, description=settings.APP_DESCRIPTION)

app.include_router(router, tags=["objects"], prefix="/objects")


if __name__ == "__main__":
    run(
        "main:app",
        host=settings.HOST,
        reload=settings.DEBUG_MODE,
        port=settings.PORT,
    )
