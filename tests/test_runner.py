#!/usr/bin/env python3
"""
Simple test runner for Meeting Agent components
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config_system():
    """Test the configuration system"""
    print("🔧 Testing Configuration System...")
    
    try:
        from src.utils.config import load_config, Config, _validate_config
        from unittest.mock import patch
        
        # Test Config class
        config_dict = {'key1': 'value1', 'nested': {'key2': 'value2'}}
        config = Config(config_dict)
        
        assert config.get('key1') == 'value1'
        assert config.get('nested.key2') == 'value2'
        assert config.get('nonexistent', 'default') == 'default'
        print("✅ Config class basic functionality")
        
        # Test validation
        valid_config = {
            'openai': {'api_key': 'test_key'},
            'email': {'address': 'test@example.com', 'password': 'password'}
        }
        _validate_config(valid_config)  # Should not raise
        print("✅ Config validation with valid config")
        
        # Test invalid config
        try:
            _validate_config({})
            assert False, "Should have raised ValueError"
        except ValueError:
            print("✅ Config validation catches missing keys")
        
        print("✅ Configuration system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration system test failed: {e}")
        return False


def test_helpers():
    """Test helper utilities"""
    print("\n🛠️ Testing Helper Utilities...")
    
    try:
        from src.utils.helpers import (
            format_duration, safe_filename, validate_email,
            truncate_text, format_file_size
        )
        
        # Test duration formatting
        assert format_duration(0) == "0s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(3661) == "1h 1m 1s"
        print("✅ Duration formatting")
        
        # Test safe filename
        assert safe_filename("normal_file.txt") == "normal_file.txt"
        assert safe_filename("file<>:\"/\\|?*name.txt") == "file_name.txt"
        assert safe_filename("") == "unnamed"
        print("✅ Safe filename generation")
        
        # Test email validation
        assert validate_email("test@example.com") is True
        assert validate_email("invalid") is False
        assert validate_email("") is False
        print("✅ Email validation")
        
        # Test text truncation
        assert truncate_text("Short text", 100) == "Short text"
        assert truncate_text("Very long text", 10) == "Very lo..."
        print("✅ Text truncation")
        
        # Test file size formatting
        assert format_file_size(0) == "0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1048576) == "1.0 MB"
        print("✅ File size formatting")
        
        print("✅ Helper utilities tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Helper utilities test failed: {e}")
        return False


def test_logger():
    """Test logging utilities"""
    print("\n📝 Testing Logger...")
    
    try:
        from src.utils.logger import setup_logger
        import tempfile
        import logging
        
        # Test basic logger setup
        logger = setup_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        print("✅ Basic logger setup")
        
        # Test logger with file
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            file_logger = setup_logger("file_logger", log_file=log_file)
            
            assert len(file_logger.handlers) >= 2  # Console + file
            assert os.path.exists(log_file)
            print("✅ Logger with file output")
        
        # Test different log levels
        debug_logger = setup_logger("debug_logger", level="DEBUG")
        assert debug_logger.level == logging.DEBUG
        print("✅ Custom log levels")
        
        print("✅ Logger tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Logger test failed: {e}")
        return False


def test_audio_system():
    """Test the audio recording system"""
    print("\n🎙️ Testing Audio Recording System...")
    
    try:
        # Import the test function from the audio tests
        from tests.test_audio_recorder import run_audio_tests
        
        return run_audio_tests()
        
    except Exception as e:
        print(f"❌ Audio system test failed: {e}")
        return False


def test_transcription_system():
    """Test the transcription system"""
    print("\n🎤 Testing Transcription System...")
    
    try:
        # Test transcription directly here due to import issues
        from src.transcription.transcriber import Transcriber, MockTranscriber
        from unittest.mock import patch, MagicMock
        import time
        
        # Test MockTranscriber basic functionality
        mock_transcriber = MockTranscriber()
        assert mock_transcriber.model == "mock-whisper-1"
        assert not mock_transcriber.is_transcribing
        print("    ✅ Mock transcriber initialization")
        
        # Test mock transcription lifecycle
        mock_transcriber.set_mock_transcript("Test transcript")
        mock_transcriber.set_mock_delay(0.1)
        
        success = mock_transcriber.start_transcription()
        assert success is True
        assert mock_transcriber.is_transcribing
        
        time.sleep(0.2)
        
        final_transcript = mock_transcriber.stop_transcription()
        assert not mock_transcriber.is_transcribing
        assert len(final_transcript) > 0
        print("    ✅ Mock transcription lifecycle")
        
        # Test audio chunk handling
        mock_transcriber.start_transcription()
        success = mock_transcriber.add_audio_chunk(b"test_audio")
        assert success is True
        mock_transcriber.stop_transcription()
        print("    ✅ Audio chunk handling")
        
        # Test mocked real transcriber
        mock_openai = MagicMock()
        mock_openai.OpenAI.return_value = MagicMock()
        
        with patch('src.transcription.transcriber.openai', mock_openai):
            real_transcriber = Transcriber(api_key="test_key")
            assert real_transcriber.model == "whisper-1"
            assert not real_transcriber.is_transcribing
        print("    ✅ Real transcriber with mocked API")
        
        print("✅ Transcription system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Transcription system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_summarization_system():
    """Test the AI summarization system"""
    print("\n🤖 Testing AI Summarization System...")
    
    try:
        # Test summarization directly here
        from src.ai.summarizer import Summarizer, MockSummarizer
        from unittest.mock import patch, MagicMock
        
        # Test MockSummarizer basic functionality
        mock_summarizer = MockSummarizer()
        assert mock_summarizer.model == "mock-gpt-4"
        assert mock_summarizer.max_tokens == 1500
        print("    ✅ Mock summarizer initialization")
        
        # Test mock meeting summarization
        transcript = "This is a test meeting transcript about project planning and budget allocation."
        summary = mock_summarizer.summarize_meeting(
            transcript=transcript,
            meeting_name="Test Meeting",
            participants=["Alice", "Bob"],
            duration_minutes=45
        )
        
        assert 'executive_summary' in summary
        assert 'key_points' in summary
        assert summary['meeting_name'] == "Test Meeting"
        assert summary['participants'] == ["Alice", "Bob"]
        print("    ✅ Mock meeting summarization")
        
        # Test action item extraction
        action_items = mock_summarizer.extract_action_items(transcript)
        assert isinstance(action_items, list)
        assert len(action_items) > 0
        print("    ✅ Mock action item extraction")
        
        # Test daily summary generation
        meeting_summaries = [
            {'meeting_name': 'Meeting 1', 'duration_minutes': 30},
            {'meeting_name': 'Meeting 2', 'duration_minutes': 45}
        ]
        daily_summary = mock_summarizer.generate_daily_summary(meeting_summaries)
        assert daily_summary['total_meetings'] == 2
        assert daily_summary['total_duration'] == 75
        print("    ✅ Mock daily summary generation")
        
        # Test mocked real summarizer
        mock_openai = MagicMock()
        mock_openai.OpenAI.return_value = MagicMock()
        
        with patch('src.ai.summarizer.openai', mock_openai):
            real_summarizer = Summarizer(api_key="test_key", model="gpt-4")
            assert real_summarizer.model == "gpt-4"
            assert real_summarizer.max_tokens == 1500
        print("    ✅ Real summarizer with mocked API")
        
        print("✅ AI Summarization system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ AI Summarization system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_email_system():
    """Test the email system"""
    print("\n📧 Testing Email System...")
    
    try:
        # Test email system directly here
        from src.notifications.sender import EmailSender, MockEmailSender
        from unittest.mock import patch, MagicMock
        
        # Test MockEmailSender basic functionality
        mock_sender = MockEmailSender()
        assert mock_sender.email_address == "test@example.com"
        assert mock_sender.smtp_server == "mock.smtp.server"
        print("    ✅ Mock email sender initialization")
        
        # Test mock meeting summary email
        summary = {
            'meeting_name': 'Test Meeting',
            'participants': ['Alice', 'Bob'],
            'duration_minutes': 30,
            'executive_summary': 'Test summary',
            'key_points': ['Point 1', 'Point 2'],
            'action_items': [{'task': 'Test task', 'assignee': 'Alice'}]
        }
        
        success = mock_sender.send_meeting_summary(summary)
        assert success is True
        
        sent_emails = mock_sender.get_sent_emails()
        assert len(sent_emails) == 1
        assert sent_emails[0]['type'] == 'meeting_summary'
        print("    ✅ Mock meeting summary email")
        
        # Test mock daily summary email
        daily_summary = {
            'total_meetings': 2,
            'total_duration': 90,
            'daily_summary': 'Productive day',
            'key_themes': ['Planning', 'Review']
        }
        
        success = mock_sender.send_daily_summary(daily_summary)
        assert success is True
        
        sent_emails = mock_sender.get_sent_emails()
        assert len(sent_emails) == 2
        assert sent_emails[1]['type'] == 'daily_summary'
        print("    ✅ Mock daily summary email")
        
        # Test custom email
        success = mock_sender.send_custom_email(
            "test@example.com", 
            "Test Subject", 
            "Test content"
        )
        assert success is True
        print("    ✅ Mock custom email")
        
        # Test connection testing
        assert mock_sender.test_connection() is True
        print("    ✅ Mock connection test")
        
        # Test mocked real email sender
        with patch.dict(os.environ, {
            'EMAIL_ADDRESS': 'test@gmail.com',
            'EMAIL_PASSWORD': 'test_password'
        }):
            real_sender = EmailSender()
            assert real_sender.email_address == 'test@gmail.com'
            assert real_sender.smtp_server == 'smtp.gmail.com'
        print("    ✅ Real email sender initialization")
        
        print("✅ Email system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Email system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🚀 Running Meeting Agent Component Tests\n")
    
    # Set up environment variables for testing
    os.environ.update({
        'OPENAI_API_KEY': 'test_key_for_testing',
        'EMAIL_ADDRESS': 'test@example.com',
        'EMAIL_PASSWORD': 'test_password'
    })
    
    tests = [
        test_config_system,
        test_helpers,
        test_logger,
        test_audio_system,
        test_transcription_system,
        test_ai_summarization_system,
        test_email_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All component tests passed!")
        print("\n✅ Ready for the next component!")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before proceeding.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)