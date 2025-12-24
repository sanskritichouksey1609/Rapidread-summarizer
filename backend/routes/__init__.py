from .youtube import router as youtube_router
from .pdf import router as pdf_router
from .article import router as article_router
from .github import router as github_router

__all__ = ["youtube_router", "pdf_router", "article_router", "github_router"]
