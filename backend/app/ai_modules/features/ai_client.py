"""Optional AI provider integrations for EduGenie.

The functions in this package must stay usable in local development even when
API keys or heavyweight model dependencies are unavailable. Provider calls
therefore return ``None`` on configuration/runtime failure and callers provide
clear local fallbacks.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .provenance import record_model


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str | None = None
    model_name: str = "gemini-1.5-pro"

    @classmethod
    def from_env(cls) -> "GeminiConfig":
        return cls(
            api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
            model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
        )


def generate_with_gemini(prompt: str, config: GeminiConfig | None = None) -> str | None:
    """Generate text with Gemini when the SDK and API key are configured."""

    config = config or GeminiConfig.from_env()
    if not config.api_key:
        return None

    try:
        import google.generativeai as genai  # type: ignore
    except Exception:
        return None

    try:
        genai.configure(api_key=config.api_key)
        model = genai.GenerativeModel(config.model_name)
        response = model.generate_content(prompt)
    except Exception:
        return None

    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        record_model(config.model_name)
        return text.strip()

    return None
