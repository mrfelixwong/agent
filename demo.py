#!/usr/bin/env python3
"""
Quick demo of the Meeting Agent system
Shows the complete workflow with mock components
"""

import sys
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import MeetingAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def demo_meeting_agent():
    """Demonstrate the Meeting Agent workflow"""
    print("🎙️ Meeting Agent Demo")
    print("=" * 30)
    
    # Initialize agent with mock components
    print("\n1. Initializing Meeting Agent...")
    agent = MeetingAgent(use_mock_components=True)
    print("   ✅ Agent initialized")
    
    # Show system status
    print("\n2. System Status:")
    status = agent.get_system_status()
    components = status.get('components', {})
    for component, details in components.items():
        comp_status = details.get('status', 'unknown')
        print(f"   {component}: {comp_status}")
    
    # Start a meeting
    print("\n3. Starting Demo Meeting...")
    meeting_info = agent.start_meeting(
        "Demo Meeting - Product Planning", 
        ["Alice (Product)", "Bob (Engineering)", "Charlie (Design)"]
    )
    print(f"   ✅ Meeting started: {meeting_info['name']}")
    print(f"   Meeting ID: {meeting_info['id']}")
    
    # Show real-time progress
    print("\n4. Recording Progress (5 seconds):")
    for i in range(5):
        status = agent.get_meeting_status()
        duration = status.get('meeting', {}).get('duration_seconds', 0)
        transcript = status.get('transcript', '')
        print(f"   {i+1}s - Duration: {duration}s, Transcript: {len(transcript)} chars")
        if transcript:
            # Show last 60 characters of transcript
            preview = transcript[-60:] if len(transcript) > 60 else transcript
            print(f"        Preview: ...{preview}")
        time.sleep(1)
    
    # Stop meeting
    print("\n5. Stopping Meeting and Processing...")
    completed = agent.stop_meeting()
    print(f"   ✅ Meeting completed: {completed['name']}")
    print(f"   Duration: {completed.get('duration_minutes', 0)} minutes")
    print(f"   Transcript: {len(completed.get('transcript', ''))} characters")
    
    # Show summary
    summary = completed.get('summary', {})
    if summary.get('executive_summary'):
        print(f"\n6. AI Summary Generated:")
        print(f"   Executive Summary: {summary['executive_summary']}")
        
        if summary.get('key_points'):
            print(f"   Key Points:")
            for point in summary['key_points'][:3]:
                print(f"   • {point}")
        
        if summary.get('action_items'):
            print(f"   Action Items:")
            for item in summary['action_items'][:3]:
                if isinstance(item, dict):
                    task = item.get('task', item.get('description', str(item)))
                    assignee = item.get('assignee', '')
                    due_date = item.get('due_date', '')
                    print(f"   • {task}" + (f" (Due: {due_date})" if due_date else "") + (f" - {assignee}" if assignee else ""))
                else:
                    print(f"   • {item}")
    
    # Show meeting history
    print(f"\n7. Meeting History:")
    history = agent.get_meeting_history()
    print(f"   Total meetings: {len(history)}")
    for meeting in history[:3]:
        name = meeting.get('name', 'Unknown')
        date = meeting.get('date', 'Unknown')
        print(f"   • {name} ({date})")
    
    # Generate daily summary
    print(f"\n8. Daily Summary:")
    daily_summary = agent.generate_daily_summary()
    print(f"   Date: {daily_summary.get('date', 'Unknown')}")
    print(f"   Total meetings: {daily_summary.get('total_meetings', 0)}")
    if daily_summary.get('daily_summary'):
        print(f"   Summary: {daily_summary['daily_summary']}")
    
    # Test email functionality
    print(f"\n9. Email Notifications:")
    email_success = agent.send_daily_summary_email()
    print(f"   Daily email sent: {email_success}")
    
    # Cleanup
    agent.cleanup()
    
    print(f"\n🎉 Demo Complete!")
    print(f"   The Meeting Agent successfully:")
    print(f"   • Recorded audio (simulated)")
    print(f"   • Transcribed speech in real-time")
    print(f"   • Generated AI-powered summaries")
    print(f"   • Sent email notifications")
    print(f"   • Stored all data in database")
    
    print(f"\n📝 Next Steps for Production:")
    print(f"   1. Set up OpenAI API keys in config/config.yaml")
    print(f"   2. Configure Gmail SMTP in config/config.yaml")
    print(f"   3. Install PyAudio: pip install pyaudio")
    print(f"   4. Run: python cli.py for interactive control")
    print(f"   5. Or run web interface from cli.py menu")


if __name__ == "__main__":
    demo_meeting_agent()