"""Quiz generation module for three MCQs with structured JSON output."""

from __future__ import annotations

import json

from .ai_client import generate_with_gemini
from .text_utils import clean_json_block, keywords, require_text, split_sentences


QuizQuestion = dict[str, object]


def generate_quiz(passage: str, num_questions: int = 3) -> list[QuizQuestion]:
    """Generate MCQ quiz questions from a passage.

    Each question contains four options and one correct answer. Gemini is used
    when configured; otherwise a deterministic local quiz is produced so the
    frontend and tests can still exercise the workflow.
    """

    passage = require_text(passage, "passage")
    num_questions = max(1, min(num_questions, 5))
    prompt = _build_prompt(passage, num_questions)

    ai_response = generate_with_gemini(prompt)
    if ai_response:
        parsed = _parse_quiz(ai_response)
        if parsed:
            return parsed[:num_questions]

    return _fallback_quiz(passage, num_questions)


def _build_prompt(passage: str, num_questions: int) -> str:
    return (
        f"Create exactly {num_questions} multiple-choice questions from the "
        "passage. Return only valid JSON as an array. Each item must contain "
        "question, options, and correct_answer. options must contain exactly "
        f"four strings.\n\nPassage:\n{passage}"
    )


def _parse_quiz(response_text: str) -> list[QuizQuestion] | None:
    try:
        data = json.loads(clean_json_block(response_text))
    except json.JSONDecodeError:
        return None

    if not isinstance(data, list):
        return None

    questions: list[QuizQuestion] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question") or item.get("question_text") or "").strip()
        options = item.get("options")
        correct = str(item.get("correct_answer") or item.get("answer") or "").strip()
        if not isinstance(options, list) or len(options) != 4:
            continue
        normalized_options = [str(option).strip() for option in options]
        if question and correct and all(normalized_options):
            questions.append(
                {
                    "question": question,
                    "options": normalized_options,
                    "correct_answer": correct,
                }
            )

    return questions or None


def _fallback_quiz(passage: str, num_questions: int) -> list[QuizQuestion]:
    terms = keywords(passage, limit=max(4, num_questions + 3))
    sentences = split_sentences(passage)
    topic = terms[0] if terms else "the passage"
    distractors = terms[1:4] or ["definition", "example", "detail"]

    quiz: list[QuizQuestion] = []
    for index in range(num_questions):
        correct = terms[index % len(terms)] if terms else topic
        source = sentences[index % len(sentences)] if sentences else passage
        options = _four_options(correct, distractors, index)
        quiz.append(
            {
                "question": (
                    f"According to the passage, which idea is most connected "
                    f"to this statement: \"{source[:120]}\"?"
                ),
                "options": options,
                "correct_answer": correct,
            }
        )
    return quiz


def _four_options(correct: str, distractors: list[str], offset: int) -> list[str]:
    values = [correct]
    for distractor in distractors:
        if distractor != correct and distractor not in values:
            values.append(distractor)
    while len(values) < 4:
        values.append(f"related idea {len(values)}")
    rotated = values[:4]
    shift = offset % 4
    return rotated[shift:] + rotated[:shift]
