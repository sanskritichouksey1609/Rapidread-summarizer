"""
Database Initialization Script

This script initializes the MySQL database tables for the Rapidread Summarizer.
Run this script once before starting the application for the first time.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.mysql_db import db

def main():
    """
    Initialize the database
    """
    print("=" * 60)
    print("Rapidread Summarizer - Database Initialization")
    print("=" * 60)
    print()
    
    try:
        print("Connecting to MySQL database...")
        print(f"Host: {db.connection_params['host']}")
        print(f"Database: {db.connection_params['database']}")
        print()
        
        # Test connection
        connection = db._get_connection()
        connection.close()
        print("✓ Database connection successful!")
        print()
        
        print("Creating database tables...")
        db._init_tables()
        print("✓ Tables created successfully!")
        print()
        
        print("=" * 60)
        print("Database initialization complete!")
        print("=" * 60)
        print()
        print("You can now start the application using:")
        print("  python run_backend.py")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("ERROR: Database initialization failed!")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Please check:")
        print("1. MySQL server is running")
        print("2. Database credentials in .env file are correct")
        print("3. Database user has proper permissions")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
