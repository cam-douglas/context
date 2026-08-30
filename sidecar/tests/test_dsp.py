import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("CONTEXT_GENERATOR", "pedalboard")

from context_sidecar.compose import compose_to_folder
from context_sidecar.dsp import apply_room_to_wav, room_impulse, room_size


class RoomDspTests(unittest.TestCase):
    def test_room_impulse_uses_pyroomacoustics(self):
        result = room_impulse()
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["backend"], "pyroomacoustics")
        self.assertGreater(result["samples"], 16)

    def test_knobs_change_room_size(self):
        small = room_size({"reverence": 0.95, "abstraction": 0.05})
        large = room_size({"reverence": 0.05, "abstraction": 0.95}, family="ambient")
        self.assertLess(small[0] * small[1], large[0] * large[1])

    def test_apply_room_rewrites_wav(self):
        with tempfile.TemporaryDirectory() as tmp:
            composed = compose_to_folder(
                "2 bar melody loop at 120 bpm",
                tmp,
                knobs={"reverence": 0.2, "abstraction": 0.9},
            )
            wav = Path(composed["wav"])
            before = wav.read_bytes()
            again = apply_room_to_wav(wav, knobs={"reverence": 0.1, "abstraction": 1.0}, family="ambient")
            self.assertTrue(again["ok"], again)
            self.assertTrue(again["wrote"])
            self.assertEqual(again["backend"], "pyroomacoustics")
            self.assertNotEqual(before, wav.read_bytes())
            self.assertEqual(composed["backends"]["room"], "pyroomacoustics")


if __name__ == "__main__":
    unittest.main()
