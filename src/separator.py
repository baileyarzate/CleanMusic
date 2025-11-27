import torch
import torchaudio
import soundfile as sf
from demucs.pretrained import get_model
from demucs.apply import apply_model
import os

def separate_vocals(audio_path, output_dir="data/separated"):
    """
    Uses Demucs to separate vocals using the Python API.
    Returns path to vocals and no_vocals (instrumental).
    """
    print(f"Separating vocals for {audio_path}...")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load Model
    # Use htdemucs as it's efficient
    model = get_model('htdemucs')
    
    # 2. Load Audio using soundfile
    # sf.read returns data, samplerate
    data, sr = sf.read(audio_path)
    
    # Convert to torch tensor
    wav = torch.from_numpy(data).float()
    
    # Handle dimensions: Demucs expects [channels, time]
    if wav.ndim == 1:
        # Mono: [time] -> [1, time]
        wav = wav.unsqueeze(0)
        # Duplicate channels for Demucs if needed
        wav = wav.repeat(2, 1)
    else:
        # Stereo/Multi: [time, channels] -> [channels, time]
        wav = wav.t()
        
    # RESAMPLE if needed
    # Demucs (htdemucs) expects 44100 Hz
    target_sr = 44100
    if sr != target_sr:
        print(f"  Resampling input from {sr} Hz to {target_sr} Hz for Demucs...")
        wav = torchaudio.functional.resample(wav, sr, target_sr)
        sr = target_sr
        
    # Add batch dimension: [1, channels, time]
    wav_input = wav.unsqueeze(0)
    
    # 3. Apply Model with proper normalization
    # Demucs expects normalized input
    ref = wav_input.mean(0)
    wav_input = (wav_input - ref.mean()) / ref.std()
    
    # shifts=10 for better quality, split=True for chunking, overlap=0.25 for smooth recombination
    sources = apply_model(model, wav_input, shifts=5, split=True, overlap=0.25, progress=True)
    # sources: [batch, sources, channels, time]
    
    # Denormalize the output
    sources = sources * ref.std() + ref.mean()
    
    # 4. Save Outputs
    filename = os.path.splitext(os.path.basename(audio_path))[0]
    save_dir = os.path.join(output_dir, filename)
    os.makedirs(save_dir, exist_ok=True)
    
    vocals_idx = model.sources.index('vocals')
    
    # Extract vocals
    # sources is [1, 4, 2, time]
    vocals_wav = sources[0, vocals_idx] # [2, time]
    vocals_path = os.path.join(save_dir, "vocals.wav")
    
    # Save using soundfile at TARGET sample rate (44100)
    print(f"  Saving vocals at {sr} Hz")
    sf.write(vocals_path, vocals_wav.t().numpy(), sr)
    
    # Extract Instrumental (sum of all other sources)
    other_sources = [sources[0, i] for i in range(sources.shape[1]) if i != vocals_idx]
    instrumental_wav = torch.stack(other_sources).sum(0) # [2, time]
    
    no_vocals_path = os.path.join(save_dir, "no_vocals.wav")
    print(f"  Saving instrumental at {sr} Hz")
    sf.write(no_vocals_path, instrumental_wav.t().numpy(), sr)
    
    print(f"Separation complete. Saved to {save_dir}")
        
    return vocals_path, no_vocals_path
