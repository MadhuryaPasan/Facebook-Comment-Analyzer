from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies.type import DBSession
from app.models.schemas.comment import CommentDetailResponseDTO,CommentFilterParams, CommentListResponseDTO, CommentSearchParams
from app.models.schemas.post import PostFilterParams, PostListResponseDTO, PostResponseDTO
from app.services.post_comment_service import PostCommentService


router = APIRouter()

# ---- Posts ----

@router.get('/posts', status_code=status.HTTP_200_OK, tags=["posts"])
def get_posts(filters: Annotated[PostFilterParams, Query()], db: DBSession) -> PostListResponseDTO:
    return PostCommentService.get_posts(filters, db)

@router.get('/posts/{post_id}', status_code=status.HTTP_200_OK, tags=["posts"])
def get_post(post_id: str, db: DBSession) -> PostResponseDTO:
    return PostCommentService.get_post(post_id, db)

@router.get('/posts/{post_id}/comments', status_code=status.HTTP_200_OK, tags=["posts"])
def get_post_comments(post_id: str, filters: Annotated[CommentFilterParams, Query()], db: DBSession) -> CommentListResponseDTO:
    return PostCommentService.get_post_comments(post_id, filters, db)

# ---- Comments ----

@router.get('/comments', status_code=status.HTTP_200_OK, tags=["comments"])
def get_comments(filters: Annotated[CommentSearchParams, Query()], db: DBSession) -> CommentListResponseDTO:
    return PostCommentService.get_comments(filters, db)

@router.get('/comments/{comment_id}', status_code=status.HTTP_200_OK, tags=["comments"])
def get_comment(comment_id: str, db: DBSession) -> CommentDetailResponseDTO:
    return PostCommentService.get_comment(comment_id, db)