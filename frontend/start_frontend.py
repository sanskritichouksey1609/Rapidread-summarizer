#!/usr/bin/env python3
"""
Rapidread Frontend Startup Script

This script helps you start the Streamlit frontend with proper configuration.
It checks for dependencies and starts the Streamlit server.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_streamlit_installed():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        print("✅ Streamlit is installed")
        return True
    except ImportError:
        print("❌ Streamlit is not installed")
        print("   Please install it with: pip install streamlit")
        return False


def check_requests_installed():
    """Check if requests library is installed"""
    try:
        import requests
        print("✅ Requests library is installed")
        return True
    except ImportError:
        print("❌ Requests library is not installed")
        print("   Please install it with: pip install requests")
        return False


def start_streamlit():
    """Start the Streamlit application"""
    print("\n🚀 Starting Rapidread Frontend...")
    print("   Frontend will be available at: http://localhost:8501")
    print("   Press Ctrl+C to stop the server\n")
    
    try:
        # Change to frontend directory
        frontend_dir = Path(__file__).parent
        os.chdir(frontend_dir)
        
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")


def main():
    """Main function"""
    print("🔍 Rapidread Frontend Startup Check\n")
    
    # Run checks
    checks = [
        check_streamlit_installed(),
        check_requests_installed()
    ]
    
    if all(checks):
        print("\n✅ All checks passed!")
        start_streamlit()
    else:
        print("\n❌ Some dependencies are missing. Please install them first.")
        sys.exit(1)


if __name__ == "__main__":
    main()