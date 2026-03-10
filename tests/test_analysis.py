# tests/test_analysis.py

import os
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
import shutil

client = TestClient(app)

@pytest.fixture
def dummy_video(tmp_path):
    video_file = tmp_path / "test.mp4"
    video_file.write_bytes(b"dummy video data")
    return video_file

@patch("app.routes.extract_audio")
@patch("app.routes.generate_transcript")
@patch("app.routes.analyze_transcript")
def test_analyze_success(mock_analyze, mock_transcript, mock_extract, dummy_video):
    # Mock return values
    mock_extract.return_value = "tmp/mock.wav"
    mock_transcript.return_value = "This is a test transcript."
    mock_analyze.return_value = {
        "summary": "Test summary",
        "chapters": [{"start": "00:00", "title": "Intro"}],
        "keywords": ["test"],
        "learning_objectives": ["learn test"]
    }

    with open(dummy_video, "rb") as f:
        response = client.post(
            "/analyze",
            files={"file": ("test.mp4", f, "video/mp4")},
            params={"engine": "openai"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Test summary"
    assert len(data["chapters"]) == 1
    
    # Ensure mocks were called
    mock_extract.assert_called_once()
    mock_transcript.assert_called_once()
    mock_analyze.assert_called_once()
