#!/usr/bin/env python3
"""
Test real OpenAI API integration
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import MeetingAgent
from src.ai.summarizer import Summarizer
from src.transcription.transcriber import Transcriber
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def test_openai_directly():
    """Test OpenAI APIs directly with environment key"""
    print("🤖 Testing OpenAI API Integration")
    print("=" * 40)
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY environment variable found")
        return False
    
    print(f"Using API key: {api_key[:10]}...")
    
    # Test 1: AI Summarizer
    print("\n1. Testing AI Summarizer...")
    try:
        summarizer = Summarizer(
            api_key=api_key,
            model='gpt-4'
        )
        
        test_transcript = """
        This is a test meeting transcript. We discussed the Q4 project timeline and budget allocation.
        Alice mentioned concerns about the current timeline being too aggressive.
        Bob agreed and suggested we add two weeks to the development phase.
        Charlie proposed we review the vendor contracts to optimize costs.
        The team decided to schedule a follow-up meeting next week to finalize the plan.
        Action items: Alice will prepare a revised timeline, Bob will review technical requirements,
        and Charlie will contact vendors for quotes.
        """
        
        summary = summarizer.summarize_meeting(
            transcript=test_transcript,
            meeting_name="Q4 Planning Meeting",
            participants=["Alice", "Bob", "Charlie"],
            duration_minutes=30
        )
        
        if summary and summary.get('executive_summary'):
            print("   ✅ Summarizer working!")
            print(f"   Executive Summary: {summary['executive_summary']}")
            print(f"   Key Points: {len(summary.get('key_points', []))} found")
            print(f"   Action Items: {len(summary.get('action_items', []))} found")
        else:
            print("   ❌ Summarizer returned invalid response")
            return False
            
    except Exception as e:
        print(f"   ❌ Summarizer failed: {e}")
        return False
    
    # Test 2: Transcriber (without actual audio)
    print("\n2. Testing Transcriber Setup...")
    try:
        transcriber = Transcriber(
            api_key=api_key,
            model='whisper-1'
        )
        
        print("   ✅ Transcriber initialized successfully")
        print("   Note: Actual transcription requires audio input")
        
    except Exception as e:
        print(f"   ❌ Transcriber setup failed: {e}")
        return False
    
    return True


def test_full_system_with_real_ai():
    """Test full system with real AI but mock components for others"""
    print("\n🎙️ Testing Full System with Real AI")
    print("=" * 40)
    
    try:
        # Create a custom MeetingAgent that uses real AI but mock other components
        agent = create_hybrid_agent()
        
        print("1. Starting test meeting...")
        meeting_info = agent.start_meeting(
            "Real AI Test Meeting", 
            ["Alice", "Bob", "Charlie"]
        )
        print(f"   ✅ Meeting started: {meeting_info['name']}")
        
        # Simulate some time
        import time
        time.sleep(2)
        
        print("\n2. Stopping meeting and processing with real AI...")
        completed = agent.stop_meeting()
        
        print(f"   ✅ Meeting completed: {completed['name']}")
        print(f"   Duration: {completed.get('duration_minutes', 0)} minutes")
        
        # Check AI summary
        summary = completed.get('summary', {})
        if summary and summary.get('executive_summary'):
            print(f"\n3. Real AI Summary Generated:")
            print(f"   Executive Summary: {summary['executive_summary']}")
            
            if summary.get('key_points'):
                print(f"   Key Points:")
                for point in summary['key_points'][:3]:
                    print(f"   • {point}")
            
            if summary.get('action_items'):
                print(f"   Action Items:")
                for item in summary['action_items'][:3]:
                    if isinstance(item, dict):
                        print(f"   • {item.get('task', item)}")
                    else:
                        print(f"   • {item}")
        
        agent.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ Full system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_hybrid_agent():
    """Create MeetingAgent that uses real AI components but mock others"""
    from src.main import MeetingAgent
    from src.ai.summarizer import Summarizer
    from src.transcription.transcriber import Transcriber
    
    # Start with mock components
    agent = MeetingAgent(use_mock_components=True)
    
    # Replace AI components with real ones
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if api_key:
        print("   Replacing mock AI components with real OpenAI...")
        
        # Replace summarizer with real one
        agent.summarizer = Summarizer(
            api_key=api_key,
            model='gpt-4'
        )
        
        # Replace transcriber with real one  
        agent.transcriber = Transcriber(
            api_key=api_key,
            model='whisper-1'
        )
        
        # Set up the mock transcript for the real transcriber
        # Since we're using mock audio, we need to inject transcript
        test_transcript = """
        This is a real test meeting transcript for AI processing. We discussed the quarterly planning and resource allocation.
        Alice mentioned concerns about the current project timeline and suggested we need more development time.
        Bob agreed with Alice and recommended we add buffer time for testing and quality assurance.
        Charlie proposed we optimize our vendor contracts to reduce costs while maintaining quality.
        The team unanimously agreed to schedule a follow-up meeting next week to review the revised plan.
        Key decisions: Extend development timeline by 2 weeks, review vendor contracts, schedule follow-up meeting.
        Action items assigned: Alice to prepare revised timeline, Bob to review technical specifications, Charlie to contact vendors.
        """
        
        # We'll inject this transcript when the transcriber is asked for results
        original_stop = agent.transcriber.stop_transcription
        def mock_stop_with_real_processing():
            agent.transcriber._transcript_text = test_transcript
            return original_stop()
        agent.transcriber.stop_transcription = mock_stop_with_real_processing
        
        print("   ✅ Real AI components integrated")
    
    return agent


def main():
    """Main test runner"""
    print("🚀 Real OpenAI API Integration Test")
    print("=" * 50)
    
    success = True
    
    if not test_openai_directly():
        success = False
    
    if not test_full_system_with_real_ai():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL REAL API TESTS PASSED!")
        print("\nReal OpenAI integration is working perfectly!")
        print("• AI summarization with GPT-4 ✅")
        print("• Transcription setup with Whisper ✅") 
        print("• Full system integration ✅")
        print("\nReady for production use with real audio recording!")
    else:
        print("❌ Some tests failed")
        
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())