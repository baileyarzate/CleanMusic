# CleanMusic

AI-powered tool to "clean" explicit songs by replacing cuss words with phonetically similar alternatives using source separation, ASR, and voice cloning.

## Prerequisites

- Python 3.8+
- NVIDIA GPU (Recommended) for faster processing with Whisper, Demucs, and Coqui TTS.
- `ffmpeg` installed and added to system PATH (required by pydub/audioprocessing).

## Installation

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  (Optional) Install PyTorch with CUDA support manually if the default install doesn't pick it up:
    [PyTorch Get Started](https://pytorch.org/get-started/locally/)

## Usage

Run the main script with your input audio file:

```bash
python src/main.py --input path/to/song.mp3
```

### Options

- `--input`: Path to the input audio file (Required).
- `--output`: Path to save the clean version (Default: `data/clean_song.mp3`).
- `--model_size`: Whisper model size (`tiny`, `base`, `small`, `medium`, `large`). Default is `base`.
- `--skip_separation`: Skip the Demucs separation step (useful if you already have separated files in the default output folder or for testing).

## How it Works

1.  **Transcription**: Uses OpenAI Whisper to transcribe lyrics and get exact word timestamps.
2.  **Detection**: Scans lyrics for cuss words using a customizable dictionary (`src/censor_manager.py`).
3.  **Separation**: Uses Demucs to split the track into `vocals` and `instrumental`.
4.  **Synthesis**: Uses Coqui TTS (XTTS) to clone the singer's voice from the separated vocals and generate clean replacements (e.g., "bitch" -> "itch").
5.  **Mixing**: Stitches the instrumental, the original safe vocals, and the generated replacements together.

## Troubleshooting

- **FFmpeg Error**: If you see errors related to audio loading, ensure `ffmpeg` is installed.
- **CUDA/Memory**: If you run out of memory, try a smaller Whisper model (`--model_size tiny`) or run on CPU (slower).
