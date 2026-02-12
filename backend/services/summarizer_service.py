"""
Summarizer Service

This service handles all AI-powered text summarization using Google Gemini.
It provides a clean interface for generating summaries from different types of content.
"""

from google import genai
from google.genai.types import GenerateContentConfig
import os
from typing import Optional


class SummarizerService:
    """
    Service class for AI-powered text summarization using Google Gemini
    """
    
    def __init__(self):
        """
        Initialize the Gemini summarizer service
        """
        # Get API key from environment
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize the client with API key
        self.client = genai.Client(api_key=self.api_key)
        
        # Get model name from environment or use default
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    def summarize_text(self, text: str, content_type: str = "text", max_sentences: int = 5) -> str:
        """
        Generate a comprehensive summary using Gemini AI
        
        Args:
            text: The content to summarize
            content_type: Type of content (text, article, youtube, github, pdf)
            max_sentences: Maximum number of sentences in summary (deprecated, kept for compatibility)
            
        Returns:
            Generated summary string (300-500 words)
        """
        try:
            if not text or not text.strip():
                return "No content available to summarize."
            
            # Limit input text length to avoid token limits (keep last 15000 chars for better context)
            if len(text) > 15000:
                text = "..." + text[-15000:]
            
            # Create appropriate prompt based on content type
            prompt = self._create_prompt(text, content_type)
            
            # Configure generation parameters for complete summaries
            config = GenerateContentConfig(
                temperature=0.3,  # Lower temperature for more consistent output
                max_output_tokens=3000,  # Increased significantly to prevent truncation
                top_p=0.8,
                top_k=40,
                stop_sequences=None  # Don't use stop sequences that might truncate
            )
            
            # Generate summary using Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            # Extract and validate the summary
            if response and response.text:
                summary = response.text.strip()
                
                # Check if summary appears to be truncated (ends abruptly)
                if self._is_summary_truncated(summary):
                    # Try with a more explicit completion request
                    completion_prompt = f"""
{prompt}

CRITICAL INSTRUCTIONS:
1. Provide a COMPLETE summary that ends with a proper conclusion
2. Ensure the summary is 300-500 words long
3. End with a complete sentence and proper punctuation
4. Do not cut off mid-sentence or mid-thought
5. Include a clear concluding statement

Please generate the complete summary now:
"""
                    
                    # Try again with higher token limit
                    extended_config = GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=4000,  # Even higher limit
                        top_p=0.8,
                        top_k=40
                    )
                    
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=completion_prompt,
                        config=extended_config
                    )
                    
                    if response and response.text:
                        summary = response.text.strip()
                
                # Ensure summary ends properly
                if summary and not summary.endswith(('.', '!', '?')):
                    # Find the last complete sentence
                    sentences = summary.split('.')
                    if len(sentences) > 1:
                        # Keep all complete sentences
                        complete_summary = '.'.join(sentences[:-1]) + '.'
                        return complete_summary
                
                return summary if summary else "Unable to generate complete summary."
            else:
                return "Unable to generate summary - no response from AI service."
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def _is_summary_truncated(self, summary: str) -> bool:
        """
        Check if a summary appears to be truncated
        
        Args:
            summary: The summary text to check
            
        Returns:
            True if summary appears truncated, False otherwise
        """
        if not summary:
            return True
        
        # Check if summary ends abruptly (common signs of truncation)
        truncation_indicators = [
            # Ends without proper punctuation
            not summary.strip().endswith(('.', '!', '?')),
            # Ends with incomplete words or phrases
            summary.strip().endswith((',', ';', ':', 'and', 'or', 'but', 'the', 'a', 'an')),
            # Very short summary (likely cut off)
            len(summary.split()) < 30,
            # Ends with "ultimately" or similar transition words without completion
            any(summary.strip().endswith(word) for word in ['ultimately', 'therefore', 'however', 'moreover', 'furthermore', 'additionally', 'consequently'])
        ]
        
        return any(truncation_indicators)
    
    def _create_prompt(self, content: str, content_type: str) -> str:
        """
        Create an appropriate prompt for different content types
        
        Args:
            content: The content to summarize
            content_type: Type of content
            
        Returns:
            Formatted prompt string
        """
        base_instruction = """Please provide a comprehensive, detailed summary of the following content. 

IMPORTANT REQUIREMENTS:
- The summary must be approximately 300-500 words
- Provide a COMPLETE summary that ends with a proper conclusion
- End with a complete sentence and proper punctuation
- Do not cut off mid-sentence or leave thoughts incomplete
- Cover all important aspects thoroughly
- Write in clear, flowing paragraphs"""
        
        if content_type == "article":
            prompt = f"""
{base_instruction}

Article Content:
{content}

Please create a detailed summary (300-500 words) of this article that includes:

1. **Main Topic & Context**: What is the article about and why is it important?
2. **Key Points & Arguments**: What are the main ideas, findings, or arguments presented?
3. **Supporting Details**: Important facts, statistics, examples, or evidence mentioned
4. **Implications & Impact**: What are the broader implications or potential impact?
5. **Conclusions & Takeaways**: What are the main conclusions and key takeaways for readers?

Write the summary in clear, flowing paragraphs that provide a comprehensive understanding of the article's content. Make it informative and engaging for someone who hasn't read the original article.

ENSURE THE SUMMARY IS COMPLETE AND ENDS WITH A PROPER CONCLUSION.

Summary:
"""
        
        elif content_type == "youtube":
            prompt = f"""
{base_instruction}

YouTube Video Transcript:
{content}

Please create a detailed summary (300-500 words) of this video content that includes:

1. **Video Overview**: What is the main topic and purpose of the video?
2. **Key Content**: What are the main points, lessons, or information shared?
3. **Important Details**: Specific examples, demonstrations, or explanations provided
4. **Insights & Analysis**: Any analysis, opinions, or insights offered by the creator
5. **Practical Value**: What can viewers learn or apply from this content?

Write the summary in clear, engaging paragraphs that capture the essence of the video content. Make it comprehensive enough that someone could understand the main value without watching the video.

ENSURE THE SUMMARY IS COMPLETE AND ENDS WITH A PROPER CONCLUSION.

Summary:
"""
        
        elif content_type == "github":
            prompt = f"""
{base_instruction}

GitHub Repository Information:
{content}

Please create a detailed summary (300-500 words) of this repository that includes:

1. **Project Overview**: What does this project do and what problem does it solve?
2. **Technical Details**: What technologies, frameworks, or languages are used?
3. **Features & Functionality**: What are the main features and capabilities?
4. **Architecture & Structure**: How is the project organized and structured?
5. **Usage & Getting Started**: How can developers use, install, or contribute to this project?

Write the summary in clear paragraphs that would help a developer understand whether this project is relevant to their needs and how they might use it.

ENSURE THE SUMMARY IS COMPLETE AND ENDS WITH A PROPER CONCLUSION.

Summary:
"""
        
        elif content_type == "pdf":
            prompt = f"""
{base_instruction}

PDF Document Content:
{content}

Please create a detailed summary (300-500 words) of this document that includes:

1. **Document Purpose**: What is the main purpose and scope of this document?
2. **Key Sections**: What are the main sections or chapters and their focus?
3. **Important Information**: Key facts, findings, data, or insights presented
4. **Methodology & Approach**: Any methods, processes, or approaches described
5. **Conclusions & Recommendations**: Main conclusions, recommendations, or outcomes

Write the summary in clear, informative paragraphs that provide a comprehensive overview of the document's content and value.

ENSURE THE SUMMARY IS COMPLETE AND ENDS WITH A PROPER CONCLUSION.

Summary:
"""
        
        else:  # Default text summarization
            prompt = f"""
{base_instruction}

Content:
{content}

Please create a detailed summary (300-500 words) that includes:

1. **Main Topic**: What is the primary subject or theme?
2. **Key Information**: What are the most important points or details?
3. **Supporting Details**: Relevant examples, evidence, or explanations
4. **Context & Significance**: Why is this information important or relevant?
5. **Key Takeaways**: What should readers remember or understand from this content?

Write the summary in clear, comprehensive paragraphs that thoroughly cover the content while remaining engaging and informative.

ENSURE THE SUMMARY IS COMPLETE AND ENDS WITH A PROPER CONCLUSION.

Summary:
"""
        
        return prompt
    
    def test_connection(self) -> dict:
        """
        Test the connection to Gemini API and check model capabilities
        
        Returns:
            Dictionary with connection test results
        """
        try:
            # Test with a simple prompt that should generate a complete response
            test_prompt = """Please write a complete 200-word summary about the importance of APIs in modern software development. 
            Make sure to end with a proper conclusion and complete sentence."""
            
            config = GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1000
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=test_prompt,
                config=config
            )
            
            if response and response.text:
                response_text = response.text.strip()
                word_count = len(response_text.split())
                is_complete = response_text.endswith(('.', '!', '?'))
                
                return {
                    "success": True,
                    "message": "Gemini API connection successful",
                    "model": self.model_name,
                    "response_length": word_count,
                    "response_complete": is_complete,
                    "sample_response": response_text[:100] + "..." if len(response_text) > 100 else response_text
                }
            else:
                return {
                    "success": False,
                    "message": "No response from Gemini API",
                    "model": self.model_name
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Gemini API connection failed: {str(e)}",
                "model": self.model_name
            }


# Create global summarizer service instance
try:
    summarizer_service = SummarizerService()
except ValueError:
    summarizer_service = None


# Legacy function for backward compatibility
def summarize_text(text: str, max_sentences: int = 5) -> str:
    """
    Legacy function for backward compatibility
    
    Args:
        text: Text to summarize
        max_sentences: Maximum sentences (deprecated, now generates 300-500 word summaries)
        
    Returns:
        Generated comprehensive summary (300-500 words)
    """
    if summarizer_service:
        return summarizer_service.summarize_text(text, "text")
    else:
        # Fallback to simple summarization if Gemini is not available
        if not text:
            return ""
        
        # For fallback, try to create a longer summary by taking more content
        sentences = text.split('.')
        # Take more sentences for a longer fallback summary
        longer_summary = '.'.join(s.strip() for s in sentences[:max_sentences * 3] if s.strip())
        
        if longer_summary:
            longer_summary += '.'
            # Add a note about the fallback
            if len(longer_summary) < 200:
                longer_summary += " (Note: This is a basic text extraction as AI summarization is not available.)"
        
        return longer_summary