"""ORM models for the EduGenie ER design.

USER 1-N USER_QUERY, USER_QUERY 1-1 AI_RESPONSE, and USER_QUERY 1-N for
QUIZ, SUMMARY, and LEARNING_PATH.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    queries: Mapped[list["UserQuery"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserQuery(Base):
    __tablename__ = "user_queries"

    query_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=True
    )
    query_type: Mapped[str] = mapped_column(String(32), index=True)
    query_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User | None"] = relationship(back_populates="queries")
    response: Mapped["AiResponse | None"] = relationship(
        back_populates="query", cascade="all, delete-orphan", uselist=False
    )
    quizzes: Mapped[list["Quiz"]] = relationship(
        back_populates="query", cascade="all, delete-orphan"
    )
    summaries: Mapped[list["Summary"]] = relationship(
        back_populates="query", cascade="all, delete-orphan"
    )
    learning_paths: Mapped[list["LearningPath"]] = relationship(
        back_populates="query", cascade="all, delete-orphan"
    )


class AiResponse(Base):
    __tablename__ = "ai_responses"

    response_id: Mapped[int] = mapped_column(primary_key=True)
    query_id: Mapped[int] = mapped_column(
        ForeignKey("user_queries.query_id", ondelete="CASCADE"), unique=True, index=True
    )
    response_text: Mapped[str] = mapped_column(Text)
    model_used: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    query: Mapped["UserQuery"] = relationship(back_populates="response")


class Quiz(Base):
    __tablename__ = "quizzes"

    quiz_id: Mapped[int] = mapped_column(primary_key=True)
    query_id: Mapped[int] = mapped_column(
        ForeignKey("user_queries.query_id", ondelete="CASCADE"), index=True
    )
    question_text: Mapped[str] = mapped_column(Text)
    option_a: Mapped[str] = mapped_column(Text)
    option_b: Mapped[str] = mapped_column(Text)
    option_c: Mapped[str] = mapped_column(Text)
    option_d: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    query: Mapped["UserQuery"] = relationship(back_populates="quizzes")


class Summary(Base):
    __tablename__ = "summaries"

    summary_id: Mapped[int] = mapped_column(primary_key=True)
    query_id: Mapped[int] = mapped_column(
        ForeignKey("user_queries.query_id", ondelete="CASCADE"), index=True
    )
    original_text: Mapped[str] = mapped_column(Text)
    summary_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    query: Mapped["UserQuery"] = relationship(back_populates="summaries")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    path_id: Mapped[int] = mapped_column(primary_key=True)
    query_id: Mapped[int] = mapped_column(
        ForeignKey("user_queries.query_id", ondelete="CASCADE"), index=True
    )
    topic: Mapped[str] = mapped_column(String(255))
    difficulty_level: Mapped[str] = mapped_column(String(32))
    recommended_resources: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    query: Mapped["UserQuery"] = relationship(back_populates="learning_paths")
