#!/usr/bin/env python3
"""
Meeting Agent - Web-Only Application
Single entry point for the Meeting Agent with enhanced web interface
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import required components
from src.main import MeetingAgent
from src.web.app import create_app


def main():
    """Main entry point for Meeting Agent web application"""
    
    print("🎙️ Meeting Agent - Web Interface")
    print("=" * 40)
    
    # Get configuration from environment variables
    port = int(os.environ.get('PORT', 5003))  # Use 5003 as default (was working before)
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    host = os.environ.get('HOST', '127.0.0.1')  # Use 127.0.0.1 instead of localhost
    
    try:
        # Initialize Meeting Agent
        print("Initializing Meeting Agent...")
        agent = MeetingAgent()
        print("✅ Meeting Agent initialized successfully")
        
        # Create web application
        print("Creating web application...")
        app = create_app(meeting_agent=agent)
        print("✅ Web application created")
        
        # Display startup information
        print(f"\n🚀 Meeting Agent Starting!")
        print(f"📱 Web Interface: http://{host}:{port}")
        print(f"🔧 Debug Mode: {'ON' if debug else 'OFF'}")
        
        if not debug:
            print(f"⚠️  Press Ctrl+C to stop the server")
        
        print(f"\n✨ Features Available:")
        print(f"   • 🎙️  Start/Stop meeting recording")
        print(f"   • 📝 Meeting transcription with summaries")
        print(f"   • 🤖 AI-powered meeting summaries") 
        print(f"   • 📚 Meeting history and search")
        print(f"   • 📊 Daily summary generation")
        print(f"   • 📋 One-click ChatGPT format copying")
        
        print(f"\n🌐 Starting web server...")
        
        # Start the web server
        try:
            app.run(
                host=host, 
                port=port, 
                debug=debug
            )
        except OSError as e:
            if "Address already in use" in str(e) or "Permission denied" in str(e):
                print(f"\n❌ Port {port} is not available")
                print(f"🔧 Try a different port:")
                print(f"   PORT=8080 python app.py")
                print(f"   PORT=3000 python app.py") 
                print(f"   PORT=8000 python app.py")
                raise
            else:
                raise
        
    except KeyboardInterrupt:
        print(f"\n\n👋 Meeting Agent stopped by user")
        
    except Exception as e:
        print(f"\n❌ Failed to start Meeting Agent: {e}")
        
        print(f"\n🔧 Troubleshooting:")
        print(f"   • Ensure OPENAI_API_KEY environment variable is set")
        print(f"   • Check if port {port} is available")
        print(f"   • Install dependencies: pip install flask")
        print(f"   • For audio support: pip install pyaudio")
        
        return 1
        
    finally:
        # Cleanup
        try:
            if 'agent' in locals():
                agent.cleanup()
                print("✅ Cleanup completed")
        except:
            pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())