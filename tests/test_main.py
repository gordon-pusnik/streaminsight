# tests/test_main.py

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_no_file():
    response = client.post("/analyze")
    # FastAPI returns 422 if no file is provided as it is a required field
    assert response.status_code == 422

# To test actual analysis without real API keys, 
# we'd need to mock services/transcript.py and services/ai.py.
