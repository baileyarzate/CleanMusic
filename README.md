# CleanMusic

AI-powered tool to "clean" explicit songs by replacing cuss words with silence or synthesized vocals while maintaining the beat.

## Features

- **Silence Replacement**: Replaces cuss words with the instrumental track (silence in vocals).
- **Synth Replacement**: Inserts a short, word-shaped noise replacement where the explicit word was. It follows the timing and cadence of the original lyric, so the beat stays intact
- **Experimental**: This project is experimental. Results may vary depending on the song's complexity, vocal isolation quality, and the uniqueness of the artist's voice.

## Demos

Here are snippets demonstrating what the tool can do:

### Original Song
[SoundCloud - Original](https://soundcloud.com/jesus-arzate-3/shake_that_monkey_original_cut-3?in=jesus-arzate-3/sets/shake-that-monkey-cut-clean&si=306142b130b44b1a8f6dec6ff73fb074&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing)

### Cut with Silence
[SoundCloud - Silence Replacement](https://soundcloud.com/jesus-arzate-3/shake_that_monkey_with_silence_cut-1?in=jesus-arzate-3/sets/shake-that-monkey-cut-clean&si=93a2b6cb29f74006b2d36a7d9fa2f5a1&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing)

### Cut with Synth Replacement
[SoundCloud - Synth Replacement](https://soundcloud.com/jesus-arzate-3/shake_that_monkey_with_synth_replacement_cut-2?in=jesus-arzate-3/sets/shake-that-monkey-cut-clean&si=b9979c6677ba4f4cab29c123b8548a73&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing)

## Installation

1.  **Prerequisites**:
    -   Python 3.8+
    -   `ffmpeg` installed and added to system PATH.
    -   NVIDIA GPU (Recommended) for faster processing.

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Verify Installation**:
    Run the included test script to ensure everything is set up correctly:
    ```bash
    python test_installation.py
    ```

## Usage

### Basic Usage (Synth Replacement)
By default, the tool attempts to synthesize replacement words to fill the gaps.
```bash
python src/main.py --input "path/to/song.mp3"
```

### Silence Replacement Only
If you prefer to just mute the cuss words (letting the instrumental play through):
```bash
python src/main.py --input "path/to/song.mp3" --no_use_synth
```

### Options
- `--input`: Path to the input audio file (Required).
- `--output`: Path to save the clean version (Default: `data/clean_song.mp3`).
- `--model_size`: Whisper model size (`tiny`, `base`, `small`, `medium`, `large`). Default is `base`. Recommended to use `medium` or `large` for better results.
- `--skip_separation`: Skip the source separation step (useful for testing if files already exist).

## Roadmap / Future Work

- [ ] Add better RVC-based vocal replacement for more natural clean edits
- [ ] Build a simple UI for non-technical users
- [ ] Batch processing for folders or playlists
- [ ] Better handling of background vocals and ad-libs.

## Why this exists

I created this because I have a newborn now and I love rap, but I don't want them to hear all those cuss words. I wished Spotify or Apple Music had a capability like this built-in, but instead, they just turn off explicit songs completely, rather than replacing or removing the cuss words. This tool allows me to enjoy my favorite music without worrying about the lyrics.

This project explores how far modern ASR + source separation can go in creating family-friendly versions of music with minimal human intervention.
