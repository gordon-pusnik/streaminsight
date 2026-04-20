# app/main.py

from fastapi import FastAPI
from app.routes import router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION
)


@app.get("/")
def service_info():
    return {
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "description": (
            "AI video intelligence microservice for extracting audio, "
            "transcribing speech, and generating structured video insights."
        ),
        "endpoints": [
            {
                "method": "GET",
                "path": "/",
                "description": "Service overview and available endpoints.",
            },
            {
                "method": "GET",
                "path": "/health",
                "description": "Health check endpoint.",
            },
            {
                "method": "POST",
                "path": "/analyze",
                "description": (
                    "Upload a video file for transcription and structured AI analysis."
                ),
                "query_params": {
                    "engine": (
                        "Optional transcription/analysis engine override "
                        "(openai or vertex)."
                    )
                },
            },
            {
                "method": "GET",
                "path": "/docs",
                "description": "Interactive OpenAPI documentation.",
            },
        ],
    }


app.include_router(router)
