import torch
import torchaudio
from demucs.pretrained import get_model
from demucs.apply import apply_model
import os

def test_demucs_api():
    print("Testing Demucs API...")
    
    # 1. Load Model
    print("Loading model...")
    model = get_model('htdemucs')
    
    # 2. Load Audio
    # Create a dummy audio file if needed, or use a known one.
    # We'll generate a dummy tensor for testing logic
    print("Generating dummy audio...")
    sr = 44100
    duration = 5
    wav = torch.randn(2, sr * duration) # Stereo
    
    # Add batch dimension: [batch, channels, time] -> [1, 2, time]
    wav_input = wav.unsqueeze(0)
    
    # 3. Apply Model
    print("Applying model...")
    # shifts=0 for speed in test
    ref = wav_input.mean(0)
    wav_input = (wav_input - ref.mean()) / ref.std()
    
    sources = apply_model(model, wav_input, shifts=0, split=True, overlap=0.25)
    
    print(f"Sources shape: {sources.shape}")
    # Expected: [batch, sources, channels, time]
    
    # 4. Save Output manually using soundfile backend
    print("Saving output...")
    vocals_idx = model.sources.index('vocals')
    vocals = sources[0, vocals_idx]
    
    output_path = "test_vocals_api.wav"
    torchaudio.save(output_path, vocals, sr, backend="soundfile")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    test_demucs_api()
