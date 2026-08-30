import unittest

from context_sidecar.stack import probe


class StackProbeTests(unittest.TestCase):
    def test_core_packages_present(self):
        installed = probe()["installed"]
        for name in (
            "numpy",
            "scipy",
            "librosa",
            "pedalboard",
            "mido",
            "pretty_midi",
            "music21",
            "note_seq",
            "pydub",
            "pyroomacoustics",
            "als_json",
        ):
            self.assertTrue(installed[name], name)


if __name__ == "__main__":
    unittest.main()
