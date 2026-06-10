import re
from typing import Optional


def is_valid_youtube_url(url: str) -> bool:
    """
    Validate if URL is a valid YouTube URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid YouTube URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    youtube_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=[a-zA-Z0-9_-]{11}',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/[a-zA-Z0-9_-]{11}',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/[a-zA-Z0-9_-]{11}',
    ]
    
    for pattern in youtube_patterns:
        if re.search(pattern, url):
            return True
    
    return False


def format_text_for_display(text: str, max_length: int = 500) -> str:
    """
    Format text for display with optional truncation.
    
    Args:
        text: Text to format
        max_length: Maximum length before truncation
        
    Returns:
        Formatted text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Truncate if needed
    if len(text) > max_length:
        return text[:max_length] + "..."
    
    return text


def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing special characters and extra whitespace.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    return text


def get_error_message(error_type: str) -> str:
    """
    Get user-friendly error message based on error type.
    
    Args:
        error_type: Type of error
        
    Returns:
        User-friendly error message
    """
    error_messages = {
        "invalid_url": "Please enter a valid YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)",
        "empty_url": "Please enter a YouTube URL",
        "empty_question": "Please enter a question",
        "ollama_not_running": "Ollama server is not running. Please start Ollama and try again.",
        "model_not_found": "Model not found in Ollama. Please pull the model and try again.",
        "transcripts_disabled": "The video does not have transcripts available. Please try another video.",
        "no_transcript": "No transcript found for this video. Please try another video.",
        "network_error": "Network error occurred. Please check your connection and try again.",
        "unknown_error": "An unexpected error occurred. Please try again.",
    }
    
    return error_messages.get(error_type, error_messages["unknown_error"])


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count
        
    Returns:
        Word count
    """
    if not text:
        return 0
    
    return len(text.split())


def calculate_reading_time(text: str, words_per_minute: int = 200) -> str:
    """
    Calculate estimated reading time for text.
    
    Args:
        text: Text to calculate for
        words_per_minute: Average reading speed
        
    Returns:
        Formatted reading time string
    """
    word_count = count_words(text)
    minutes = max(1, round(word_count / words_per_minute))
    
    if minutes == 1:
        return "1 minute"
    return f"{minutes} minutes"
