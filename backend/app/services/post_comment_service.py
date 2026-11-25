from sqlmodel import Session

from app.models.schemas.comment import CommentDetailResponseDTO,CommentFilterParams,CommentListResponseDTO,CommentSearchParams
from app.models.schemas.post import PostFilterParams, PostListResponseDTO, PostResponseDTO


class PostCommentService:


    # ---- Posts ----

    @staticmethod
    def get_posts(filters: PostFilterParams, db: Session) -> PostListResponseDTO:
        pass

    @staticmethod
    def get_post(post_id: str, db: Session) -> PostResponseDTO:
        pass

    # ---- Comments ----

    @staticmethod
    def get_post_comments(post_id: str, filters: CommentFilterParams, db: Session) -> CommentListResponseDTO:
        pass

    @staticmethod
    def get_comments(filters: CommentSearchParams, db: Session) -> CommentListResponseDTO:
        pass

    @staticmethod
    def get_comment(comment_id: str, db: Session) -> CommentDetailResponseDTO:
        pass