import torch
import torchaudio
import os

def test_save():
    print("Testing torchaudio save...")
    # Create dummy audio
    waveform = torch.randn(1, 16000)
    sample_rate = 16000
    path = "test_save.wav"
    
    try:
        torchaudio.save(path, waveform, sample_rate)
        print(f"Successfully saved {path}")
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Failed to save: {e}")
        # Check available backends
        print(f"Available backends: {torchaudio.list_audio_backends()}")

if __name__ == "__main__":
    test_save()
