# app/models.py

from pydantic import BaseModel
from typing import List

class Chapter(BaseModel):
    start: str
    title: str

class AnalysisResponse(BaseModel):
    summary: str
    chapters: List[Chapter]
    keywords: List[str]
    learning_objectives: List[str]
