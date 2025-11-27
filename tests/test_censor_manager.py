import unittest

from src.censor_manager import detect_cuss_words


class TestCensorManager(unittest.TestCase):
    def test_handles_punctuation_and_case(self):
        lyrics = [
            {"word": "ShIT!!!", "start": 0.0, "end": 0.5},
        ]
        result = detect_cuss_words(lyrics)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["replacement"], "ship")
        self.assertEqual(result[0]["start"], 0.0)

    def test_detects_g_dropped_variants(self):
        lyrics = [
            {"word": "fuckin", "start": 1.0, "end": 1.4},
            {"word": "fuckin'", "start": 1.5, "end": 1.9},
        ]
        result = detect_cuss_words(lyrics)
        self.assertEqual(len(result), 2)
        for seg in result:
            self.assertEqual(seg["replacement"], "ducking")

    def test_detects_plural_slurs(self):
        lyrics = [
            {"word": "Niggas", "start": 2.0, "end": 2.5},
        ]
        result = detect_cuss_words(lyrics)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["replacement"], "neighbor")


if __name__ == "__main__":
    unittest.main()
