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
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
from tqdm import tqdm
from config import Config

class commentProcessor:
    """Classifies Facebook comments (issue category, sentiment, churn risk)
    using a TypeSafe model served through Ollama."""

    def __init__(self):
        self.model = Config.MODEL
        self.base_url = Config.BASE_URL
        self.api_key = Config.API_KEY
        self.timeout = Config.TIMEOUT
        self.churn_threshold = Config.CHURN_THRESHOLD
        self.sentiment_levels = Config.SENTIMENT_LEVELS
        self.questions = {
            "issue_category": Choice(
                instructions=Config.ISSUE_CATEGORY_INSTRUCTIONS,
                criteria=Config.ISSUE_CATEGORIES,
            ),
            "sentiment_score": Score(
                instructions=Config.SENTIMENT_INSTRUCTIONS,
                criteria=self.sentiment_levels,
            ),
            "churn_risk": Noul(
                instructions=Config.CHURN_INSTRUCTIONS,
            ),
        }

    def _client(self):
        return TypeSafeClient(
            timeout=self.timeout, api_key=self.api_key, base_url=self.base_url
        )

    def _analyze(self, client, comment):
        result = client.system_one(
            state=comment, questions=self.questions, model=self.model
        )
        sentiment_score = result.scores["sentiment_score"].score
        sentiment_level = round(sentiment_score)
        churn_risk = result.nouls["churn_risk"].noul
        return {
            "comment": comment,
            "issue_category": result.choices["issue_category"].choice,
            "sentiment_score": sentiment_score,
            "sentiment_level": sentiment_level,
            "sentiment_label": self.sentiment_levels[sentiment_level],
            "churn_risk": churn_risk,
            "priority": self.is_priority(sentiment_level, churn_risk),
        }

    def is_priority(self, sentiment_level, churn_risk):
        """Angry customer with high churn risk -> route to the priority care desk."""
        return sentiment_level == 0 and churn_risk > self.churn_threshold

    def process_comment(self, comment):
        """Analyze a single comment dict (post_context, comment_text, user_account_tier)."""
        with self._client() as client:
            return self._analyze(client, comment)

    def process_batch(self, comments, show_progress=True):
        """Analyze a list of comment dicts, reusing one client connection."""
        results = []
        with self._client() as client:
            for comment in tqdm(
                comments,
                unit="comment",
                desc="Analyzing Comments",
                disable=not show_progress,
            ):
                results.append(self._analyze(client, comment))
        return results

    @staticmethod
    def print_result(result):
        print(result["comment"])
        print(f"Issue Category: {result['issue_category']}")
        print(
            f"Sentiment Level (0-2): {result['sentiment_score']}, "
            f"{result['sentiment_level']} = {result['sentiment_label']}"
        )
        print(f"Churn Risk Probability: {result['churn_risk']:.2f}")
        if result["priority"]:
            print(
                "Action: Route immediately to Mobitel Priority Social Media Care Desk for retention workflow."
            )
        print("-" * 72)


if __name__ == "__main__":
    processor = commentProcessor()
    sample = [
        {
            "post_context": "Mobitel 4G Unlimited Data Promotion Announcement",
            "comment_text": "Why is my 4G data dropping to 3G speeds in Colombo 03 since yesterday? I paid for unlimited and this is absolute garbage. Fix this or I am switching to Dialog!",
            "user_account_tier": "Postpaid Unlimited",
        },
        {
            "post_context": "Mobitel 4G Unlimited Data Promotion Announcement",
            "comment_text": "Thank you Mobitel! The new package speeds in Kandy have been super consistent this week.",
            "user_account_tier": "Prepaid",
        },
    ]
    for r in processor.process_batch(sample):
        commentProcessor.print_result(r)