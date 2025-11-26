from pydub import AudioSegment
import os

def load_audio(file_path):
    """Loads an audio file into a pydub AudioSegment."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    print(f"Loading audio: {file_path}")
    return AudioSegment.from_file(file_path)

def save_audio(audio_segment, output_path, format="mp3"):
    """Exports an audio segment to a file."""
    print(f"Saving audio to: {output_path}")
    audio_segment.export(output_path, format=format)

def slice_audio(audio_segment, start_ms, end_ms):
    """Slices audio from start_ms to end_ms."""
    return audio_segment[start_ms:end_ms]

def crossfade_segments(first, second, crossfade_ms=50):
    """Crossfades two audio segments."""
    return first.append(second, crossfade=crossfade_ms)

def get_duration_ms(audio_segment):
    return len(audio_segment)
