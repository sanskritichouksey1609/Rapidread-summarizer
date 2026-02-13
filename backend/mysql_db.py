import pymysql
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MySQLDatabase:
    
    def __init__(self):
        database_url = os.getenv('DATABASE_URL', '')
        
        if database_url.startswith('mysql+pymysql://'):
            connection_string = database_url.replace('mysql+pymysql://', '')
            
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
        
        self._init_tables()
    
    def _get_connection(self):
        return pymysql.connect(**self.connection_params)
    
    def _init_tables(self):
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
    
    def create_user(self, full_name: str, email: str, password: str) -> Dict[str, Any]:
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    raise ValueError("User with this email already exists")
                
                user_id = str(uuid.uuid4())
                created_at = datetime.now()
                
                cursor.execute("""
                    INSERT INTO users (id, full_name, email, password, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, full_name, email, password, created_at))
                
            connection.commit()
            
            return {
                'id': user_id,
                'full_name': full_name,
                'email': email,
                'created_at': created_at.isoformat()
            }
        finally:
            connection.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
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
        user = self.get_user_by_email(email)
        
        if user and user['password'] == password:
            # Return user info without password
            user_info = user.copy()
            del user_info['password']
            return user_info
        
        return None
    
    def create_summary(self, user_id: str, source_type: str, source_url: str, 
                      original_content: str, summary: str) -> Dict[str, Any]:
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

db = MySQLDatabase()
