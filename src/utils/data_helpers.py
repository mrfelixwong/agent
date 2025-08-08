"""
Data processing utilities for Meeting Agent
Common patterns for JSON parsing, meeting data processing, etc.
"""

import json
from typing import Dict, Any, List, Optional

def parse_meeting_json_fields(meeting_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse JSON fields in meeting dictionary
    
    Handles the common pattern of parsing JSON strings back to Python objects
    for participants, summary, and action_items fields.
    
    Args:
        meeting_dict: Dictionary with potentially JSON string fields
        
    Returns:
        Dictionary with parsed JSON fields
    """
    if not meeting_dict:
        return meeting_dict
    
    # Common JSON fields in meeting records
    json_fields = ['participants', 'summary', 'action_items']
    
    for field in json_fields:
        if meeting_dict.get(field):
            try:
                meeting_dict[field] = json.loads(meeting_dict[field])
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, keep original value
                pass
    
    return meeting_dict

def format_meeting_participants(participants: Optional[List[str]]) -> str:
    """
    Format participants list for display
    
    Args:
        participants: List of participant names
        
    Returns:
        Formatted string of participants
    """
    if not participants:
        return "No participants listed"
    return ", ".join(participants)

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