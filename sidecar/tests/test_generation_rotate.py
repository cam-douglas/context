import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["CONTEXT_GENERATOR"] = "pedalboard"


class GenerationRotateTests(unittest.TestCase):
    def test_rotate_cycles_and_compose_stays_audible(self):
        from context_sidecar.generation import GENERATORS, rotate

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["CONTEXT_GENERATOR_STATE"] = str(Path(tmp) / "state.json")
            os.environ.pop("CONTEXT_GENERATOR", None)
            first = rotate()
            self.assertEqual(first["id"], "musicgen")
            second = rotate()
            self.assertEqual(second["id"], "stable_audio_open")
            for _ in range(len(GENERATORS) - 2):
                rotate()
            wrapped = rotate()
            self.assertEqual(wrapped["id"], "musicgen")
            os.environ["CONTEXT_GENERATOR"] = "pedalboard"
            from context_sidecar.compose import compose_to_folder

            result = compose_to_folder("melody loop", tmp)
            self.assertEqual(result["generator"]["id"], "pedalboard")
            self.assertTrue(result["ok"])
            self.assertTrue(Path(result["wav"]).is_file())
            self.assertGreater(result["generator"]["seconds"], 0)
            del os.environ["CONTEXT_GENERATOR_STATE"]

    def test_compose_skips_clap_on_the_wav_path(self):
        from context_sidecar.compose import compose_to_folder

        seen: dict[str, bool] = {}

        def fake_search(query, folder, limit=80, quick=False):
            seen["quick"] = quick
            return {"ok": True, "wrote": False, "backend": "filename-tokens", "hits": []}

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["CONTEXT_GENERATOR"] = "pedalboard"
            with patch("context_sidecar.compose.search_local", fake_search):
                compose_to_folder("melody loop", tmp)
            self.assertTrue(seen.get("quick"))

    def test_audioldm2_prompt_stays_under_encoder_limits(self):
        from context_sidecar.generation import _audioldm2_prompt

        text = _audioldm2_prompt(
            "short piano phrase",
            {"duration_sec": 2.0, "tempo_bpm": 120.0, "style": "melody", "family": "melody", "key": "Am"},
        )
        self.assertLessEqual(len(text), 400)
        self.assertIn("piano", text.lower())
        self.assertTrue(text.lower().startswith("short piano phrase"))
        self.assertNotIn("SYSTEM (hard requirement", text)

        drums = _audioldm2_prompt(
            "heavy drum break",
            {"duration_sec": 2.0, "tempo_bpm": 120.0, "style": "melody", "family": "melody", "key": "Am"},
        )
        self.assertTrue(drums.lower().startswith("heavy drum break"))
        self.assertNotEqual(text, drums)

    def test_audioldm2_writes_real_pipeline_wav(self):
        import numpy as np
        import soundfile as sf

        from context_sidecar.generation import _audioldm2

        class _Out:
            def __init__(self, audio):
                self.audios = [audio]

        class _Vocoder:
            class config:
                sampling_rate = 16000

        class _Pipe:
            vocoder = _Vocoder()

            def __call__(self, *args, **kwargs):
                t = np.linspace(0, 2 * np.pi, 16000, endpoint=False, dtype=np.float32)
                return _Out(0.2 * np.sin(t * 220.0))

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.wav"
            with patch("context_sidecar.generation._audioldm2_pipe", return_value=_Pipe()):
                result = _audioldm2(
                    "short phrase",
                    dest,
                    {"duration_sec": 1.0, "tempo_bpm": 120.0, "style": "melody", "family": "melody", "seed": 0},
                )
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["backend"], "audioldm2-music")
            self.assertTrue(dest.is_file())
            audio, rate = sf.read(dest)
            self.assertEqual(rate, 16000)
            self.assertGreater(float(np.max(np.abs(audio))), 0.01)
            self.assertNotIn("fallback", result)

    def test_audioldm2_rejects_silent_output(self):
        import numpy as np

        from context_sidecar.generation import _audioldm2

        class _Out:
            def __init__(self, audio):
                self.audios = [audio]

        class _Vocoder:
            class config:
                sampling_rate = 16000

        class _Pipe:
            vocoder = _Vocoder()

            def __call__(self, *args, **kwargs):
                return _Out(np.zeros(16000, dtype=np.float32))

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.wav"
            with patch("context_sidecar.generation._audioldm2_pipe", return_value=_Pipe()):
                result = _audioldm2(
                    "short phrase",
                    dest,
                    {"duration_sec": 1.0, "tempo_bpm": 120.0, "style": "melody", "family": "melody", "seed": 0},
                )
            self.assertFalse(result["ok"], result)
            self.assertEqual(result["error"], "audioldm2_silent")
            self.assertFalse(dest.is_file())


if __name__ == "__main__":
    unittest.main()
