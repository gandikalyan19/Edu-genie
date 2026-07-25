"""RESTful endpoints for every EduGenie educational feature."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..database.session import get_db, get_engine
from ..schemas.education import (
    ExplanationRequest,
    ExplanationResponse,
    HealthResponse,
    HistoryItem,
    LearningPathRequest,
    LearningPathResponse,
    QuestionRequest,
    QuestionResponse,
    QuizRequest,
    QuizResponse,
    SummaryRequest,
    SummaryResponse,
)
from ..services import EducationService, list_recent_queries


api_router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> EducationService:
    return EducationService(db)


@api_router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    settings = get_settings()
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        database_ready = True
    except Exception:
        database_ready = False

    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        database_ready=database_ready,
        gemini_configured=settings.ai_provider_configured,
        local_model_enabled=settings.edugenie_use_local_model,
    )


@api_router.post("/qa", response_model=QuestionResponse, tags=["education"])
def question_answering(
    payload: QuestionRequest, service: EducationService = Depends(get_service)
) -> QuestionResponse:
    result = _run(service.answer, payload.question, payload.context, payload.user_id)
    return QuestionResponse(**result)


@api_router.post("/explain", response_model=ExplanationResponse, tags=["education"])
def explanation(
    payload: ExplanationRequest, service: EducationService = Depends(get_service)
) -> ExplanationResponse:
    result = _run(service.explain, payload.topic, payload.audience, payload.user_id)
    return ExplanationResponse(**result)


@api_router.post("/quiz", response_model=QuizResponse, tags=["education"])
def quiz(
    payload: QuizRequest, service: EducationService = Depends(get_service)
) -> QuizResponse:
    result = _run(service.quiz, payload.passage, payload.num_questions, payload.user_id)
    return QuizResponse(**result)


@api_router.post("/summarize", response_model=SummaryResponse, tags=["education"])
def summarize(
    payload: SummaryRequest, service: EducationService = Depends(get_service)
) -> SummaryResponse:
    result = _run(service.summarize, payload.text, payload.max_sentences, payload.user_id)
    return SummaryResponse(**result)


@api_router.post(
    "/learn/recommendations", response_model=LearningPathResponse, tags=["education"]
)
def learning_recommendations(
    payload: LearningPathRequest, service: EducationService = Depends(get_service)
) -> LearningPathResponse:
    result = _run(service.learning_path, payload.topic, payload.level, payload.user_id)
    return LearningPathResponse(**result)


@api_router.get("/qa", response_model=QuestionResponse, tags=["education"])
def question_answering_get(
    question: str = Query(min_length=1, max_length=2000),
    context: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    service: EducationService = Depends(get_service),
) -> QuestionResponse:
    return QuestionResponse(**_run(service.answer, question, context, user_id))


@api_router.get(
    "/learn/recommendations", response_model=LearningPathResponse, tags=["education"]
)
def learning_recommendations_get(
    topic: str = Query(min_length=1, max_length=500),
    level: str = Query(default="beginner"),
    user_id: int | None = Query(default=None),
    service: EducationService = Depends(get_service),
) -> LearningPathResponse:
    return LearningPathResponse(**_run(service.learning_path, topic, level, user_id))


@api_router.get("/history", response_model=list[HistoryItem], tags=["education"])
def history(
    limit: int = Query(default=20, ge=1, le=100),
    query_type: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[HistoryItem]:
    records = list_recent_queries(db, limit=limit, query_type=query_type, user_id=user_id)
    return [HistoryItem(**record) for record in records]


def _run(handler, *args):
    """Translate module-level input validation into HTTP 422 responses."""

    try:
        return handler(*args)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
