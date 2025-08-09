#!/usr/bin/env python3
"""
Comprehensive test of the SimpleTranscriber implementation
"""

import time
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import MeetingAgent

def test_comprehensive():
    """Comprehensive test covering all functionality"""
    print("🔍 COMPREHENSIVE SIMPLE TRANSCRIBER TEST")
    print("="*50)
    
    agent = None
    try:
        # 1. Initialization test
        print("1. Testing initialization...")
        agent = MeetingAgent()
        
        # Check transcriber attributes exist
        transcriber = agent.transcriber
        required_attrs = [
            'is_transcribing', 'current_transcript', 'audio_chunks',
            'total_cost', 'total_audio_duration', '_on_transcript_callback',
            '_on_error_callback', 'api_key', 'model'
        ]
        
        for attr in required_attrs:
            if not hasattr(transcriber, attr):
                print(f"   ❌ Missing attribute: {attr}")
                return False
        
        print("   ✅ All required attributes present")
        
        # 2. Method interface test
        print("2. Testing method interface...")
        required_methods = [
            'start_transcription', 'stop_transcription', 'add_audio_chunk',
            'get_current_transcript', 'get_transcription_status', 'get_cost_info',
            'set_transcript_callback', 'set_error_callback', 'set_processing_interval',
            'cleanup'
        ]
        
        for method in required_methods:
            if not hasattr(transcriber, method) or not callable(getattr(transcriber, method)):
                print(f"   ❌ Missing or non-callable method: {method}")
                return False
        
        print("   ✅ All required methods present")
        
        # 3. Initial state test
        print("3. Testing initial state...")
        assert transcriber.is_transcribing == False, "Should not be transcribing initially"
        assert transcriber.current_transcript == "", "Transcript should be empty initially"
        assert len(transcriber.audio_chunks) == 0, "Audio chunks should be empty initially"
        print("   ✅ Initial state correct")
        
        # 4. Status method test
        print("4. Testing status methods...")
        status = transcriber.get_transcription_status()
        expected_keys = {'is_transcribing', 'current_length', 'buffer_chunks', 'model'}
        if not expected_keys.issubset(status.keys()):
            print(f"   ❌ Status missing keys. Got: {status.keys()}, Expected: {expected_keys}")
            return False
        print("   ✅ Status method working")
        
        # 5. Callback setting test
        print("5. Testing callback methods...")
        transcriber.set_transcript_callback(lambda text, final: None)
        transcriber.set_error_callback(lambda error: None)
        transcriber.set_processing_interval(2.0)
        print("   ✅ Callback methods working")
        
        # 6. Full meeting workflow test
        print("6. Testing full meeting workflow...")
        
        # Start meeting
        meeting_info = agent.start_meeting("Full Review Test", ["Reviewer"])
        print(f"   📝 Meeting started: {meeting_info['name']}")
        
        # Verify transcription started
        assert transcriber.is_transcribing == True, "Should be transcribing after start"
        print("   ✅ Transcription started")
        
        # Record for reasonable time
        print("   🎤 Recording for 8 seconds...")
        time.sleep(8)
        
        # Check chunks collected
        chunk_count = len(transcriber.audio_chunks)
        print(f"   📊 Collected {chunk_count} audio chunks")
        if chunk_count < 10:
            print(f"   ⚠️  Warning: Low chunk count ({chunk_count}), may not generate transcript")
        
        # Stop meeting
        print("   🛑 Stopping meeting...")
        start_stop = time.time()
        completed_meeting = agent.stop_meeting()
        stop_time = time.time() - start_stop
        
        print(f"   ⏱️  Stop processing took: {stop_time:.1f}s")
        
        # 7. Results validation test
        print("7. Validating results...")
        
        # Check meeting completed
        if completed_meeting.get('status') != 'completed':
            print(f"   ❌ Meeting status: {completed_meeting.get('status')} (expected: completed)")
            return False
        
        # Check transcript
        transcript = completed_meeting.get('transcript', '')
        transcript_len = len(transcript)
        print(f"   📝 Transcript length: {transcript_len} characters")
        
        if transcript_len == 0:
            print("   ❌ No transcript generated")
            return False
        
        print(f"   📝 Transcript: '{transcript[:100]}{'...' if transcript_len > 100 else ''}'")
        
        # Check cost info
        cost_info = completed_meeting.get('cost_info', {})
        total_cost = cost_info.get('total_cost', 0)
        duration_seconds = cost_info.get('total_duration_seconds', 0)
        
        print(f"   💰 Total cost: ${total_cost:.4f}")
        print(f"   🕒 Audio duration: {duration_seconds:.1f}s")
        
        if total_cost <= 0:
            print("   ❌ No cost calculated")
            return False
        
        # Check transcriber state after completion
        if transcriber.is_transcribing:
            print("   ❌ Transcriber still in transcribing state after stop")
            return False
        
        if transcriber.current_transcript != transcript:
            print("   ❌ Transcriber current_transcript doesn't match returned transcript")
            return False
        
        print("   ✅ All results validated")
        
        # 8. Cleanup test
        print("8. Testing cleanup...")
        agent.cleanup()
        
        # Verify cleanup
        if transcriber.is_transcribing:
            print("   ❌ Still transcribing after cleanup")
            return False
            
        if len(transcriber.audio_chunks) > 0:
            print("   ❌ Audio chunks not cleared after cleanup")
            return False
            
        if transcriber.current_transcript != "":
            print("   ❌ Transcript not cleared after cleanup")
            return False
        
        print("   ✅ Cleanup successful")
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED! SimpleTranscriber fully working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if agent:
            try:
                agent.cleanup()
            except:
                pass

if __name__ == "__main__":
    success = test_comprehensive()
    exit(0 if success else 1)