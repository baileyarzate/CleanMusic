import whisper
import torch

def load_whisper_model(model_size="base"):
    """Loads the Whisper model."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Whisper model '{model_size}' on {device}...")
    model = whisper.load_model(model_size, device=device)
    return model

def transcribe_audio(model, audio_path):
    """
    Transcribes audio and returns word-level timestamps.
    Returns a list of dicts: {'word': str, 'start': float, 'end': float, 'confidence': float}
    """
    print(f"Transcribing {audio_path}...")
    # word_timestamps=True is crucial for our use case
    result = model.transcribe(audio_path, word_timestamps=True)
    
    words = []
    for segment in result["segments"]:
        if "words" in segment:
            for word in segment["words"]:
                words.append({
                    "word": word["word"].strip().lower().replace(",", "").replace(".", ""),
                    "start": word["start"],
                    "end": word["end"],
                    "confidence": word["probability"]
                })
    return words
