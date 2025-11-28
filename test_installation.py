import sys
import shutil
import subprocess
import importlib

def check_python_version():
    print(f"Checking Python version... {sys.version.split()[0]}")
    if sys.version_info < (3, 8):
        print("[FAIL] Python 3.8+ is required.")
        return False
    print("[OK] Python version OK.")
    return True

def check_ffmpeg():
    print("Checking for ffmpeg...")
    if shutil.which("ffmpeg") is None:
        print("[FAIL] ffmpeg not found in PATH. Please install ffmpeg.")
        return False
    print("[OK] ffmpeg found.")
    return True

def check_imports():
    print("Checking dependencies...")
    dependencies = [
        ("torch", "PyTorch"),
        ("pydub", "Pydub"),
        ("openai_whisper", "Whisper"), # package name is usually 'whisper' but let's check import
        ("demucs", "Demucs")
    ]
    
    all_good = True
    for module_name, display_name in dependencies:
        try:
            # Handle whisper specifically if needed, but usually 'import whisper' works
            if module_name == "openai_whisper":
                importlib.import_module("whisper")
            else:
                importlib.import_module(module_name)
            print(f"[OK] {display_name} installed.")
        except ImportError:
            print(f"[FAIL] {display_name} not found. Run 'pip install -r requirements.txt'")
            all_good = False
    return all_good

def main():
    print("=== CleanMusic Environment Check ===\n")
    
    checks = [
        check_python_version(),
        check_ffmpeg(),
        check_imports()
    ]
    
    print("\n" + "="*30)
    if all(checks):
        print("SUCCESS: Your environment is ready to run CleanMusic!")
        print("Try running: python src/main.py --input path/to/song.mp3")
    else:
        print("ISSUES FOUND: Please fix the errors above before running.")
    print("="*30)

if __name__ == "__main__":
    main()
