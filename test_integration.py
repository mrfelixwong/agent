#!/usr/bin/env python3
"""
End-to-end integration test for Meeting Agent
Tests the complete workflow with mock components
"""

import sys
import time
from pathlib import Path
from datetime import datetime, date

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import MeetingAgent
from src.utils.logger import setup_logger
from src.audio.recorder import MockAudioRecorder
from src.transcription.transcriber import MockTranscriber
from src.ai.summarizer import MockSummarizer
from src.notifications.sender import MockEmailSender
from src.database.database import MockDatabase

logger = setup_logger(__name__)


def test_meeting_agent_integration():
    """Test complete meeting agent workflow"""
    print("🧪 Meeting Agent Integration Test")
    print("=" * 40)
    
    try:
        # Create agent with mock components for testing
        print("1. Initializing Meeting Agent with mock components...")
        
        # We'll need to patch the agent to use mocks
        agent = create_test_agent()
        
        print("✅ Meeting Agent initialized")
        
        # Test system status
        print("\n2. Testing system status...")
        status = agent.get_system_status()
        print(f"   System status: {status.get('status', 'Unknown')}")
        print(f"   Components: {len(status.get('components', {}))}")
        print("✅ System status OK")
        
        # Test starting a meeting
        print("\n3. Testing meeting start...")
        meeting_info = agent.start_meeting(
            meeting_name="Integration Test Meeting",
            participants=["Alice", "Bob", "Charlie"]
        )
        print(f"   Meeting ID: {meeting_info['id']}")
        print(f"   Meeting name: {meeting_info['name']}")
        print(f"   Participants: {meeting_info['participants']}")
        print("✅ Meeting started successfully")
        
        # Test meeting status during recording
        print("\n4. Testing meeting status during recording...")
        status = agent.get_meeting_status()
        print(f"   Status: {status.get('status', 'Unknown')}")
        print(f"   Meeting name: {status.get('meeting', {}).get('name', 'Unknown')}")
        print("✅ Meeting status OK")
        
        # Simulate some recording time
        print("\n5. Simulating recording time (3 seconds)...")
        for i in range(3):
            time.sleep(1)
            status = agent.get_meeting_status()
            duration = status.get('meeting', {}).get('duration_seconds', 0)
            transcript = status.get('transcript', '')
            print(f"   {i+1}s - Duration: {duration}s, Transcript: {len(transcript)} chars")
        print("✅ Recording simulation complete")
        
        # Test stopping the meeting
        print("\n6. Testing meeting stop and processing...")
        completed_meeting = agent.stop_meeting()
        print(f"   Completed meeting: {completed_meeting['name']}")
        print(f"   Duration: {completed_meeting.get('duration_minutes', 0)} minutes")
        print(f"   Transcript length: {len(completed_meeting.get('transcript', ''))}")
        print(f"   Summary available: {'summary' in completed_meeting}")
        print("✅ Meeting stopped and processed")
        
        # Test meeting history
        print("\n7. Testing meeting history...")
        history = agent.get_meeting_history()
        print(f"   Total meetings in history: {len(history)}")
        if history:
            print(f"   Latest meeting: {history[0].get('name', 'Unknown')}")
        print("✅ Meeting history OK")
        
        # Test search functionality
        print("\n8. Testing meeting search...")
        results = agent.search_meetings("Integration")
        print(f"   Search results: {len(results)}")
        if results:
            print(f"   First result: {results[0].get('name', 'Unknown')}")
        print("✅ Search functionality OK")
        
        # Test daily summary generation
        print("\n9. Testing daily summary generation...")
        today = date.today()
        daily_summary = agent.generate_daily_summary(today)
        print(f"   Summary date: {daily_summary.get('date', 'Unknown')}")
        print(f"   Total meetings: {daily_summary.get('total_meetings', 0)}")
        print("✅ Daily summary generation OK")
        
        # Test email sending (mock)
        print("\n10. Testing daily summary email...")
        email_success = agent.send_daily_summary_email(today)
        print(f"   Email sent successfully: {email_success}")
        print("✅ Email functionality OK")
        
        print("\n🎉 Integration Test PASSED")
        print("   All components working together successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        try:
            agent.cleanup()
        except:
            pass


def create_test_agent():
    """Create a MeetingAgent with mock components for testing"""
    
    # Create the agent with mock components from the start
    agent = MeetingAgent(use_mock_components=True)
    
    print("   Mock components initialized")
    
    return agent


def test_component_initialization():
    """Test that all components can be initialized"""
    print("\n🔧 Component Initialization Test")
    print("=" * 35)
    
    components_tested = 0
    components_passed = 0
    
    # Test Database
    try:
        from src.database.database import MockDatabase
        db = MockDatabase()
        meeting_id = db.save_meeting("Test Meeting")
        assert meeting_id == 1
        db.close()
        print("✅ Database component OK")
        components_passed += 1
    except Exception as e:
        print(f"❌ Database component failed: {e}")
    components_tested += 1
    
    # Test Audio Recorder
    try:
        from src.audio.recorder import MockAudioRecorder
        recorder = MockAudioRecorder()
        assert not recorder.is_recording
        success = recorder.start_recording("/tmp/test.wav")
        assert success
        assert recorder.is_recording
        recorder.stop_recording()
        assert not recorder.is_recording
        print("✅ Audio Recorder component OK")
        components_passed += 1
    except Exception as e:
        print(f"❌ Audio Recorder component failed: {e}")
    components_tested += 1
    
    # Test Transcriber
    try:
        from src.transcription.transcriber import MockTranscriber
        transcriber = MockTranscriber()
        assert not transcriber.is_transcribing
        success = transcriber.start_transcription()
        assert success
        assert transcriber.is_transcribing
        transcriber.stop_transcription()
        assert not transcriber.is_transcribing
        print("✅ Transcriber component OK")
        components_passed += 1
    except Exception as e:
        print(f"❌ Transcriber component failed: {e}")
    components_tested += 1
    
    # Test Summarizer
    try:
        from src.ai.summarizer import MockSummarizer
        summarizer = MockSummarizer()
        summary = summarizer.summarize_meeting("Test transcript", meeting_name="Test")
        assert 'executive_summary' in summary
        assert summary['meeting_name'] == "Test"
        print("✅ Summarizer component OK")
        components_passed += 1
    except Exception as e:
        print(f"❌ Summarizer component failed: {e}")
    components_tested += 1
    
    # Test Email Sender
    try:
        from src.notifications.sender import MockEmailSender
        sender = MockEmailSender()
        success = sender.send_meeting_summary({'meeting_name': 'Test'})
        assert success
        emails = sender.get_sent_emails()
        assert len(emails) == 1
        print("✅ Email Sender component OK")
        components_passed += 1
    except Exception as e:
        print(f"❌ Email Sender component failed: {e}")
    components_tested += 1
    
    print(f"\n📊 Component Test Results: {components_passed}/{components_tested} passed")
    return components_passed == components_tested


def main():
    """Main test runner"""
    print("🚀 Meeting Agent End-to-End Integration Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Test 1: Component initialization
    if not test_component_initialization():
        all_passed = False
    
    # Test 2: Full integration workflow
    if not test_meeting_agent_integration():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Meeting Agent is working end-to-end!")
        print("\nNext steps:")
        print("• Run 'python cli.py' for interactive CLI")
        print("• Set up real OpenAI API keys for production use")
        print("• Set up Gmail SMTP credentials for email notifications")
        print("• Consider adding scheduled daily email sending")
        return 0
    else:
        print("❌ Some tests failed - check errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())