#!/usr/bin/env python3
"""
Simple test to verify the start meeting functionality works
"""

import requests
import json
import time

def test_start_meeting():
    """Test starting a meeting via the API"""
    print("🧪 Testing Start Meeting Functionality\n")
    
    # Test 1: Check if server is running
    print("1. Checking server connectivity...")
    try:
        response = requests.get("http://127.0.0.1:5003/")
        if response.status_code == 200:
            print("   ✅ Server is running on port 5003")
        else:
            print(f"   ❌ Server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        print("   Make sure the app is running with: python app.py")
        return False
    
    # Test 2: Test the API endpoint
    print("\n2. Testing /api/start_meeting endpoint...")
    test_data = {
        "name": "Simple Test Meeting",
        "participants": ["Test User"],
        "_csrf_token": "test-token"  # Will be bypassed
    }
    
    try:
        print(f"   Sending: {json.dumps(test_data, indent=2)}")
        response = requests.post(
            "http://127.0.0.1:5003/api/start_meeting",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response data: {json.dumps(data, indent=2)}")
            
            if data.get("success"):
                print("   ✅ Meeting started successfully!")
                print(f"   Meeting ID: {data['meeting']['id']}")
                print(f"   Meeting Name: {data['meeting']['name']}")
                return True
            else:
                print(f"   ❌ API returned error: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw response: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    return False

def test_with_javascript():
    """Generate JavaScript code to test from browser console"""
    print("\n3. JavaScript test code for browser console:")
    print("   Copy and paste this into your browser's developer console:")
    print("   " + "="*50)
    
    js_code = """
// Test start meeting from browser console
fetch('/api/start_meeting', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        name: 'Browser Console Test',
        participants: [],
        _csrf_token: 'console-test'
    })
})
.then(response => {
    console.log('Response status:', response.status);
    return response.json();
})
.then(data => {
    console.log('Response data:', data);
    if (data.success) {
        console.log('✅ Success! Meeting ID:', data.meeting.id);
    } else {
        console.error('❌ Error:', data.error);
    }
})
.catch(error => {
    console.error('❌ Fetch error:', error);
});
"""
    print(js_code)
    print("   " + "="*50)

if __name__ == "__main__":
    # Run the test
    success = test_start_meeting()
    
    # Show JavaScript test code
    test_with_javascript()
    
    # Summary
    print("\n📊 Test Summary:")
    if success:
        print("   ✅ API is working correctly!")
        print("   The issue is likely in the frontend JavaScript or event binding.")
    else:
        print("   ❌ API test failed. Check the errors above.")
    
    print("\n💡 Next Steps:")
    print("   1. Open http://127.0.0.1:5003/debug_start_button.html in your browser")
    print("   2. Run through each test to identify where the issue occurs")
    print("   3. Check browser console for JavaScript errors (F12 -> Console)")