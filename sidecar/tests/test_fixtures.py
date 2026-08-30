import struct
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "fixtures"


class FixtureTests(unittest.TestCase):
    def test_silence_wav(self):
        path = FIXTURES / "silence.wav"
        self.assertTrue(path.is_file())
        with wave.open(str(path), "r") as handle:
            self.assertEqual(handle.getnchannels(), 2)
            self.assertEqual(handle.getframerate(), 44100)
            self.assertGreaterEqual(handle.getnframes(), 44100)

    def test_empty_midi(self):
        path = FIXTURES / "empty.mid"
        data = path.read_bytes()
        self.assertTrue(data.startswith(b"MThd"))
        _header, fmt, tracks, _ppqn = struct.unpack(">IHHH", data[4:14])
        self.assertEqual(fmt, 0)
        self.assertEqual(tracks, 1)
        self.assertIn(b"MTrk", data)


if __name__ == "__main__":
    unittest.main()
