#!/usr/bin/env python3
"""
Test real API integrations with user's API keys
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def test_config_loading():
    """Test if configuration loads properly with API keys"""
    print("🔧 Testing Configuration Loading...")
    
    try:
        config = load_config()
        
        # Check OpenAI API key
        openai_key = config.get('openai.api_key')
        if openai_key and openai_key != '${OPENAI_API_KEY}' and 'sk-' in openai_key:
            print(f"   ✅ OpenAI API Key: Found (starts with: {openai_key[:10]}...)")
        else:
            print(f"   ❌ OpenAI API Key: Not found or invalid")
            print(f"      Current value: {openai_key}")
            return False
            
        # Check Email configuration
        email_address = config.get('email.address')
        email_password = config.get('email.password')
        
        if email_address and '@' in email_address and email_address != '${EMAIL_ADDRESS}':
            print(f"   ✅ Email Address: {email_address}")
        else:
            print(f"   ❌ Email Address: Not found or invalid")
            print(f"      Current value: {email_address}")
            
        if email_password and email_password != '${EMAIL_PASSWORD}' and len(email_password) > 8:
            print(f"   ✅ Email Password: Found ({len(email_password)} chars)")
        else:
            print(f"   ❌ Email Password: Not found or invalid")
            print(f"      Current value: {email_password}")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration loading failed: {e}")
        return False


def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🤖 Testing OpenAI Connection...")
    
    try:
        from src.transcription.transcriber import Transcriber
        from src.ai.summarizer import Summarizer
        
        config = load_config()
        api_key = config.get('openai.api_key')
        
        if not api_key or 'sk-' not in api_key:
            print("   ❌ No valid OpenAI API key found")
            return False
            
        # Test summarizer (quicker than transcriber)
        print("   Testing AI Summarizer...")
        summarizer = Summarizer(api_key=api_key)
        
        # Test with a simple summary request
        test_transcript = "This is a test meeting. We discussed project timelines and budget allocation. The team agreed on next steps."
        summary = summarizer.summarize_meeting(
            transcript=test_transcript,
            meeting_name="API Test Meeting",
            participants=["Test User"],
            duration_minutes=1
        )
        
        if summary and summary.get('executive_summary'):
            print(f"   ✅ OpenAI API working")
            print(f"   Response: {summary['executive_summary'][:100]}...")
            return True
        else:
            print(f"   ❌ OpenAI API returned invalid response")
            return False
            
    except Exception as e:
        print(f"   ❌ OpenAI connection failed: {e}")
        return False


def test_email_connection():
    """Test email SMTP connection"""
    print("\n📧 Testing Email Connection...")
    
    try:
        from src.notifications.sender import EmailSender
        
        config = load_config()
        email_address = config.get('email.address')
        email_password = config.get('email.password')
        
        if not email_address or not email_password:
            print("   ❌ Email credentials not found")
            return False
            
        sender = EmailSender(
            email_address=email_address,
            email_password=email_password,
            smtp_server=config.get('email.smtp_server', 'smtp.gmail.com'),
            smtp_port=config.get('email.smtp_port', 587)
        )
        
        # Test connection (without sending)
        connection_ok = sender.test_connection()
        
        if connection_ok:
            print(f"   ✅ Email SMTP connection successful")
            return True
        else:
            print(f"   ❌ Email SMTP connection failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Email connection failed: {e}")
        return False


def main():
    """Main test runner"""
    print("🚀 Real API Integration Test")
    print("=" * 40)
    
    all_passed = True
    
    # Test 1: Configuration loading
    if not test_config_loading():
        all_passed = False
        print("\n❌ Configuration test failed. Please check your API keys are set correctly.")
        print("\nOptions:")
        print("1. Set environment variables:")
        print("   export OPENAI_API_KEY='sk-your-key-here'")
        print("   export EMAIL_ADDRESS='your-email@gmail.com'")
        print("   export EMAIL_PASSWORD='your-app-password'")
        print("\n2. Or modify config/settings.yml directly with your keys")
        return 1
    
    # Test 2: OpenAI connection
    if not test_openai_connection():
        all_passed = False
    
    # Test 3: Email connection  
    if not test_email_connection():
        all_passed = False
    
    print("\n" + "=" * 40)
    
    if all_passed:
        print("🎉 ALL API TESTS PASSED!")
        print("\nReady to run with real APIs:")
        print("• python real_demo.py")
        print("• Or modify cli.py to use use_mock_components=False")
        return 0
    else:
        print("❌ Some API tests failed")
        print("Please check your configuration and try again")
        return 1


if __name__ == "__main__":
    sys.exit(main())