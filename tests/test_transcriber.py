"""
Unit tests for transcription system
"""

import os
import tempfile
import time
import threading
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the components we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.transcription.transcriber import Transcriber, MockTranscriber


class TestMockTranscriber:
    """Test MockTranscriber (no API dependencies)"""
    
    def test_mock_transcriber_initialization(self):
        """Test mock transcriber initialization"""
        transcriber = MockTranscriber(model="test-model")
        
        assert transcriber.model == "test-model"
        assert not transcriber.is_transcribing
        assert transcriber.current_transcript == ""
        
    def test_mock_transcriber_default_initialization(self):
        """Test mock transcriber with default values"""
        transcriber = MockTranscriber()
        
        assert transcriber.model == "mock-whisper-1"
        assert not transcriber.is_transcribing
        
    def test_mock_transcription_lifecycle(self):
        """Test complete mock transcription lifecycle"""
        transcriber = MockTranscriber()
        transcriber.set_mock_transcript("Hello world test")
        transcriber.set_mock_delay(0.1)
        
        # Initially not transcribing
        assert not transcriber.is_transcribing
        status = transcriber.get_transcription_status()
        assert not status['is_transcribing']
        
        # Start transcription
        success = transcriber.start_transcription()
        assert success is True
        assert transcriber.is_transcribing
        
        # Let mock processing run briefly
        time.sleep(0.5)
        
        # Should have some transcript
        assert len(transcriber.get_current_transcript()) > 0
        
        # Stop transcription
        final_transcript = transcriber.stop_transcription()
        assert not transcriber.is_transcribing
        assert len(final_transcript) > 0
        
    def test_mock_transcription_already_running(self):
        """Test starting transcription when already running"""
        transcriber = MockTranscriber()
        
        # Start first transcription
        success1 = transcriber.start_transcription()
        assert success1 is True
        
        # Try to start second transcription (should fail)
        success2 = transcriber.start_transcription()
        assert success2 is False
        
        # Clean up
        transcriber.stop_transcription()
        
    def test_mock_stop_transcription_not_running(self):
        """Test stopping transcription when not running"""
        transcriber = MockTranscriber()
        
        result = transcriber.stop_transcription()
        assert result == ""
        
    def test_mock_add_audio_chunk(self):
        """Test adding audio chunks to mock transcriber"""
        transcriber = MockTranscriber()
        
        # When not transcribing, should return False
        success = transcriber.add_audio_chunk(b"mock_audio_data")
        assert success is False
        
        # When transcribing, should return True
        transcriber.start_transcription()
        success = transcriber.add_audio_chunk(b"mock_audio_data")
        assert success is True
        
        transcriber.stop_transcription()
        
    def test_mock_callbacks(self):
        """Test callback setting and execution"""
        transcriber = MockTranscriber()
        transcriber.set_mock_transcript("Test transcript")
        transcriber.set_mock_delay(0.1)
        
        transcript_updates = []
        error_received = None
        
        def transcript_callback(text, is_final):
            transcript_updates.append((text, is_final))
            
        def error_callback(error):
            nonlocal error_received
            error_received = error
            
        transcriber.set_transcript_callback(transcript_callback)
        transcriber.set_error_callback(error_callback)
        
        # Run transcription
        transcriber.start_transcription()
        time.sleep(0.5)
        transcriber.stop_transcription()
        
        # Should have received transcript updates
        assert len(transcript_updates) > 0
        
        # Should have at least one final update
        final_updates = [update for update in transcript_updates if update[1] is True]
        assert len(final_updates) > 0
        
    def test_mock_error_simulation(self):
        """Test simulated transcription errors"""
        transcriber = MockTranscriber()
        transcriber.set_simulate_error(True)
        
        error_callback_called = False
        error_received = None
        
        def error_callback(error):
            nonlocal error_callback_called, error_received
            error_callback_called = True
            error_received = error
            
        transcriber.set_error_callback(error_callback)
        
        # Should fail to start transcription
        success = transcriber.start_transcription()
        assert success is False
        assert not transcriber.is_transcribing
        assert error_callback_called
        assert error_received is not None
        
    def test_mock_custom_settings(self):
        """Test mock transcriber with custom settings"""
        transcriber = MockTranscriber()
        
        # Set custom transcript and delay
        custom_transcript = "Custom test transcript for validation"
        transcriber.set_mock_transcript(custom_transcript)
        transcriber.set_mock_delay(0.05)
        
        transcriber.start_transcription()
        time.sleep(0.3)
        final_transcript = transcriber.stop_transcription()
        
        # Should contain words from custom transcript
        assert "Custom" in final_transcript
        assert "test" in final_transcript
        
    def test_mock_status_reporting(self):
        """Test transcription status reporting"""
        transcriber = MockTranscriber()
        
        # Before transcription
        status = transcriber.get_transcription_status()
        assert not status['is_transcribing']
        assert status['current_length'] == 0
        assert status['model'] == "mock-whisper-1"
        
        # During transcription
        transcriber.start_transcription()
        time.sleep(0.2)
        status = transcriber.get_transcription_status()
        assert status['is_transcribing']
        
        # After transcription
        transcriber.stop_transcription()
        status = transcriber.get_transcription_status()
        assert not status['is_transcribing']
        
    def test_mock_cleanup(self):
        """Test mock transcriber cleanup"""
        transcriber = MockTranscriber()
        
        # Start transcription
        transcriber.start_transcription()
        assert transcriber.is_transcribing
        
        # Cleanup should stop transcription
        transcriber.cleanup()
        assert not transcriber.is_transcribing


