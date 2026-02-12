"""
PDF Service

This service handles PDF document processing and text extraction.
It extracts readable text content from PDF files for summarization.
"""

import PyPDF2
from io import BytesIO
from typing import Dict, Any
import os


def extract_text_from_pdf(path: str) -> str:
    """
    Extract text from PDF file at given path
    
    Args:
        path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        with open(path, 'rb') as file:
            pdf_content = file.read()
            return extract_text_from_pdf_bytes(pdf_content)
    except Exception:
        return ""


def extract_text_from_pdf_bytes(pdf_content: bytes) -> str:
    """
    Extract text content from PDF bytes
    
    Args:
        pdf_content: PDF file content as bytes
        
    Returns:
        Extracted text content
    """
    try:
        # Create a BytesIO object from the PDF content
        pdf_file = BytesIO(pdf_content)
        
        # Create PDF reader
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"
        
        # Clean up the text
        text_content = clean_pdf_text(text_content)
        
        # Limit content length for API efficiency
        if len(text_content) > 15000:
            text_content = text_content[:15000] + "..."
        
        return text_content
        
    except Exception:
        return ""


def clean_pdf_text(text: str) -> str:
    """
    Clean and normalize text extracted from PDF
    
    Args:
        text: Raw text from PDF extraction
        
    Returns:
        Cleaned text content
    """
    try:
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
        
    except Exception:
        return text


def validate_pdf_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Validate PDF file content and metadata
    
    Args:
        file_content: PDF file content as bytes
        filename: Original filename
        
    Returns:
        Dictionary with validation results
    """
    try:
        # Check file extension
        if not filename.lower().endswith('.pdf'):
            return {
                "valid": False,
                "error": "File must have .pdf extension"
            }
        
        # Check file size (get limit from environment)
        max_size = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
        if len(file_content) > max_size:
            return {
                "valid": False,
                "error": f"File size exceeds {max_size // (1024*1024)}MB limit"
            }
        
        # Try to read PDF structure
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            page_count = len(pdf_reader.pages)
            
            if page_count == 0:
                return {
                    "valid": False,
                    "error": "PDF file appears to be empty"
                }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Invalid PDF file: {str(e)}"
            }
        
        return {
            "valid": True,
            "page_count": page_count,
            "file_size": len(file_content)
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation failed: {str(e)}"
        }


def get_pdf_info(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Get comprehensive PDF information including content and metadata
    
    Args:
        file_content: PDF file content as bytes
        filename: Original filename
        
    Returns:
        Dictionary with PDF information
    """
    try:
        # Validate the PDF first
        validation = validate_pdf_file(file_content, filename)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "content": "",
                "filename": filename
            }
        
        # Extract text content
        text_content = extract_text_from_pdf_bytes(file_content)
        
        if not text_content.strip():
            return {
                "success": False,
                "error": "No text content found in the PDF",
                "content": "",
                "filename": filename
            }
        
        return {
            "success": True,
            "content": text_content,
            "filename": filename,
            "page_count": validation.get("page_count", 0),
            "file_size": validation.get("file_size", 0)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to process PDF: {str(e)}",
            "content": "",
            "filename": filename
        }
