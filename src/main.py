"""Meeting Agent Main Application - Orchestrates all components"""

from datetime import datetime, date
from typing import Dict, Any, Optional, List
from pathlib import Path

from .utils.logger import setup_logger
from .utils.config import load_config, get_config_value
from .utils.helpers import ensure_directory
from .database.database import Database
from .audio.recorder import AudioRecorder
from .transcription.simple_transcriber import SimpleTranscriber
from .ai.summarizer import Summarizer
from .notifications.sender import EmailSender

logger = setup_logger(__name__)

class MeetingAgent:
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = load_config(config_path, validate_secrets=True)
        self.current_meeting: Optional[Dict] = None
        self._init_components()
    def _init_components(self):
        db_path = get_config_value(self.config, 'database.path', 'data/meetings.db')
        self.db = Database(db_path)
        self.audio_recorder = AudioRecorder(
            sample_rate=get_config_value(self.config, 'audio.sample_rate', 44100),
            channels=get_config_value(self.config, 'audio.channels', 1),
            chunk_size=get_config_value(self.config, 'audio.chunk_size', 1024)
        )
        self.transcriber = SimpleTranscriber(
            api_key=get_config_value(self.config, 'openai.api_key'),
            model=get_config_value(self.config, 'openai.transcription_model', 'whisper-1')
        )
        self.summarizer = Summarizer(
            api_key=get_config_value(self.config, 'openai.api_key'),
            model=get_config_value(self.config, 'openai.summarization_model', 'gpt-4')
        )
        email_address = get_config_value(self.config, 'email.address')
        email_password = get_config_value(self.config, 'email.password')
        
        if email_address and email_password:
            self.email_sender = EmailSender(
                email_address=email_address,
                email_password=email_password,
                smtp_server=get_config_value(self.config, 'email.smtp_server', 'smtp.gmail.com'),
                smtp_port=get_config_value(self.config, 'email.smtp_port', 587)
            )
        else:
            self.email_sender = None
            logger.warning("Email credentials not configured - email features will be disabled")
        self.audio_recorder.set_chunk_callback(
            lambda audio_data: self.transcriber.add_audio_chunk(audio_data) 
            if self.current_meeting and self.transcriber.is_transcribing else None
        )
    
    def start_meeting(self, meeting_name: str) -> Dict[str, Any]:
        if self.current_meeting:
            raise ValueError("A meeting is already being recorded")
        
        start_time = datetime.now()
        recordings_dir = Path("data/recordings")
        ensure_directory(recordings_dir)
        meeting_id = self.db.save_meeting(
            name=meeting_name,
            start_time=start_time
        )
        audio_filename = f"meeting_{meeting_id}_{start_time.strftime('%Y%m%d_%H%M%S')}.wav"
        audio_file_path = recordings_dir / audio_filename
        if not self.audio_recorder.start_recording(str(audio_file_path)):
            raise RuntimeError("Failed to start audio recording")
        if not self.transcriber.start_transcription():
            self.audio_recorder.stop_recording()
            raise RuntimeError("Failed to start transcription")
        self.current_meeting = {
            'id': meeting_id,
            'name': meeting_name,
            'start_time': start_time,
            'audio_file_path': str(audio_file_path),
            'status': 'recording'
        }
        
        return self.current_meeting.copy()
    
    def stop_meeting(self) -> Dict[str, Any]:
        if not self.current_meeting:
            raise ValueError("No meeting is currently being recorded")
        
        meeting_id = self.current_meeting['id']
        self.audio_recorder.stop_recording()
        final_transcript = self.transcriber.stop_transcription()
        end_time = datetime.now()
        duration_seconds = (end_time - self.current_meeting['start_time']).total_seconds()
        duration_minutes = int(duration_seconds / 60)
        self.db.update_meeting_duration(meeting_id, end_time, duration_minutes, duration_seconds)
        self.db.update_meeting_transcript(meeting_id, final_transcript)
        
        try:
            summary = self.summarizer.summarize_transcript(
                transcript=final_transcript,
                meeting_name=meeting_name,
                duration_minutes=duration_minutes
            )
            self.db.update_meeting_summary(meeting_id, summary)
            if self.email_sender:
                self.email_sender.send_meeting_summary(summary)
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            summary = {}
        completed_meeting = {
            'id': meeting_id,
            'name': self.current_meeting['name'],
            'start_time': self.current_meeting['start_time'],
            'end_time': end_time,
            'duration_seconds': duration_seconds,
            'duration_minutes': duration_minutes,
            'transcript': final_transcript,
            'summary': summary,
            'status': 'completed',
            'audio_file_path': self.current_meeting['audio_file_path']
        }
        self.current_meeting = None
        return completed_meeting
    
    def get_meeting_status(self) -> Dict[str, Any]:
        if not self.current_meeting:
            return {'status': 'idle'}
        current_time = datetime.now()
        duration = (current_time - self.current_meeting['start_time']).total_seconds()
        
        return {
            'status': 'recording',
            'meeting': self.current_meeting,
            'duration_seconds': duration,
            'duration_minutes': int(duration / 60)
        }
    
    def get_meeting_history(self, days_back: int = 30) -> List[Dict[str, Any]]:
        return self.db.get_meetings_by_date_range(days_back)
    
    def get_meeting_details(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        return self.db.get_meeting(meeting_id)
    
    def generate_daily_summary(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        if target_date is None:
            target_date = date.today()
        meetings = self.db.get_meetings_by_date(target_date)
        
        if not meetings:
            return {
                'date': target_date.isoformat(),
                'total_meetings': 0,
                'daily_summary': 'No meetings recorded for this date.'
            }
        
        try:
            daily_summary = self.summarizer.summarize_daily_meetings(meetings, target_date.isoformat())
            self.db.save_daily_summary(
                date=target_date,
                total_meetings=daily_summary['total_meetings'],
                summary=daily_summary['daily_summary'],
                key_themes=daily_summary.get('key_themes', [])
            )
            
            return daily_summary
        except Exception as e:
            logger.error(f"Failed to generate daily summary: {e}")
            return {
                'date': target_date.isoformat(),
                'total_meetings': len(meetings),
                'daily_summary': 'Failed to generate summary.',
                'error': str(e)
            }
    
    def cleanup(self):
        self.audio_recorder.cleanup()
        self.transcriber.cleanup()
        self.db.close()
