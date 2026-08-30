import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("CONTEXT_GENERATOR", "pedalboard")

from context_sidecar.compose import compose_to_folder, parse_prompt
from context_sidecar.magenta_models import generate_notes, status


class MagentaNoteAdapterTests(unittest.TestCase):
    def test_status_does_not_import_tensorflow_magenta(self):
        info = status()
        self.assertIn("venv_ready", info)
        self.assertIn("attention_rnn", info)

    def test_missing_worker_does_not_invent_notes(self):
        plan = parse_prompt("8 bars at 120 bpm")
        with mock.patch("context_sidecar.magenta_models.VENV_PYTHON", Path("/missing/python")):
            notes, reason = generate_notes(plan)
        self.assertIsNone(notes)
        self.assertEqual(reason, "magenta_venv_missing")

    def test_same_magenta_path_regardless_of_style_words(self):
        calls: list[str] = []

        def fake_run(payload):
            calls.append(str(payload.get("model")))
            if payload.get("model") == "music_vae":
                return {"ok": True, "backend": "music_vae", "notes": [{"pitch": 64, "start": 0, "length": 0.5, "velocity": 90}]}
            return {"ok": True, "backend": "melody_rnn", "notes": [{"pitch": 67, "start": 0, "length": 1, "velocity": 90}]}

        with mock.patch("context_sidecar.magenta_models.status", return_value={"venv_ready": True, "attention_rnn": True, "music_vae_mel": True}):
            with mock.patch("context_sidecar.magenta_models._run", side_effect=fake_run):
                generate_notes(parse_prompt("8 bars at 120 bpm"))
                generate_notes(parse_prompt("make a house loop"))
        self.assertEqual(calls, ["music_vae", "melody_rnn", "music_vae", "melody_rnn"])

    def test_compose_falls_back_to_notes_for_without_standin(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("context_sidecar.compose.magenta_generate_notes", return_value=(None, "magenta_venv_missing")):
                result = compose_to_folder("8 bars at 120 bpm", tmp)
            self.assertEqual(result["backends"]["notes"], "notes_for")
            self.assertEqual(result["backends"]["notes_detail"], "magenta_venv_missing")
            self.assertTrue(any(path.endswith(".mid") for path in result["files"]))


if __name__ == "__main__":
    unittest.main()
