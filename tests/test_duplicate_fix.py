#!/usr/bin/env python3
"""
Test fix for duplicate meeting entries
"""

import time
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import MeetingAgent

def test_no_duplicates():
    print("🧪 Testing duplicate meeting fix...")
    
    agent = None
    try:
        # Initialize agent
        agent = MeetingAgent()
        print("✅ MeetingAgent initialized")
        
        # Get initial meeting count
        initial_meetings = agent.get_meeting_history(days_back=1)
        initial_count = len(initial_meetings)
        print(f"📊 Initial meeting count: {initial_count}")
        
        # Start a meeting
        meeting_name = "Duplicate Fix Test"
        meeting_info = agent.start_meeting(meeting_name, ["Test User"])
        meeting_id = meeting_info['id']
        print(f"✅ Meeting started: {meeting_name} (ID: {meeting_id})")
        
        # Check meeting count after start (should be +1)
        after_start_meetings = agent.get_meeting_history(days_back=1)
        after_start_count = len(after_start_meetings)
        print(f"📊 After start count: {after_start_count}")
        
        if after_start_count != initial_count + 1:
            print(f"❌ DUPLICATE CREATED! Expected {initial_count + 1}, got {after_start_count}")
            return False
        
        # Record briefly
        time.sleep(5)
        
        # Stop meeting
        completed_meeting = agent.stop_meeting()
        print(f"✅ Meeting stopped: {completed_meeting.get('name')}")
        
        # Check final meeting count (should still be +1)
        final_meetings = agent.get_meeting_history(days_back=1)
        final_count = len(final_meetings)
        print(f"📊 Final count: {final_count}")
        
        if final_count != initial_count + 1:
            print(f"❌ DUPLICATE FOUND! Expected {initial_count + 1}, got {final_count}")
            
            # Show the meetings for debugging
            print("Recent meetings:")
            for i, meeting in enumerate(final_meetings[:5]):
                print(f"  {i+1}. '{meeting.get('name')}' - {meeting.get('status')} - ID: {meeting.get('id')}")
                
            return False
        
        print("✅ No duplicates found!")
        
        # Extra check: ensure our meeting exists and is complete
        our_meetings = [m for m in final_meetings if m.get('name') == meeting_name]
        if len(our_meetings) != 1:
            print(f"❌ Found {len(our_meetings)} meetings with name '{meeting_name}', expected 1")
            return False
        
        our_meeting = our_meetings[0]
        if our_meeting.get('status') not in ['completed', 'summarized']:
            print(f"❌ Meeting status is '{our_meeting.get('status')}', expected completed/summarized")
            return False
        
        print(f"✅ Meeting properly completed with status: {our_meeting.get('status')}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if agent:
            agent.cleanup()

if __name__ == "__main__":
    success = test_no_duplicates()
    print(f"\n🎯 Test {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)