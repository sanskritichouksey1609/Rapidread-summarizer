import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, parse_qs

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False


def fetch_transcript_sync(video_url: str) -> str:
    if not YOUTUBE_API_AVAILABLE:
        return "Error: YouTube Transcript API not installed. Please install with: pip install youtube-transcript-api"
    
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return "Error: Could not extract video ID from URL"
        
        # Create YouTube Transcript API instance
        ytt_api = YouTubeTranscriptApi()
        
        # Try to get transcript in different languages (preference order)
        language_codes = ['en', 'en-US', 'en-GB', 'en-CA', 'en-AU']
        transcript_data = None
        used_language = None
        transcript_type = "Unknown"
        
        # Try each language code
        for lang_code in language_codes:
            try:
                fetched_transcript = ytt_api.fetch(video_id, languages=[lang_code])
                transcript_data = fetched_transcript.snippets
                used_language = fetched_transcript.language_code
                transcript_type = "Auto-generated" if fetched_transcript.is_generated else "Manual"
                break
            except Exception:
                continue
        
        # If no specific language worked, try auto-detection
        if not transcript_data:
            try:
                fetched_transcript = ytt_api.fetch(video_id)
                transcript_data = fetched_transcript.snippets
                used_language = fetched_transcript.language_code
                transcript_type = "Auto-generated" if fetched_transcript.is_generated else "Manual"
            except Exception as e:
                return f"Error: Could not fetch transcript for video {video_id}. The video may not have captions enabled or may be private/restricted. Details: {str(e)}"
        
        if not transcript_data:
            return "Error: No transcript available for this video. The video may not have captions enabled."
        
        # Convert snippets to readable text
        try:
            # Extract text from transcript snippets
            transcript_texts = [snippet.text for snippet in transcript_data if hasattr(snippet, 'text')]
            formatted_transcript = " ".join(transcript_texts)
        except Exception:
            # Fallback: try to convert to string
            formatted_transcript = str(transcript_data)
        
        # Clean up the transcript
        cleaned_transcript = clean_transcript_text(formatted_transcript)
        
        # Limit transcript length for API efficiency
        if len(cleaned_transcript) > 15000:
            cleaned_transcript = cleaned_transcript[:15000] + "..."
        
        return cleaned_transcript
        
    except Exception as e:
        error_msg = f"Error fetching YouTube transcript: {str(e)}"
        return error_msg


def clean_transcript_text(transcript: str) -> str:
    if not transcript:
        return ""
    
    try:
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', transcript)
        
        # Remove common transcript artifacts
        cleaned = re.sub(r'\[.*?\]', '', cleaned)  # Remove [Music], [Applause], etc.
        cleaned = re.sub(r'\(.*?\)', '', cleaned)  # Remove (inaudible), etc.
        
        # Fix common punctuation issues
        cleaned = re.sub(r'\s+([,.!?])', r'\1', cleaned)  # Remove space before punctuation
        cleaned = re.sub(r'([.!?])\s*([a-z])', r'\1 \2', cleaned)  # Ensure space after sentence end
        
        # Capitalize first letter of sentences
        sentences = re.split(r'([.!?]\s+)', cleaned)
        capitalized_sentences = []
        for i, sentence in enumerate(sentences):
            if i % 2 == 0 and sentence.strip():  # Only process actual sentences, not delimiters
                sentence = sentence.strip()
                if sentence:
                    sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
            capitalized_sentences.append(sentence)
        
        cleaned = ''.join(capitalized_sentences)
        
        cleaned = cleaned.strip()
        
        return cleaned
        
    except Exception:
        return transcript


def extract_video_id(video_url: str) -> Optional[str]:
    if not video_url:
        return None
    
    try:
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                video_id = match.group(1)
                # Clean up video ID (remove any additional parameters)
                video_id = video_id.split('&')[0].split('?')[0].split('#')[0]
                return video_id
        
        parsed_url = urlparse(video_url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'm.youtube.com']:
            if parsed_url.path == '/watch':
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    return query_params['v'][0]
        elif parsed_url.hostname in ['youtu.be']:
            return parsed_url.path.lstrip('/')
        
        return None
        
    except Exception:
        return None


