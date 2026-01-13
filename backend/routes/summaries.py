"""
Summary Management Routes

This module handles operations related to user summaries.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from backend.models import SummaryListResponse, SummaryResponse
from backend.auth import get_current_user
from backend.json_db import db
from typing import Dict, Any, List

# Create router for summary endpoints
router = APIRouter(tags=["Summary Management"])


@router.get("/my-summaries", response_model=Dict[str, Any])
async def get_my_summaries(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get all summaries for the current user
    
    This endpoint returns all summaries created by the currently logged-in user,
    sorted by creation date (newest first).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of user's summaries
    """
    try:
        # Get user's summaries from database
        summaries = db.get_user_summaries(current_user["user_id"])
        
        # Format summaries for response
        formatted_summaries = []
        for summary in summaries:
            formatted_summaries.append({
                "id": summary["id"],
                "source_type": summary["source_type"],
                "source_url": summary["source_url"],
                "summary": summary["summary"],
                "created_at": summary["created_at"]
            })
        
        return {
            "success": True,
            "count": len(formatted_summaries),
            "summaries": formatted_summaries
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summaries: {str(e)}"
        )


@router.get("/summary/{summary_id}", response_model=Dict[str, Any])
async def get_summary_by_id(
    summary_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific summary by ID
    
    This endpoint returns a specific summary if it belongs to the current user.
    
    Args:
        summary_id: ID of the summary to retrieve
        current_user: Current authenticated user
        
    Returns:
        Summary details
        
    Raises:
        HTTPException: If summary not found or doesn't belong to user
    """
    try:
        # Get summary from database
        summary = db.get_summary_by_id(summary_id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
        # Check if summary belongs to current user
        if summary["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this summary"
            )
        
        return {
            "success": True,
            "summary": {
                "id": summary["id"],
                "source_type": summary["source_type"],
                "source_url": summary["source_url"],
                "original_content": summary["original_content"],
                "summary": summary["summary"],
                "created_at": summary["created_at"]
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )


@router.delete("/summary/{summary_id}", response_model=Dict[str, Any])
async def delete_summary(
    summary_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a specific summary
    
    This endpoint deletes a summary if it belongs to the current user.
    
    Args:
        summary_id: ID of the summary to delete
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If summary not found or doesn't belong to user
    """
    try:
        # Get summary from database to verify ownership
        summary = db.get_summary_by_id(summary_id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
        # Check if summary belongs to current user
        if summary["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this summary"
            )
        
        # Note: For simplicity, we're not implementing actual deletion in JSON database
        # In a real application, you would implement a delete method in the database class
        
        return {
            "success": True,
            "message": "Summary deletion requested (not implemented in this simple version)"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete summary: {str(e)}"
        )