#!/usr/bin/env python3
"""
Rapidread Backend Startup Script

This script starts the FastAPI backend server with proper configuration.
Run this from the project root directory.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """
    Main function to start the backend server
    """
    print("🚀 Starting Rapidread Summarizer Backend...")
    
    # Get the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Add the project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Import and run the FastAPI app
    try:
        import uvicorn
        from backend.main import app
        
        # Get configuration from environment
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        
        print(f"📍 Server will run on: http://{host}:{port}")
        print(f"📚 API Documentation: http://{host}:{port}/docs")
        print(f"🔍 Health Check: http://{host}:{port}/health")
        print("Press Ctrl+C to stop the server\n")
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed all dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()