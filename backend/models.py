from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr  # Automatically validates email format
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    created_at: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class SummaryRequest(BaseModel):
    url: str


class ArticleRequest(SummaryRequest):
    pass


class YouTubeRequest(SummaryRequest):
    pass


class GitHubRequest(BaseModel):
    repo_url: str


class PDFUpload(BaseModel):
    filename: str


class SummaryResponse(BaseModel):
    id: str
    source_type: str
    source_url: str
    summary: str
    created_at: str


class SummaryListResponse(BaseModel):
    summaries: List[SummaryResponse]


class SuccessResponse(BaseModel):
    success: bool
    message: str


class ErrorResponse(BaseModel):
    detail: str
