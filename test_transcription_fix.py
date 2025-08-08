#!/usr/bin/env python3
"""
Test the fixed transcription system
"""

import sys
import time
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_transcription_fix():
    """Test the fixed transcription system"""
    print("🔧 Testing Fixed Transcription System")
    print("=" * 40)
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found")
        return False
    
    try:
        from src.main import MeetingAgent
        
        print("1. Creating Meeting Agent with real components...")
        agent = MeetingAgent(use_mock_components=False)
        print("   ✅ Agent created successfully")
        
        print("2. Testing system status...")
        status = agent.get_system_status()
        print(f"   System status: {status.get('status', 'Unknown')}")
        
        components = status.get('components', {})
        for component, details in components.items():
            comp_status = details.get('status', 'unknown')
            print(f"   {component}: {comp_status}")
        
        print("3. Testing transcriber separately...")
        from src.transcription.transcriber import Transcriber
        
        transcriber = Transcriber(api_key=api_key)
        
        # Create some dummy audio chunks (silence)
        chunk_size = 1024 * 2 * 2  # 16-bit stereo
        dummy_chunks = [b'\x00' * chunk_size for _ in range(3)]
        
        print(f"   Created {len(dummy_chunks)} audio chunks for testing")
        
        # Test WAV creation
        wav_data = transcriber._create_wav_from_chunks(dummy_chunks)
        print(f"   Generated WAV: {len(wav_data)} bytes")
        
        if wav_data.startswith(b'RIFF') and b'WAVE' in wav_data[:20]:
            print("   ✅ WAV creation working")
        else:
            print("   ❌ WAV creation failed")
        
        transcriber.cleanup()
        agent.cleanup()
        
        print("\n✅ Transcription fix test completed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_transcription_fix()