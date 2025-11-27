
import torchaudio
import sys

print(f"Torchaudio version: {torchaudio.__version__}")
try:
    print(f"Available backends: {torchaudio.list_audio_backends()}")
except:
    print("list_audio_backends not available")

try:
    import soundfile
    print(f"Soundfile version: {soundfile.__version__}")
except ImportError:
    print("Soundfile not installed")

print(f"Dir torchaudio: {dir(torchaudio)}")
