"""
Meeting Agent Main Application
Orchestrates all components of the meeting agent system
"""

import os
import time
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

from .utils.logger import setup_logger
from .utils.config import load_config
from .utils.helpers import ensure_directory
from .database.database import Database
from .audio.recorder import AudioRecorder
from .transcription.simple_transcriber import SimpleTranscriber
from .ai.summarizer import Summarizer
from .notifications.sender import EmailSender

logger = setup_logger(__name__)  # Will be reconfigured after config load


class MeetingAgent:
    """Main Meeting Agent application orchestrator"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Meeting Agent with configuration"""
        # Load configuration
        self.config = load_config(config_path, validate_secrets=True)
        
        # Configure logging with settings from config
        global logger
        logger = setup_logger(
            __name__, 
            log_file=self.config.get('logging.file', 'logs/meeting_agent.log'),
            level=self.config.get('logging.level', 'DEBUG')
        )
        logger.info("=== Meeting Agent Starting ===")
        
        # State management
        self.is_running = False
        self.current_meeting: Optional[Dict] = None
        
        # Initialize components
        self._init_components()
        
        logger.info("Meeting Agent initialized successfully")
        
    def _init_components(self):
        """Initialize all system components"""
        logger.info("Initializing Meeting Agent components...")
        
        try:
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
        # Removed complex transcriber import
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
        
        # Simple synchronous transcription
        self.transcriber = SimpleTranscriber(
            api_key=self.config.get('openai.api_key'),
            model=self.config.get('openai.transcription_model', 'whisper-1')
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
            # Email is optional - if not configured, skip email features
            self.email_sender = None
            logger.warning("Email credentials not configured - email features will be disabled")
    
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
                    logger.info(f"🎯 FINAL transcript update: {text[:100]}...")
                else:
                    logger.info(f"⚡ PARTIAL transcript: {text[:50]}...")
                
                # WebSocket removed for simplicity
            else:
                logger.warning(f"❌ Received transcript update but no current meeting: {text[:50]}...")
        
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
        meeting_name: str
    ) -> Dict[str, Any]:
        """Start recording a new meeting"""
        
        if self.current_meeting:
            raise ValueError("A meeting is already being recorded")
            
        
        try:
            # Prepare audio file path first
            start_time = datetime.now()
            recordings_dir = Path("data/recordings")
            ensure_directory(recordings_dir)
            
            # Use temporary filename, will update with real meeting_id
            temp_audio_filename = f"meeting_temp_{start_time.strftime('%Y%m%d_%H%M%S')}.wav"
            temp_audio_file_path = recordings_dir / temp_audio_filename
            
            # Create meeting record in database (single call with audio path)
            meeting_id = self.db.save_meeting(
                name=meeting_name,
                start_time=start_time,
                audio_file_path=str(temp_audio_file_path)  # Include audio path in initial save
            )
            
            # Rename audio file to include the actual meeting ID
            audio_filename = f"meeting_{meeting_id}_{start_time.strftime('%Y%m%d_%H%M%S')}.wav"
            audio_file_path = recordings_dir / audio_filename
            
            # Start audio recording
            success = self.audio_recorder.start_recording(str(audio_file_path))
            if not success:
                raise RuntimeError("Failed to start audio recording")
            
            # Start transcription
            
            success = self.transcriber.start_transcription()
            if not success:
                self.audio_recorder.stop_recording()
                raise RuntimeError("Failed to start transcription")
            
            # Set current meeting state
            self.current_meeting = {
                'id': meeting_id,
                'name': meeting_name,
                'start_time': start_time,
                'audio_file_path': str(audio_file_path),
                'status': 'recording'
            }
            
            return_value = self.current_meeting.copy()
            return return_value
            
        except Exception as e:
            import traceback
            # Cleanup on failure
            if hasattr(self, 'audio_recorder'):
                self.audio_recorder.stop_recording()
            if hasattr(self, 'transcriber'):
                self.transcriber.stop_transcription()
            raise
    
    def stop_meeting(self) -> Dict[str, Any]:
        """Stop recording the current meeting and process it"""
        logger.info("=== STOP MEETING REQUESTED ===")
        
        if not self.current_meeting:
            logger.warning("Stop meeting rejected - no meeting in progress")
            raise ValueError("No meeting is currently being recorded")
            
        meeting_name = self.current_meeting['name']
        logger.info(f"=== STOPPING MEETING: {meeting_name} ===")
        meeting_id = self.current_meeting['id']
        
        logger.info(f"Stopping meeting: {meeting_name}")
        
        try:
            # Stop audio recording
            logger.info("🎤 Stopping audio recording...")
            audio_info = self.audio_recorder.stop_recording()
            
            # Stop transcription and get final transcript
            logger.info("🎯 Stopping transcription...")
            final_transcript = self.transcriber.stop_transcription()
            
            # Calculate meeting duration
            end_time = datetime.now()
            duration_total_seconds = (end_time - self.current_meeting['start_time']).total_seconds()
            duration_minutes = int(duration_total_seconds / 60)
            
            # Update meeting with final duration and end time
            logger.info(f"💾 Updating meeting duration in database...")
            duration_success = self.db.update_meeting_duration(
                meeting_id, end_time, duration_minutes, duration_total_seconds
            )
            
            # Update meeting with transcript
            logger.info(f"💾 Updating meeting transcript in database...")
            
            success = self.db.update_meeting_transcript(meeting_id, final_transcript)
            if not success:
                logger.error("❌ Failed to update meeting transcript in database")
            else:
                logger.info("✅ Meeting transcript updated in database")
            
            # Generate AI summary
            logger.info("Generating meeting summary...")
            try:
                summary = self.summarizer.summarize_meeting(
                    transcript=final_transcript,
                    meeting_name=meeting_name,
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
            
            # Send immediate email summary if configured
            if self.email_sender:
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
            else:
                logger.info("Email not configured - skipping email summary")
            
            # Prepare completed meeting data
            completed_meeting = self.current_meeting.copy()
            completed_meeting.update({
                'end_time': end_time,
                'duration_minutes': duration_minutes,
                'transcript': final_transcript,
                'summary': summary,
                'audio_info': audio_info,
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
        
        return {
            'status': 'recording',
            'meeting': {
                'id': self.current_meeting['id'],
                'name': self.current_meeting['name'],
                'start_time': self.current_meeting['start_time'].isoformat(),
                'duration_seconds': int(current_duration),
                'audio_file_path': self.current_meeting['audio_file_path']
            },
            'transcript': current_transcript,
            'transcription_status': self.transcriber.get_transcription_status(),
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
        
        if not self.email_sender:
            logger.warning(f"Email not configured - cannot send daily summary for {target_date}")
            return False
        
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
