import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("CONTEXT_GENERATOR", "pedalboard")
os.environ["CONTEXT_ENABLE_DEMUCS"] = "0"
os.environ["CONTEXT_ENABLE_CLAP"] = "0"
os.environ["CONTEXT_ENABLE_GENERATION"] = "0"

from context_sidecar.adapters import synthesize_texture
from context_sidecar.compose import compose_to_folder
from context_sidecar.search import search_local
from context_sidecar.stems import split_stems

SILENCE = Path(__file__).resolve().parents[2] / "fixtures" / "silence.wav"


class HeavyAdapterTests(unittest.TestCase):
    def test_flags_off_stay_honest(self):
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "loop.wav"
            wav.write_bytes(SILENCE.read_bytes())
            self.assertEqual(split_stems(str(wav))["error"], "demucs_disabled")
            self.assertEqual(search_local("dark punchy snare", tmp)["backend"], "filename-tokens")
            self.assertEqual(synthesize_texture("riser", backend="musicgen")["error"], "generation_disabled")

    def test_demucs_writes_stems_when_enabled(self):
        os.environ["CONTEXT_ENABLE_DEMUCS"] = "1"
        self.addCleanup(lambda: os.environ.__setitem__("CONTEXT_ENABLE_DEMUCS", "0"))
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "mix.wav"
            source.write_bytes(SILENCE.read_bytes())

            class FakeSep:
                samplerate = 44100

                def separate_audio_file(self, path):
                    return None, {name: object() for name in ("drums", "bass", "vocals", "other")}

            def fake_save(tensor, dest, samplerate=44100):
                Path(dest).write_bytes(b"RIFF")

            import sys
            from types import ModuleType

            api = ModuleType("demucs.api")
            api.Separator = FakeSep
            api.save_audio = fake_save
            pkg = ModuleType("demucs")
            pkg.api = api
            with patch.dict(sys.modules, {"demucs": pkg, "demucs.api": api}):
                result = split_stems(str(source), dest_dir=tmp)
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["backend"], "demucs")
            self.assertEqual(set(result["stems"]), {"drums", "bass", "vocals", "other"})

    def test_clap_ranks_when_enabled(self):
        os.environ["CONTEXT_ENABLE_CLAP"] = "1"
        self.addCleanup(lambda: os.environ.__setitem__("CONTEXT_ENABLE_CLAP", "0"))
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "dark-snare.wav"
            wav.write_bytes(SILENCE.read_bytes())

            def fake_clap(query, paths, root=None, limit=80):
                return [{"file_path": str(paths[0]), "score": 0.91, "backend": "clap"}]

            with patch("context_sidecar.search._clap_hits", fake_clap):
                result = search_local("dark punchy snare", tmp)
            self.assertEqual(result["backend"], "clap")
            self.assertAlmostEqual(result["hits"][0]["score"], 0.91)

    def test_compose_records_enabled_backends(self):
        os.environ["CONTEXT_ENABLE_DEMUCS"] = "1"
        os.environ["CONTEXT_ENABLE_CLAP"] = "1"
        self.addCleanup(lambda: os.environ.__setitem__("CONTEXT_ENABLE_DEMUCS", "0"))
        self.addCleanup(lambda: os.environ.__setitem__("CONTEXT_ENABLE_CLAP", "0"))
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["CONTEXT_SAMPLE_LIBRARY"] = tmp
            self.addCleanup(lambda: os.environ.pop("CONTEXT_SAMPLE_LIBRARY", None))
            (Path(tmp) / "dark-snare.wav").write_bytes(SILENCE.read_bytes())

            def fake_split(path, dest_dir=None):
                dest = Path(dest_dir or tmp) / "drums.wav"
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(b"RIFF")
                return {"ok": True, "wrote": True, "backend": "demucs", "stems": {"drums": str(dest)}}

            def fake_search(query, folder, limit=80, quick=False):
                return {
                    "ok": True,
                    "wrote": False,
                    "backend": "clap",
                    "hits": [{"file_path": str(Path(folder) / "dark-snare.wav"), "score": 0.8, "backend": "clap"}],
                }

            with patch("context_sidecar.compose.split_stems", fake_split), patch(
                "context_sidecar.compose.search_local", fake_search
            ):
                result = compose_to_folder("2 bar melody loop at 120 bpm", tmp, split_stems_after=True)
            self.assertEqual(result["backends"]["stems"], "demucs")
            self.assertEqual(result["backends"]["search"], "clap")
            self.assertTrue(result["stems"]["ok"])
            self.assertTrue(result["samples"]["hits"])


if __name__ == "__main__":
    unittest.main()
