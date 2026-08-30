import os
import tempfile
import unittest
from pathlib import Path


class ProgressTests(unittest.TestCase):
    def test_eta_after_two_steps(self):
        from context_sidecar import progress

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["CONTEXT_PROGRESS_PATH"] = str(Path(tmp) / "progress.json")
            os.environ["CONTEXT_PREVIEW_WAV"] = str(Path(tmp) / "live.wav")
            self.addCleanup(lambda: os.environ.pop("CONTEXT_PROGRESS_PATH", None))
            self.addCleanup(lambda: os.environ.pop("CONTEXT_PREVIEW_WAV", None))
            progress.begin("audioldm2", steps=24, message="generating")
            progress.update(step=2, phase="denoise")
            first = progress.snapshot()
            self.assertTrue(first["active"])
            self.assertEqual(first["id"], "audioldm2")
            import time
            time.sleep(0.02)
            progress.update(step=12, phase="denoise")
            mid = progress.snapshot()
            self.assertEqual(mid["step"], 12)
            self.assertEqual(mid["steps"], 24)
            self.assertIsNotNone(mid["eta_sec"])
            progress.finish(ok=True, message="done")
            done = progress.snapshot()
            self.assertFalse(done["active"])
            self.assertEqual(done["eta_sec"], 0.0)


if __name__ == "__main__":
    unittest.main()
