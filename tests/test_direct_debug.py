#!/usr/bin/env python3
"""
Test script to debug meeting transcription issue by direct MeetingAgent access
"""

import time
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import MeetingAgent

def test_direct_meeting():
    print("🧪 Starting direct Meeting Agent debug test...")
    
    try:
        # Initialize Meeting Agent
        print("\n1. Initializing Meeting Agent...")
        agent = MeetingAgent()
        print("   ✅ MeetingAgent initialized")
        
        # Start meeting
        print("\n2. Starting meeting...")
        meeting_info = agent.start_meeting("Direct Debug Test", ["Debug User"])
        print(f"   ✅ Meeting started: {meeting_info}")
        
        # Let meeting run for a bit
        print(f"\n3. Letting meeting run for 15 seconds...")
        time.sleep(15)
        
        # Stop meeting and check debugging
        print("\n4. Stopping meeting...")
        completed_meeting = agent.stop_meeting()
        print(f"   ✅ Meeting stopped")
        
        # Analyze results
        print(f"\n5. Analyzing results...")
        print(f"   📝 Meeting name: {completed_meeting.get('name', 'Unknown')}")
        print(f"   📝 Status: {completed_meeting.get('status', 'Unknown')}")
        print(f"   📝 Duration (minutes): {completed_meeting.get('duration_minutes', 0)}")
        print(f"   📝 Transcript length: {len(completed_meeting.get('transcript', ''))}")
        print(f"   📝 Cost info: {completed_meeting.get('cost_info', {})}")
        
        transcript = completed_meeting.get('transcript', '')
        if transcript:
            print(f"   📝 Transcript preview: {transcript[:200]}...")
        else:
            print("   ❌ NO TRANSCRIPT GENERATED!")
            
        print("\n🧪 Direct debug test completed!")
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            if 'agent' in locals():
                agent.cleanup()
        except:
            pass

if __name__ == "__main__":
    test_direct_meeting()