#!/usr/bin/env python3
"""
Simple OpenAI API test
"""

import os
import openai

def test_openai():
    """Test OpenAI client initialization and simple API call"""
    print("🤖 Simple OpenAI Test")
    print("=" * 20)
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY found")
        return False
    
    print(f"API Key: {api_key[:10]}...")
    print(f"OpenAI version: {openai.__version__}")
    
    try:
        print("\n1. Initializing OpenAI client...")
        client = openai.OpenAI(api_key=api_key)
        print("   ✅ Client initialized")
        
        print("\n2. Testing simple API call...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper model for testing
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one word."}
            ],
            max_tokens=10
        )
        
        if response.choices and response.choices[0].message.content:
            print(f"   ✅ API Response: {response.choices[0].message.content}")
            return True
        else:
            print("   ❌ Empty response")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   Error type: {type(e)}")
        return False

if __name__ == "__main__":
    test_openai()