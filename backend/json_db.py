"""
Simple JSON Database System

This module provides a simple JSON-based database for storing users and summaries.
It's perfect for beginners and small-scale applications.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class JSONDatabase:
    """
    Simple JSON Database Class
    
    This class handles all database operations using JSON files.
    It's much simpler than SQL databases and perfect for learning.
    """
    
    def __init__(self, data_dir: str = "json_storage"):
        """
        Initialize the JSON database
        
        Args:
            data_dir: Directory where JSON files will be stored
        """
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.summaries_file = os.path.join(data_dir, "summaries.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize JSON files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """
        Initialize JSON files with empty data if they don't exist
        """
        # Initialize users file
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump([], f, indent=2)
        
        # Initialize summaries file
        if not os.path.exists(self.summaries_file):
            with open(self.summaries_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def _read_json(self, file_path: str) -> List[Dict]:
        """
        Read data from a JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of dictionaries containing the data
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _write_json(self, file_path: str, data: List[Dict]):
        """
        Write data to a JSON file
        
        Args:
            file_path: Path to the JSON file
            data: List of dictionaries to write
        """
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
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
        users = self._read_json(self.users_file)
        
        # Check if user already exists
        for user in users:
            if user['email'] == email:
                raise ValueError("User with this email already exists")
        
        # Create new user
        new_user = {
            'id': str(uuid.uuid4()),
            'full_name': full_name,
            'email': email,
            'password': password,  # Plain text password (not recommended for production)
            'created_at': datetime.now().isoformat()
        }
        
        # Add user to list and save
        users.append(new_user)
        self._write_json(self.users_file, users)
        
        # Return user info without password
        user_info = new_user.copy()
        del user_info['password']
        return user_info
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address
        
        Args:
            email: User's email address
            
        Returns:
            User dictionary if found, None otherwise
        """
        users = self._read_json(self.users_file)
        
        for user in users:
            if user['email'] == email:
                return user
        
        return None
    
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
        summaries = self._read_json(self.summaries_file)
        
        # Create new summary
        new_summary = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'source_type': source_type,
            'source_url': source_url,
            'original_content': original_content,
            'summary': summary,
            'created_at': datetime.now().isoformat()
        }
        
        # Add summary to list and save
        summaries.append(new_summary)
        self._write_json(self.summaries_file, summaries)
        
        return new_summary
    
    def get_user_summaries(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all summaries for a specific user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of summary dictionaries
        """
        summaries = self._read_json(self.summaries_file)
        
        user_summaries = [s for s in summaries if s['user_id'] == user_id]
        
        # Sort by creation date (newest first)
        user_summaries.sort(key=lambda x: x['created_at'], reverse=True)
        
        return user_summaries
    
    def get_summary_by_id(self, summary_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific summary by ID
        
        Args:
            summary_id: ID of the summary
            
        Returns:
            Summary dictionary if found, None otherwise
        """
        summaries = self._read_json(self.summaries_file)
        
        for summary in summaries:
            if summary['id'] == summary_id:
                return summary
        
        return None


# Create global database instance
db = JSONDatabase()