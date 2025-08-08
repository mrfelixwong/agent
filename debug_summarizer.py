#!/usr/bin/env python3
"""
Debug AI Summarizer test
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_summarizer():
    """Test AI Summarizer in detail"""
    print("🤖 AI Summarizer Debug Test")
    print("=" * 25)
    
    try:
        from src.ai.summarizer import Summarizer, MockSummarizer
        
        api_key = os.environ.get('OPENAI_API_KEY')
        print(f"API Key available: {'Yes' if api_key else 'No'}")
        
        # Test real summarizer
        print("\n1. Testing Real Summarizer...")
        summarizer = Summarizer(api_key=api_key)
        print("   Summarizer created successfully")
        
        summary = summarizer.summarize_meeting(
            transcript="Test meeting about project status.",
            meeting_name="Test",
            participants=["Alice"],
            duration_minutes=1
        )
        
        print(f"   Summary returned: {type(summary)}")
        print(f"   Has executive_summary: {'executive_summary' in summary}")
        
        if summary.get('executive_summary'):
            print("   ✅ Real summarizer working")
            print(f"   Summary: {summary['executive_summary']}")
        else:
            print("   ❌ No executive summary found")
            print(f"   Full response: {summary}")
        
        # Test mock summarizer
        print("\n2. Testing Mock Summarizer...")
        mock_summarizer = MockSummarizer()
        mock_summary = mock_summarizer.summarize_meeting("test transcript", "Test Meeting")
        print(f"   Mock summary has executive_summary: {'executive_summary' in mock_summary}")
        
        if mock_summary.get('executive_summary'):
            print("   ✅ Mock summarizer working")
        else:
            print("   ❌ Mock summarizer failed")
            print(f"   Mock response: {mock_summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ Summarizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_summarizer()