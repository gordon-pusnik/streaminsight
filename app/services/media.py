# app/services/media.py

import os
import shutil
import uuid
import asyncio
from fastapi import UploadFile
from app.utils.logging import logger

UPLOAD_DIR = "tmp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def extract_audio(file: UploadFile) -> str:
    """
    Asynchronously extracts audio from an uploaded video file using ffmpeg.
    Returns the path to the generated audio file.
    """
    temp_id = str(uuid.uuid4())
    video_path = os.path.join(UPLOAD_DIR, f"{temp_id}_{file.filename}")
    audio_path = os.path.join(UPLOAD_DIR, f"{temp_id}.wav")

    try:
        # Save uploaded video
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract audio via ffmpeg asynchronously
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            audio_path,
            "-y"  # Overwrite output files without asking
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error(f"FFmpeg failed with exit code {process.returncode}: {error_msg}")
            raise RuntimeError(f"FFmpeg error: {error_msg}")

        return audio_path

    except Exception as e:
        # Cleanup video path if something fails during extraction
        if os.path.exists(video_path):
            os.remove(video_path)
        raise e