class TestTranscriberWithMocks:
    """Test Transcriber with mocked OpenAI API"""
    
    def test_transcriber_init_no_openai(self):
        """Test Transcriber when OpenAI package is not available"""
        with patch('src.transcription.transcriber.openai', None):
            try:
                transcriber = Transcriber(api_key="test_key")
                assert False, "Should have raised ImportError"
            except ImportError as e:
                assert "OpenAI package is not installed" in str(e)
                
    def test_transcriber_init_no_api_key(self):
        """Test Transcriber when no API key is provided"""
        mock_openai = MagicMock()
        
        with patch('src.transcription.transcriber.openai', mock_openai):
            with patch.dict(os.environ, {}, clear=True):
                try:
                    transcriber = Transcriber()
                    assert False, "Should have raised ValueError"
                except ValueError as e:
                    assert "OpenAI API key required" in str(e)
                    
    def test_transcriber_successful_init(self):
        """Test successful Transcriber initialization"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        with patch('src.transcription.transcriber.openai', mock_openai):
            transcriber = Transcriber(api_key="test_key")
            
            assert transcriber.model == "whisper-1"
            assert not transcriber.is_transcribing
            assert transcriber.current_transcript == ""
            mock_openai.OpenAI.assert_called_once_with(api_key="test_key")
            
    def test_transcriber_with_env_api_key(self):
        """Test Transcriber initialization with environment API key"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        with patch('src.transcription.transcriber.openai', mock_openai):
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'env_test_key'}):
                transcriber = Transcriber()
                
                mock_openai.OpenAI.assert_called_once_with()
                
    def test_callback_setting(self):
        """Test setting callbacks"""
        mock_openai = MagicMock()
        mock_openai.OpenAI.return_value = MagicMock()
        
        with patch('src.transcription.transcriber.openai', mock_openai):
            transcriber = Transcriber(api_key="test_key")
            
            def transcript_callback(text, is_final):
                pass
                
            def error_callback(error):
                pass
                
            transcriber.set_transcript_callback(transcript_callback)
            transcriber.set_error_callback(error_callback)
            
            assert transcriber._on_transcript_callback == transcript_callback
            assert transcriber._on_error_callback == error_callback
            
    def test_processing_interval_setting(self):
        """Test setting processing interval"""
        mock_openai = MagicMock()
        mock_openai.OpenAI.return_value = MagicMock()
        
        with patch('src.transcription.transcriber.openai', mock_openai):
            transcriber = Transcriber(api_key="test_key")
            
            # Test normal interval
            transcriber.set_processing_interval(5.0)
            assert transcriber._process_interval == 5.0
            
            # Test minimum interval
            transcriber.set_processing_interval(0.1)
            assert transcriber._process_interval == 0.5  # Should be clamped to minimum
            
    def test_transcription_status(self):
        """Test transcription status reporting"""
        mock_openai = MagicMock()
        mock_openai.OpenAI.return_value = MagicMock()
        
        with patch('src.transcription.transcriber.openai', mock_openai):
            transcriber = Transcriber(api_key="test_key", model="whisper-2")
            
            status = transcriber.get_transcription_status()
            assert not status['is_transcribing']
            assert status['current_length'] == 0
            assert status['buffer_size'] == 0
            assert status['model'] == "whisper-2"
            
    def test_mocked_transcription_process(self):
        """Test transcription with mocked API calls"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        # Mock the transcription API response
        mock_transcript_response = "This is a test transcript"
        mock_client.audio.transcriptions.create.return_value = mock_transcript_response
        
        with patch('src.transcription.transcriber.openai', mock_openai):
            transcriber = Transcriber(api_key="test_key")
            
            # Test the internal transcription method
            with tempfile.NamedTemporaryFile(suffix='.wav') as temp_file:
                temp_file.write(b"fake_audio_data")
                temp_file.flush()
                
                result = transcriber._transcribe_audio_file(temp_file.name)
                assert result == mock_transcript_response
                
                # Verify API was called correctly
                mock_client.audio.transcriptions.create.assert_called_once()
                call_args = mock_client.audio.transcriptions.create.call_args
                assert call_args[1]['model'] == "whisper-1"
                assert call_args[1]['response_format'] == "text"
                
    def test_transcription_lifecycle_mocked(self):
        """Test complete transcription lifecycle with mocked API"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = "Mock transcript"
        
        with patch('src.transcription.transcriber.openai', mock_openai):
            transcriber = Transcriber(api_key="test_key")
            
            # Start transcription
            success = transcriber.start_transcription()
            assert success is True
            assert transcriber.is_transcribing
            
            # Add some audio chunks
            transcriber.add_audio_chunk(b"audio_data_1")
            transcriber.add_audio_chunk(b"audio_data_2")
            
            # Let processing run briefly
            time.sleep(0.1)
            
            # Stop transcription
            final_transcript = transcriber.stop_transcription()
            assert not transcriber.is_transcribing
            assert isinstance(final_transcript, str)
            
    def test_cleanup_mocked(self):
        """Test transcriber cleanup with mocked API"""
        mock_openai = MagicMock()
        mock_openai.OpenAI.return_value = MagicMock()
        
        with patch('src.transcription.transcriber.openai', mock_openai):
            transcriber = Transcriber(api_key="test_key")
            
            transcriber.start_transcription()
            assert transcriber.is_transcribing
            
            # Cleanup should stop transcription
            transcriber.cleanup()
            assert not transcriber.is_transcribing


