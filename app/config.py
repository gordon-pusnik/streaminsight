# app/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = "StreamInsight AI Service"
    VERSION: str = "0.1.0"
    TRANSCRIBE_ENGINE: str = os.getenv("TRANSCRIBE_ENGINE")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL")
    GOOGLE_PROJECT_ID: str | None = os.getenv("GOOGLE_PROJECT_ID")
    GOOGLE_REGION: str = os.getenv("GOOGLE_REGION")
    GOOGLE_VERTEX_MODEL: str = os.getenv("GOOGLE_VERTEX_MODEL")
    MAX_FILE_SIZE_MB: int = os.getenv("MAX_FILE_SIZE_MB")

settings = Settings()
