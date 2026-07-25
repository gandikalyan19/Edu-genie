"""Runs the AI feature modules and records each request and result."""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from ..ai_modules.features import (
    answer_question,
    capture_model,
    explain_concept,
    generate_quiz,
    get_learning_recommendations,
    summarize_text,
)
from ..database.models import AiResponse, LearningPath, Quiz, Summary, UserQuery


class EducationService:
    """Each method executes one educational task and stores its output."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def answer(self, question: str, context: str | None, user_id: int | None) -> dict:
        with capture_model() as usage:
            answer = answer_question(question, context)

        query = self._record_query("qna", question, user_id)
        self._record_response(query, answer, usage.model_used)
        self.db.commit()

        return {
            "query_id": query.query_id,
            "question": question,
            "answer": answer,
            "model_used": usage.model_used,
        }

    def explain(self, topic: str, audience: str, user_id: int | None) -> dict:
        with capture_model() as usage:
            explanation = explain_concept(topic, audience)

        query = self._record_query("explanation", topic, user_id)
        self._record_response(query, explanation, usage.model_used)
        self.db.commit()

        return {
            "query_id": query.query_id,
            "topic": topic,
            "audience": audience,
            "explanation": explanation,
            "model_used": usage.model_used,
        }

    def quiz(self, passage: str, num_questions: int, user_id: int | None) -> dict:
        with capture_model() as usage:
            questions = generate_quiz(passage, num_questions)

        query = self._record_query("quiz", passage, user_id)
        self._record_response(query, json.dumps(questions), usage.model_used)
        for item in questions:
            options = list(item["options"])
            self.db.add(
                Quiz(
                    query_id=query.query_id,
                    question_text=str(item["question"]),
                    option_a=options[0],
                    option_b=options[1],
                    option_c=options[2],
                    option_d=options[3],
                    correct_answer=str(item["correct_answer"]),
                )
            )
        self.db.commit()

        return {
            "query_id": query.query_id,
            "questions": questions,
            "model_used": usage.model_used,
        }

    def summarize(self, text: str, max_sentences: int, user_id: int | None) -> dict:
        with capture_model() as usage:
            summary = summarize_text(text, max_sentences)

        query = self._record_query("summary", text, user_id)
        self._record_response(query, summary, usage.model_used)
        self.db.add(
            Summary(query_id=query.query_id, original_text=text, summary_text=summary)
        )
        self.db.commit()

        return {
            "query_id": query.query_id,
            "summary": summary,
            "model_used": usage.model_used,
        }

    def learning_path(self, topic: str, level: str, user_id: int | None) -> dict:
        with capture_model() as usage:
            path = get_learning_recommendations(topic, level)

        query = self._record_query("recommendation", topic, user_id)
        self._record_response(query, path, usage.model_used)
        self.db.add(
            LearningPath(
                query_id=query.query_id,
                topic=topic,
                difficulty_level=level,
                recommended_resources=path,
            )
        )
        self.db.commit()

        return {
            "query_id": query.query_id,
            "topic": topic,
            "level": level,
            "learning_path": path,
            "model_used": usage.model_used,
        }

    def _record_query(self, query_type: str, query_text: str, user_id: int | None) -> UserQuery:
        query = UserQuery(query_type=query_type, query_text=query_text, user_id=user_id)
        self.db.add(query)
        self.db.flush()
        return query

    def _record_response(self, query: UserQuery, text: str, model_used: str) -> None:
        self.db.add(
            AiResponse(query_id=query.query_id, response_text=text, model_used=model_used)
        )
