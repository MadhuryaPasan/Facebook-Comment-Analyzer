from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.core.dependencies import DBSession
from app.modules.posts.models.schemas import PostFilterParams, PostListResponseDTO, PostResponseDTO
from app.modules.posts.service import PostService
from app.shared.dtos import ErrorResponseDTO

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=PostListResponseDTO,
    summary="List Facebook posts",
    description=(
        "Retrieve Facebook page posts stored in the analyzer database, optionally "
        "filtered by an inclusive `from` / `to` publication date range, along with "
        "comment counts and aggregated sentiment summaries."
    ),
    response_description="List of posts with their comment and sentiment counts.",
)
def get_posts(
    filters: Annotated[PostFilterParams, Query()],
    db: DBSession,
) -> PostListResponseDTO:
    return PostService.get_posts(filters, db)


@router.get(
    "/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=PostResponseDTO,
    summary="Get post details",
    description=(
        "Retrieve a single Facebook post by its Meta `post_id`, including total "
        "comment count, analyzed comment count, and sentiment breakdown."
    ),
    response_description="Detailed post record with sentiment summary.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponseDTO,
            "description": "Post with the given ID was not found (`POST_NOT_FOUND`).",
        },
    },
)
def get_post(
    post_id: Annotated[str, Path(description="Meta Facebook post ID, e.g. `1029384756_5566778899`")],
    db: DBSession,
) -> PostResponseDTO:
    return PostService.get_post(post_id, db)
