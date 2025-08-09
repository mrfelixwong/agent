"""
Helper utilities for Meeting Agent
"""

import re
import os
import json
from datetime import datetime, timedelta
from typing import Union, Optional, Dict, Any, List


def format_duration(seconds: Union[int, float]) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "1h 23m 45s")
    """
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return "0s"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:  # Always show seconds if nothing else
        parts.append(f"{secs}s")
        
    return " ".join(parts)


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Convert string to safe filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Safe filename string
    """
    if not filename:
        return "unnamed"
    
    # Remove or replace invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores and trim
    safe = re.sub(r'_+', '_', safe).strip('_')
    
    # Ensure not empty
    if not safe:
        safe = "unnamed"
    
    # Truncate if too long
    if len(safe) > max_length:
        safe = safe[:max_length].rstrip('_')
    
    return safe


def parse_time_string(time_str: str) -> Optional[datetime]:
    """
    Parse time string in HH:MM format to datetime object for today
    
    Args:
        time_str: Time string in HH:MM format (e.g., "22:00")
        
    Returns:
        datetime object for today at specified time, or None if invalid
    """
    try:
        time_parts = time_str.split(':')
        if len(time_parts) != 2:
            return None
            
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None
            
        now = datetime.now()
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
    except (ValueError, AttributeError):
        return None


def ensure_directory(path: Union[str, os.PathLike]) -> bool:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        path: Directory path to ensure exists
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text with suffix if needed
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def validate_email(email: str) -> bool:
    """
    Basic email validation
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format appears valid
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def get_file_size(file_path: Union[str, os.PathLike]) -> int:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable string
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size (e.g., "1.2 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(size_bytes)
    
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.1f} {units[i]}"


# Data processing utilities (merged from data_helpers.py)

def parse_meeting_json_fields(meeting_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse JSON fields in meeting dictionary
    
    Handles the common pattern of parsing JSON strings back to Python objects
    for summary and action_items fields.
    
    Args:
        meeting_dict: Dictionary with potentially JSON string fields
        
    Returns:
        Dictionary with parsed JSON fields
    """
    if not meeting_dict:
        return meeting_dict
    
    # Common JSON fields in meeting records
    json_fields = ['summary', 'action_items']
    
    for field in json_fields:
        if meeting_dict.get(field):
            try:
                meeting_dict[field] = json.loads(meeting_dict[field])
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, keep original value
                pass
    
    return meeting_dict

def calculate_meeting_duration(start_time, end_time) -> int:
    """
    Calculate meeting duration in minutes
    
    Args:
        start_time: Meeting start datetime
        end_time: Meeting end datetime
        
    Returns:
        Duration in minutes
    """
    if not start_time or not end_time:
        return 0
    
    duration = end_time - start_time
    return int(duration.total_seconds() / 60)

def extract_action_items_count(summary: Optional[Dict[str, Any]]) -> int:
    """
    Extract action items count from meeting summary
    
    Args:
        summary: Meeting summary dictionary
        
    Returns:
        Number of action items
    """
    if not summary:
        return 0
    
    action_items = summary.get('action_items', [])
    return len(action_items) if action_items else 0