# src/mixer.py
import os
from typing import Dict, List, Optional, Tuple

from pydub import AudioSegment

from src.audio_utils import load_audio, save_audio


def _segment_bounds(segment: Dict) -> Tuple[int, int]:
    start_ms = max(0, int(segment['start'] * 1000))
    end_ms = max(start_ms, int(segment['end'] * 1000))
    return start_ms, end_ms


def _load_synth_clip(
    seg: Dict,
    synth_dir: str,
    duration_ms: int,
    cache: Dict[str, AudioSegment]
) -> Optional[AudioSegment]:
    replacement_word = seg.get('replacement', 'clean')
    synth_path = seg.get('synth_path') or os.path.join(synth_dir, f"{replacement_word}.wav")

    if not synth_path or not os.path.exists(synth_path):
        return None

    if synth_path not in cache:
        cache[synth_path] = load_audio(synth_path)

    synth_clip = cache[synth_path]
    if duration_ms <= 0:
        return synth_clip

    if len(synth_clip) > duration_ms:
        return synth_clip[:duration_ms]
    if len(synth_clip) < duration_ms:
        padding = AudioSegment.silent(duration=duration_ms - len(synth_clip))
        return synth_clip + padding
    return synth_clip


def _build_clean_vocals(vocals: AudioSegment, cuss_segments: List[Dict], synth_dir: str) -> AudioSegment:
    clean_vocals = vocals[:0]
    current_pos = 0
    synth_cache: Dict[str, AudioSegment] = {}

    for i, seg in enumerate(cuss_segments):
        start_ms, end_ms = _segment_bounds(seg)
        duration = end_ms - start_ms
        print(f"\nDEBUG: --- Vocal Segment {i+1}/{len(cuss_segments)} ---")
        print(f"DEBUG: Original word '{seg.get('word')}' mapped to '{seg.get('replacement')}'")
        print(f"DEBUG: Muting vocals from {start_ms}ms to {end_ms}ms (duration {duration}ms)")

        if start_ms > current_pos:
            safe_chunk = vocals[current_pos:start_ms]
            clean_vocals += safe_chunk
            print(f"DEBUG: Added {len(safe_chunk)}ms of safe vocals before the cuss word.")

        if duration <= 0:
            current_pos = end_ms
            continue

        replacement = AudioSegment.silent(duration=duration)
        synth_clip = _load_synth_clip(seg, synth_dir, duration, synth_cache)
        if synth_clip:
            replacement = replacement.overlay(synth_clip)

        clean_vocals += replacement
        current_pos = end_ms

    remaining = vocals[current_pos:]
    clean_vocals += remaining
    print(f"DEBUG: Added {len(remaining)}ms of tail vocals after last cuss word.")
    print(f"DEBUG: Clean vocals total length: {len(clean_vocals)}ms")
    return clean_vocals


def _fallback_mix(
    original: AudioSegment,
    instrumental: AudioSegment,
    cuss_segments: List[Dict],
    synth_dir: str
) -> AudioSegment:
    """
    Legacy path when we don't have an isolated vocal track. This guarantees cuss
    segments are muted even if that means pure silence.
    """
    final_audio = original[:0]
    current_pos = 0
    synth_cache: Dict[str, AudioSegment] = {}

    for i, seg in enumerate(cuss_segments):
        start_ms, end_ms = _segment_bounds(seg)
        duration = end_ms - start_ms
        print(f"\nDEBUG: --- Fallback Segment {i+1}/{len(cuss_segments)} ---")
        print(f"DEBUG: Muting original audio from {start_ms}ms to {end_ms}ms")

        if start_ms > current_pos:
            safe_section = original[current_pos:start_ms]
            final_audio += safe_section

        if duration <= 0:
            current_pos = end_ms
            continue

        inst_slice = instrumental[start_ms:end_ms]
        if len(inst_slice) < duration:
            inst_slice += AudioSegment.silent(duration - len(inst_slice))

        replacement = inst_slice - 15  # drop any residual bleed substantially
        synth_clip = _load_synth_clip(seg, synth_dir, duration, synth_cache)
        if synth_clip:
            replacement = replacement.overlay(synth_clip)

        final_audio += replacement
        current_pos = end_ms

    final_audio += original[current_pos:]
    return final_audio


def create_clean_version(
    original_audio_path: str,
    instrumental_path: str,
    cuss_segments,
    vocals_path: Optional[str] = None,
    synth_dir: str = "data/synth",
    output_path: str = "data/clean_song.mp3"
):
    """
    Builds a clean song by muting the separated vocal stem over cuss regions,
    optionally overlaying synthesized replacements, and then re-mixing with the
    instrumental stem.
    """
    print("Mixing clean version...")
    print(f"DEBUG: Number of cuss segments to process: {len(cuss_segments)}")
    print(f"DEBUG: Original audio path: {original_audio_path}")
    print(f"DEBUG: Instrumental path: {instrumental_path}")
    if vocals_path:
        print(f"DEBUG: Vocals path: {vocals_path}")
    print(f"DEBUG: Output path: {output_path}")

    original = load_audio(original_audio_path)
    instrumental = load_audio(instrumental_path)
    vocals = load_audio(vocals_path) if vocals_path and os.path.exists(vocals_path) else None

    print(f"DEBUG: Original audio length: {len(original)}ms")
    print(f"DEBUG: Instrumental audio length: {len(instrumental)}ms")
    if vocals:
        print(f"DEBUG: Vocals audio length: {len(vocals)}ms")

    cuss_segments.sort(key=lambda x: x['start'])

    if vocals:
        clean_vocals = _build_clean_vocals(vocals, cuss_segments, synth_dir)
        final_audio = instrumental.overlay(clean_vocals)
    else:
        print("WARNING: Vocals track missing, falling back to destructive mute in the original mix.")
        final_audio = _fallback_mix(original, instrumental, cuss_segments, synth_dir)

    print(f"DEBUG: Final audio total length: {len(final_audio)}ms")
    save_audio(final_audio, output_path)
    print(f"DEBUG: Saved final audio to: {output_path}")
    return output_path
