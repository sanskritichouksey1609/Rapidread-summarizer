from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class GitHubRequest(BaseModel):
    repo_url: str


@router.post("/summarize")
async def summarize_repo(req: GitHubRequest):
    return {"message": "GitHub repo summarize endpoint", "repo_url": req.repo_url}
