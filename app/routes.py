# app/routes.py

import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, BackgroundTasks
from app.services.media import extract_audio
from app.services.transcript import generate_transcript
from app.services.ai import analyze_transcript
from app.models import AnalysisResponse
from app.config import settings
from app.utils.logging import logger

router = APIRouter()

def cleanup_files(*file_paths: str):
    """
    Deletes the provided files from the filesystem.
    """
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Cleaned up file: {path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {path}: {e}")

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    engine: str = Query(settings.TRANSCRIBE_ENGINE, description="Transcription engine to use (openai or vertex)")
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file")

    audio_path = None
    video_path = None
    
    try:
        # Extract audio (this also saves the video temporarily)
        audio_path = await extract_audio(file)
        
        # We need to derive the video path to clean it up. 
        # In media.py, video_path is UPLOAD_DIR/{temp_id}_{file.filename}
        # and audio_path is UPLOAD_DIR/{temp_id}.wav
        # Let's rely on the fact that audio_path share the same UUID prefix.
        temp_id = os.path.basename(audio_path).split('.')[0]
        video_path = os.path.join("tmp", f"{temp_id}_{file.filename}")

        # Process the audio
        transcript = await generate_transcript(audio_path, engine=engine)
        result = await analyze_transcript(transcript, engine=engine)

        return result

    except Exception as e:
        logger.exception("Error during video analysis")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Schedule cleanup
        files_to_remove = []
        if audio_path: files_to_remove.append(audio_path)
        if video_path: files_to_remove.append(video_path)
        
        if files_to_remove:
            background_tasks.add_task(cleanup_files, *files_to_remove)
