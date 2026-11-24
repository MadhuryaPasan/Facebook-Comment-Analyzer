from fastapi import APIRouter, status



router = APIRouter(tags=["analysis"])

@router.post('/comments/analyze', status_code=status.HTTP_202_ACCEPTED)
def analyze_post_comments(analyze_request: AnalyzeRequest, db: DBSession) -> AnalyzeTaskResponseDTO:
    return AnalysisService.queue_post_analysis(analyze_request, db)
