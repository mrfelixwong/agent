"""
Meeting Agent Main Application
Orchestrates all components of the meeting agent system
"""

import os
import threading
import time
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

from .utils.logger import setup_logger
from .utils.config import load_config
from .utils.helpers import ensure_directory
from .database.database import Database
from .audio.recorder import AudioRecorder
from .transcription.transcriber import Transcriber
from .ai.summarizer import Summarizer
from .notifications.sender import EmailSender

logger = setup_logger(__name__)


class MeetingAgent:
    """Main Meeting Agent application orchestrator"""
    
    def __init__(self, config_path: Optional[str] = None, use_mock_components: bool = False):
        """Initialize Meeting Agent with configuration"""
        # Load configuration
        self.config = load_config(config_path, validate_secrets=not use_mock_components)
        
        # State management
        self.is_running = False
        self.current_meeting: Optional[Dict] = None
        self._recording_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.use_mock_components = use_mock_components
        
        # Initialize components
        self._init_components()
        
        logger.info("Meeting Agent initialized successfully")
        
    def _init_components(self):
        """Initialize all system components"""
        logger.info("Initializing Meeting Agent components...")
        
        try:
            if self.use_mock_components:
                logger.info("Using mock components for testing...")
                self._init_mock_components()
            else:
                logger.info("Using real components...")
                self._init_real_components()
            
            # Set up callbacks
            self._setup_callbacks()
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _init_real_components(self):
        """Initialize real components"""
        from .database.database import Database
        from .audio.recorder import AudioRecorder
        from .transcription.transcriber import Transcriber
        from .ai.summarizer import Summarizer
        from .notifications.sender import EmailSender
        
        # Database
        db_path = self.config.get('database.path', 'data/meetings.db')
        self.db = Database(db_path)
        
        # Audio recording (use mono for better compatibility)
        self.audio_recorder = AudioRecorder(
            sample_rate=self.config.get('audio.sample_rate', 44100),
            channels=self.config.get('audio.channels', 1),  # Use mono by default
            chunk_size=self.config.get('audio.chunk_size', 1024)
        )
        
        # Real-time transcription
        self.transcriber = Transcriber(
            api_key=self.config.get('openai.api_key'),
            model=self.config.get('openai.transcription_model', 'whisper-1'),
            cost_per_minute=self.config.get('cost.whisper_per_minute', 0.006)
        )
        
        # AI summarization
        self.summarizer = Summarizer(
            api_key=self.config.get('openai.api_key'),
            model=self.config.get('openai.summarization_model', 'gpt-4')
        )
        
        # Email notifications (optional - use mock if not configured)
        email_address = self.config.get('email.address')
        email_password = self.config.get('email.password')
        
        if email_address and email_password:
            self.email_sender = EmailSender(
                email_address=email_address,
                email_password=email_password,
                smtp_server=self.config.get('email.smtp_server', 'smtp.gmail.com'),
                smtp_port=self.config.get('email.smtp_port', 587)
            )
            logger.info("Real email sender initialized")
        else:
            # Use mock email sender if not configured
            from .notifications.sender import MockEmailSender
            self.email_sender = MockEmailSender()
            logger.info("Using mock email sender (no email credentials configured)")
    
    def _init_mock_components(self):
        """Initialize mock components for testing"""
        from .database.database import MockDatabase
        from .audio.recorder import MockAudioRecorder
        from .transcription.transcriber import MockTranscriber
        from .ai.summarizer import MockSummarizer
        from .notifications.sender import MockEmailSender
        
        # Mock Database
        self.db = MockDatabase()
        
        # Mock Audio recording
        self.audio_recorder = MockAudioRecorder(
            sample_rate=self.config.get('audio.sample_rate', 44100),
            channels=self.config.get('audio.channels', 2),
            chunk_size=self.config.get('audio.chunk_size', 1024)
        )
        
        # Mock Real-time transcription
        self.transcriber = MockTranscriber()
        self.transcriber.set_mock_transcript(
            "This is a test meeting transcript. We are discussing important project topics. "
            "Alice mentioned the timeline concerns. Bob agreed with the budget allocation. "
            "Charlie suggested we schedule a follow-up meeting next week. The team agreed on the next steps."
        )
        self.transcriber.set_mock_delay(0.5)  # Faster for testing
        
        # Mock AI summarization
        self.summarizer = MockSummarizer()
        
        # Mock Email notifications
        self.email_sender = MockEmailSender()
        
        logger.info("Mock components initialized")
            
    def _setup_callbacks(self):
        """Set up inter-component callbacks"""
        # Set up audio -> transcription callback
        def on_audio_chunk(audio_data: bytes):
            if self.current_meeting and self.transcriber.is_transcribing:
                self.transcriber.add_audio_chunk(audio_data)
        
        self.audio_recorder.set_chunk_callback(on_audio_chunk)
        
        # Set up transcription -> UI callback  
        def on_transcript_update(text: str, is_final: bool):
            if self.current_meeting:
                if is_final:
                    logger.info(f"Transcript update: {text[:100]}...")
                else:
                    logger.info(f"Partial transcript: {text[:50]}...")
                
                # Emit transcript update via WebSocket if available
                if hasattr(self, '_socketio') and self._socketio:
                    try:
                        # Get current transcript from transcriber for word count
                        current_full_transcript = self.transcriber.get_current_transcript()
                        self._socketio.emit('transcript_update', {
                            'text': text,
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'is_final': is_final,
                            'meeting_id': self.current_meeting.get('id'),
                            'word_count': len(current_full_transcript.split()) if current_full_transcript else 0
                        })
                        logger.info(f"Emitted transcript update via WebSocket: {len(text)} chars, is_final={is_final}")
                    except Exception as e:
                        logger.warning(f"Failed to emit transcript update: {e}")
            else:
                logger.warning(f"Received transcript update but no current meeting: {text[:50]}...")
        
        self.transcriber.set_transcript_callback(on_transcript_update)
        
        # Set up error callbacks
        def on_audio_error(error: Exception):
            logger.error(f"Audio recording error: {error}")
            
        def on_transcription_error(error: Exception):
            logger.error(f"Transcription error: {error}")
            
        self.audio_recorder.set_error_callback(on_audio_error)
        self.transcriber.set_error_callback(on_transcription_error)
    
    def start_meeting(
        self, 
        meeting_name: str, 
        participants: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Start recording a new meeting"""
        if self.current_meeting:
            raise ValueError("A meeting is already being recorded")
            
        logger.info(f"Starting meeting: {meeting_name}")
        logger.debug(f"Audio config: {self.config.get('audio', {})}")
        logger.debug(f"Using transcription model: {self.config.get('openai.transcription_model', 'whisper-1')}")
        
        try:
            # Create meeting record in database
            start_time = datetime.now()
            meeting_id = self.db.save_meeting(
                name=meeting_name,
                participants=participants or [],
                start_time=start_time
            )
            
            # Prepare audio file path
            recordings_dir = Path("data/recordings")
            ensure_directory(recordings_dir)
            
            audio_filename = f"meeting_{meeting_id}_{start_time.strftime('%Y%m%d_%H%M%S')}.wav"
            audio_file_path = recordings_dir / audio_filename
            
            # Start audio recording
            success = self.audio_recorder.start_recording(str(audio_file_path))
            if not success:
                raise RuntimeError("Failed to start audio recording")
            
            # Start real-time transcription
            success = self.transcriber.start_transcription()
            if not success:
                self.audio_recorder.stop_recording()
                raise RuntimeError("Failed to start transcription")
            
            # Update meeting with audio file path
            self.db.save_meeting(
                name=meeting_name,
                participants=participants or [],
                audio_file_path=str(audio_file_path),
                start_time=start_time
            )
            
            # Set current meeting state
            self.current_meeting = {
                'id': meeting_id,
                'name': meeting_name,
                'participants': participants or [],
                'start_time': start_time,
                'audio_file_path': str(audio_file_path),
                'status': 'recording'
            }
            
            logger.info(f"Meeting started successfully: {meeting_name} (ID: {meeting_id})")
            return self.current_meeting.copy()
            
        except Exception as e:
            logger.error(f"Failed to start meeting: {e}")
            # Cleanup on failure
            if hasattr(self, 'audio_recorder'):
                self.audio_recorder.stop_recording()
            if hasattr(self, 'transcriber'):
                self.transcriber.stop_transcription()
            raise
    
    def stop_meeting(self) -> Dict[str, Any]:
        """Stop recording the current meeting and process it"""
        if not self.current_meeting:
            raise ValueError("No meeting is currently being recorded")
            
        meeting_name = self.current_meeting['name']
        meeting_id = self.current_meeting['id']
        
        logger.info(f"Stopping meeting: {meeting_name}")
        
        try:
            # Stop audio recording
            audio_info = self.audio_recorder.stop_recording()
            
            # Stop transcription and get final transcript
            final_transcript = self.transcriber.stop_transcription()
            
            # Calculate meeting duration
            end_time = datetime.now()
            duration_minutes = int((end_time - self.current_meeting['start_time']).total_seconds() / 60)
            
            # Update meeting with transcript and cost info
            cost_info = self.transcriber.get_cost_info()
            self.db.update_meeting_transcript(meeting_id, final_transcript, cost_info)
            
            # Generate AI summary
            logger.info("Generating meeting summary...")
            try:
                summary = self.summarizer.summarize_meeting(
                    transcript=final_transcript,
                    meeting_name=meeting_name,
                    participants=self.current_meeting['participants'],
                    duration_minutes=duration_minutes
                )
                
                # Save summary to database
                self.db.update_meeting_summary(meeting_id, summary)
                
            except Exception as e:
                logger.error(f"Failed to generate summary: {e}")
                summary = {
                    'executive_summary': 'Summary generation failed',
                    'key_points': [],
                    'decisions_made': [],
                    'action_items': [],
                    'next_steps': [],
                    'error': str(e)
                }
            
            # Send immediate email summary
            try:
                logger.info("Sending meeting summary email...")
                success = self.email_sender.send_meeting_summary(summary)
                if success:
                    self.db.mark_meeting_sent(meeting_id)
                    logger.info("Meeting summary email sent successfully")
                else:
                    logger.warning("Failed to send meeting summary email")
            except Exception as e:
                logger.error(f"Email sending failed: {e}")
            
            # Prepare completed meeting data
            completed_meeting = self.current_meeting.copy()
            completed_meeting.update({
                'end_time': end_time,
                'duration_minutes': duration_minutes,
                'transcript': final_transcript,
                'summary': summary,
                'audio_info': audio_info,
                'cost_info': cost_info,
                'status': 'completed'
            })
            
            # Clear current meeting
            self.current_meeting = None
            
            logger.info(f"Meeting completed successfully: {meeting_name}")
            return completed_meeting
            
        except Exception as e:
            logger.error(f"Failed to stop meeting: {e}")
            # Try to cleanup anyway
            try:
                self.audio_recorder.stop_recording()
                self.transcriber.stop_transcription()
            except:
                pass
            self.current_meeting = None
            raise
    
    def get_meeting_status(self) -> Dict[str, Any]:
        """Get current meeting status"""
        if not self.current_meeting:
            return {
                'status': 'idle',
                'message': 'No meeting in progress'
            }
        
        # Calculate current duration
        current_duration = (datetime.now() - self.current_meeting['start_time']).total_seconds()
        
        # Get current transcript
        current_transcript = self.transcriber.get_current_transcript()
        
        # Get cost info
        cost_info = self.transcriber.get_cost_info()
        
        return {
            'status': 'recording',
            'meeting': {
                'id': self.current_meeting['id'],
                'name': self.current_meeting['name'],
                'participants': self.current_meeting['participants'],
                'start_time': self.current_meeting['start_time'].isoformat(),
                'duration_seconds': int(current_duration),
                'audio_file_path': self.current_meeting['audio_file_path']
            },
            'transcript': current_transcript,
            'transcription_status': self.transcriber.get_transcription_status(),
            'cost_info': cost_info
        }
    
    def get_meeting_history(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get recent meeting history"""
        cutoff_date = date.today() - timedelta(days=days_back)
        
        # Get meetings from database
        all_meetings = []
        current_date = date.today()
        
        while current_date >= cutoff_date:
            daily_meetings = self.db.get_meetings_by_date(current_date)
            all_meetings.extend(daily_meetings)
            current_date -= timedelta(days=1)
        
        # Sort by start time (most recent first)
        all_meetings.sort(key=lambda x: x.get('start_time', x.get('created_at', '')), reverse=True)
        
        return all_meetings
    
    def get_meeting_details(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed meeting information"""
        return self.db.get_meeting(meeting_id)
    
    def search_meetings(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search meetings by name, transcript, or summary"""
        return self.db.search_meetings(query, limit)
    
    def generate_daily_summary(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Generate daily summary for a specific date"""
        if target_date is None:
            target_date = date.today()
        
        logger.info(f"Generating daily summary for {target_date}")
        
        # Get all meetings for the date
        meetings = self.db.get_meetings_by_date(target_date)
        
        if not meetings:
            return {
                'date': target_date.isoformat(),
                'message': 'No meetings found for this date',
                'total_meetings': 0,
                'total_duration': 0
            }
        
        # Prepare meeting summaries for AI processing
        meeting_summaries = []
        for meeting in meetings:
            if meeting.get('summary'):
                meeting_summaries.append(meeting['summary'])
        
        if not meeting_summaries:
            return {
                'date': target_date.isoformat(),
                'message': 'No meeting summaries available for this date',
                'total_meetings': len(meetings),
                'meetings': [{'name': m['name'], 'duration': m.get('duration_minutes', 0)} for m in meetings]
            }
        
        # Generate daily summary using AI
        try:
            daily_summary = self.summarizer.generate_daily_summary(meeting_summaries)
            
            # Save to database
            self.db.save_daily_summary(target_date, daily_summary)
            
            logger.info(f"Daily summary generated for {target_date}")
            return daily_summary
            
        except Exception as e:
            logger.error(f"Failed to generate daily summary: {e}")
            return {
                'date': target_date.isoformat(),
                'error': str(e),
                'total_meetings': len(meetings),
                'meetings': [{'name': m['name'], 'duration': m.get('duration_minutes', 0)} for m in meetings]
            }
    
    def send_daily_summary_email(self, target_date: Optional[date] = None) -> bool:
        """Send daily summary email"""
        if target_date is None:
            target_date = date.today()
        
        logger.info(f"Sending daily summary email for {target_date}")
        
        try:
            # Get or generate daily summary
            daily_summary = self.db.get_daily_summary(target_date)
            
            if not daily_summary:
                daily_summary = self.generate_daily_summary(target_date)
            
            # Send email
            success = self.email_sender.send_daily_summary(daily_summary['summary'])
            
            if success:
                logger.info(f"Daily summary email sent for {target_date}")
            else:
                logger.warning(f"Failed to send daily summary email for {target_date}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send daily summary email: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            # Test database connection
            db_stats = self.db.get_statistics()
            
            # Test email connection
            email_status = self.email_sender.test_connection()
            
            # Get audio devices
            audio_devices = self.audio_recorder.get_audio_devices()
            
            return {
                'status': 'healthy',
                'components': {
                    'database': {
                        'status': 'connected',
                        'statistics': db_stats
                    },
                    'email': {
                        'status': 'connected' if email_status else 'disconnected',
                        'address': self.email_sender.email_address
                    },
                    'audio': {
                        'status': 'available',
                        'devices_count': len(audio_devices),
                        'default_device': self.audio_recorder.get_default_device()
                    },
                    'transcription': {
                        'status': 'available',
                        'model': self.transcriber.model
                    },
                    'summarization': {
                        'status': 'available',
                        'model': self.summarizer.model
                    }
                },
                'current_meeting': self.get_meeting_status()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'current_meeting': self.get_meeting_status()
            }
    
    def cleanup(self):
        """Clean up all resources"""
        logger.info("Cleaning up Meeting Agent...")
        
        try:
            # Stop any ongoing meeting
            if self.current_meeting:
                try:
                    self.stop_meeting()
                except Exception as e:
                    logger.error(f"Error stopping meeting during cleanup: {e}")
            
            # Cleanup components
            if hasattr(self, 'audio_recorder'):
                self.audio_recorder.cleanup()
                
            if hasattr(self, 'transcriber'):
                self.transcriber.cleanup()
                
            if hasattr(self, 'db'):
                self.db.close()
                
            self.is_running = False
            logger.info("Meeting Agent cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


def main():
    """Main entry point"""
    import signal
    import sys
    
    # Set up signal handlers for graceful shutdown
    agent = None
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        if agent:
            agent.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize and start agent
        logger.info("Starting Meeting Agent...")
        agent = MeetingAgent()
        
        logger.info("Meeting Agent is running. Press Ctrl+C to stop.")
        logger.info("System status:")
        status = agent.get_system_status()
        
        for component, details in status.get('components', {}).items():
            logger.info(f"  {component}: {details.get('status', 'unknown')}")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            
    except Exception as e:
        logger.error(f"Failed to start Meeting Agent: {e}")
        sys.exit(1)
        
    finally:
        if agent:
            agent.cleanup()


if __name__ == "__main__":
    main()