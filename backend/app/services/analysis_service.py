from sqlmodel import Session

from app.models.schemas.comment import AnalyzeRequest, AnalyzeTaskResponseDTO


class AnalysisService:


    @staticmethod
    def queue_post_analysis(analyze_request: AnalyzeRequest, db: Session) -> AnalyzeTaskResponseDTO:
        pass
