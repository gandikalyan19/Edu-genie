"""Educational summarization module powered by Gemini with local fallback."""

from __future__ import annotations

from .ai_client import generate_with_gemini
from .text_utils import require_text, split_sentences


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Summarize long educational content for quick revision."""

    text = require_text(text, "text")
    max_sentences = max(1, min(max_sentences, 6))
    prompt = (
        "Summarize the following educational text in clear, concise language. "
        f"Keep the summary within {max_sentences} sentences and preserve the "
        f"most important ideas.\n\nText:\n{text}"
    )

    ai_summary = generate_with_gemini(prompt)
    if ai_summary:
        return ai_summary

    return _fallback_summary(text, max_sentences)


def _fallback_summary(text: str, max_sentences: int) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return ""
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    selected = [sentences[0]]
    if max_sentences > 2:
        selected.extend(sentences[1 : max_sentences - 1])
    if max_sentences > 1:
        selected.append(sentences[-1])
    return " ".join(selected)
