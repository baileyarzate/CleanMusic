import subprocess
import os

def separate_vocals(audio_path, output_dir="data/separated"):
    """
    Uses Demucs to separate vocals.
    Returns path to vocals and no_vocals (instrumental).
    """
    # Demucs command: demucs -n htdemucs --two-stems=vocals <audio_path> -o <output_dir>
    print(f"Separating vocals for {audio_path}...")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        "demucs",
        "-n", "htdemucs",
        "--two-stems=vocals",
        audio_path,
        "-o", output_dir
    ]
    
    # Run Demucs
    # Note: This might take a while depending on GPU/CPU
    subprocess.run(cmd, check=True)
    
    # Construct expected paths
    # Demucs output structure: <output_dir>/htdemucs/<filename_no_ext>/vocals.wav
    filename = os.path.splitext(os.path.basename(audio_path))[0]
    model_name = "htdemucs"
    
    vocals_path = os.path.join(output_dir, model_name, filename, "vocals.wav")
    no_vocals_path = os.path.join(output_dir, model_name, filename, "no_vocals.wav")
    
    if not os.path.exists(vocals_path) or not os.path.exists(no_vocals_path):
        raise FileNotFoundError(f"Demucs separation failed to produce output files at {vocals_path} or {no_vocals_path}")
        
    return vocals_path, no_vocals_path
