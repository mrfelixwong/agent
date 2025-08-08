#!/usr/bin/env python3
"""
Command-line interface for Meeting Agent
Provides a simple CLI for testing and controlling the meeting agent
"""

import sys
import time
import signal
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import MeetingAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MeetingAgentCLI:
    """Command-line interface for Meeting Agent"""
    
    def __init__(self):
        self.agent = None
        self.running = True
        
    def start(self):
        """Start the CLI"""
        print("🎙️ Meeting Agent CLI")
        print("=" * 30)
        
        try:
            # Initialize agent with mock components for testing
            print("Initializing Meeting Agent...")
            self.agent = MeetingAgent(use_mock_components=True)
            print("✅ Meeting Agent initialized successfully\n")
            
            # Show system status
            self.show_status()
            print()
            
            # Main CLI loop
            self.cli_loop()
            
        except Exception as e:
            print(f"❌ Failed to initialize Meeting Agent: {e}")
            sys.exit(1)
        
        finally:
            if self.agent:
                self.agent.cleanup()
    
    def show_status(self):
        """Show system status"""
        try:
            status = self.agent.get_system_status()
            meeting_status = self.agent.get_meeting_status()
            
            print("📊 System Status:")
            print(f"  Overall: {status.get('status', 'Unknown')}")
            
            components = status.get('components', {})
            for component, details in components.items():
                comp_status = details.get('status', 'unknown')
                print(f"  {component}: {comp_status}")
            
            print(f"\n🎬 Meeting Status: {meeting_status.get('status', 'Unknown')}")
            
            if meeting_status.get('meeting'):
                meeting = meeting_status['meeting']
                print(f"  Current Meeting: {meeting.get('name', 'Unknown')}")
                print(f"  Duration: {meeting.get('duration_seconds', 0):.0f} seconds")
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    def cli_loop(self):
        """Main CLI interaction loop"""
        while self.running:
            try:
                print("\n📋 Commands:")
                print("  1. Start Meeting")
                print("  2. Stop Meeting") 
                print("  3. Show Status")
                print("  4. Meeting History")
                print("  5. Generate Daily Summary")
                print("  6. Search Meetings")
                print("  7. Test Web Interface")
                print("  0. Exit")
                
                choice = input("\nSelect option (0-7): ").strip()
                
                if choice == "0":
                    self.running = False
                    print("👋 Goodbye!")
                    
                elif choice == "1":
                    self.start_meeting()
                    
                elif choice == "2":
                    self.stop_meeting()
                    
                elif choice == "3":
                    self.show_status()
                    
                elif choice == "4":
                    self.show_meeting_history()
                    
                elif choice == "5":
                    self.generate_daily_summary()
                    
                elif choice == "6":
                    self.search_meetings()
                    
                elif choice == "7":
                    self.start_web_interface()
                    
                else:
                    print("❌ Invalid choice. Please select 0-7.")
                    
            except KeyboardInterrupt:
                self.running = False
                print("\n👋 Goodbye!")
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def start_meeting(self):
        """Start a new meeting"""
        try:
            meeting_name = input("Enter meeting name: ").strip()
            if not meeting_name:
                print("❌ Meeting name cannot be empty")
                return
            
            participants_input = input("Enter participants (comma-separated, optional): ").strip()
            participants = [p.strip() for p in participants_input.split(",") if p.strip()] if participants_input else []
            
            print(f"🎬 Starting meeting: {meeting_name}")
            
            meeting_info = self.agent.start_meeting(meeting_name, participants)
            
            print(f"✅ Meeting started successfully!")
            print(f"   Meeting ID: {meeting_info['id']}")
            print(f"   Name: {meeting_info['name']}")
            print(f"   Participants: {', '.join(meeting_info.get('participants', []))}")
            print(f"   Audio file: {meeting_info.get('audio_file_path', 'N/A')}")
            
            # Show real-time updates for a few seconds
            print(f"\n📝 Real-time transcript (showing for 10 seconds):")
            for i in range(10):
                try:
                    status = self.agent.get_meeting_status()
                    transcript = status.get('transcript', '')
                    if transcript and transcript.strip():
                        print(f"   {transcript[-100:]}...")  # Show last 100 chars
                    else:
                        print(f"   [Recording... {i+1}s]")
                    time.sleep(1)
                except KeyboardInterrupt:
                    print("\n   [Stopped showing transcript]")
                    break
                    
        except Exception as e:
            print(f"❌ Failed to start meeting: {e}")
    
    def stop_meeting(self):
        """Stop the current meeting"""
        try:
            print("🛑 Stopping current meeting...")
            
            meeting_info = self.agent.stop_meeting()
            
            print(f"✅ Meeting stopped successfully!")
            print(f"   Name: {meeting_info.get('name', 'Unknown')}")
            print(f"   Duration: {meeting_info.get('duration_minutes', 0)} minutes")
            print(f"   Transcript length: {len(meeting_info.get('transcript', ''))} characters")
            
            # Show summary if available
            summary = meeting_info.get('summary', {})
            if summary and summary.get('executive_summary'):
                print(f"\n📋 Executive Summary:")
                print(f"   {summary['executive_summary']}")
                
                if summary.get('key_points'):
                    print(f"\n🔑 Key Points:")
                    for point in summary['key_points'][:3]:  # Show first 3
                        print(f"   • {point}")
                
                if summary.get('action_items'):
                    print(f"\n📝 Action Items:")
                    for item in summary['action_items'][:3]:  # Show first 3
                        if isinstance(item, dict):
                            print(f"   • {item.get('task', item)}")
                        else:
                            print(f"   • {item}")
            
        except Exception as e:
            print(f"❌ Failed to stop meeting: {e}")
    
    def show_meeting_history(self):
        """Show recent meeting history"""
        try:
            print("📚 Recent Meeting History:")
            
            meetings = self.agent.get_meeting_history(days_back=7)
            
            if not meetings:
                print("   No meetings found")
                return
            
            print(f"   Found {len(meetings)} meetings in the last 7 days\n")
            
            for i, meeting in enumerate(meetings[:10], 1):  # Show last 10
                name = meeting.get('name', 'Unknown')
                date_str = str(meeting.get('date', 'Unknown'))
                duration = meeting.get('duration_minutes', 0)
                status = meeting.get('status', 'Unknown')
                
                print(f"   {i:2d}. {name}")
                print(f"       Date: {date_str}, Duration: {duration}min, Status: {status}")
                
                if meeting.get('participants'):
                    participants = ', '.join(meeting['participants'])
                    print(f"       Participants: {participants}")
                
                print()
                
        except Exception as e:
            print(f"❌ Failed to get meeting history: {e}")
    
    def generate_daily_summary(self):
        """Generate daily summary"""
        try:
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            
            target_date = None
            if date_input:
                from datetime import datetime
                try:
                    target_date = datetime.strptime(date_input, '%Y-%m-%d').date()
                except ValueError:
                    print("❌ Invalid date format. Use YYYY-MM-DD")
                    return
            
            print("🤖 Generating daily summary...")
            
            summary = self.agent.generate_daily_summary(target_date)
            
            print(f"✅ Daily Summary Generated:")
            print(f"   Date: {summary.get('date', 'Unknown')}")
            print(f"   Total Meetings: {summary.get('total_meetings', 0)}")
            print(f"   Total Duration: {summary.get('total_duration', 0)} minutes")
            
            if summary.get('daily_summary'):
                print(f"\n📋 Summary:")
                print(f"   {summary['daily_summary']}")
            
            if summary.get('key_themes'):
                print(f"\n🎯 Key Themes:")
                for theme in summary['key_themes']:
                    print(f"   • {theme}")
                    
        except Exception as e:
            print(f"❌ Failed to generate daily summary: {e}")
    
    def search_meetings(self):
        """Search meetings"""
        try:
            query = input("Enter search query: ").strip()
            
            if not query:
                print("❌ Search query cannot be empty")
                return
            
            print(f"🔍 Searching for: {query}")
            
            results = self.agent.search_meetings(query, limit=5)
            
            if not results:
                print("   No meetings found")
                return
            
            print(f"   Found {len(results)} meetings:")
            
            for i, meeting in enumerate(results, 1):
                name = meeting.get('name', 'Unknown')
                date_str = str(meeting.get('date', 'Unknown'))
                
                print(f"   {i}. {name} ({date_str})")
                
                # Show snippet if transcript exists
                transcript = meeting.get('transcript', '')
                if transcript:
                    # Find query in transcript for context
                    query_lower = query.lower()
                    transcript_lower = transcript.lower()
                    
                    if query_lower in transcript_lower:
                        start_idx = transcript_lower.find(query_lower)
                        start_context = max(0, start_idx - 50)
                        end_context = min(len(transcript), start_idx + len(query) + 50)
                        snippet = transcript[start_context:end_context]
                        print(f"      ...{snippet}...")
                
                print()
                
        except Exception as e:
            print(f"❌ Failed to search meetings: {e}")
    
    def start_web_interface(self):
        """Start web interface"""
        try:
            print("🌐 Starting web interface...")
            print("   This will start a web server at http://localhost:5000")
            print("   Press Ctrl+C to stop the web server and return to CLI")
            
            from src.web.app import create_simple_app
            
            app = create_simple_app(self.agent)
            
            try:
                app.run(host='localhost', port=5000, debug=False)
            except KeyboardInterrupt:
                print("\n   Web server stopped")
            
        except ImportError:
            print("❌ Flask not available. Install with: pip install flask")
        except Exception as e:
            print(f"❌ Failed to start web interface: {e}")


def main():
    """Main entry point"""
    # Set up signal handlers
    cli = MeetingAgentCLI()
    
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down...")
        cli.running = False
        if cli.agent:
            cli.agent.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start CLI
    cli.start()


if __name__ == "__main__":
    main()