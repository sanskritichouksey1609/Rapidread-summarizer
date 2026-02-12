"""
Article Summarization Routes

This module handles web article summarization using modular services.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from backend.models import ArticleRequest
from backend.auth import get_current_user
from backend.services.article_service import get_article_info
from backend.services.summarizer_service import summarizer_service
from backend.mysql_db import db
from typing import Dict, Any

# Create router for article endpoints
router = APIRouter(tags=["Article Summarization"])


@router.post("/summarize", response_model=Dict[str, Any])
async def summarize_article(
    request: ArticleRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Summarize a web article from URL
    
    This endpoint takes a web article URL, extracts the content,
    and generates a summary using Gemini AI.
    
    Args:
        request: Article request containing the URL
        current_user: Current authenticated user
        
    Returns:
        Summary response with generated summary
        
    Raises:
        HTTPException: If URL is invalid or summarization fails
    """
    try:
        # Check if summarizer service is available
        if not summarizer_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not available. Please check GEMINI_API_KEY configuration."
            )
        
        # Extract content from the article URL using article service
        article_info = get_article_info(request.url)
        
        if not article_info["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract article content: {article_info['error']}"
            )
        
        # Generate summary using summarizer service
        article_content = article_info["content"]
        summary = summarizer_service.summarize_text(article_content, "article")
        
        # Save summary to database
        summary_record = db.create_summary(
            user_id=current_user["user_id"],
            source_type="article",
            source_url=request.url,
            original_content=article_content[:1000] + "..." if len(article_content) > 1000 else article_content,
            summary=summary
        )
        
        return {
            "success": True,
            "message": "Article summarized successfully",
            "summary": {
                "id": summary_record["id"],
                "source_type": "article",
                "source_url": request.url,
                "title": article_info.get("title", "Article"),
                "domain": article_info.get("domain", ""),
                "authors": article_info.get("authors", []),
                "publish_date": article_info.get("publish_date", ""),
                "keywords": article_info.get("keywords", []),
                "top_image": article_info.get("top_image", ""),
                "extraction_method": article_info.get("extraction_method", "unknown"),
                "summary": summary,
                "created_at": summary_record["created_at"]
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Article summarization failed: {str(e)}"
        )
