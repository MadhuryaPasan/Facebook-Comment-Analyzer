from fastapi import APIRouter, status

from app.core.dependencies import DBSession
from app.modules.analysis.models.schemas import AnalyzeRequest, AnalyzeTaskResponseDTO
from app.modules.analysis.service import AnalysisService
from app.shared.dtos import ErrorResponseDTO

router = APIRouter(tags=["analysis"])


@router.post(
    "/comments/analyze",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AnalyzeTaskResponseDTO,
    summary="Queue comment analysis for a post",
    description=(
        "Enqueue an asynchronous background job to fetch comments for the given "
        "Facebook `post_id` via the Graph API client and run sentiment, intent, "
        "language, and aspect extraction."
    ),
    response_description="Queued analysis task identifier and initial status.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponseDTO,
            "description": "Target post could not be found (`POST_NOT_FOUND`).",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponseDTO,
            "description": "Background task queue is currently unreachable (`TASK_QUEUE_UNAVAILABLE`).",
        },
    },
)
def analyze_post_comments(
    analyze_request: AnalyzeRequest,
    db: DBSession,
) -> AnalyzeTaskResponseDTO:
    return AnalysisService.queue_post_analysis(analyze_request, db)
