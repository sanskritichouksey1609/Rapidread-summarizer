"""
Rapidread Summarizer Backend

This is the main FastAPI application that handles all API endpoints
for the Rapidread content summarization service.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Rapidread Summarizer API",
    description="AI-powered content summarization service using Google Gemini",
    version="1.0.0"
)

# Configure CORS for frontend access
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include all routers
from backend.routes import auth, article, youtube, pdf, github, summaries

# Authentication routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Content summarization routes
app.include_router(article.router, prefix="/article", tags=["Article Summarization"])
app.include_router(youtube.router, prefix="/youtube", tags=["YouTube Summarization"])
app.include_router(pdf.router, prefix="/pdf", tags=["PDF Summarization"])
app.include_router(github.router, prefix="/github", tags=["GitHub Summarization"])

# Summary management routes
app.include_router(summaries.router, prefix="/summaries", tags=["Summary Management"])


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint
    
    Returns basic information about the API.
    """
    return {
        "message": "Rapidread Summarizer API",
        "version": "1.0.0",
        "description": "AI-powered content summarization service",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint
    
    Returns the health status of the API and its dependencies.
    """
    try:
        # Check if Gemini API key is configured
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        gemini_configured = gemini_api_key and gemini_api_key != "your-gemini-api-key-here"
        
        # Test Gemini connection if configured
        gemini_status = "not_configured"
        gemini_details = {}
        
        if gemini_configured:
            try:
                from backend.services.summarizer_service import summarizer_service
                if summarizer_service:
                    test_result = summarizer_service.test_connection()
                    if test_result["success"]:
                        gemini_status = "connected"
                        gemini_details = {
                            "model": test_result["model"],
                            "test_response": test_result["response"]
                        }
                    else:
                        gemini_status = "connection_failed"
                        gemini_details = {"error": test_result["message"]}
                else:
                    gemini_status = "service_unavailable"
            except Exception as e:
                gemini_status = "error"
                gemini_details = {"error": str(e)}
        
        # Check MySQL database
        from backend.mysql_db import db
        db_status = "connected"
        
        return {
            "status": "healthy",
            "database": db_status,
            "ai_service": {
                "status": gemini_status,
                "configured": gemini_configured,
                "details": gemini_details
            },
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/storage-info", tags=["System"])
def get_storage_info():
    """
    Get information about the storage system
    
    Returns details about the MySQL database storage.
    """
    try:
        from backend.mysql_db import db
        
        # Get basic storage statistics
        connection = db._get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM users")
                users_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM summaries")
                summaries_count = cursor.fetchone()['count']
        finally:
            connection.close()
        
        return {
            "storage_type": "MySQL",
            "database": db.connection_params['database'],
            "host": db.connection_params['host'],
            "users_count": users_count,
            "summaries_count": summaries_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get storage info: {str(e)}")


# Run the application using run_backend.py script
