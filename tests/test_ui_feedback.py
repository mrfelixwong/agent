#!/usr/bin/env python3
"""
Test the improved UI feedback and timer functionality
"""

import time
import requests
import json

API_BASE = "http://127.0.0.1:5004"

def test_ui_workflow():
    print("🧪 Testing improved UI workflow...")
    
    # Start meeting
    print("\n1. Starting meeting with improved feedback...")
    start_data = {
        "name": "UI Test Meeting",
        "participants": []
    }
    
    response = requests.post(
        f"{API_BASE}/api/start_meeting",
        json=start_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Meeting started successfully")
            meeting_id = result['meeting']['id']
            
            # Let it record for a few seconds
            print("   ⏱️  Letting meeting record for 8 seconds...")
            time.sleep(8)
            
            # Stop meeting
            print("   🛑 Stopping meeting...")
            stop_response = requests.post(
                f"{API_BASE}/api/stop_meeting",
                json={},
                headers={"Content-Type": "application/json"}
            )
            
            if stop_response.status_code == 200:
                stop_result = stop_response.json()
                if stop_result.get('success'):
                    transcript = stop_result['meeting'].get('transcript', '')
                    print(f"   ✅ Meeting stopped successfully")
                    print(f"   📝 Transcript: '{transcript[:100]}{'...' if len(transcript) > 100 else ''}'")
                    print(f"   📊 Status: {stop_result['meeting'].get('status')}")
                    return True
                else:
                    print(f"   ❌ Stop failed: {stop_result.get('error')}")
            else:
                print(f"   ❌ Stop API failed: {stop_response.status_code}")
        else:
            print(f"   ❌ Start failed: {result.get('error')}")
    else:
        print(f"   ❌ Start API failed: {response.status_code}")
    
    return False

if __name__ == "__main__":
    success = test_ui_workflow()
    print(f"\n🎯 Test {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)