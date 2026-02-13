from fastapi import APIRouter, HTTPException, Depends, status
from backend.models import ArticleRequest
from backend.auth import get_current_user
from backend.services.article_service import get_article_info
from backend.services.summarizer_service import summarizer_service
from backend.mysql_db import db
from typing import Dict, Any

router = APIRouter(tags=["Article Summarization"])


@router.post("/summarize", response_model=Dict[str, Any])
async def summarize_article(
    request: ArticleRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
  
    try:
        if not summarizer_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not available. Please check GEMINI_API_KEY configuration."
            )
        
        article_info = get_article_info(request.url)
        
        if not article_info["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract article content: {article_info['error']}"
            )
        
        article_content = article_info["content"]
        summary = summarizer_service.summarize_text(article_content, "article")
        
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
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Article summarization failed: {str(e)}"
        )
