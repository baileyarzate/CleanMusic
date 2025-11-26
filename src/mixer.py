# src/mixer.py
from src.audio_utils import load_audio, save_audio
import os

def create_clean_version(original_audio_path, instrumental_path, cuss_segments, synth_dir="data/synth", output_path="data/clean_song.mp3"):
    """
    Replaces cuss words in the original audio with synthesized clean versions.
    """
    print("Mixing clean version...")
    original = load_audio(original_audio_path)
    instrumental = load_audio(instrumental_path)
    
    # Sort segments by start time just in case
    cuss_segments.sort(key=lambda x: x['start'])
    
    final_audio = original[:0] # Empty audio segment
    current_pos = 0
    
    for seg in cuss_segments:
        start_ms = int(seg['start'] * 1000)
        end_ms = int(seg['end'] * 1000)
        replacement_word = seg['replacement']
        
        # 1. Append safe audio before the cuss word
        if start_ms > current_pos:
            final_audio += original[current_pos:start_ms]
            
        # 2. Handle the cuss word section
        # We want the instrumental background + synthesized vocal
        
        # Get instrumental slice
        inst_slice = instrumental[start_ms:end_ms]
        
        # Load synthesized vocal
        # We assume the synth file is named after the replacement word and index or unique ID
        # For simplicity in this 'bones' version, we'll look for word.wav
        # In a real app, we'd pass the specific path for this instance
        synth_filename = f"{replacement_word}.wav" 
        # Better: use the one generated for this specific instance if we had IDs. 
        # For now, let's assume the caller handles unique naming or we just use the word.
        # Actually, let's look for a specific file if provided in the segment, else default.
        
        synth_path = seg.get('synth_path')
        if not synth_path:
             synth_path = os.path.join(synth_dir, f"{replacement_word}.wav")

        if os.path.exists(synth_path):
            synth_vocal = load_audio(synth_path)
            
            # Simple overlay:
            # If synth is longer than the gap, we might want to crop it or let it bleed slightly?
            # If we let it bleed, we need to be careful about the next segment.
            # For this demo, we will force fit it to the gap or just overlay on the gap duration.
            
            # Let's try to match the length of the instrumental slice
            # If synth is shorter, it's fine. If longer, we crop.
            if len(synth_vocal) > len(inst_slice):
                synth_vocal = synth_vocal[:len(inst_slice)]
            
            mixed_segment = inst_slice.overlay(synth_vocal)
        else:
            print(f"Warning: Synth file not found for {replacement_word} at {synth_path}. Using instrumental only (silence for vocal).")
            mixed_segment = inst_slice
            
        final_audio += mixed_segment
        
        current_pos = end_ms
        
    # Append remaining audio
    final_audio += original[current_pos:]
    
    save_audio(final_audio, output_path)
    return output_path
