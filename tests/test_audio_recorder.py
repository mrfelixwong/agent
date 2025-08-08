"""
Unit tests for audio recording system
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

from src.audio.recorder import AudioRecorder, MockAudioRecorder


class TestMockAudioRecorder:
    """Test MockAudioRecorder (no hardware dependencies)"""
    
    def test_mock_recorder_initialization(self):
        """Test mock recorder initialization"""
        recorder = MockAudioRecorder(
            sample_rate=48000,
            channels=1,
            chunk_size=512,
            audio_format="24bit"
        )
        
        assert recorder.sample_rate == 48000
        assert recorder.channels == 1
        assert recorder.chunk_size == 512
        assert recorder.audio_format == "24bit"
        assert not recorder.is_recording
        
    def test_mock_recorder_default_initialization(self):
        """Test mock recorder with default values"""
        recorder = MockAudioRecorder()
        
        assert recorder.sample_rate == 44100
        assert recorder.channels == 2
        assert recorder.chunk_size == 1024
        assert recorder.audio_format == "16bit"
        
    def test_mock_get_audio_devices(self):
        """Test getting mock audio devices"""
        recorder = MockAudioRecorder()
        devices = recorder.get_audio_devices()
        
        assert isinstance(devices, dict)
        assert 0 in devices
        assert devices[0]['name'] == 'Mock Microphone'
        assert devices[0]['is_input'] is True
        
    def test_mock_recording_lifecycle(self):
        """Test complete mock recording lifecycle"""
        recorder = MockAudioRecorder()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test_recording.wav")
            
            # Initially not recording
            assert not recorder.is_recording
            info = recorder.get_recording_info()
            assert info['status'] == 'idle'
            
            # Start recording
            success = recorder.start_recording(output_file)
            assert success is True
            assert recorder.is_recording
            assert recorder.current_file_path == output_file
            assert recorder.start_time is not None
            
            # Check recording info
            info = recorder.get_recording_info()
            assert info['status'] == 'recording'
            assert info['file_path'] == output_file
            assert info['sample_rate'] == 44100
            
            # File should be created (even if empty)
            assert os.path.exists(output_file)
            
            # Stop recording
            result = recorder.stop_recording()
            assert not recorder.is_recording
            assert recorder.current_file_path is None
            assert result['file_path'] == output_file
            assert result['duration_seconds'] >= 0
            assert result['sample_rate'] == 44100
            
    def test_mock_recording_already_recording(self):
        """Test starting recording when already recording"""
        recorder = MockAudioRecorder()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file1 = os.path.join(temp_dir, "recording1.wav")
            output_file2 = os.path.join(temp_dir, "recording2.wav")
            
            # Start first recording
            success1 = recorder.start_recording(output_file1)
            assert success1 is True
            
            # Try to start second recording (should fail)
            success2 = recorder.start_recording(output_file2)
            assert success2 is False
            assert recorder.current_file_path == output_file1  # Still first file
            
            # Clean up
            recorder.stop_recording()
            
    def test_mock_stop_recording_not_recording(self):
        """Test stopping recording when not recording"""
        recorder = MockAudioRecorder()
        
        result = recorder.stop_recording()
        assert result == {}
        
    def test_mock_recording_with_custom_duration(self):
        """Test mock recording with custom duration"""
        recorder = MockAudioRecorder()
        recorder.set_mock_duration(5.0)  # 5 seconds
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "duration_test.wav")
            
            recorder.start_recording(output_file)
            # Don't wait, just stop immediately
            result = recorder.stop_recording()
            
            # Should report the mock duration, not actual elapsed time
            assert result['duration_seconds'] == 5.0
            
    def test_mock_recording_error_simulation(self):
        """Test simulated recording errors"""
        recorder = MockAudioRecorder()
        recorder.set_simulate_error(True)
        
        error_callback_called = False
        error_received = None
        
        def error_callback(error):
            nonlocal error_callback_called, error_received
            error_callback_called = True
            error_received = error
            
        recorder.set_error_callback(error_callback)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "error_test.wav")
            
            # Should fail to start recording
            success = recorder.start_recording(output_file)
            assert success is False
            assert not recorder.is_recording
            assert error_callback_called
            assert error_received is not None
            
    def test_mock_callbacks(self):
        """Test callback setting and handling"""
        recorder = MockAudioRecorder()
        
        chunk_callback_called = False
        error_callback_called = False
        
        def chunk_callback(data):
            nonlocal chunk_callback_called
            chunk_callback_called = True
            
        def error_callback(error):
            nonlocal error_callback_called
            error_callback_called = True
            
        recorder.set_chunk_callback(chunk_callback)
        recorder.set_error_callback(error_callback)
        
        # Callbacks should be set (can't test execution without real recording)
        assert recorder._on_chunk_callback == chunk_callback
        assert recorder._on_error_callback == error_callback
        
    def test_mock_cleanup(self):
        """Test mock recorder cleanup"""
        recorder = MockAudioRecorder()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "cleanup_test.wav")
            
            # Start recording
            recorder.start_recording(output_file)
            assert recorder.is_recording
            
            # Cleanup should stop recording
            recorder.cleanup()
            assert not recorder.is_recording


class TestAudioRecorderWithMocks:
    """Test AudioRecorder with mocked PyAudio"""
    
    def test_audio_recorder_init_no_pyaudio(self):
        """Test AudioRecorder when PyAudio is not available"""
        with patch('src.audio.recorder.pyaudio', None):
            try:
                recorder = AudioRecorder()
                assert False, "Should have raised ImportError"
            except ImportError as e:
                assert "PyAudio is not installed" in str(e)
                
    def test_audio_recorder_init_pyaudio_failure(self):
        """Test AudioRecorder when PyAudio initialization fails"""
        mock_pyaudio = MagicMock()
        mock_pyaudio.PyAudio.side_effect = Exception("PyAudio init failed")
        
        with patch('src.audio.recorder.pyaudio', mock_pyaudio):
            try:
                recorder = AudioRecorder()
                assert False, "Should have raised Exception"
            except Exception as e:
                assert "PyAudio init failed" in str(e)
                
    def test_audio_recorder_successful_init(self):
        """Test successful AudioRecorder initialization"""
        mock_pyaudio = MagicMock()
        mock_audio_instance = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_audio_instance
        mock_pyaudio.paInt16 = 8  # Mock format constant
        
        with patch('src.audio.recorder.pyaudio', mock_pyaudio):
            recorder = AudioRecorder(
                sample_rate=48000,
                channels=1,
                audio_format="16bit"
            )
            
            assert recorder.sample_rate == 48000
            assert recorder.channels == 1
            assert recorder.audio_format == "16bit"
            assert not recorder.is_recording
            mock_pyaudio.PyAudio.assert_called_once()
            
    def test_get_audio_devices(self):
        """Test getting audio devices"""
        mock_pyaudio = MagicMock()
        mock_audio_instance = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_audio_instance
        mock_pyaudio.paInt16 = 8
        
        # Mock device info
        mock_audio_instance.get_device_count.return_value = 2
        mock_audio_instance.get_device_info_by_index.side_effect = [
            {
                'name': 'Microphone',
                'maxInputChannels': 2,
                'maxOutputChannels': 0,
                'defaultSampleRate': 44100
            },
            {
                'name': 'Speakers',
                'maxInputChannels': 0,
                'maxOutputChannels': 2,
                'defaultSampleRate': 44100
            }
        ]
        
        with patch('src.audio.recorder.pyaudio', mock_pyaudio):
            recorder = AudioRecorder()
            devices = recorder.get_audio_devices()
            
            assert len(devices) == 2
            assert devices[0]['name'] == 'Microphone'
            assert devices[0]['is_input'] is True
            assert devices[1]['name'] == 'Speakers'
            assert devices[1]['is_output'] is True
            
    def test_get_default_device(self):
        """Test getting default input device"""
        mock_pyaudio = MagicMock()
        mock_audio_instance = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_audio_instance
        mock_pyaudio.paInt16 = 8
        
        mock_audio_instance.get_default_input_device_info.return_value = {'index': 0}
        
        with patch('src.audio.recorder.pyaudio', mock_pyaudio):
            recorder = AudioRecorder()
            default_device = recorder.get_default_device()
            
            assert default_device == 0
            
    def test_recording_with_mocked_pyaudio(self):
        """Test recording lifecycle with mocked PyAudio"""
        mock_pyaudio = MagicMock()
        mock_audio_instance = MagicMock()
        mock_stream = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_audio_instance
        mock_pyaudio.paInt16 = 8
        mock_audio_instance.get_sample_size.return_value = 2
        mock_audio_instance.open.return_value = mock_stream
        mock_stream.read.return_value = b'mock_audio_data'
        
        with patch('src.audio.recorder.pyaudio', mock_pyaudio):
            with patch('wave.open') as mock_wave_open:
                mock_wave_file = MagicMock()
                mock_wave_open.return_value = mock_wave_file
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_file = os.path.join(temp_dir, "mocked_recording.wav")
                    
                    recorder = AudioRecorder()
                    
                    # Start recording
                    success = recorder.start_recording(output_file)
                    assert success is True
                    assert recorder.is_recording
                    
                    # Give recording thread a moment to start
                    time.sleep(0.1)
                    
                    # Stop recording
                    result = recorder.stop_recording()
                    
                    assert not recorder.is_recording
                    assert result['file_path'] == output_file
                    assert result['duration_seconds'] >= 0
                    
                    # Verify PyAudio calls
                    mock_audio_instance.open.assert_called_once()
                    mock_wave_open.assert_called_once_with(output_file, 'wb')
                    
    def test_cleanup(self):
        """Test recorder cleanup"""
        mock_pyaudio = MagicMock()
        mock_audio_instance = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_audio_instance
        mock_pyaudio.paInt16 = 8
        
        with patch('src.audio.recorder.pyaudio', mock_pyaudio):
            recorder = AudioRecorder()
            
            # Cleanup should terminate PyAudio
            recorder.cleanup()
            mock_audio_instance.terminate.assert_called_once()


class TestAudioRecorderIntegration:
    """Integration tests for audio recording"""
    
    def test_directory_creation(self):
        """Test that output directory is created if it doesn't exist"""
        recorder = MockAudioRecorder()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested path that doesn't exist
            nested_dir = os.path.join(temp_dir, "level1", "level2", "level3")
            output_file = os.path.join(nested_dir, "test.wav")
            
            success = recorder.start_recording(output_file)
            assert success is True
            
            # Directory should have been created
            assert os.path.exists(nested_dir)
            assert os.path.exists(output_file)
            
            recorder.stop_recording()
            
    def test_concurrent_recording_prevention(self):
        """Test that multiple recordings can't run simultaneously"""
        recorder = MockAudioRecorder()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = os.path.join(temp_dir, "recording1.wav")
            file2 = os.path.join(temp_dir, "recording2.wav")
            
            # Start first recording
            success1 = recorder.start_recording(file1)
            assert success1 is True
            
            # Second recording should fail
            success2 = recorder.start_recording(file2)
            assert success2 is False
            
            # Only first file should exist
            assert os.path.exists(file1)
            assert not os.path.exists(file2)
            
            # Stop and verify we can start a new recording
            recorder.stop_recording()
            success3 = recorder.start_recording(file2)
            assert success3 is True
            
            recorder.stop_recording()
            
    def test_recording_info_updates(self):
        """Test that recording info updates correctly during recording"""
        recorder = MockAudioRecorder()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "info_test.wav")
            
            # Before recording
            info = recorder.get_recording_info()
            assert info['status'] == 'idle'
            
            # During recording
            recorder.start_recording(output_file)
            info = recorder.get_recording_info()
            assert info['status'] == 'recording'
            assert info['file_path'] == output_file
            assert info['duration_seconds'] >= 0
            assert info['sample_rate'] == recorder.sample_rate
            assert info['channels'] == recorder.channels
            
            # After recording
            recorder.stop_recording()
            info = recorder.get_recording_info()
            assert info['status'] == 'idle'


def run_audio_tests():
    """Run all audio recorder tests"""
    print("🎙️ Testing Audio Recording System...")
    
    test_classes = [
        TestMockAudioRecorder,
        TestAudioRecorderWithMocks,
        TestAudioRecorderIntegration
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
    
    print(f"\n📊 Audio Tests: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests


if __name__ == '__main__':
    success = run_audio_tests()
    exit(0 if success else 1)