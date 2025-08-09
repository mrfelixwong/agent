#!/usr/bin/env python3
"""
Test script to debug meeting transcription issue
"""

import time
import requests
import json

API_BASE = "http://127.0.0.1:5004"

def test_meeting_flow():
    print("🧪 Starting debug meeting test...")
    
    # Get initial status
    print("\n1. Getting initial status...")
    response = requests.get(f"{API_BASE}/api/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Status: {status}")
    else:
        print(f"   ❌ Status request failed: {response.status_code}")
        return
    
    # Start meeting
    print("\n2. Starting meeting...")
    start_data = {
        "name": "Debug Test Meeting",
        "participants": ["Debug User"]
    }
    
    # Get CSRF token first
    index_response = requests.get(f"{API_BASE}/")
    if index_response.status_code != 200:
        print(f"   ❌ Could not get index page for CSRF token")
        return
        
    # Extract CSRF token (simplified)
    csrf_token = "dummy"  # For testing, we'll handle CSRF in a simple way
    
    start_data["_csrf_token"] = csrf_token
    
    response = requests.post(
        f"{API_BASE}/api/start_meeting",
        json=start_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Meeting started: {result}")
    else:
        print(f"   ❌ Start meeting failed: {response.status_code} - {response.text}")
        return
    
    # Let meeting run for a bit
    print(f"\n3. Letting meeting run for 10 seconds...")
    time.sleep(10)
    
    # Check status during meeting
    print("\n4. Getting status during meeting...")
    response = requests.get(f"{API_BASE}/api/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Status during meeting: {status}")
    
    # Stop meeting
    print("\n5. Stopping meeting...")
    stop_data = {"_csrf_token": csrf_token}
    
    response = requests.post(
        f"{API_BASE}/api/stop_meeting", 
        json=stop_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Meeting stopped: {result}")
        
        # Check transcript
        meeting = result.get("meeting", {})
        transcript = meeting.get("transcript", "")
        print(f"   📝 Transcript length: {len(transcript)}")
        if transcript:
            print(f"   📝 Transcript preview: {transcript[:200]}...")
        else:
            print("   ❌ NO TRANSCRIPT GENERATED!")
            
    else:
        print(f"   ❌ Stop meeting failed: {response.status_code} - {response.text}")
    
    print("\n🧪 Debug test completed. Check logs for detailed debugging info!")

if __name__ == "__main__":
    test_meeting_flow()