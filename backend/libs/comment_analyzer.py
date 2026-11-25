"""Standalone comment analyzer library.

This module MUST NOT import anything from `app.*` (no FastAPI, SQLModel,
`Config`, `RawComment` or `AnalysisResult`). All settings are passed into
`CommentAnalyzer.__init__` by the caller (`app/pipeline/ingestion.py`).

`analyze()` returns a plain dict with exactly these keys:

    language          "en" | "si" | "ta" | "mixed"
    sentiment         "positive" | "neutral" | "negative"
    sentiment_score   float, 0.0 - 1.0
    intent            "complaint" | "suggestion" | "question" | "praise" | "spam" | "other"
    aspects           list of {"aspect": str, "sentiment": str, "score": float}
    keywords          list[str]
    is_actionable     bool
    model_version     str

String values must match the enums in `app/shared/enums.py`, so ingestion can
build an `AnalysisResult` from the dict without any mapping.
"""

from typing import Any


class CommentAnalyzer:
    """Turns comment text into sentiment, intent, language, aspects and keywords."""

    def __init__(self, model_version: str) -> None:
        """Load models here, once. Add model settings (model name, base URL) as arguments."""
        self.model_version = model_version

    def analyze(self, text: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Analyze one comment's text. `context` can carry extra info, e.g. the post text."""
        raise NotImplementedError("CommentAnalyzer.analyze is not implemented yet")

    def analyze_batch(self, texts: list[str]) -> list[dict[str, Any]]:
        """Analyze several comments (override for batched inference)."""
        return [self.analyze(text) for text in texts]
