from fastapi import APIRouter, HTTPException, Depends, status
from backend.models import SummaryListResponse, SummaryResponse
from backend.auth import get_current_user
from backend.mysql_db import db
from typing import Dict, Any, List

router = APIRouter(tags=["Summary Management"])


@router.get("/my-summaries", response_model=Dict[str, Any])
async def get_my_summaries(current_user: Dict[str, Any] = Depends(get_current_user)):
  
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
    try:
       
        summary = db.get_summary_by_id(summary_id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
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
   
    try:
        summary = db.get_summary_by_id(summary_id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
        if summary["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this summary"
            )
        
        
        return {
            "success": True,
            "message": "Summary deletion requested (not implemented in this simple version)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete summary: {str(e)}"
        )