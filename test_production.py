#!/usr/bin/env python3
"""
Test production components initialization
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_production_components():
    """Test if all production components can initialize"""
    print("🚀 Production Components Test")
    print("=" * 30)
    
    # Test environment
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return False
    
    print(f"✅ OpenAI API Key: {api_key[:10]}...")
    
    # Test individual components
    components_passed = 0
    total_components = 0
    
    # Test PyAudio
    total_components += 1
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        p.terminate()
        print(f"✅ PyAudio: {device_count} audio devices found")
        components_passed += 1
    except Exception as e:
        print(f"❌ PyAudio: {e}")
    
    # Test OpenAI
    total_components += 1
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        print(f"✅ OpenAI: Client initialized (v{openai.__version__})")
        components_passed += 1
    except Exception as e:
        print(f"❌ OpenAI: {e}")
    
    # Test Audio Recorder
    total_components += 1
    try:
        from src.audio.recorder import AudioRecorder
        recorder = AudioRecorder()
        devices = recorder.get_audio_devices()
        recorder.cleanup()
        print(f"✅ AudioRecorder: {len(devices)} devices available")
        components_passed += 1
    except Exception as e:
        print(f"❌ AudioRecorder: {e}")
    
    # Test Transcriber
    total_components += 1
    try:
        from src.transcription.transcriber import Transcriber
        transcriber = Transcriber(api_key=api_key)
        transcriber.cleanup()
        print(f"✅ Transcriber: Initialized with Whisper")
        components_passed += 1
    except Exception as e:
        print(f"❌ Transcriber: {e}")
    
    # Test Summarizer
    total_components += 1
    try:
        from src.ai.summarizer import Summarizer
        summarizer = Summarizer(api_key=api_key)
        print(f"✅ Summarizer: Initialized with GPT-4")
        components_passed += 1
    except Exception as e:
        print(f"❌ Summarizer: {e}")
    
    print(f"\n📊 Results: {components_passed}/{total_components} components working")
    
    if components_passed == total_components:
        print("🎉 ALL PRODUCTION COMPONENTS READY!")
        print("\nYour system is ready for real meeting recording with:")
        print("• Real audio recording")
        print("• Live transcription")
        print("• AI summarization")
        
        print(f"\nTo start using:")
        print(f"python production_cli.py")
        
        return True
    else:
        print("❌ Some components failed")
        return False


def test_meeting_agent():
    """Test full MeetingAgent with real components"""
    print("\n🎙️ Testing Full Meeting Agent")
    print("=" * 30)
    
    try:
        from src.main import MeetingAgent
        
        print("Initializing MeetingAgent with real components...")
        agent = MeetingAgent(use_mock_components=False)
        
        print("✅ MeetingAgent initialized successfully!")
        
        # Test system status
        status = agent.get_system_status()
        print(f"System status: {status.get('status', 'Unknown')}")
        
        components = status.get('components', {})
        for component, details in components.items():
            comp_status = details.get('status', 'unknown')
            print(f"  {component}: {comp_status}")
        
        agent.cleanup()
        
        print("\n🎉 PRODUCTION MEETING AGENT READY!")
        print("Ready to record real meetings with live AI processing!")
        
        return True
        
    except Exception as e:
        print(f"❌ MeetingAgent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner"""
    success1 = test_production_components()
    success2 = test_meeting_agent()
    
    if success1 and success2:
        print(f"\n" + "=" * 50)
        print("🚀 PRODUCTION SYSTEM READY!")
        print(f"\nNext steps:")
        print(f"1. Run: python production_cli.py")
        print(f"2. Select option 1 to start recording") 
        print(f"3. Speak into your microphone")
        print(f"4. Select option 2 to stop and get AI summary")
        return 0
    else:
        print(f"\n" + "=" * 50)
        print("❌ Production system not ready")
        return 1


if __name__ == "__main__":
    sys.exit(main())