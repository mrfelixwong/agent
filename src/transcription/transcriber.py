"""
Real-time transcription system using OpenAI Whisper
Handles audio chunk processing and live transcript generation
"""

import os
import io
import time
import wave
import tempfile
import threading
from typing import Optional, Callable, List, Dict, Any
from pathlib import Path

try:
    import openai
except ImportError:
    openai = None

from ..utils.logger import setup_logger
from ..utils.config import load_config

logger = setup_logger(__name__)


class Transcriber:
    """
    Real-time transcriber using OpenAI Whisper API
    
    Processes audio chunks in real-time and provides live transcription
    for meeting recordings.
    """
    
    # Whisper API pricing per minute (as of 2024)
    WHISPER_COST_PER_MINUTE = 0.006  # $0.006 per minute
    
    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-1"):
        """
        Initialize transcriber
        
        Args:
            api_key: OpenAI API key (optional, can use environment variable)
            model: Whisper model to use
        """
        self.model = model
        self.is_transcribing = False
        self.current_transcript = ""
        
        # Cost tracking
        self.total_audio_duration = 0.0  # in seconds
        self.total_cost = 0.0
        
        # Audio buffer for processing
        self._audio_chunks: List[bytes] = []
        self._buffer_lock = threading.Lock()
        self._last_process_time = 0
        self._process_interval = 3.0  # Process every 3 seconds
        
        # Audio parameters (will be set when audio starts)
        self._sample_rate = 44100
        self._channels = 1  # Use mono by default
        self._sample_width = 2  # 16-bit audio
        
        # Threading
        self._processing_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Callbacks
        self._on_transcript_callback: Optional[Callable[[str, bool], None]] = None
        self._on_error_callback: Optional[Callable[[Exception], None]] = None
        
        # Initialize OpenAI client
        if openai is None:
            raise ImportError(
                "OpenAI package is not installed. Please install with: pip install openai"
            )
        
        # Set up API key
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        elif os.getenv('OPENAI_API_KEY'):
            self.client = openai.OpenAI()
        else:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        logger.info(f"Transcriber initialized with model: {model}")
    
    def set_transcript_callback(self, callback: Callable[[str, bool], None]):
        """
        Set callback function to receive transcript updates
        
        Args:
            callback: Function that receives (transcript_text, is_final)
        """
        self._on_transcript_callback = callback
    
    def set_error_callback(self, callback: Callable[[Exception], None]):
        """Set callback function to handle transcription errors"""
        self._on_error_callback = callback
    
    def set_processing_interval(self, seconds: float):
        """Set how often to process buffered audio (default: 2.0 seconds)"""
        self._process_interval = max(0.5, seconds)
    
    def start_transcription(self) -> bool:
        """
        Start real-time transcription
        
        Returns:
            True if transcription started successfully
        """
        if self.is_transcribing:
            logger.warning("Transcription is already running")
            return False
        
        try:
            self.is_transcribing = True
            self.current_transcript = ""
            self._stop_event.clear()
            
            # Clear audio buffer
            with self._buffer_lock:
                self._audio_chunks.clear()
            
            # Start processing thread
            self._processing_thread = threading.Thread(
                target=self._processing_loop,
                daemon=True
            )
            self._processing_thread.start()
            
            logger.info("Real-time transcription started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start transcription: {e}")
            self._handle_error(e)
            self.is_transcribing = False
            return False
    
    def stop_transcription(self) -> str:
        """
        Stop transcription and return final transcript
        
        Returns:
            Final complete transcript
        """
        if not self.is_transcribing:
            logger.warning("Transcription is not running")
            return self.current_transcript
        
        logger.info("Stopping transcription...")
        
        # Signal processing thread to stop
        self._stop_event.set()
        
        # Wait for processing thread to finish
        if self._processing_thread and self._processing_thread.is_alive():
            self._processing_thread.join(timeout=10.0)
        
        # Process any remaining audio in buffer
        self._process_remaining_audio()
        
        self.is_transcribing = False
        
        logger.info("Transcription stopped")
        logger.info(f"Total transcription cost: ${self.total_cost:.4f} for {self.total_audio_duration/60:.1f} minutes")
        return self.current_transcript
    
    def get_cost_info(self) -> Dict[str, float]:
        """Get current cost information"""
        return {
            'total_duration_seconds': self.total_audio_duration,
            'total_duration_minutes': self.total_audio_duration / 60.0,
            'total_cost': self.total_cost,
            'cost_per_minute': self.WHISPER_COST_PER_MINUTE
        }
    
    def add_audio_chunk(self, audio_data: bytes) -> bool:
        """
        Add audio chunk for transcription processing
        
        Args:
            audio_data: Raw audio data bytes
            
        Returns:
            True if chunk was added successfully
        """
        if not self.is_transcribing:
            return False
        
        try:
            with self._buffer_lock:
                self._audio_chunks.append(audio_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add audio chunk: {e}")
            self._handle_error(e)
            return False
    
    def get_current_transcript(self) -> str:
        """Get current transcript text"""
        return self.current_transcript
    
    def get_transcription_status(self) -> Dict[str, Any]:
        """
        Get current transcription status
        
        Returns:
            Dictionary with transcription status and info
        """
        return {
            'is_transcribing': self.is_transcribing,
            'current_length': len(self.current_transcript),
            'buffer_chunks': len(self._audio_chunks) if hasattr(self, '_audio_chunks') else 0,
            'model': self.model
        }
    
    def _processing_loop(self):
        """Main transcription processing loop (runs in separate thread)"""
        try:
            while not self._stop_event.is_set() and self.is_transcribing:
                current_time = time.time()
                
                # Check if it's time to process buffered audio
                if current_time - self._last_process_time >= self._process_interval:
                    self._process_audio_buffer()
                    self._last_process_time = current_time
                
                # Sleep briefly to avoid busy waiting
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Fatal transcription loop error: {e}")
            self._handle_error(e)
    
    def _process_audio_buffer(self):
        """Process current audio buffer and update transcript"""
        try:
            # Get buffered audio chunks
            with self._buffer_lock:
                if not self._audio_chunks:
                    return  # No data to process
                
                # Take all current chunks and clear buffer
                chunks_to_process = self._audio_chunks.copy()
                self._audio_chunks.clear()
            
            if len(chunks_to_process) < 2:  # Need at least 2 chunks for meaningful transcription
                return
            
            # Create WAV file from audio chunks
            wav_data = self._create_wav_from_chunks(chunks_to_process)
            
            if len(wav_data) < 1000:  # Skip very small files
                return
            
            # Create temporary WAV file for Whisper API
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(wav_data)
                temp_path = temp_file.name
            
            try:
                # Calculate audio duration for this chunk
                audio_duration = len(chunks_to_process) * 1024 / (self._sample_rate * self._channels * self._sample_width)
                
                # Transcribe audio chunk
                transcript = self._transcribe_audio_file(temp_path)
                
                # Update cost tracking
                self.total_audio_duration += audio_duration
                chunk_cost = (audio_duration / 60.0) * self.WHISPER_COST_PER_MINUTE
                self.total_cost += chunk_cost
                
                logger.info(f"Transcribed {audio_duration:.1f}s of audio (cost: ${chunk_cost:.4f})")
                
                if transcript and transcript.strip():
                    # Update current transcript
                    if self.current_transcript:
                        self.current_transcript += " " + transcript
                    else:
                        self.current_transcript = transcript
                    
                    # Notify callback with partial transcript
                    if self._on_transcript_callback:
                        try:
                            self._on_transcript_callback(transcript, False)
                        except Exception as e:
                            logger.warning(f"Transcript callback error: {e}")
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                    
        except Exception as e:
            logger.error(f"Audio buffer processing error: {e}")
            self._handle_error(e)
    
    def _create_wav_from_chunks(self, audio_chunks: List[bytes]) -> bytes:
        """
        Create a WAV file in memory from raw audio chunks
        
        Args:
            audio_chunks: List of raw audio data bytes
            
        Returns:
            bytes: WAV file data
        """
        # Create in-memory WAV file
        wav_buffer = io.BytesIO()
        
        try:
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(self._channels)
                wav_file.setsampwidth(self._sample_width)
                wav_file.setframerate(self._sample_rate)
                
                # Write all chunks
                for chunk in audio_chunks:
                    wav_file.writeframes(chunk)
        
            wav_buffer.seek(0)
            return wav_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create WAV from chunks: {e}")
            return b''
    
    def _process_remaining_audio(self):
        """Process any remaining audio in buffer when stopping"""
        try:
            with self._buffer_lock:
                if self._audio_chunks:
                    self._process_audio_buffer()
                    
            # Send final transcript
            if self._on_transcript_callback and self.current_transcript:
                try:
                    self._on_transcript_callback(self.current_transcript, True)
                except Exception as e:
                    logger.warning(f"Final transcript callback error: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to process remaining audio: {e}")
            self._handle_error(e)
    
    def _transcribe_audio_file(self, audio_file_path: str) -> str:
        """
        Transcribe audio file using OpenAI Whisper API
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            with open(audio_file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="text"
                )
                
            return transcript.strip() if transcript else ""
            
        except Exception as e:
            logger.error(f"Whisper API transcription failed: {e}")
            raise
    
    def _handle_error(self, error: Exception):
        """Handle transcription errors"""
        logger.error(f"Transcription error: {error}")
        
        if self._on_error_callback:
            try:
                self._on_error_callback(error)
            except Exception as e:
                logger.error(f"Error callback failed: {e}")
    
    def cleanup(self):
        """Clean up all resources"""
        if self.is_transcribing:
            self.stop_transcription()
        
        logger.info("Transcriber cleaned up")


class MockTranscriber(Transcriber):
    """
    Mock transcriber for testing without actual API calls
    """
    
    def __init__(self, **kwargs):
        """Initialize mock transcriber"""
        # Don't call parent __init__ to avoid OpenAI API setup
        self.model = kwargs.get('model', 'mock-whisper-1')
        self.is_transcribing = False
        self.current_transcript = ""
        
        # Cost tracking (mock)
        self.total_audio_duration = 0.0
        self.total_cost = 0.0
        
        # Audio buffer for compatibility with tests
        self._audio_buffer = io.BytesIO()
        
        self._on_transcript_callback: Optional[Callable[[str, bool], None]] = None
        self._on_error_callback: Optional[Callable[[Exception], None]] = None
        
        # Mock settings
        self._mock_transcript = "This is a mock transcription of the meeting audio."
        self._mock_delay = 1.0  # Simulate processing delay
        self._simulate_error = False
        
        # Threading for mock processing
        self._processing_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
    def set_mock_transcript(self, transcript: str):
        """Set mock transcript text for testing"""
        self._mock_transcript = transcript
    
    def set_mock_delay(self, delay: float):
        """Set mock processing delay"""
        self._mock_delay = max(0.1, delay)
    
    def set_simulate_error(self, should_error: bool):
        """Set whether to simulate transcription errors"""
        self._simulate_error = should_error
    
    def start_transcription(self) -> bool:
        """Mock start transcription"""
        if self.is_transcribing:
            return False
        
        if self._simulate_error:
            self._handle_error(Exception("Simulated transcription error"))
            return False
        
        self.is_transcribing = True
        self.current_transcript = ""
        self._stop_event.clear()
        
        # Start mock processing thread
        self._processing_thread = threading.Thread(
            target=self._mock_processing_loop,
            daemon=True
        )
        self._processing_thread.start()
        
        return True
    
    def stop_transcription(self) -> str:
        """Mock stop transcription"""
        if not self.is_transcribing:
            return self.current_transcript
        
        self._stop_event.set()
        
        if self._processing_thread and self._processing_thread.is_alive():
            self._processing_thread.join(timeout=2.0)
        
        self.is_transcribing = False
        
        # Send final transcript callback
        if self._on_transcript_callback and self.current_transcript:
            try:
                self._on_transcript_callback(self.current_transcript, True)
            except Exception as e:
                logger.warning(f"Mock final callback error: {e}")
        
        return self.current_transcript
    
    def get_cost_info(self) -> Dict[str, float]:
        """Get current cost information (mock)"""
        return {
            'total_duration_seconds': self.total_audio_duration,
            'total_duration_minutes': self.total_audio_duration / 60.0,
            'total_cost': self.total_cost,
            'cost_per_minute': 0.006
        }
    
    def add_audio_chunk(self, audio_data: bytes) -> bool:
        """Mock add audio chunk"""
        # Simulate cost tracking
        chunk_duration = len(audio_data) / (44100 * 2)  # Assume 44100Hz, 16-bit
        self.total_audio_duration += chunk_duration
        self.total_cost += (chunk_duration / 60.0) * 0.006
        return self.is_transcribing
    
    def _mock_processing_loop(self):
        """Mock processing loop that simulates transcription"""
        try:
            words = self._mock_transcript.split()
            word_index = 0
            
            while not self._stop_event.is_set() and self.is_transcribing and word_index < len(words):
                # Simulate processing delay
                time.sleep(self._mock_delay)
                
                if not self.is_transcribing:
                    break
                
                # Add next word(s) to transcript
                words_to_add = min(3, len(words) - word_index)  # Add 1-3 words at a time
                new_words = " ".join(words[word_index:word_index + words_to_add])
                
                if self.current_transcript:
                    self.current_transcript += " " + new_words
                else:
                    self.current_transcript = new_words
                
                word_index += words_to_add
                
                # Send partial transcript callback
                if self._on_transcript_callback:
                    try:
                        self._on_transcript_callback(new_words, False)
                    except Exception as e:
                        logger.warning(f"Mock callback error: {e}")
                        
        except Exception as e:
            logger.error(f"Mock processing loop error: {e}")
            self._handle_error(e)
    
    def cleanup(self):
        """Mock cleanup"""
        self.is_transcribing = False