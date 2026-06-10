#!/usr/bin/env python3
"""
Test script for YouTube Chatbot - Tests transcript fetching with youtube-transcript-api==0.6.2
"""

from youtube_transcript_api import YouTubeTranscriptApi
from chatbot import extract_video_id, get_transcript


def test_video_id_extraction():
    """Test video ID extraction from various URL formats"""
    test_urls = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/_8H2n0nDfd4?si=DqvZ", "_8H2n0nDfd4"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s", "dQw4w9WgXcQ"),
    ]
    
    print("Testing video ID extraction...")
    for url, expected_id in test_urls:
        result = extract_video_id(url)
        status = "✅" if result == expected_id else "❌"
        print(f"{status} {url[:50]}... -> {result}")
    print()


def test_transcript_api():
    """Test new YouTubeTranscriptApi v1.2.4 API"""
    print("Testing YouTubeTranscriptApi v1.2.4...")
    
    # Test video ID
    test_video_id = "dQw4w9WgXcQ"
    
    try:
        print(f"Fetching transcript for video: {test_video_id}")
        transcript = YouTubeTranscriptApi.get_transcript(test_video_id)
        print(f"✅ Transcript fetched successfully")
        print(f"   Items returned: {len(transcript)}")
        if transcript:
            print(f"   First item: {transcript[0]}")
            text = " ".join([entry["text"] for entry in transcript])
            print(f"   Combined text length: {len(text)} characters")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()


def test_get_transcript_function():
    """Test the chatbot get_transcript function"""
    print("Testing chatbot.get_transcript()...")
    
    test_cases = [
        ("dQw4w9WgXcQ", "Rick Astley video"),
        ("invalid_id_12345", "Invalid ID"),
    ]
    
    for video_id, description in test_cases:
        try:
            print(f"Testing: {description} ({video_id})")
            transcript = get_transcript(video_id)
            print(f"✅ Success - Transcript length: {len(transcript)} chars")
        except ValueError as e:
            print(f"⚠️  ValueError: {str(e)}")
        except ConnectionError as e:
            print(f"⚠️  ConnectionError: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
    print()


def test_transcript(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print(transcript[:5])


if __name__ == "__main__":
    print("=" * 60)
    print("YouTube Chatbot - API Tests")
    print("=" * 60)
    print()
    
    test_video_id_extraction()
    test_transcript_api()
    test_get_transcript_function()
    
    print("=" * 60)
    print("Tests completed!")
    print("=" * 60)
