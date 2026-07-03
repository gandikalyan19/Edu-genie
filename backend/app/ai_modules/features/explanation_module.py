"""Concept explanation module using LaMini-Flan-T5 when available."""

from __future__ import annotations

import os
from functools import lru_cache

from .text_utils import keywords, require_text


DEFAULT_MODEL = "MBZUAI/LaMini-Flan-T5-783M"


def explain_concept(topic: str, audience: str = "beginner") -> str:
    """Explain a concept in simple, learner-friendly language."""

    topic = require_text(topic, "topic")
    audience = (audience or "beginner").strip()
    prompt = (
        f"Explain {topic} for a {audience} learner. Use simple language, "
        "one relatable example, and keep the explanation concise."
    )

    local_answer = _generate_with_lamini(prompt)
    if local_answer:
        return local_answer

    return _fallback_explanation(topic, audience)


def _generate_with_lamini(prompt: str) -> str | None:
    if os.getenv("EDUGENIE_USE_LOCAL_MODEL", "1") == "0":
        return None

    try:
        generator = _load_lamini_pipeline()
        output = generator(prompt, max_new_tokens=180, do_sample=False)
    except Exception:
        return None

    if isinstance(output, list) and output:
        text = output[0].get("generated_text")
        if isinstance(text, str) and text.strip():
            return text.strip()
    return None


@lru_cache(maxsize=1)
def _load_lamini_pipeline():
    from transformers import pipeline  # type: ignore

    model_name = os.getenv("LAMINI_MODEL", DEFAULT_MODEL)
    return pipeline("text2text-generation", model=model_name)


def _fallback_explanation(topic: str, audience: str) -> str:
    terms = keywords(topic, limit=3)
    focus = ", ".join(terms) if terms else topic
    return (
        f"{topic} is best understood by breaking it into small parts. "
        f"For a {audience} learner, start with the main idea: {focus}. "
        "Then look at one example, notice the pattern, and practice explaining "
        "it back in your own words."
    )
