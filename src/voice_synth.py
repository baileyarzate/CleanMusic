# src/voice_synth.py
import torch
from TTS.api import TTS
import os

class VoiceSynthesizer:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initializing TTS with model {model_name} on {self.device}...")
        # This will download the model on first run
        self.tts = TTS(model_name).to(self.device)

    def generate_speech(self, text, speaker_wav, output_path, language="en"):
        """
        Generates speech using the reference speaker_wav.
        """
        print(f"Generating speech for '{text}'...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        self.tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language=language,
            file_path=output_path
        )
        return output_path
