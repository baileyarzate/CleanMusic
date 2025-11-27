import sys
import types
import unittest
from unittest.mock import patch


class FakeSegment:
    def __init__(self, samples):
        self.samples = list(samples)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = 0 if item.start is None else max(0, item.start)
            stop = len(self.samples) if item.stop is None else max(0, item.stop)
            return FakeSegment(self.samples[start:stop])
        raise TypeError("Unsupported index type for FakeSegment")

    def __add__(self, other):
        return FakeSegment(self.samples + other.samples)

    def __iadd__(self, other):
        self.samples.extend(other.samples)
        return self

    def __sub__(self, value):
        return FakeSegment([sample - value for sample in self.samples])

    def overlay(self, other):
        new_len = max(len(self.samples), len(other.samples))
        data = []
        for i in range(new_len):
            base = self.samples[i] if i < len(self.samples) else 0
            over = other.samples[i] if i < len(other.samples) else 0
            data.append(base + over)
        return FakeSegment(data)

    @classmethod
    def silent(cls, duration):
        return cls([0] * max(0, duration))

    @property
    def rms(self):
        if not self.samples:
            return 0
        return sum(abs(sample) for sample in self.samples) / len(self.samples)


if "pydub" not in sys.modules:
    pydub_stub = types.ModuleType("pydub")
    pydub_stub.AudioSegment = FakeSegment
    sys.modules["pydub"] = pydub_stub

from src.mixer import create_clean_version  # noqa  E402


class TestMixer(unittest.TestCase):
    @patch("src.mixer.os.path.exists", new=lambda path: path == "vocals.wav")
    @patch("src.mixer.save_audio")
    @patch("src.mixer.load_audio")
    def test_cuss_segment_is_silenced_in_vocals_mix(self, mock_load_audio, mock_save_audio):
        tone = FakeSegment([5] * 1000)
        instrumental = FakeSegment([0] * 1000)
        original = instrumental.overlay(tone)

        mock_load_audio.side_effect = [original, instrumental, tone]

        cuss_segments = [{
            "word": "shit",
            "replacement": "ship",
            "start": 0.2,
            "end": 0.4
        }]

        create_clean_version(
            original_audio_path="orig.wav",
            instrumental_path="inst.wav",
            cuss_segments=cuss_segments,
            vocals_path="vocals.wav",
            output_path="clean.wav"
        )

        saved_audio = mock_save_audio.call_args[0][0]
        safe_rms = saved_audio[0:150].rms
        muted_rms = saved_audio[200:400].rms

        self.assertGreater(safe_rms, 0)
        self.assertLess(muted_rms, safe_rms * 0.1 + 1)


if __name__ == "__main__":
    unittest.main()
