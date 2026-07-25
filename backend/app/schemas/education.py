"""Pydantic models describing educational requests and AI responses."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DifficultyLevel = Literal["beginner", "intermediate", "advanced"]


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    context: str | None = Field(default=None, max_length=20000)
    user_id: int | None = None


class QuestionResponse(BaseModel):
    query_id: int
    question: str
    answer: str
    model_used: str


class ExplanationRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    audience: str = Field(default="beginner", max_length=60)
    user_id: int | None = None


class ExplanationResponse(BaseModel):
    query_id: int
    topic: str
    audience: str
    explanation: str
    model_used: str


class QuizRequest(BaseModel):
    passage: str = Field(min_length=1, max_length=20000)
    num_questions: int = Field(default=3, ge=1, le=5)
    user_id: int | None = None


class QuizQuestionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correct_answer: str


class QuizResponse(BaseModel):
    query_id: int
    questions: list[QuizQuestionModel]
    model_used: str


class SummaryRequest(BaseModel):
    text: str = Field(min_length=1, max_length=40000)
    max_sentences: int = Field(default=3, ge=1, le=6)
    user_id: int | None = None


class SummaryResponse(BaseModel):
    query_id: int
    summary: str
    model_used: str


class LearningPathRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    level: DifficultyLevel = "beginner"
    user_id: int | None = None


class LearningPathResponse(BaseModel):
    query_id: int
    topic: str
    level: str
    learning_path: str
    model_used: str


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    query_id: int
    query_type: str
    query_text: str
    created_at: datetime
    response_text: str | None = None
    model_used: str | None = None


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    database_ready: bool
    gemini_configured: bool
    local_model_enabled: bool
