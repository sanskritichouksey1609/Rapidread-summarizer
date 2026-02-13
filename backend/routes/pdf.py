from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from backend.auth import get_current_user
from backend.services.pdf_service import get_pdf_info
from backend.services.summarizer_service import summarizer_service
from backend.mysql_db import db
from typing import Dict, Any

router = APIRouter(tags=["PDF Summarization"])


@router.post("/summarize", response_model=Dict[str, Any])
async def summarize_pdf_document(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
  
    try:
        if not summarizer_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not available. Please check GEMINI_API_KEY configuration."
            )
        
        file_content = await file.read()
        
        pdf_info = get_pdf_info(file_content, file.filename)
        
        if not pdf_info["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=pdf_info["error"]
            )
        
        pdf_content = pdf_info["content"]
        summary = summarizer_service.summarize_text(pdf_content, "pdf")
        
        summary_record = db.create_summary(
            user_id=current_user["user_id"],
            source_type="pdf",
            source_url=file.filename,
            original_content=pdf_content[:1000] + "..." if len(pdf_content) > 1000 else pdf_content,
            summary=summary
        )
        
        return {
            "success": True,
            "message": "PDF document summarized successfully",
            "summary": {
                "id": summary_record["id"],
                "source_type": "pdf",
                "filename": file.filename,
                "page_count": pdf_info.get("page_count", 0),
                "file_size": pdf_info.get("file_size", 0),
                "summary": summary,
                "created_at": summary_record["created_at"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF summarization failed: {str(e)}"
        )


@router.post("/upload", response_model=Dict[str, Any])
async def upload_pdf_legacy(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    
    return await summarize_pdf_document(file, current_user)
