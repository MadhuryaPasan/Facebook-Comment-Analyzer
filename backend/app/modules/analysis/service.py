from sqlmodel import Session

from backend.app.modules.analysis.models.schemas import AnalyzeRequest, AnalyzeTaskResponseDTO


class AnalysisService:
    """Orchestrates queuing background Graph API fetches and NLP comment analysis."""

    @staticmethod
    def queue_post_analysis(
        analyze_request: AnalyzeRequest,
        db: Session,
    ) -> AnalyzeTaskResponseDTO:
        """Validate target post and enqueue an asynchronous analysis job."""
        raise NotImplementedError("AnalysisService.queue_post_analysis is not implemented yet")
