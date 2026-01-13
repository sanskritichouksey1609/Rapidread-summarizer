"""
GitHub Repository Summarization Routes

This module handles GitHub repository summarization using modular services.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from backend.models import GitHubRequest
from backend.auth import get_current_user
from backend.services.github_service import get_repo_info
from backend.services.summarizer_service import summarizer_service
from backend.json_db import db
from typing import Dict, Any

# Create router for GitHub endpoints
router = APIRouter(tags=["GitHub Summarization"])


@router.post("/summarize", response_model=Dict[str, Any])
async def summarize_github_repository(
    request: GitHubRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Summarize a GitHub repository
    
    This endpoint takes a GitHub repository URL and generates a summary.
    Note: This is a simplified implementation with placeholder content.
    
    Args:
        request: GitHub request containing the repository URL
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
        
        # Process GitHub repository URL using GitHub service
        repo_info = get_repo_info(request.repo_url)
        
        if not repo_info["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process GitHub repository: {repo_info['error']}"
            )
        
        # Generate summary using summarizer service
        repo_content = repo_info["content"]
        summary = summarizer_service.summarize_text(repo_content, "github")
        
        # Save summary to database
        summary_record = db.create_summary(
            user_id=current_user["user_id"],
            source_type="github",
            source_url=request.repo_url,
            original_content=repo_content[:1000] + "..." if len(repo_content) > 1000 else repo_content,
            summary=summary
        )
        
        return {
            "success": True,
            "message": "GitHub repository summarized successfully",
            "summary": {
                "id": summary_record["id"],
                "source_type": "github",
                "source_url": request.repo_url,
                "owner": repo_info.get("owner", ""),
                "repo": repo_info.get("repo", ""),
                "full_name": repo_info.get("full_name", ""),
                "description": repo_info.get("description", ""),
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
            detail=f"GitHub repository summarization failed: {str(e)}"
        )
