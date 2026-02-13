import subprocess
import sys
import os
from pathlib import Path


def check_streamlit_installed():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        print("Streamlit is installed")
        return True
    except ImportError:
        print("Streamlit is not installed")
        print("   Please install it with: pip install streamlit")
        return False


def check_requests_installed():
    try:
        import requests
        print("Requests library is installed")
        return True
    except ImportError:
        print("Requests library is not installed")
        print("   Please install it with: pip install requests")
        return False


def start_streamlit():
    print("\nStarting Rapidread Frontend...")
    print("   Frontend will be available at: http://localhost:8501")
    print("   Press Ctrl+C to stop the server\n")
    
    try:
        frontend_dir = Path(__file__).parent
        os.chdir(frontend_dir)
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\nFrontend server stopped")
    except Exception as e:
        print(f"Error starting frontend: {e}")


def main():
    """Main function"""
    print("Rapidread Frontend Startup Check\n")
    
    checks = [
        check_streamlit_installed(),
        check_requests_installed()
    ]
    
    if all(checks):
        print("\nAll checks passed!")
        start_streamlit()
    else:
        print("\nSome dependencies are missing. Please install them first.")
        sys.exit(1)


if __name__ == "__main__":
    main()