"""FastAPI application entrypoint for EduGenie."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api import api_router
from .core.config import get_settings, sync_environment
from .database.session import init_db


settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


@asynccontextmanager
async def lifespan(app: FastAPI):
    sync_environment(settings)
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered educational assistant for Q&A, explanations, quizzes, "
    "summaries, and personalized learning paths.",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.include_router(api_router)


@app.get("/", include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": settings.app_name, "version": settings.app_version},
    )
