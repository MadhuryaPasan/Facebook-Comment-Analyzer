from fastapi import APIRouter

from app.modules.analysis.router import router as analysis_router
from app.modules.comments.router import router as comments_router
from app.modules.posts.router import router as posts_router

api_v1_router = APIRouter()
api_v1_router.include_router(posts_router)
api_v1_router.include_router(comments_router)
api_v1_router.include_router(analysis_router)
