#!/usr/bin/env python3
"""
Fix for real-time transcription issue
The problem: Raw audio chunks need to be formatted as WAV before sending to Whisper API
"""

import sys
import wave
import io
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def create_wav_from_chunks(audio_chunks, sample_rate=44100, channels=2, sample_width=2):
    """
    Create a WAV file in memory from raw audio chunks
    
    Args:
        audio_chunks: List of raw audio data bytes
        sample_rate: Audio sample rate
        channels: Number of audio channels
        sample_width: Sample width in bytes (2 = 16-bit)
    
    Returns:
        bytes: WAV file data
    """
    # Create in-memory WAV file
    wav_buffer = io.BytesIO()
    
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        
        # Write all chunks
        for chunk in audio_chunks:
            wav_file.writeframes(chunk)
    
    wav_buffer.seek(0)
    return wav_buffer.getvalue()

def test_wav_creation():
    """Test WAV creation from dummy audio chunks"""
    print("🔧 Testing WAV Creation from Audio Chunks")
    print("=" * 40)
    
    try:
        # Create some dummy audio chunks (silence)
        chunk_size = 1024
        dummy_chunks = [b'\x00' * chunk_size * 2 * 2 for _ in range(5)]  # 2 bytes per sample, 2 channels
        
        print(f"Created {len(dummy_chunks)} dummy audio chunks")
        print(f"Each chunk: {len(dummy_chunks[0])} bytes")
        
        # Create WAV from chunks
        wav_data = create_wav_from_chunks(dummy_chunks)
        print(f"Generated WAV data: {len(wav_data)} bytes")
        
        # Verify WAV header
        if wav_data.startswith(b'RIFF') and b'WAVE' in wav_data[:20]:
            print("✅ Valid WAV file created")
            return True
        else:
            print("❌ Invalid WAV file")
            return False
            
    except Exception as e:
        print(f"❌ WAV creation failed: {e}")
        return False

if __name__ == "__main__":
    test_wav_creation()