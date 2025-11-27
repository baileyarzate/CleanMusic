import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import torch
import torchaudio
import soundfile as sf

# === FIX FOR PYTORCH 2.6+ ===
# Coqui TTS uses older pickle formats that are blocked by the new 'weights_only=True' default.
# We override torch.load to use 'weights_only=False' by default before importing TTS.
_original_load = torch.load

def load_wrapper(*args, **kwargs):
    # If weights_only is not specified, force it to False
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _original_load(*args, **kwargs)

torch.load = load_wrapper
# ============================

# === FIX FOR TORCHAUDIO 2.9+ ===
# Torchaudio 2.9+ forces the use of TorchCodec for load(), which fails if not installed.
# It also ignores the 'backend' argument.
# We monkeypatch torchaudio.load to use soundfile directly.
def custom_load(uri, **kwargs):
    # soundfile.read returns (data, samplerate)
    # data is (time, channels) or (time,)
    data, samplerate = sf.read(uri)
    
    # Convert to tensor
    tensor = torch.from_numpy(data)
    
    # Ensure float32
    tensor = tensor.float()
    
    # Handle dimensions: soundfile is (time, channels), torchaudio expects (channels, time)
    if tensor.ndim == 1:
        # Mono: (time) -> (1, time)
        tensor = tensor.unsqueeze(0)
    else:
        # Multi-channel: (time, channels) -> (channels, time)
        tensor = tensor.t()
        
    return tensor, samplerate

torchaudio.load = custom_load
# ===============================

from TTS.api import TTS

class VoiceSynthesizer:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initializing TTS with model {model_name} on {self.device}...")
        
        # This will download the model on first run
        self.tts = TTS(model_name).to(self.device)

    def generate_speech(self, text, speaker_wav, output_path, language="en", duration=None):
        """
        Generates speech using the reference speaker_wav.
        If duration (seconds) is provided, the output will be trimmed/stretched to fit.
        """
        print(f"Generating speech for '{text}'...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # XTTS parameters for better short text generation
        # temperature: lower = more deterministic/stable
        # repetition_penalty: higher = less repetition
        # speed: default 1.0
        self.tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language=language,
            file_path=output_path,
            temperature=0.7, 
            repetition_penalty=2.0,
            speed=1.0
        )
        
        # Post-processing: Trim to duration if specified
        if duration:
            try:
                data, sr = sf.read(output_path)
                
                # Smart Trimming: Remove silence from start
                threshold = 0.01
                if data.ndim == 2:
                    mono = data.mean(axis=1)
                else:
                    mono = data
                
                start_idx = 0
                for i, sample in enumerate(mono):
                    if abs(sample) > threshold:
                        start_idx = i
                        break
                
                if start_idx > 0:
                    print(f"Trimming {start_idx/sr:.3f}s of silence from start")
                    data = data[start_idx:]

                # Convert to tensor for torchaudio processing
                # data is (time, channels) or (time,) -> need (channels, time) or (1, time)
                tensor = torch.from_numpy(data).float()
                if tensor.ndim == 1:
                    tensor = tensor.unsqueeze(0) # (1, T)
                else:
                    tensor = tensor.t() # (C, T)

                # Match Duration using Time Stretch
                tensor = self._match_duration(tensor, sr, duration)
                
                # Convert back to numpy for saving
                data = tensor.t().numpy()
                
                sf.write(output_path, data, sr)
            except Exception as e:
                print(f"Warning: Failed to process audio duration: {e}")
                import traceback
                traceback.print_exc()

        print(f"Saved to: {output_path}")
        return output_path

    def _match_duration(self, waveform, sample_rate, target_duration):
        """
        Stretches/compresses the waveform to match the target duration 
        without changing pitch, using Phase Vocoder.
        """
        current_samples = waveform.shape[-1]
        target_samples = int(target_duration * sample_rate)
        
        if current_samples == 0:
            return waveform

        current_duration = current_samples / sample_rate
        print(f"Matching duration: {current_duration:.3f}s -> {target_duration:.3f}s")
        
        # Tolerance check (e.g. within 50ms is fine? User wants exact timing, let's try to get close)
        if abs(current_duration - target_duration) < 0.05:
            # Just trim or pad slightly if very close
            if current_samples > target_samples:
                return waveform[:, :target_samples]
            elif current_samples < target_samples:
                return torch.nn.functional.pad(waveform, (0, target_samples - current_samples))
            return waveform

        # Rate for TimeStretch: 
        # rate > 1.0 speeds up (shorter)
        # rate < 1.0 slows down (longer)
        rate = current_duration / target_duration
        
        # STFT parameters
        n_fft = 1024
        hop_length = 512
        # Ensure we have enough samples for at least one frame
        if current_samples < n_fft:
             # Pad if too short for STFT
             pad_amt = n_fft - current_samples
             waveform = torch.nn.functional.pad(waveform, (0, pad_amt))
        
        # Complex Spectrogram: (..., F, T)
        # return_complex=True is required for PhaseVocoder/TimeStretch in newer torch
        stft = torch.stft(waveform, n_fft=n_fft, hop_length=hop_length, return_complex=True)
        
        # TimeStretch expects complex input
        stretcher = torchaudio.transforms.TimeStretch(hop_length=hop_length, n_freq=n_fft//2 + 1, fixed_rate=rate)
        
        stretched_stft = stretcher(stft)
        
        # Inverse STFT
        new_waveform = torch.istft(stretched_stft, n_fft=n_fft, hop_length=hop_length, length=target_samples)
        
        # Ensure exact length
        if new_waveform.shape[-1] > target_samples:
            new_waveform = new_waveform[:, :target_samples]
        elif new_waveform.shape[-1] < target_samples:
            new_waveform = torch.nn.functional.pad(new_waveform, (0, target_samples - new_waveform.shape[-1]))
            
        return new_waveform