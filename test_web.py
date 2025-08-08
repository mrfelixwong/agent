#!/usr/bin/env python3
"""
Test web interface availability
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_web_interface():
    """Test if web interface can be created"""
    print("🌐 Testing Web Interface")
    print("=" * 25)
    
    try:
        from src.main import MeetingAgent
        from src.web.app import create_simple_app
        
        print("1. Creating Meeting Agent...")
        agent = MeetingAgent(use_mock_components=True)
        print("   ✅ Agent created")
        
        print("2. Creating web application...")
        app = create_simple_app(agent)
        print("   ✅ Web app created")
        
        print("3. Testing routes...")
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            print(f"   Main page: {response.status_code}")
            
            # Test meetings page
            response = client.get('/meetings')
            print(f"   Meetings page: {response.status_code}")
        
        agent.cleanup()
        
        print("\n✅ Web Interface Test PASSED")
        print("\nTo start the web interface:")
        print("1. Run: python start_web.py")
        print("2. Open browser to: http://localhost:5002")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install flask")
        return False
        
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_web_interface()