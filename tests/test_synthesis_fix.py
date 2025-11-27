
import os
import sys
# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.voice_synth import VoiceSynthesizer
import soundfile as sf

def test_synthesis():
    voice = VoiceSynthesizer()
    
    # Use existing paths
    ref_audio = r"C:\Users\baile\Documents\Artificial Intelligence\CleanMusic\data\example\ytmp3free.cc_shake-that-monkey-youtubemp3free.org.wav"
    out_audio = r"C:\Users\baile\Documents\Artificial Intelligence\CleanMusic\data\synth\test_short.wav"
    
    # Target duration: 0.5 seconds (short word)
    target_duration = 0.5
    
    print(f"Testing synthesis with target duration: {target_duration}s")
    voice.generate_speech("clean", ref_audio, out_audio, duration=target_duration)
    
    # Verify duration
    data, sr = sf.read(out_audio)
    actual_duration = len(data) / sr
    print(f"Actual duration: {actual_duration:.2f}s")
    
    # Check if start is silent (should be non-silent now)
    threshold = 0.01
    is_silent_start = abs(data[0]) < threshold if data.ndim == 1 else abs(data[0].mean()) < threshold
    
    if abs(actual_duration - target_duration) < 0.1:
        print("SUCCESS: Duration matches!")
    else:
        print("FAILURE: Duration mismatch!")
        
    if not is_silent_start:
        print("SUCCESS: Start is not silent (smart trimming worked)!")
    else:
        print("WARNING: Start might still be silent.")

if __name__ == "__main__":
    test_synthesis()
