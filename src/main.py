# src/main.py
import argparse
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.lyrics import load_whisper_model, transcribe_audio
from src.censor_manager import detect_cuss_words
from src.separator import separate_vocals
from src.voice_synth import VoiceSynthesizer
from src.mixer import create_clean_version

def main():
    parser = argparse.ArgumentParser(description="CleanMusic: AI-powered song censorship.")
    parser.add_argument("--input", required=True, help="Path to the input audio file.")
    parser.add_argument("--output", default="data/clean_song.mp3", help="Path to the output clean audio.")
    parser.add_argument("--model_size", default="base", help="Whisper model size (tiny, base, small, medium, large).")
    parser.add_argument("--skip_separation", action="store_true", help="Skip source separation (for testing mixing only).")
    parser.add_argument(
        "--use_synth",
        action="store_true",
        help="Enable voice synthesis for cuss words."
    )
    parser.add_argument(
        "--no_use_synth",
        dest="use_synth",
        action="store_false",
        help="Disable voice synthesis."
    )
    parser.set_defaults(use_synth=True)

    
    args = parser.parse_args()
    
    input_path = args.input
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
        
    print(f"Processing: {input_path}")
    
    # 1. Transcribe
    print("--- Step 1: Transcription ---")
    whisper_model = load_whisper_model(args.model_size)
    lyrics_data = transcribe_audio(whisper_model, input_path)
    
    # 2. Detect Cuss Words
    print("--- Step 2: Cuss Word Detection ---")
    cuss_segments = detect_cuss_words(lyrics_data)
    print(f"Found {len(cuss_segments)} cuss words.")
    for seg in cuss_segments:
        print(f"  - {seg['word']} -> {seg['replacement']} ({seg['start']:.2f}s - {seg['end']:.2f}s)")
        
    if not cuss_segments:
        print("No cuss words found! Song is already clean.")
        return

    # 3. Source Separation
    print("--- Step 3: Source Separation ---")
    if not args.skip_separation:
        print("Separating vocals and instrumental...")
        vocals_path, instrumental_path = separate_vocals(input_path)
    else:
        # Fallback for testing if files exist
        filename = os.path.splitext(os.path.basename(input_path))[0]
        vocals_path = f"data/separated/htdemucs/{filename}/vocals.wav"
        instrumental_path = f"data/separated/htdemucs/{filename}/no_vocals.wav"
        if not os.path.exists(vocals_path):
             print("Error: separation skipped but files not found.")
             sys.exit(1)

    # 4. Voice Synthesis
    print("--- Step 4: Voice Synthesis ---")
    if args.use_synth:
        try:
            synth = VoiceSynthesizer()
            synth_dir = "data/synth"
            os.makedirs(synth_dir, exist_ok=True)
            
            for i, seg in enumerate(cuss_segments):
                replacement = seg['replacement']
                # Unique filename for this instance
                output_name = f"{replacement}_{i}.wav"
                output_path = os.path.join(synth_dir, output_name)
                
                # Check if already exists to save time (simple caching)
                if not os.path.exists(output_path):
                    # Calculate duration of the segment
                    duration = seg['end'] - seg['start']
                    
                    synth.generate_speech(
                        text=replacement,
                        speaker_wav=vocals_path, # Use extracted vocals as reference
                        output_path=output_path,
                        duration=duration
                    )
                
                # Store the specific path in the segment for the mixer
                seg['synth_path'] = output_path
                
        except Exception as e:
            print(f"Warning: Voice synthesis failed or not set up correctly: {e}")
            print("Proceeding with instrumental-only replacement (silence for cuss words).")
    else:
        print("Voice synthesis disabled. Using silence for cuss words.")

    # 5. Mixing
    print("--- Step 5: Mixing ---")
    create_clean_version(
        original_audio_path=input_path,
        instrumental_path=instrumental_path,
        cuss_segments=cuss_segments,
        vocals_path=vocals_path,
        output_path=args.output
    )
    
    print(f"Done! Clean version saved to: {args.output}")

if __name__ == "__main__":
    main()
