import sys
from unittest.mock import MagicMock

# Mock TTS before importing project modules to avoid dependency errors in test env
sys.modules["TTS"] = MagicMock()
sys.modules["TTS.api"] = MagicMock()
sys.modules["pydub"] = MagicMock()
sys.modules["whisper"] = MagicMock()
sys.modules["torch"] = MagicMock()

import unittest
from unittest.mock import patch
import os
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestCleanMusicPipeline(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests_data"
        os.makedirs(self.test_dir, exist_ok=True)
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("src.main.load_whisper_model")
    @patch("src.main.transcribe_audio")
    @patch("src.main.separate_vocals")
    @patch("src.main.VoiceSynthesizer")
    @patch("src.main.create_clean_version")
    def test_main_flow(self, mock_create_clean, mock_synth_cls, mock_separate, mock_transcribe, mock_load_model):
        # Mock returns
        mock_transcribe.return_value = [
            {"word": "hello", "start": 0.0, "end": 1.0, "confidence": 0.9},
            {"word": "shit", "start": 1.5, "end": 2.0, "confidence": 0.9}, # Cuss word
            {"word": "world", "start": 2.5, "end": 3.0, "confidence": 0.9}
        ]
        mock_separate.return_value = ("vocals.wav", "instrumental.wav")
        
        # Mock Synth instance
        mock_synth_instance = MagicMock()
        mock_synth_cls.return_value = mock_synth_instance
        
        # Create dummy input file
        input_file = os.path.join(self.test_dir, "test_song.mp3")
        with open(input_file, "w") as f:
            f.write("dummy audio content")
            
        # Run main with args
        # We need to patch sys.argv
        test_args = ["main.py", "--input", input_file, "--output", os.path.join(self.test_dir, "clean.mp3")]
        with patch.object(sys, 'argv', test_args):
            from src.main import main
            main()
            
        # Verify calls
        mock_load_model.assert_called_once()
        mock_transcribe.assert_called_once()
        mock_separate.assert_called_once()
        
        # Verify synthesis was called for the cuss word
        # "shit" -> "ship" (from censor_manager default mapping)
        mock_synth_instance.generate_speech.assert_called() 
        args, kwargs = mock_synth_instance.generate_speech.call_args
        self.assertEqual(kwargs['text'], "ship") # text argument
        
        mock_create_clean.assert_called_once()

if __name__ == "__main__":
    unittest.main()
