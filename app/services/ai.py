# app/services/ai.py

import json
from app.config import settings
from app.models import AnalysisResponse

SYSTEM_PROMPT = """
You are an expert media analysis assistant.
Analyze the following transcript and produce:
1. A concise summary
2. Logical chapter breakdown with estimated timestamps
3. Keywords
4. Learning objectives

Return structured JSON only.
Do not include explanations.
"""

async def analyze_transcript(transcript: str, engine: str = settings.TRANSCRIBE_ENGINE) -> AnalysisResponse:
    engine = engine.lower()

    if engine == "vertex":
        import vertexai
        from vertexai.generative_models import GenerativeModel, GenerationConfig

        if not settings.GOOGLE_PROJECT_ID:
            raise ValueError("GOOGLE_PROJECT_ID must be set for vertex engine")

        vertexai.init(project=settings.GOOGLE_PROJECT_ID, location=settings.GOOGLE_REGION)
        model = GenerativeModel(settings.GOOGLE_VERTEX_MODEL)

        response = await model.generate_content_async(
            f"{SYSTEM_PROMPT}\n\nTranscript:\n{transcript}",
            generation_config=GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "chapters": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "start": {"type": "string"},
                                    "title": {"type": "string"}
                                },
                                "required": ["start", "title"]
                            }
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "learning_objectives": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": [
                        "summary",
                        "chapters",
                        "keywords",
                        "learning_objectives"
                    ]
                }
            )
        )
        
        # Parse the JSON response text
        structured_data = json.loads(response.text)
        return AnalysisResponse(**structured_data)

    else:
        # Default to OpenAI
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        response = await client.chat.completions.parse(
            model=settings.OPENAI_MODEL,
            temperature=0.2,
            response_format=AnalysisResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Transcript:\n{transcript}"}
            ]
        )

        return response.choices[0].message.parsed
    