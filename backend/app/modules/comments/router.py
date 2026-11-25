from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.core.dependencies import DBSession
from backend.app.modules.comments.models.schemas import (
    CommentDetailResponseDTO,
    CommentFilterParams,
    CommentListResponseDTO,
    CommentSearchParams,
)
from app.modules.comments.service import CommentService
from backend.app.shared.dtos import ErrorResponseDTO

router = APIRouter()


@router.get(
    "/posts/{post_id}/comments",
    status_code=status.HTTP_200_OK,
    response_model=CommentListResponseDTO,
    tags=["posts"],
    summary="List comments for a post",
    description=(
        "Retrieve comments belonging to a specific Facebook post, with optional "
        "filtering by sentiment, intent, aspect, or analysis completion status."
    ),
    response_description="Filtered list of comments belonging to the specified post.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponseDTO,
            "description": "Post with the given ID was not found (`POST_NOT_FOUND`).",
        },
    },
)
def get_post_comments(
    post_id: Annotated[str, Path(description="Meta Facebook post ID, e.g. `1029384756_5566778899`")],
    filters: Annotated[CommentFilterParams, Query()],
    db: DBSession,
) -> CommentListResponseDTO:
    return CommentService.get_post_comments(post_id, filters, db)


@router.get(
    "/comments",
    status_code=status.HTTP_200_OK,
    response_model=CommentListResponseDTO,
    tags=["comments"],
    summary="Search comments across posts",
    description=(
        "Search and filter comments across all ingested Facebook posts by sentiment, "
        "intent, aspect, `post_id`, analysis state, and inclusive date range."
    ),
    response_description="List of comments matching the provided search filters.",
)
def get_comments(
    filters: Annotated[CommentSearchParams, Query()],
    db: DBSession,
) -> CommentListResponseDTO:
    return CommentService.get_comments(filters, db)


@router.get(
    "/comments/{comment_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommentDetailResponseDTO,
    tags=["comments"],
    summary="Get comment details",
    description=(
        "Retrieve a single Facebook comment by its Meta `comment_id`, including "
        "full NLP analysis details (language, keywords, actionability, model version) "
        "and nested replies."
    ),
    response_description="Detailed comment record with full analysis and replies.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponseDTO,
            "description": "Comment with the given ID was not found (`COMMENT_NOT_FOUND`).",
        },
    },
)
def get_comment(
    comment_id: Annotated[str, Path(description="Meta Facebook comment ID, e.g. `5566778899_1122334455`")],
    db: DBSession,
) -> CommentDetailResponseDTO:
    return CommentService.get_comment(comment_id, db)
