"""
Simple MySQL Database System

This module provides a simple MySQL-based database for storing users and summaries.
It's perfect for beginners and small-scale applications.
"""

import pymysql
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MySQLDatabase:
    """
    Simple MySQL Database Class
    
    This class handles all database operations using MySQL.
    It's much simpler than complex ORM systems and perfect for learning.
    """
    
    def __init__(self):
        """
        Initialize the MySQL database connection
        """
        # Parse DATABASE_URL from environment
        database_url = os.getenv('DATABASE_URL', '')
        
        # Extract connection details from DATABASE_URL
        # Format: mysql+pymysql://user:password@host:port/database
        if database_url.startswith('mysql+pymysql://'):
            connection_string = database_url.replace('mysql+pymysql://', '')
            
            # Split user:password@host:port/database
            auth_part, host_part = connection_string.split('@')
            user, password = auth_part.split(':')
            host_db = host_part.split('/')
            host_port = host_db[0].split(':')
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 3306
            database = host_db[1] if len(host_db) > 1 else 'rapidread_db'
            
            self.connection_params = {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'database': database,
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.DictCursor
            }
        else:
            # Fallback to individual environment variables
            self.connection_params = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 3306)),
                'user': os.getenv('DB_USER', 'rapidread_user'),
                'password': os.getenv('DB_PASSWORD', 'rapidread123'),
                'database': os.getenv('DB_NAME', 'rapidread_db'),
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.DictCursor
            }
        
        # Initialize database tables
        self._init_tables()
    
    def _get_connection(self):
        """
        Get a new database connection
        
        Returns:
            pymysql connection object
        """
        return pymysql.connect(**self.connection_params)
    
    def _init_tables(self):
        """
        Initialize database tables if they don't exist
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(36) PRIMARY KEY,
                        full_name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        created_at DATETIME NOT NULL,
                        INDEX idx_email (email)
                    )
                """)
                
                # Create summaries table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS summaries (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        source_type VARCHAR(50) NOT NULL,
                        source_url TEXT NOT NULL,
                        original_content TEXT,
                        summary TEXT NOT NULL,
                        created_at DATETIME NOT NULL,
                        INDEX idx_user_id (user_id)
                    )
                """)
                
            connection.commit()
        finally:
            connection.close()
    
    # User Management Methods
    
    def create_user(self, full_name: str, email: str, password: str) -> Dict[str, Any]:
        """
        Create a new user
        
        Args:
            full_name: User's full name
            email: User's email address
            password: User's password (stored as plain text for simplicity)
            
        Returns:
            Dictionary with user information
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                # Check if user already exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    raise ValueError("User with this email already exists")
                
                # Create new user
                user_id = str(uuid.uuid4())
                created_at = datetime.now()
                
                cursor.execute("""
                    INSERT INTO users (id, full_name, email, password, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, full_name, email, password, created_at))
                
            connection.commit()
            
            # Return user info without password
            return {
                'id': user_id,
                'full_name': full_name,
                'email': email,
                'created_at': created_at.isoformat()
            }
        finally:
            connection.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address
        
        Args:
            email: User's email address
            
        Returns:
            User dictionary if found, None otherwise
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, full_name, email, password, created_at
                    FROM users WHERE email = %s
                """, (email,))
                
                user = cursor.fetchone()
                
                if user:
                    # Convert datetime to ISO format string
                    user['created_at'] = user['created_at'].isoformat()
                
                return user
        finally:
            connection.close()
    
    def verify_user_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Verify user password and return user info
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            User dictionary (without password) if credentials are correct, None otherwise
        """
        user = self.get_user_by_email(email)
        
        if user and user['password'] == password:
            # Return user info without password
            user_info = user.copy()
            del user_info['password']
            return user_info
        
        return None
    
    # Summary Management Methods
    
    def create_summary(self, user_id: str, source_type: str, source_url: str, 
                      original_content: str, summary: str) -> Dict[str, Any]:
        """
        Create a new summary
        
        Args:
            user_id: ID of the user who created the summary
            source_type: Type of source (article, youtube, pdf, github)
            source_url: URL or identifier of the source
            original_content: Original content that was summarized
            summary: The generated summary
            
        Returns:
            Dictionary with summary information
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                # Create new summary
                summary_id = str(uuid.uuid4())
                created_at = datetime.now()
                
                cursor.execute("""
                    INSERT INTO summaries (id, user_id, source_type, source_url, 
                                         original_content, summary, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (summary_id, user_id, source_type, source_url, 
                      original_content, summary, created_at))
                
            connection.commit()
            
            return {
                'id': summary_id,
                'user_id': user_id,
                'source_type': source_type,
                'source_url': source_url,
                'original_content': original_content,
                'summary': summary,
                'created_at': created_at.isoformat()
            }
        finally:
            connection.close()
    
    def get_user_summaries(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all summaries for a specific user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of summary dictionaries
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, user_id, source_type, source_url, 
                           original_content, summary, created_at
                    FROM summaries
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
                
                summaries = cursor.fetchall()
                
                # Convert datetime to ISO format string
                for summary in summaries:
                    summary['created_at'] = summary['created_at'].isoformat()
                
                return summaries
        finally:
            connection.close()
    
    def get_summary_by_id(self, summary_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific summary by ID
        
        Args:
            summary_id: ID of the summary
            
        Returns:
            Summary dictionary if found, None otherwise
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, user_id, source_type, source_url, 
                           original_content, summary, created_at
                    FROM summaries
                    WHERE id = %s
                """, (summary_id,))
                
                summary = cursor.fetchone()
                
                if summary:
                    # Convert datetime to ISO format string
                    summary['created_at'] = summary['created_at'].isoformat()
                
                return summary
        finally:
            connection.close()


# Create global database instance
db = MySQLDatabase()
