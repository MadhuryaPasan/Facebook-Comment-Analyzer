from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Intent(str, Enum):
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    PRAISE = "praise"
    SPAM = "spam"
    OTHER = "other"

class Language(str, Enum):
    ENGLISH = "en"
    SINHALA = "si"
    TAMIL = "ta"
    MIXED = "mixed" # Singlish / code-mixed

class TaskStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"
