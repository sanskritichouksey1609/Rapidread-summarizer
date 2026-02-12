"""
Pydantic Schemas

These schemas define the structure of data that comes in and goes out of our API.
They help validate data and provide automatic documentation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User Schemas

class UserRegister(BaseModel):
    """
    Schema for user registration
    
    This defines what data we need when someone creates a new account.
    """
    full_name: str
    email: EmailStr  # Automatically validates email format
    password: str


class UserLogin(BaseModel):
    """
    Schema for user login
    
    This defines what data we need when someone tries to log in.
    """
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema for user data in responses
    
    This defines what user data we send back (without password).
    """
    id: str
    full_name: str
    email: str
    created_at: str


class LoginResponse(BaseModel):
    """
    Schema for login response
    
    This defines what we send back when login is successful.
    """
    access_token: str
    token_type: str
    user: UserResponse


# Summary Schemas

class SummaryRequest(BaseModel):
    """
    Base schema for summary requests
    """
    url: str


class ArticleRequest(SummaryRequest):
    """Schema for article summarization requests"""
    pass


class YouTubeRequest(SummaryRequest):
    """Schema for YouTube summarization requests"""
    pass


class GitHubRequest(BaseModel):
    """Schema for GitHub repository summarization requests"""
    repo_url: str


class PDFUpload(BaseModel):
    """Schema for PDF upload (file will be handled separately)"""
    filename: str


class SummaryResponse(BaseModel):
    """
    Schema for summary responses
    
    This defines what we send back when summarization is complete.
    """
    id: str
    source_type: str
    source_url: str
    summary: str
    created_at: str


class SummaryListResponse(BaseModel):
    """
    Schema for list of summaries
    """
    summaries: List[SummaryResponse]


# Generic Response Schemas

class SuccessResponse(BaseModel):
    """
    Schema for generic success responses
    """
    success: bool
    message: str


class ErrorResponse(BaseModel):
    """
    Schema for error responses
    """
    detail: str
