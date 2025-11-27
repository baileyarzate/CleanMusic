import sys
import os
import torch
import soundfile as sf
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Mock TTS module
from unittest.mock import MagicMock
sys.modules["TTS"] = MagicMock()
sys.modules["TTS.api"] = MagicMock()

from src.voice_synth import VoiceSynthesizer

def test_time_stretch():
    print("Testing time stretching...")
    
    # Create a dummy sine wave: 1 second at 22050Hz
    sr = 22050
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration))
    # A simple sine wave
    waveform = np.sin(2 * np.pi * 440 * t)
    
    # Save to temp file
    os.makedirs("tests/temp", exist_ok=True)
    input_path = "tests/temp/test_input.wav"
    sf.write(input_path, waveform, sr)
    
    # Initialize Synthesizer (mocking TTS part if possible, but we just want to test _match_duration)
    # We can test _match_duration directly if we instantiate the class
    # But initialization loads the model which is heavy. 
    # Let's just monkeypatch or instantiate and use the method directly if possible.
    # Or better, let's extract the method to test it, or just run the full thing if we have a model.
    # Since we don't want to download the model in this test if not needed, let's try to just test the method.
    
    # We can create a dummy class or just import the method if it was static, but it's an instance method.
    # Let's just copy the method logic here for a quick unit test of the logic, 
    # OR better: instantiate VoiceSynthesizer but mock the TTS load?
    # The __init__ loads TTS.
    
    # Let's try to test the _match_duration logic by creating a dummy instance without loading TTS
    class DummySynth(VoiceSynthesizer):
        def __init__(self):
            self.device = "cpu"
            # Skip TTS load
            pass
            
    synth = DummySynth()
    
    # Convert to tensor
    tensor = torch.from_numpy(waveform).float().unsqueeze(0) # (1, T)
    
    # Test 1: Stretch to 2.0s (slower)
    target_dur = 2.0
    print(f"Stretching 1.0s -> {target_dur}s")
    stretched = synth._match_duration(tensor, sr, target_dur)
    
    new_dur = stretched.shape[-1] / sr
    print(f"Result duration: {new_dur:.3f}s")
    assert abs(new_dur - target_dur) < 0.01, f"Failed: {new_dur} != {target_dur}"
    
    # Test 2: Compress to 0.5s (faster)
    target_dur = 0.5
    print(f"Compressing 1.0s -> {target_dur}s")
    compressed = synth._match_duration(tensor, sr, target_dur)
    
    new_dur = compressed.shape[-1] / sr
    print(f"Result duration: {new_dur:.3f}s")
    assert abs(new_dur - target_dur) < 0.01, f"Failed: {new_dur} != {target_dur}"
    
    print("Time stretch tests passed!")

if __name__ == "__main__":
    test_time_stretch()
