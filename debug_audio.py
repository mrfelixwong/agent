#!/usr/bin/env python3
"""
Debug audio device configuration
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_audio_devices():
    """Debug audio device configuration"""
    print("🎤 Audio Device Debug")
    print("=" * 25)
    
    try:
        from src.audio.recorder import AudioRecorder
        
        print("1. Creating audio recorder...")
        recorder = AudioRecorder()
        
        print("2. Getting audio devices...")
        devices = recorder.get_audio_devices()
        
        print(f"   Found {len(devices)} audio devices:")
        for device_id, device in devices.items():
            name = device.get('name', 'Unknown')
            max_input = device.get('maxInputChannels', 0)
            max_output = device.get('maxOutputChannels', 0)
            default_rate = device.get('defaultSampleRate', 0)
            print(f"   {device_id}: {name}")
            print(f"      Input channels: {max_input}")
            print(f"      Output channels: {max_output}")
            print(f"      Sample rate: {default_rate}")
            print()
        
        print("3. Testing different configurations...")
        
        # Try mono first
        print("   Testing mono (1 channel)...")
        try:
            recorder_mono = AudioRecorder(channels=1)
            print("   ✅ Mono configuration OK")
            recorder_mono.cleanup()
        except Exception as e:
            print(f"   ❌ Mono failed: {e}")
        
        # Try with different sample rates
        print("   Testing different sample rates...")
        for rate in [16000, 22050, 44100, 48000]:
            try:
                recorder_test = AudioRecorder(sample_rate=rate, channels=1)
                print(f"   ✅ {rate}Hz mono OK")
                recorder_test.cleanup()
            except Exception as e:
                print(f"   ❌ {rate}Hz mono failed: {e}")
        
        recorder.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Audio debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_audio_devices()