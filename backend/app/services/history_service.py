"""Read access to stored educational queries and their AI responses."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database.models import UserQuery


def list_recent_queries(
    db: Session,
    limit: int = 20,
    query_type: str | None = None,
    user_id: int | None = None,
) -> list[dict]:
    statement = (
        select(UserQuery)
        .options(joinedload(UserQuery.response))
        .order_by(UserQuery.query_id.desc())
        .limit(limit)
    )
    if query_type:
        statement = statement.where(UserQuery.query_type == query_type)
    if user_id is not None:
        statement = statement.where(UserQuery.user_id == user_id)

    records = db.execute(statement).unique().scalars().all()

    return [
        {
            "query_id": record.query_id,
            "query_type": record.query_type,
            "query_text": record.query_text,
            "created_at": record.created_at,
            "response_text": record.response.response_text if record.response else None,
            "model_used": record.response.model_used if record.response else None,
        }
        for record in records
    ]