class TestTranscriberIntegration:
    """Integration tests for transcription system"""
    
    def test_audio_chunk_buffering(self):
        """Test audio chunk buffering functionality"""
        transcriber = MockTranscriber()
        
        # Test buffering when not transcribing
        success = transcriber.add_audio_chunk(b"test_data")
        assert success is False
        
        # Test buffering when transcribing
        transcriber.start_transcription()
        
        success1 = transcriber.add_audio_chunk(b"chunk_1")
        success2 = transcriber.add_audio_chunk(b"chunk_2")
        success3 = transcriber.add_audio_chunk(b"chunk_3")
        
        assert success1 is True
        assert success2 is True
        assert success3 is True
        
        transcriber.stop_transcription()
        
    def test_concurrent_transcription_prevention(self):
        """Test that multiple transcriptions can't run simultaneously"""
        transcriber = MockTranscriber()
        
        # Start first transcription
        success1 = transcriber.start_transcription()
        assert success1 is True
        
        # Second transcription should fail
        success2 = transcriber.start_transcription()
        assert success2 is False
        
        # Stop and verify we can start a new transcription
        transcriber.stop_transcription()
        success3 = transcriber.start_transcription()
        assert success3 is True
        
        transcriber.stop_transcription()
        
    def test_transcript_accumulation(self):
        """Test that transcript accumulates over time"""
        transcriber = MockTranscriber()
        transcriber.set_mock_transcript("Word by word transcript")
        transcriber.set_mock_delay(0.05)
        
        transcript_history = []
        
        def track_transcript(text, is_final):
            transcript_history.append((len(transcriber.get_current_transcript()), is_final))
        
        transcriber.set_transcript_callback(track_transcript)
        
        transcriber.start_transcription()
        time.sleep(0.3)
        transcriber.stop_transcription()
        
        # Transcript should grow over time
        assert len(transcript_history) > 1
        
        # Should have both partial and final updates
        partial_updates = [h for h in transcript_history if not h[1]]
        final_updates = [h for h in transcript_history if h[1]]
        
        assert len(partial_updates) > 0
        assert len(final_updates) > 0
        
    def test_error_handling_propagation(self):
        """Test error handling and callback propagation"""
        transcriber = MockTranscriber()
        transcriber.set_simulate_error(True)
        
        errors_received = []
        
        def error_handler(error):
            errors_received.append(str(error))
        
        transcriber.set_error_callback(error_handler)
        
        # Should trigger error during start
        success = transcriber.start_transcription()
        assert success is False
        assert len(errors_received) > 0
        assert "Simulated transcription error" in errors_received[0]


def run_transcription_tests():
    """Run all transcription tests"""
    print("🎤 Testing Transcription System...")
    
    test_classes = [
        TestMockTranscriber,
        TestTranscriberWithMocks,
        TestTranscriberIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__name__
        print(f"\n  Testing {class_name}:")
        
        instance = test_class()
        test_methods = [method for method in dir(instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                getattr(instance, test_method)()
                print(f"    ✅ {test_method}")
                passed_tests += 1
            except Exception as e:
                print(f"    ❌ {test_method}: {e}")
    
    print(f"\n📊 Transcription Tests: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests


if __name__ == '__main__':
    success = run_transcription_tests()
    exit(0 if success else 1)