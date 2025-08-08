#!/usr/bin/env python3
"""
Start web interface for Meeting Agent
Uses the simple web interface that doesn't require HTML templates
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import MeetingAgent
from src.web.app import create_simple_app, create_app


def start_web_interface():
    """Start the web interface"""
    print("🌐 Starting Meeting Agent Web Interface")
    print("=" * 40)
    
    try:
        # Initialize Meeting Agent
        print("Initializing Meeting Agent...")
        agent = MeetingAgent(use_mock_components=True)  # Use mock for web demo
        print("✅ Meeting Agent initialized")
        
        # Create web app with SocketIO support for real-time transcript
        print("Creating web interface...")
        try:
            app = create_app(meeting_agent=agent)
            socketio = app.socketio
            print("✅ Web interface with SocketIO created")
            use_socketio = True
        except ImportError:
            # Fall back to simple app if Flask-SocketIO is not available
            app = create_simple_app(agent)
            print("✅ Simple web interface created (no real-time features)")
            use_socketio = False
        
        print(f"\n🚀 Web Interface Starting!")
        print(f"📱 Open your browser to: http://localhost:5002")
        print(f"⚠️  Press Ctrl+C to stop the server")
        print(f"\nFeatures available:")
        print(f"• Meeting dashboard")
        print(f"• Start/stop meeting controls")
        print(f"• Meeting history")
        print(f"• System status")
        if use_socketio:
            print(f"• 🔴 Real-time transcript display during meetings")
        
        # Start the web server
        if use_socketio:
            socketio.run(app, host='localhost', port=5002, debug=False, allow_unsafe_werkzeug=True)
        else:
            app.run(host='localhost', port=5002, debug=False)
        
    except KeyboardInterrupt:
        print(f"\n👋 Web server stopped")
    except Exception as e:
        print(f"❌ Failed to start web interface: {e}")
        print(f"\nTroubleshooting:")
        print(f"• Make sure Flask is installed: pip install flask")
        print(f"• Check if port 5002 is available")
        print(f"• Try the production CLI instead: python production_cli.py")
    finally:
        if 'agent' in locals():
            agent.cleanup()


if __name__ == "__main__":
    start_web_interface()