"""Simplified synchronous transcriber - no threading, no hanging"""

import os
import time
import tempfile
import wave
from typing import List, Dict, Any, Optional, Callable
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class SimpleTranscriber:
    
    def __init__(self, api_key: str, model: str = "whisper-1"):
        self.api_key = api_key
        self.model = model
        
        self.is_transcribing = False
        self.audio_chunks: List[bytes] = []
        self.current_transcript = ""  # For web debugging compatibility
        
        self._sample_rate = 44100
        self._channels = 2
        self._sample_width = 2
    
    def start_transcription(self, on_transcript_callback: Optional[Callable] = None) -> bool:
        self.is_transcribing = True
        self.audio_chunks.clear()
        self.current_transcript = ""
        return True
    
    def add_audio_chunk(self, audio_data: bytes) -> bool:
        if not self.is_transcribing:
            return False
        
        self.audio_chunks.append(audio_data)
        return True
    
    def stop_transcription(self) -> str:
        """Process all audio chunks and return transcript"""
        
        if not self.audio_chunks:
            logger.warning("No audio chunks collected - returning empty transcript")
            self.is_transcribing = False
            return ""
        
        try:
            # Process all chunks in one batch
            full_transcript = self._process_all_chunks_sync()
            
            # Update current transcript for compatibility
            self.current_transcript = full_transcript
            
            self.is_transcribing = False
            
            return full_transcript
            
        except Exception as e:
            logger.error(f"Simple transcription failed: {e}")
            self.is_transcribing = False
            return ""
    
    def _process_all_chunks_sync(self) -> str:
        """Process all audio chunks synchronously in batches"""
        
        if len(self.audio_chunks) < 10:  # Need minimum chunks
            logger.warning(f"Too few chunks ({len(self.audio_chunks)}) for transcription")
            return ""
        
        # Create one large WAV file from all chunks
        wav_data = self._create_wav_from_chunks(self.audio_chunks)
        
        if len(wav_data) < 5000:  # Skip very small files
            logger.warning(f"Audio file too small ({len(wav_data)} bytes)")
            return ""
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(wav_data)
            temp_path = temp_file.name
        
        try:
            # Calculate total audio duration
            audio_duration = len(self.audio_chunks) * 1024 / (self._sample_rate * self._channels * self._sample_width)
            self.total_audio_duration = audio_duration
            
            logger.info(f"Transcribing {audio_duration:.1f}s of audio in one batch...")
            
            # Single OpenAI API call for entire meeting
            start_time = time.time()
            transcript = self._transcribe_audio_file(temp_path)
            api_time = time.time() - start_time
            
            
            return transcript
            
        finally:
            # Cleanup temp file
            try:
                os.unlink(temp_path)
            except OSError:
                pass
    
    def _create_wav_from_chunks(self, audio_chunks: List[bytes]) -> bytes:
        """Create a WAV file from audio chunks"""
        if not audio_chunks:
            return b""
        
        # Calculate total data size
        total_frames = len(audio_chunks) * (len(audio_chunks[0]) // (self._channels * self._sample_width))
        
        # Create WAV file in memory
        with tempfile.NamedTemporaryFile() as temp_wav:
            with wave.open(temp_wav.name, 'wb') as wav_file:
                wav_file.setnchannels(self._channels)
                wav_file.setsampwidth(self._sample_width)
                wav_file.setframerate(self._sample_rate)
                
                # Write all audio data
                for chunk in audio_chunks:
                    wav_file.writeframes(chunk)
            
            # Read the WAV data
            with open(temp_wav.name, 'rb') as f:
                return f.read()
    
    def _transcribe_audio_file(self, audio_file_path: str) -> str:
        """Transcribe audio file using OpenAI Whisper API"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            with open(audio_file_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file
                )
            
            return transcript.text.strip()
            
        except Exception as e:
            logger.error(f"OpenAI transcription API error: {e}")
            return ""
    
    
    def get_current_transcript(self) -> str:
        """Get current transcript (empty during recording, full after stop)"""
        return self.current_transcript
    
    def get_transcription_status(self) -> Dict[str, Any]:
        """Get current transcription status"""
        return {
            'is_transcribing': self.is_transcribing,
            'current_length': len(self.current_transcript),
            'buffer_chunks': len(self.audio_chunks),
            'model': self.model
        }
    
    def set_transcript_callback(self, callback: Optional[Callable] = None):
        """Set transcript callback (no-op in simple mode)"""
        pass
        
    def set_error_callback(self, callback: Optional[Callable] = None):
        """Set error callback (no-op in simple mode)"""
        pass
        
    def cleanup(self):
        """Cleanup resources"""
        self.is_transcribing = False
        self.audio_chunks.clear()
        self.current_transcript = ""
