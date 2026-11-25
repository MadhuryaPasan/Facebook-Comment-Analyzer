from fastapi import APIRouter, status

from app.dependencies.type import DBSession
from app.models.schemas.comment import AnalyzeRequest, AnalyzeTaskResponseDTO
from app.services.analysis_service import AnalysisService


router = APIRouter(tags=["analysis"])

@router.post('/comments/analyze', status_code=status.HTTP_202_ACCEPTED)
def analyze_post_comments(analyze_request: AnalyzeRequest, db: DBSession) -> AnalyzeTaskResponseDTO:
    return AnalysisService.queue_post_analysis(analyze_request, db)
