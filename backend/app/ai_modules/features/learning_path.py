"""Personalized learning recommendation module."""

from __future__ import annotations

from .ai_client import generate_with_gemini
from .text_utils import require_text


def get_learning_recommendations(topic: str, level: str = "beginner") -> str:
    """Return a structured path from beginner to advanced learning."""

    topic = require_text(topic, "topic")
    level = (level or "beginner").strip().lower()
    prompt = (
        f"Create a personalized learning path for {topic}. The learner is at "
        f"{level} level. Organize it into Beginner, Intermediate, and Advanced "
        "stages. Include key concepts, practice tasks, and useful resources "
        "such as videos, articles, or books."
    )

    ai_path = generate_with_gemini(prompt)
    if ai_path:
        return ai_path

    return _fallback_learning_path(topic, level)


def _fallback_learning_path(topic: str, level: str) -> str:
    return (
        f"Personalized learning path for {topic} ({level} starting point)\n\n"
        "Beginner:\n"
        f"- Learn the basic vocabulary and purpose of {topic}.\n"
        "- Watch one introductory video and write five key takeaways.\n"
        "- Practice with small examples until the core idea feels familiar.\n\n"
        "Intermediate:\n"
        f"- Study common patterns, problem types, and real uses of {topic}.\n"
        "- Read a beginner-friendly article or documentation chapter.\n"
        "- Complete guided exercises and review mistakes carefully.\n\n"
        "Advanced:\n"
        f"- Build a mini project or solve scenario-based problems using {topic}.\n"
        "- Compare multiple resources such as a course, official docs, and a book.\n"
        "- Teach the topic back in your own words to check mastery."
    )
