import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("CONTEXT_GENERATOR", "pedalboard")

from context_sidecar.compose import compose_to_folder, notes_for, parse_prompt
from context_sidecar.magenta_seq import quantize_notes
from context_sidecar.midi_io import write_midi


class MidiStackTests(unittest.TestCase):
    def test_mido_writes_readable_midi(self):
        plan = parse_prompt("4 bar melody loop at 120 bpm")
        notes = notes_for(plan)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "phrase.mid"
            self.assertEqual(write_midi(plan, notes, dest), "mido")
            self.assertTrue(dest.is_file())
            import mido

            mid = mido.MidiFile(str(dest))
            ons = [msg for msg in mid if msg.type == "note_on" and msg.velocity > 0]
            self.assertGreaterEqual(len(ons), 4)
            self.assertTrue(any(msg.type == "set_tempo" for msg in mid))

    def test_note_seq_quantizes_off_grid_notes(self):
        plan = {"tempo_bpm": 120.0, "style": "melody", "family": "melody"}
        notes = [{"pitch": 60, "start": 0.13, "length": 0.41, "velocity": 90}]
        snapped, backend = quantize_notes(plan, notes)
        self.assertEqual(backend, "note_seq")
        self.assertEqual(snapped[0]["pitch"], 60)
        self.assertAlmostEqual(snapped[0]["start"] % 0.25, 0.0, places=6)

    def test_compose_reports_mido_and_note_seq(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = compose_to_folder("melody loop at 120 bpm", tmp)
            self.assertEqual(result["backends"]["midi"], "mido")
            self.assertEqual(result["backends"]["quantize"], "note_seq")
            self.assertEqual(result["backends"]["scale"], "music21")
            self.assertEqual(result["backends"]["room"], "pyroomacoustics")
            mid = next(path for path in result["files"] if path.endswith(".mid"))
            self.assertTrue(Path(mid).is_file())


if __name__ == "__main__":
    unittest.main()
