from app.core.config import Config
from app.pipeline.contracts import AnalysisResult, RawComment


class CommentAnalyzer:
    """NLP analyzer that turns `RawComment` inputs into structured `AnalysisResult` outputs."""

    def __init__(self, model_version: str = Config.ANALYZER_MODEL_VERSION) -> None:
        self.model_version = model_version

    def analyze(self, comment: RawComment) -> AnalysisResult:
        """Analyze a single comment for sentiment, intent, language, and aspects."""
        raise NotImplementedError("CommentAnalyzer.analyze is not implemented yet")

    def analyze_batch(self, comments: list[RawComment]) -> list[AnalysisResult]:
        """Analyze a batch of comments sequentially (override for batched inference)."""
        return [self.analyze(comment) for comment in comments]
