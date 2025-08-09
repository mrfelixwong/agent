#!/usr/bin/env python3
"""
Simple test runner for Meeting Agent Web-Only System
"""

import sys
import os
import time
import subprocess
from pathlib import Path

def run_component_tests():
    """Run the component tests"""
    print("🧪 Running Meeting Agent Tests")
    print("=" * 40)
    
    try:
        result = subprocess.run([sys.executable, 'test_production.py'], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_web_startup():
    """Test if the web interface can start"""
    print("\n🌐 Testing Web Interface Startup")
    print("=" * 35)
    
    try:
        # Start the web interface in a subprocess
        print("Starting web interface...")
        process = subprocess.Popen([sys.executable, 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Give it a few seconds to start
        time.sleep(3)
        
        # Check if it's still running
        if process.poll() is None:
            print("✅ Web interface started successfully")
            print("📱 Interface should be available at http://127.0.0.1:5003")
            
            # Terminate the process
            process.terminate()
            process.wait(timeout=5)
            print("✅ Web interface stopped cleanly")
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ Web interface failed to start")
            print("Output:", stdout)
            print("Errors:", stderr)
            return False
            
    except Exception as e:
        print(f"❌ Web startup test failed: {e}")
        try:
            process.terminate()
        except:
            pass
        return False

def main():
    """Main test runner"""
    print("🎙️ Meeting Agent - Web-Only Test Suite")
    print("=" * 50)
    
    # Run component tests
    components_ok = run_component_tests()
    
    # Test web startup
    web_ok = test_web_startup()
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"   Web Interface: {'✅ PASS' if web_ok else '❌ FAIL'}")
    
    if components_ok and web_ok:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"\n🚀 Your Meeting Agent is ready to use:")
        print(f"   python app.py")
        return 0
    else:
        print(f"\n❌ Some tests failed")
        print(f"\n🔧 Troubleshooting:")
        print(f"   • Set OPENAI_API_KEY environment variable")
        print(f"   • Install dependencies: pip install flask flask-socketio pyaudio openai")
        return 1

if __name__ == "__main__":
    sys.exit(main())