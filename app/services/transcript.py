# app/services/transcript.py

import os
from app.config import settings

# Google Vertex AI
import vertexai
from vertexai.generative_models import GenerativeModel, Part

async def generate_transcript(audio_path: str, engine: str = settings.TRANSCRIBE_ENGINE) -> str:
    """
    Transcribe audio using selected engine (OpenAI or Google Vertex AI)
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    engine = engine.lower()

    if engine == "openai":
        # OpenAI Whisper transcription
        from openai import AsyncOpenAI
        client_openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        with open(audio_path, "rb") as audio_file:
            transcript = await client_openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript

    elif engine == "vertex":
        # Google Vertex AI transcription using Gemini
        if not settings.GOOGLE_PROJECT_ID:
            raise ValueError("GOOGLE_PROJECT_ID must be set for vertex engine")

        vertexai.init(project=settings.GOOGLE_PROJECT_ID, location=settings.GOOGLE_REGION)
        model = GenerativeModel(settings.GOOGLE_VERTEX_MODEL)

        with open(audio_path, "rb") as f:
            audio_content = f.read()

        # Determine mime type (defaulting to audio/wav as per media.py)
        mime_type = "audio/wav"
        if audio_path.lower().endswith(".mp3"):
            mime_type = "audio/mpeg"
        elif audio_path.lower().endswith(".ogg"):
            mime_type = "audio/ogg"

        audio_part = Part.from_data(data=audio_content, mime_type=mime_type)
        
        # Request transcript from Gemini
        response = await model.generate_content_async(
            [audio_part, "Provide a verbatim transcript of this audio. Output only the transcript text, no preamble."],
            generation_config={"temperature": 0.0}
        )

        return response.text.strip()

    else:
        raise ValueError(f"Unknown transcription engine: {engine}")