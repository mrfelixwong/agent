#!/usr/bin/env python3
"""
Test real-time transcription with simulated audio
"""

import sys
import time
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_realtime_transcription():
    """Test real-time transcription with simulated audio chunks"""
    print("🎙️ Testing Real-time Transcription")
    print("=" * 35)
    
    try:
        from src.main import MeetingAgent
        
        print("1. Creating Meeting Agent...")
        agent = MeetingAgent(use_mock_components=False)
        
        print("2. Starting meeting...")
        meeting_info = agent.start_meeting("Real-time Test Meeting")
        print(f"   Meeting started: {meeting_info['name']}")
        
        print("3. Simulating audio chunks for 10 seconds...")
        
        # Get current transcript every second
        for i in range(10):
            time.sleep(1)
            
            # Simulate adding audio chunks
            if hasattr(agent.transcriber, '_audio_chunks'):
                chunk_count = len(agent.transcriber._audio_chunks)
                
                # Add a dummy audio chunk periodically
                if i % 2 == 0:  # Every 2 seconds
                    dummy_chunk = b'\x00' * 1024 * 4  # 16-bit stereo chunk
                    agent.transcriber.add_audio_chunk(dummy_chunk)
            
            # Check current status
            status = agent.get_meeting_status()
            transcript = status.get('transcript', '')
            duration = status.get('meeting', {}).get('duration_seconds', 0)
            
            print(f"   {i+1}s - Duration: {duration}s, Transcript: {len(transcript)} chars")
            
            if transcript:
                # Show last 50 characters of transcript
                preview = transcript[-50:] if len(transcript) > 50 else transcript
                print(f"        Current: {preview}")
        
        print("\n4. Stopping meeting...")
        completed = agent.stop_meeting()
        
        transcript = completed.get('transcript', '')
        print(f"   Final transcript: {len(transcript)} characters")
        
        if transcript:
            print(f"   Content: {transcript[:100]}{'...' if len(transcript) > 100 else ''}")
        
        agent.cleanup()
        
        print(f"\n✅ Real-time transcription test completed")
        print(f"   Note: Real audio recording will work much better than simulated chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_realtime_transcription()