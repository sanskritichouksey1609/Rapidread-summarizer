"""
YouTube Summarization Routes

This module handles YouTube video summarization using real transcript extraction.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from backend.models import YouTubeRequest
from backend.auth import get_current_user
from backend.services.youtube_service import get_video_info, get_available_languages
from backend.services.summarizer_service import summarizer_service
from backend.mysql_db import db
from typing import Dict, Any

# Create router for YouTube endpoints
router = APIRouter(tags=["YouTube Summarization"])


@router.post("/summarize", response_model=Dict[str, Any])
async def summarize_youtube_video(
    request: YouTubeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Summarize a YouTube video using real transcript extraction
    
    This endpoint takes a YouTube video URL, extracts the actual transcript
    using the YouTube Transcript API, and generates a summary using Gemini AI.
    
    Args:
        request: YouTube request containing the video URL
        current_user: Current authenticated user
        
    Returns:
        Summary response with generated summary
        
    Raises:
        HTTPException: If URL is invalid or summarization fails
    """
    try:
        print(f"DEBUG: YouTube summarize request for URL: {request.url}")
        
        # Check if summarizer service is available
        if not summarizer_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not available. Please check GEMINI_API_KEY configuration."
            )
        
        # Check if YouTube API is available
        from backend.services.youtube_service import YOUTUBE_API_AVAILABLE
        if not YOUTUBE_API_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="YouTube Transcript API is not installed. Please install with: pip install youtube-transcript-api"
            )
        
        # Process YouTube URL using YouTube service
        print("DEBUG: Calling get_video_info...")
        video_info = get_video_info(request.url)
        print(f"DEBUG: get_video_info result: success={video_info.get('success')}")
        
        if not video_info["success"]:
            # Provide more specific error messages
            error_msg = video_info["error"]
            print(f"DEBUG: Video info error: {error_msg}")
            
            if "Invalid YouTube URL" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid YouTube URL. Please provide a valid YouTube video URL (e.g., https://youtube.com/watch?v=VIDEO_ID or https://youtu.be/VIDEO_ID)"
                )
            elif "No transcript" in error_msg or "captions" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This video does not have transcripts/captions available. Please try a different video that has captions enabled."
                )
            elif "Could not access transcripts" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to access video transcripts. The video may be private, restricted, or have disabled captions."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to process YouTube video: {error_msg}"
                )
        
        # Generate summary using summarizer service
        video_content = video_info["content"]
        print(f"DEBUG: Video content length: {len(video_content)} characters")
        
        if len(video_content.strip()) < 50:  # Very short transcript
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The video transcript is too short to generate a meaningful summary."
            )
        
        print("DEBUG: Generating summary...")
        summary = summarizer_service.summarize_text(video_content, "youtube")
        print(f"DEBUG: Summary generated, length: {len(summary)} characters")
        
        # Save summary to database
        print("DEBUG: Saving to database...")
        summary_record = db.create_summary(
            user_id=current_user["user_id"],
            source_type="youtube",
            source_url=request.url,
            original_content=video_content[:1000] + "..." if len(video_content) > 1000 else video_content,
            summary=summary
        )
        print(f"DEBUG: Saved with ID: {summary_record['id']}")
        
        return {
            "success": True,
            "message": "YouTube video summarized successfully",
            "summary": {
                "id": summary_record["id"],
                "source_type": "youtube",
                "source_url": request.url,
                "video_id": video_info.get("video_id", ""),
                "title": video_info.get("title", "YouTube Video"),
                "duration": video_info.get("duration", "Unknown"),
                "language": video_info.get("language", "Unknown"),
                "transcript_type": video_info.get("transcript_type", "Unknown"),
                "transcript_length": len(video_content),
                "summary": summary,
                "created_at": summary_record["created_at"]
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"YouTube summarization failed: {str(e)}"
        )


@router.get("/test/{video_id}", response_model=Dict[str, Any])
async def test_youtube_video(
    video_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Test endpoint to debug YouTube video processing
    
    This endpoint helps debug issues with YouTube video processing
    by testing each step individually.
    
    Args:
        video_id: YouTube video ID (11 characters)
        current_user: Current authenticated user
        
    Returns:
        Detailed debug information
    """
    try:
        from backend.services.youtube_service import (
            extract_video_id, 
            validate_youtube_url, 
            get_available_languages,
            fetch_transcript_sync,
            YOUTUBE_API_AVAILABLE
        )
        
        # Test URL construction
        test_url = f"https://youtube.com/watch?v={video_id}"
        
        debug_info = {
            "youtube_api_available": YOUTUBE_API_AVAILABLE,
            "input_video_id": video_id,
            "test_url": test_url,
            "url_validation": validate_youtube_url(test_url),
            "extracted_video_id": extract_video_id(test_url),
            "available_languages": [],
            "transcript_test": "Not tested",
            "errors": []
        }
        
        # Test available languages
        try:
            languages = get_available_languages(video_id)
            debug_info["available_languages"] = languages
        except Exception as e:
            debug_info["errors"].append(f"Language check failed: {str(e)}")
        
        # Test transcript fetch
        try:
            transcript = fetch_transcript_sync(test_url)
            if transcript.startswith("Error:"):
                debug_info["transcript_test"] = f"Failed: {transcript}"
            else:
                debug_info["transcript_test"] = f"Success: {len(transcript)} characters"
                debug_info["transcript_preview"] = transcript[:200] + "..." if len(transcript) > 200 else transcript
        except Exception as e:
            debug_info["transcript_test"] = f"Exception: {str(e)}"
            debug_info["errors"].append(f"Transcript fetch failed: {str(e)}")
        
        return {
            "success": True,
            "debug_info": debug_info
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Test failed: {str(e)}"
        }


@router.get("/video-info/{video_id}", response_model=Dict[str, Any])
async def get_youtube_video_info(
    video_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get information about a YouTube video's available transcripts
    
    This endpoint provides information about what transcript languages
    are available for a given video without processing the full transcript.
    
    Args:
        video_id: YouTube video ID
        current_user: Current authenticated user
        
    Returns:
        Video information including available transcript languages
    """
    try:
        # Get available languages for the video
        available_languages = get_available_languages(video_id)
        
        if not available_languages:
            return {
                "success": False,
                "message": "No transcripts available for this video",
                "video_id": video_id,
                "available_languages": []
            }
        
        return {
            "success": True,
            "message": "Video transcript information retrieved",
            "video_id": video_id,
            "available_languages": available_languages,
            "transcript_count": len(available_languages)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get video info: {str(e)}"
        )
