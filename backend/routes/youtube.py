from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class YouTubeRequest(BaseModel):
    url: str


@router.post("/summarize")
async def summarize_youtube(req: YouTubeRequest):
    # Placeholder: integrate youtube_service to fetch and summarize
    return {"message": "YouTube summarize endpoint", "url": req.url}
