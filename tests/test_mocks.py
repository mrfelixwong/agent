"""
Mock implementations for testing
These should only be imported in test files, not in production code
"""

from datetime import datetime
from typing import Optional, Callable, List, Dict, Any


class MockAudioRecorder:
    """Mock audio recorder for testing without actual microphone access"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self._simulate_error = False
        self._error_callback = None
        self._mock_duration = 5.0  # Default mock recording duration
        self._recording_start_time = None
        
    def set_simulate_error(self, should_error: bool):
        self._simulate_error = should_error
    
    def set_mock_duration(self, duration: float):
        self._mock_duration = duration
    
    def set_error_callback(self, callback: Callable[[Exception], None]):
        self._error_callback = callback
    
    def start_recording(self, output_path: str) -> bool:
        if self._simulate_error:
            if self._error_callback:
                self._error_callback(Exception("Mock recording error"))
            return False
        
        self.is_recording = True
        self._recording_start_time = datetime.now()
        return True
    
    def stop_recording(self) -> Optional[str]:
        if not self.is_recording:
            return None
        
        self.is_recording = False
        # Return a fake path that would have been created
        return "mock_recording.wav"
    
    def get_volume_level(self) -> float:
        return 0.5 if self.is_recording else 0.0
    
    def is_silence(self) -> bool:
        return False


class MockSummarizer:
    """Mock summarizer for testing without OpenAI API calls"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or "mock-api-key"
        self.model = model
        self._simulate_error = False
        self._mock_summary = None
        self._mock_daily_summary = None
        
    def set_simulate_error(self, should_error: bool):
        self._simulate_error = should_error
    
    def set_mock_summary(self, summary: Dict[str, Any]):
        self._mock_summary = summary
    
    def set_mock_daily_summary(self, daily_summary: Dict[str, Any]):
        self._mock_daily_summary = daily_summary
    
    def summarize_transcript(
        self, 
        transcript: str, 
        meeting_name: str,
        duration_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        if self._simulate_error:
            raise Exception("Mock summarization error")
        
        if self._mock_summary:
            return self._mock_summary
        
        # Default mock summary
        return {
            "meeting_name": meeting_name,
            "duration_minutes": duration_minutes or 30,
            "executive_summary": f"Mock executive summary for {meeting_name}",
            "key_points": [
                "Mock key point 1",
                "Mock key point 2",
                "Mock key point 3"
            ],
            "action_items": [
                {
                    "task": "Mock action item 1",
                    "assignee": "Team Member A",
                    "deadline": "Next week",
                    "priority": "high"
                },
                {
                    "task": "Mock action item 2", 
                    "assignee": "Team Member B",
                    "deadline": "This month",
                    "priority": "medium"
                }
            ],
            "decisions_made": [
                "Mock decision 1",
                "Mock decision 2"
            ],
            "next_steps": [
                "Mock next step 1",
                "Mock next step 2"
            ]
        }
    
    def summarize_daily_meetings(self, meetings: List[Dict[str, Any]], date: Optional[str] = None) -> Dict[str, Any]:
        if self._simulate_error:
            raise Exception("Mock daily summary error")
        
        if self._mock_daily_summary:
            return self._mock_daily_summary
        
        # Default mock daily summary
        total_duration = sum(m.get('duration_minutes', 0) for m in meetings)
        all_action_items = []
        
        for i, meeting in enumerate(meetings):
            all_action_items.extend([
                {
                    "task": f"Action from {meeting.get('name', f'Meeting {i+1}')}",
                    "assignee": "Team",
                    "deadline": "TBD",
                    "priority": "medium"
                }
            ])
        
        return {
            "date": date or datetime.now().strftime('%Y-%m-%d'),
            "total_meetings": len(meetings),
            "total_duration": total_duration,
            "daily_summary": f"Mock daily summary for {len(meetings)} meetings",
            "key_themes": [
                "Mock theme 1",
                "Mock theme 2"
            ],
            "meeting_titles": [m.get('name', f'Meeting {i+1}') for i, m in enumerate(meetings)],
            "all_action_items": all_action_items
        }


class MockEmailSender:
    """Mock email sender for testing without actual email sending"""
    
    def __init__(self, **kwargs):
        self.smtp_server = kwargs.get('smtp_server', 'mock.smtp.server')
        self.smtp_port = kwargs.get('smtp_port', 587)
        self.email_address = kwargs.get('email_address', 'test@example.com')
        self.email_password = kwargs.get('email_password', 'mock_password')
        self._simulate_error = False
        self._sent_emails = []
        
    def set_simulate_error(self, should_error: bool):
        self._simulate_error = should_error
    
    def get_sent_emails(self) -> List[Dict[str, Any]]:
        return self._sent_emails.copy()
    
    def clear_sent_emails(self):
        self._sent_emails.clear()
    
    def send_meeting_summary(self, summary: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        if self._simulate_error:
            return False
        
        recipient = recipient or self.email_address
        email_record = {
            'type': 'meeting_summary',
            'recipient': recipient,
            'subject': f"Meeting Summary: {summary.get('meeting_name', 'Unknown')}",
            'meeting_name': summary.get('meeting_name'),
            'sent_at': datetime.now().isoformat()
        }
        self._sent_emails.append(email_record)
        return True
    
    def send_daily_summary(self, daily_summary: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        if self._simulate_error:
            return False
        
        recipient = recipient or self.email_address
        email_record = {
            'type': 'daily_summary',
            'recipient': recipient,
            'subject': f"Daily Summary - {daily_summary.get('total_meetings', 0)} meetings",
            'total_meetings': daily_summary.get('total_meetings', 0),
            'sent_at': datetime.now().isoformat()
        }
        self._sent_emails.append(email_record)
        return True
    
    def send_custom_email(self, recipient: str, subject: str, content: str, is_html: bool = False) -> bool:
        if self._simulate_error:
            return False
        
        email_record = {
            'type': 'custom',
            'recipient': recipient,
            'subject': subject,
            'content_length': len(content),
            'is_html': is_html,
            'sent_at': datetime.now().isoformat()
        }
        self._sent_emails.append(email_record)
        return True
    
    def test_connection(self) -> bool:
        return not self._simulate_error