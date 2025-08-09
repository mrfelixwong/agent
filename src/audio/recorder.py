"""
Audio recording system for Meeting Agent
Handles system audio capture during meetings
"""

import os
import wave
import time
import threading
from typing import Optional, Callable, Dict, Any
from pathlib import Path

try:
    import pyaudio
except ImportError:
    pyaudio = None

from ..utils.logger import setup_logger
from ..utils.helpers import ensure_directory

logger = setup_logger(__name__)


class AudioRecorder:
    """
    System audio recorder for meeting capture
    
    Handles recording system audio during meetings with configurable
    sample rates, channels, and output formats.
    """
    
    def __init__(
        self, 
        sample_rate: int = 44100,
        channels: int = 2,
        chunk_size: int = 1024,
        audio_format: str = "16bit"
    ):
        """
        Initialize audio recorder
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1=mono, 2=stereo)
            chunk_size: Number of frames per buffer
            audio_format: Audio bit depth ("16bit", "24bit", "32bit")
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio_format = audio_format
        
        # PyAudio format mapping
        self._format_map = {
            "16bit": pyaudio.paInt16 if pyaudio else None,
            "24bit": pyaudio.paInt24 if pyaudio else None,
            "32bit": pyaudio.paInt32 if pyaudio else None
        }
        
        # Recording state
        self.is_recording = False
        self.current_file_path: Optional[str] = None
        self.start_time: Optional[float] = None
        
        # PyAudio objects
        self._audio: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._wave_file: Optional[wave.Wave_write] = None
        
        # Threading
        self._recording_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Callbacks
        self._on_chunk_callback: Optional[Callable[[bytes], None]] = None
        self._on_error_callback: Optional[Callable[[Exception], None]] = None
        
        # Validate PyAudio availability
        if pyaudio is None:
            raise ImportError(
                "PyAudio is not installed. Please install with: pip install pyaudio"
            )
        
        # Initialize PyAudio
        try:
            self._audio = pyaudio.PyAudio()
            logger.info("Audio recorder initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio: {e}")
            raise
            
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()
        
    def set_chunk_callback(self, callback: Callable[[bytes], None]):
        """Set callback function to receive audio chunks in real-time"""
        self._on_chunk_callback = callback
        
    def set_error_callback(self, callback: Callable[[Exception], None]):
        """Set callback function to handle recording errors"""
        self._on_error_callback = callback
        
    def get_audio_devices(self) -> Dict[int, Dict[str, Any]]:
        """
        Get list of available audio devices
        
        Returns:
            Dictionary mapping device index to device info
        """
        if not self._audio:
            return {}
            
        devices = {}
        device_count = self._audio.get_device_count()
        
        for i in range(device_count):
            try:
                device_info = self._audio.get_device_info_by_index(i)
                devices[i] = {
                    'name': device_info.get('name', 'Unknown'),
                    'channels': device_info.get('maxInputChannels', 0),
                    'sample_rate': device_info.get('defaultSampleRate', 0),
                    'is_input': device_info.get('maxInputChannels', 0) > 0,
                    'is_output': device_info.get('maxOutputChannels', 0) > 0
                }
            except Exception as e:
                logger.warning(f"Could not get info for device {i}: {e}")
                
        return devices
        
    def get_default_device(self) -> Optional[int]:
        """Get default input device index"""
        if not self._audio:
            return None
            
        try:
            device_info = self._audio.get_default_input_device_info()
            return device_info['index']
        except Exception as e:
            logger.warning(f"Could not get default input device: {e}")
            return None
            
    def start_recording(self, output_file_path: str, device_index: Optional[int] = None) -> bool:
        """
        Start recording audio to file
        
        Args:
            output_file_path: Path to output WAV file
            device_index: Optional specific audio device to use
            
        Returns:
            True if recording started successfully
        """
        if self.is_recording:
            logger.warning("Recording is already in progress")
            return False
            
        if not self._audio:
            logger.error("PyAudio not initialized")
            return False
            
        try:
            # Ensure output directory exists
            output_path = Path(output_file_path)
            ensure_directory(output_path.parent)
            
            # Open wave file for writing
            self._wave_file = wave.open(output_file_path, 'wb')
            self._wave_file.setnchannels(self.channels)
            self._wave_file.setsampwidth(self._audio.get_sample_size(self._format_map[self.audio_format]))
            self._wave_file.setframerate(self.sample_rate)
            
            # Open audio stream
            self._stream = self._audio.open(
                format=self._format_map[self.audio_format],
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            
            # Set recording state
            self.is_recording = True
            self.current_file_path = output_file_path
            self.start_time = time.time()
            self._stop_event.clear()
            
            # Start recording thread
            self._recording_thread = threading.Thread(
                target=self._recording_loop,
                daemon=True
            )
            self._recording_thread.start()
            
            logger.info(f"Started recording to: {output_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self._handle_error(e)
            self._cleanup_recording()
            return False
            
    def stop_recording(self) -> Dict[str, Any]:
        """
        Stop recording and return recording info
        
        Returns:
            Dictionary with recording information
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return {}
            
        logger.info("Stopping recording...")
        
        # Signal recording thread to stop
        self._stop_event.set()
        
        # Wait for recording thread to finish
        if self._recording_thread and self._recording_thread.is_alive():
            self._recording_thread.join(timeout=5.0)
            
        # Calculate recording info
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0
        
        recording_info = {
            'file_path': self.current_file_path,
            'duration_seconds': duration,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'format': self.audio_format,
            'file_size_bytes': self._get_file_size(self.current_file_path) if self.current_file_path else 0
        }
        
        # Cleanup
        self._cleanup_recording()
        
        logger.info(f"Recording stopped. Duration: {duration:.1f}s")
        return recording_info
        
    def pause_recording(self) -> bool:
        """Pause recording (if supported)"""
        # Note: PyAudio doesn't directly support pause/resume
        # This would need to be implemented by stopping/starting the stream
        logger.warning("Pause/resume not implemented for PyAudio recorder")
        return False
        
    def resume_recording(self) -> bool:
        """Resume recording (if supported)"""
        logger.warning("Pause/resume not implemented for PyAudio recorder")
        return False
        
    def get_recording_info(self) -> Dict[str, Any]:
        """
        Get current recording information
        
        Returns:
            Dictionary with current recording status and info
        """
        if not self.is_recording:
            return {'status': 'idle'}
            
        current_time = time.time()
        duration = current_time - self.start_time if self.start_time else 0
        
        return {
            'status': 'recording',
            'file_path': self.current_file_path,
            'duration_seconds': duration,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'format': self.audio_format
        }
        
    def _recording_loop(self):
        """Main recording loop (runs in separate thread)"""
        try:
            while not self._stop_event.is_set() and self.is_recording:
                try:
                    # Read audio data
                    audio_data = self._stream.read(
                        self.chunk_size,
                        exception_on_overflow=False
                    )
                    
                    # Write to file
                    if self._wave_file:
                        self._wave_file.writeframes(audio_data)
                        
                    # Send to real-time callback if set
                    if self._on_chunk_callback:
                        try:
                            self._on_chunk_callback(audio_data)
                        except Exception as e:
                            logger.warning(f"Chunk callback error: {e}")
                            
                except Exception as e:
                    if self.is_recording:  # Only log if we're supposed to be recording
                        logger.error(f"Recording loop error: {e}")
                        self._handle_error(e)
                    break
                    
        except Exception as e:
            logger.error(f"Fatal recording loop error: {e}")
            self._handle_error(e)
            
    def _cleanup_recording(self):
        """Clean up recording resources"""
        self.is_recording = False
        
        # Close wave file
        if self._wave_file:
            try:
                self._wave_file.close()
            except Exception as e:
                logger.warning(f"Error closing wave file: {e}")
            finally:
                self._wave_file = None
                
        # Close audio stream
        if self._stream:
            try:
                if not self._stream.is_stopped():
                    self._stream.stop_stream()
                self._stream.close()
            except Exception as e:
                logger.warning(f"Error closing audio stream: {e}")
            finally:
                self._stream = None
                
        # Reset state
        self.current_file_path = None
        self.start_time = None
        
    def _handle_error(self, error: Exception):
        """Handle recording errors"""
        logger.error(f"Recording error: {error}")
        
        if self._on_error_callback:
            try:
                self._on_error_callback(error)
            except Exception as e:
                logger.error(f"Error callback failed: {e}")
                
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
            
    def cleanup(self):
        """Clean up all resources"""
        if self.is_recording:
            self.stop_recording()
            
        if self._audio:
            try:
                self._audio.terminate()
            except Exception as e:
                logger.warning(f"Error terminating PyAudio: {e}")
            finally:
                self._audio = None
                
        logger.info("Audio recorder cleaned up")
