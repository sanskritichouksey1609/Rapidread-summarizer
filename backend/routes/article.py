from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ArticleRequest(BaseModel):
    url: str


@router.post("/summarize")
async def summarize_article(req: ArticleRequest):
    return {"message": "Article summarize endpoint", "url": req.url}
