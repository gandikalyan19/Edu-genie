"""Question answering module powered by Gemini with a local fallback."""

from __future__ import annotations

from .ai_client import generate_with_gemini
from .text_utils import keywords, require_text


def answer_question(question: str, context: str | None = None) -> str:
    """Return a concise educational answer for a learner's question."""

    question = require_text(question, "question")
    context_text = (context or "").strip()
    prompt = _build_prompt(question, context_text)

    ai_answer = generate_with_gemini(prompt)
    if ai_answer:
        return ai_answer

    return _fallback_answer(question, context_text)


def _build_prompt(question: str, context: str) -> str:
    context_section = f"\nReference material:\n{context}" if context else ""
    return (
        "You are EduGenie, an educational assistant. Answer the student's "
        "question accurately, clearly, and briefly. Include one helpful "
        f"learning note when useful.{context_section}\n\nQuestion: {question}"
    )


def _fallback_answer(question: str, context: str) -> str:
    terms = keywords(f"{question} {context}", limit=4)
    focus = ", ".join(terms) if terms else "the topic"
    if context:
        return (
            f"Based on the provided material, focus on {focus}. "
            "Read the relevant sentences carefully, identify the main idea, "
            "and connect it directly to the question before finalizing your answer."
        )

    return (
        f"I can help with this question about {focus}. "
        "Add a short passage or more details for a more precise answer; with no "
        "reference material configured, EduGenie is using its local study fallback."
    )
