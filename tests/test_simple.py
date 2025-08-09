#!/usr/bin/env python3
"""
Test the simplified thread-free transcription system
"""

import time
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import MeetingAgent

def test_simple_transcription():
    print("🧪 Testing simplified thread-free transcription...")
    
    agent = None
    try:
        # Initialize Meeting Agent (now with SimpleTranscriber)
        print("1. Initializing MeetingAgent with SimpleTranscriber...")
        agent = MeetingAgent()
        print("   ✅ MeetingAgent initialized")
        
        # Start meeting
        print("2. Starting meeting...")
        meeting_info = agent.start_meeting("Simple Transcription Test", ["Test User"])
        print(f"   ✅ Meeting started: {meeting_info['name']}")
        
        # Record for a short time
        print("3. Recording for 10 seconds...")
        time.sleep(10)
        
        print("4. Stopping meeting (this will process all audio synchronously)...")
        start_time = time.time()
        completed_meeting = agent.stop_meeting()
        stop_time = time.time()
        
        processing_time = stop_time - start_time
        print(f"   ✅ Meeting stopped (processing took {processing_time:.1f}s)")
        
        # Analyze results
        print("5. Results:")
        transcript = completed_meeting.get('transcript', '')
        cost_info = completed_meeting.get('cost_info', {})
        
        print(f"   📝 Status: {completed_meeting.get('status', 'Unknown')}")
        print(f"   📝 Duration seconds: {completed_meeting.get('duration_seconds', 'N/A')}")
        print(f"   📝 Transcript length: {len(transcript)} characters")
        print(f"   💰 Total cost: ${cost_info.get('total_cost', 0):.4f}")
        print(f"   🕒 Audio duration: {cost_info.get('total_duration_seconds', 0):.1f}s")
        
        if transcript:
            print(f"   📝 SUCCESS! Transcript: '{transcript[:150]}{'...' if len(transcript) > 150 else ''}'")
            return True
        else:
            print("   ❌ FAILED: No transcript generated")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if agent:
            print("6. Cleaning up...")
            agent.cleanup()

if __name__ == "__main__":
    success = test_simple_transcription()
    print(f"\n🎯 Test {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)