from enum import Enum


class Sentiment(str, Enum):
    """Predicted emotional polarity of a comment."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Intent(str, Enum):
    """Primary communicative intent behind a comment."""

    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    PRAISE = "praise"
    SPAM = "spam"
    OTHER = "other"


class Language(str, Enum):
    """Detected language of a comment."""

    ENGLISH = "en"
    SINHALA = "si"
    TAMIL = "ta"
    MIXED = "mixed"  # Singlish / code-mixed


class TaskStatus(str, Enum):
    """Lifecycle status of an asynchronous comment analysis job."""

    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"
