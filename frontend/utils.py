import requests
import streamlit as st
from typing import Optional, Dict, Any

BACKEND_URL = "http://localhost:8000"


def get_auth_headers() -> Dict[str, str]:
    """
    Get authentication headers for API requests
    
    Returns:
        Dictionary with Authorization header if user is logged in
    """
    headers = {"Content-Type": "application/json"}
    
    if st.session_state.get('user_token'):
        headers["Authorization"] = f"Bearer {st.session_state.user_token}"
    
    return headers


def summarize_article(url: str) -> Dict[str, Any]:
    """
    Summarize an article from URL
    
    Args:
        url: The article URL to summarize
        
    Returns:
        Dictionary with summary result
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/article/summarize",
            json={"url": url},
            headers=get_auth_headers(),
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            return {"success": False, "error": error_data.get("detail", "Summarization failed")}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}


def summarize_pdf(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Summarize a PDF file
    
    Args:
        file_content: The PDF file content as bytes
        filename: The original filename
        
    Returns:
        Dictionary with summary result
    """
    try:
        files = {"file": (filename, file_content, "application/pdf")}
        headers = {}
        if st.session_state.get('user_token'):
            headers["Authorization"] = f"Bearer {st.session_state.user_token}"
        
        response = requests.post(
            f"{BACKEND_URL}/pdf/summarize",
            files=files,
            headers=headers,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            return {"success": False, "error": error_data.get("detail", "PDF summarization failed")}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}


def summarize_youtube(url: str) -> Dict[str, Any]:
    """
    Summarize a YouTube video
    
    Args:
        url: The YouTube video URL
        
    Returns:
        Dictionary with summary result
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/youtube/summarize",
            json={"url": url},
            headers=get_auth_headers(),
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            return {"success": False, "error": error_data.get("detail", "YouTube summarization failed")}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}


def summarize_github(repo_url: str) -> Dict[str, Any]:
    """
    Summarize a GitHub repository
    
    Args:
        repo_url: The GitHub repository URL
        
    Returns:
        Dictionary with summary result
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/github/summarize",
            json={"repo_url": repo_url},
            headers=get_auth_headers(),
            timeout=180
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            return {"success": False, "error": error_data.get("detail", "GitHub summarization failed")}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}


def get_my_summaries() -> Dict[str, Any]:
    """
    Get all summaries for the current user
    
    Returns:
        Dictionary with user's summaries
    """
    try:
        response = requests.get(
            f"{BACKEND_URL}/summaries/my-summaries",
            headers=get_auth_headers(),
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            return {"success": False, "error": error_data.get("detail", "Failed to get summaries")}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
