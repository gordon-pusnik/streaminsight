# app/main.py

from fastapi import FastAPI
from app.routes import router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION
)

app.include_router(router)