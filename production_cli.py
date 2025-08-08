#!/usr/bin/env python3
"""
Production CLI for Meeting Agent with Real Components
Uses real audio recording, transcription, and AI processing
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


class ProductionMeetingAgentCLI:
    """Production CLI with real components"""
    
    def __init__(self):
        self.agent = None
        self.running = True
        
    def start(self):
        """Start the production CLI"""
        print("🎙️ Meeting Agent - Production Mode")
        print("=" * 35)
        
        try:
            # Initialize agent with REAL components
            print("Initializing Meeting Agent with real components...")
            print("⚠️  This will use:")
            print("   • Real audio recording (PyAudio)")
            print("   • Real OpenAI transcription (Whisper)")
            print("   • Real OpenAI summarization (GPT-4)")
            print("   • Real email notifications (if configured)")
            
            self.agent = MeetingAgent(use_mock_components=False)
            print("✅ Production Meeting Agent initialized successfully\n")
            
            # Show system status
            self.show_status()
            print()
            
            # Main CLI loop
            self.cli_loop()
            
        except Exception as e:
            print(f"❌ Failed to initialize Production Meeting Agent: {e}")
            print("\nCommon issues:")
            print("• Missing OpenAI API key (set OPENAI_API_KEY)")
            print("• PyAudio not installed (run: pip install pyaudio)")
            print("• No microphone access permissions")
            sys.exit(1)
        
        finally:
            if self.agent:
                self.agent.cleanup()
    
    def show_status(self):
        """Show production system status"""
        try:
            status = self.agent.get_system_status()
            meeting_status = self.agent.get_meeting_status()
            
            print("📊 Production System Status:")
            print(f"  Overall: {status.get('status', 'Unknown')}")
            
            components = status.get('components', {})
            for component, details in components.items():
                comp_status = details.get('status', 'unknown')
                if comp_status == 'connected' or comp_status == 'available':
                    status_icon = "✅"
                elif comp_status == 'disconnected':
                    status_icon = "❌"
                else:
                    status_icon = "⚠️"
                print(f"  {component}: {status_icon} {comp_status}")
            
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
                print("\n📋 Production Commands:")
                print("  1. Start Real Meeting Recording")
                print("  2. Stop Meeting & Generate AI Summary") 
                print("  3. Show System Status")
                print("  4. Meeting History")
                print("  5. Generate Daily Summary")
                print("  6. Search Meetings")
                print("  7. Test Audio Devices")
                print("  8. Start Web Interface")
                print("  0. Exit")
                
                choice = input("\nSelect option (0-8): ").strip()
                
                if choice == "0":
                    self.running = False
                    print("👋 Goodbye!")
                    
                elif choice == "1":
                    self.start_real_meeting()
                    
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
                    self.test_audio_devices()
                    
                elif choice == "8":
                    self.start_web_interface()
                    
                else:
                    print("❌ Invalid choice. Please select 0-8.")
                    
            except KeyboardInterrupt:
                self.running = False
                print("\n👋 Goodbye!")
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def start_real_meeting(self):
        """Start a real meeting with audio recording"""
        try:
            meeting_name = input("Enter meeting name: ").strip()
            if not meeting_name:
                print("❌ Meeting name cannot be empty")
                return
            
            participants_input = input("Enter participants (comma-separated, optional): ").strip()
            participants = [p.strip() for p in participants_input.split(",") if p.strip()] if participants_input else []
            
            print(f"\n🎬 Starting REAL meeting recording: {meeting_name}")
            print("⚠️  This will:")
            print("   • Start recording your system audio")
            print("   • Begin real-time transcription")
            print("   • Process audio with OpenAI Whisper")
            
            confirm = input("\nStart recording? (y/n): ").lower()
            if confirm != 'y':
                print("Recording cancelled")
                return
            
            meeting_info = self.agent.start_meeting(meeting_name, participants)
            
            print(f"\n✅ REAL RECORDING STARTED!")
            print(f"   Meeting ID: {meeting_info['id']}")
            print(f"   Name: {meeting_info['name']}")
            print(f"   Participants: {', '.join(meeting_info.get('participants', []))}")
            print(f"   Audio file: {meeting_info.get('audio_file_path', 'N/A')}")
            
            # Show real-time transcript updates
            print(f"\n📝 Live Transcript (Press Ctrl+C to stop viewing):")
            print("   🔴 RECORDING - Speak into your microphone")
            print("   " + "="*50)
            
            try:
                while True:
                    time.sleep(2)
                    status = self.agent.get_meeting_status()
                    
                    if status.get('status') != 'recording':
                        break
                        
                    transcript = status.get('transcript', '')
                    duration = status.get('meeting', {}).get('duration_seconds', 0)
                    
                    # Clear previous lines and show updated transcript
                    print(f"\r   Duration: {duration}s", end="")
                    
                    if transcript and transcript.strip():
                        # Show last 150 characters of transcript
                        recent_transcript = transcript[-150:] if len(transcript) > 150 else transcript
                        print(f"\n   Latest: ...{recent_transcript}")
                    else:
                        print(f" | Listening for audio...")
                        
            except KeyboardInterrupt:
                print(f"\n   [Stopped showing live transcript]")
                print(f"   Recording continues in background...")
                print(f"   Use option 2 to stop and process")
                    
        except Exception as e:
            print(f"❌ Failed to start real meeting: {e}")
    
    def stop_meeting(self):
        """Stop current meeting and process with real AI"""
        try:
            print("🛑 Stopping meeting and processing with AI...")
            print("   This may take a few moments for:")
            print("   • Final transcription processing")
            print("   • AI summary generation (GPT-4)")
            print("   • Email notification sending")
            
            meeting_info = self.agent.stop_meeting()
            
            print(f"\n✅ REAL MEETING PROCESSED!")
            print(f"   Name: {meeting_info.get('name', 'Unknown')}")
            print(f"   Duration: {meeting_info.get('duration_minutes', 0)} minutes")
            print(f"   Transcript: {len(meeting_info.get('transcript', ''))} characters")
            
            # Show real AI summary
            summary = meeting_info.get('summary', {})
            if summary and summary.get('executive_summary'):
                print(f"\n🤖 REAL AI SUMMARY GENERATED:")
                print(f"📋 Executive Summary:")
                print(f"   {summary['executive_summary']}")
                
                if summary.get('key_points'):
                    print(f"\n🔑 Key Points:")
                    for i, point in enumerate(summary['key_points'][:3], 1):
                        print(f"   {i}. {point}")
                
                if summary.get('action_items'):
                    print(f"\n📝 Action Items:")
                    for i, item in enumerate(summary['action_items'][:3], 1):
                        if isinstance(item, dict):
                            print(f"   {i}. {item.get('task', item)}")
                        else:
                            print(f"   {i}. {item}")
                            
                if summary.get('decisions_made'):
                    print(f"\n✅ Decisions Made:")
                    for i, decision in enumerate(summary['decisions_made'][:3], 1):
                        print(f"   {i}. {decision}")
            
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
            
            for i, meeting in enumerate(meetings[:10], 1):
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
        """Generate daily summary with real AI"""
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
            
            print("🤖 Generating daily summary with real AI...")
            
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
    
    def test_audio_devices(self):
        """Test available audio devices"""
        try:
            print("🎤 Testing Audio Devices...")
            
            devices = self.agent.audio_recorder.get_audio_devices()
            
            print(f"\nAvailable Audio Devices ({len(devices)} found):")
            for i, device in enumerate(devices):
                name = device.get('name', 'Unknown')
                channels = device.get('maxInputChannels', 0)
                sample_rate = device.get('defaultSampleRate', 0)
                print(f"   {i}: {name} ({channels} input channels, {sample_rate} Hz)")
            
            default_device = self.agent.audio_recorder.get_default_device()
            if default_device:
                print(f"\nDefault Device: {default_device.get('name', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Failed to test audio devices: {e}")
    
    def start_web_interface(self):
        """Start web interface"""
        try:
            print("🌐 Starting Web Interface...")
            print("   This will start a web server at http://localhost:5002")
            print("   Features available:")
            print("   • Meeting dashboard")
            print("   • Start/stop meeting controls") 
            print("   • Meeting history")
            print("   • System status")
            print("   Press Ctrl+C to stop the web server and return to CLI")
            
            from src.web.app import create_simple_app
            
            app = create_simple_app(self.agent)
            
            try:
                print(f"\n🚀 Web server starting...")
                print(f"📱 Open your browser to: http://localhost:5002")
                app.run(host='localhost', port=5002, debug=False)
            except KeyboardInterrupt:
                print("\n   Web server stopped")
            
        except ImportError:
            print("❌ Flask not available. Install with: pip install flask")
        except Exception as e:
            print(f"❌ Failed to start web interface: {e}")


def main():
    """Main entry point"""
    # Set up signal handlers
    cli = ProductionMeetingAgentCLI()
    
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down...")
        cli.running = False
        if cli.agent:
            cli.agent.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start production CLI
    cli.start()


if __name__ == "__main__":
    main()