def get_video_info(video_url: str) -> Dict[str, Any]:
    try:
        # Check if YouTube API is available
        if not YOUTUBE_API_AVAILABLE:
            return {
                "success": False,
                "error": "YouTube Transcript API not available. Please install with: pip install youtube-transcript-api",
                "transcript": "",
                "video_id": "",
                "language": "Unknown",
                "transcript_type": "Unknown",
                "transcript_length": 0,
                "available_languages": []
            }
        
        video_id = extract_video_id(video_url)
        
        if not video_id:
            return {
                "success": False,
                "error": "Could not extract video ID from URL",
                "transcript": "",
                "video_id": "",
                "language": "Unknown",
                "transcript_type": "Unknown",
                "transcript_length": 0,
                "available_languages": []
            }
        
        transcript = fetch_transcript_sync(video_url)
        
        if transcript.startswith("Error:"):
            return {
                "success": False,
                "error": transcript,
                "transcript": "",
                "video_id": video_id,
                "language": "Unknown",
                "transcript_type": "Unknown",
                "transcript_length": 0,
                "available_languages": []
            }
        
        metadata = get_video_metadata(video_id)
        
        return {
            "success": True,
            "transcript": transcript,
            "video_id": video_id,
            "language": metadata.get("language", "Unknown"),
            "transcript_type": metadata.get("transcript_type", "Unknown"),
            "transcript_length": len(transcript),
            "available_languages": metadata.get("available_languages", [])
        }
        
    except Exception as e:
        error_msg = f"Failed to process YouTube video: {str(e)}"
        return {
            "success": False,
            "error": error_msg,
            "transcript": "",
            "video_id": "",
            "language": "Unknown",
            "transcript_type": "Unknown",
            "transcript_length": 0,
            "available_languages": []
        }


def get_video_metadata(video_id: str) -> Dict[str, Any]:
    if not YOUTUBE_API_AVAILABLE:
        return {
            "language": "Unknown",
            "transcript_type": "Unknown",
            "available_languages": []
        }
    
    try:
        ytt_api = YouTubeTranscriptApi()
        
        try:
            transcript_list = ytt_api.list(video_id)
            
            available_languages = []
            primary_language = "Unknown"
            transcript_type = "Unknown"
            
            for transcript in transcript_list:
                lang_info = {
                    "language": transcript.language,
                    "language_code": transcript.language_code,
                    "is_generated": transcript.is_generated
                }
                available_languages.append(lang_info)
                
                if primary_language == "Unknown":
                    primary_language = transcript.language_code
                    transcript_type = "Auto-generated" if transcript.is_generated else "Manual"
            
            return {
                "language": primary_language,
                "transcript_type": transcript_type,
                "available_languages": available_languages
            }
            
        except Exception:
            try:
                fetched_transcript = ytt_api.fetch(video_id)
                return {
                    "language": fetched_transcript.language_code,
                    "transcript_type": "Auto-generated" if fetched_transcript.is_generated else "Manual",
                    "available_languages": [{"language": fetched_transcript.language, "language_code": fetched_transcript.language_code, "is_generated": fetched_transcript.is_generated}]
                }
            except Exception:
                return {
                    "language": "Unknown",
                    "transcript_type": "Unknown",
                    "available_languages": []
                }
        
    except Exception:
        return {
            "language": "Unknown",
            "transcript_type": "Unknown",
            "available_languages": []
        }


def get_available_languages(video_id: str) -> List[Dict[str, Any]]:
    if not YOUTUBE_API_AVAILABLE:
        return []
    
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        available_languages = []
        for transcript in transcript_list:
            lang_info = {
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable if hasattr(transcript, 'is_translatable') else False
            }
            available_languages.append(lang_info)
        
        return available_languages
        
    except Exception:
        available_languages = []
        common_languages = ['en', 'en-US', 'en-GB']
        
        ytt_api = YouTubeTranscriptApi()
        for lang_code in common_languages:
            try:
                fetched_transcript = ytt_api.fetch(video_id, languages=[lang_code])
                lang_info = {
                    "language": fetched_transcript.language,
                    "language_code": fetched_transcript.language_code,
                    "is_generated": fetched_transcript.is_generated,
                    "is_translatable": False
                }
                available_languages.append(lang_info)
                break  # If one works, we have at least one language
            except Exception:
                continue
        
        return available_languages


# Legacy function for backward compatibility
def get_youtube_transcript(video_url: str) -> str:
    return fetch_transcript_sync(video_url)