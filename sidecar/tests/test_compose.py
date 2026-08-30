import os
import tempfile
import unittest
import wave
from pathlib import Path

os.environ.setdefault("CONTEXT_GENERATOR", "pedalboard")
os.environ["CONTEXT_ENABLE_DEMUCS"] = "0"
os.environ["CONTEXT_ENABLE_CLAP"] = "0"
os.environ["CONTEXT_ENABLE_GENERATION"] = "0"

from context_sidecar.compose import apply_knobs, compose_to_folder, notes_for, parse_prompt, publish_drops


class ComposePromptTests(unittest.TestCase):
    def test_house_only_when_asked(self):
        self.assertEqual(parse_prompt("make a house loop")["style"], "house")
        self.assertEqual(parse_prompt("melody loop")["style"], "melody")
        self.assertEqual(parse_prompt("add a beat with percussion")["style"], "drums")
        self.assertTrue(parse_prompt("melody loop")["slug"].startswith("melody-"))
        self.assertFalse(parse_prompt("dark ambient pad")["slug"].startswith("house-"))

    def test_ambient_and_bass_and_tempo(self):
        ambient = parse_prompt("dark ambient pad")
        self.assertEqual(ambient["style"], "dark ambient")
        self.assertEqual(ambient["family"], "ambient")
        bass = parse_prompt("make a bassline in am at 100bpm")
        self.assertIn(bass["style"], {"bass", "bassline"})
        self.assertEqual(bass["family"], "bass")
        self.assertEqual(bass["tempo_bpm"], 100.0)
        self.assertEqual(bass["key"], "Am")

    def test_bar_count_and_wide_genres(self):
        eight = parse_prompt("8 bar shoegaze loop at 120 bpm")
        self.assertEqual(eight["bars"], 8)
        self.assertEqual(eight["style"], "shoegaze")
        self.assertAlmostEqual(eight["duration_sec"], 16.0)
        thirty_two = parse_prompt("32 bars of uk garage")
        self.assertEqual(thirty_two["bars"], 32)
        self.assertEqual(thirty_two["style"], "uk garage")
        boom = parse_prompt("4 bar boom bap at 90 bpm")
        self.assertEqual(boom["style"], "boom bap")
        self.assertAlmostEqual(boom["duration_sec"], 4 * 4 * 60 / 90)
        dnb = parse_prompt("8 bar dnb loop")
        self.assertIn(dnb["style"], {"drum and bass", "dnb"})

    def test_empty_prompt_rejected(self):
        with self.assertRaises(ValueError):
            parse_prompt("   ")

    def test_writes_audible_non_house_wav(self):
        with tempfile.TemporaryDirectory() as tmp:
            house = compose_to_folder("make a house loop", tmp)
            ambient = compose_to_folder("dark ambient pad", tmp)
            self.assertEqual(house["style"], "house")
            self.assertEqual(ambient["style"], "dark ambient")
            house_wav = Path(house["wav"])
            ambient_wav = Path(ambient["wav"])
            self.assertNotEqual(house_wav.name, ambient_wav.name)
            with wave.open(str(ambient_wav), "rb") as handle:
                frames = handle.getnframes()
                self.assertGreater(frames / handle.getframerate(), 2.0)
                raw = handle.readframes(frames)
            self.assertGreater(max(raw), 1)
            self.assertTrue(house_wav.name.startswith("pedalboard-"))
            self.assertTrue(ambient_wav.name.startswith("pedalboard-"))
            self.assertEqual(house["backends"]["room"], "pyroomacoustics")
            self.assertEqual(house["backends"]["stems"], "stems_skipped")
            self.assertEqual(house["backends"]["search"], "filename-tokens")
            self.assertTrue(house["room"]["ok"])
            self.assertTrue(house["room"]["wrote"])
            self.assertTrue(house["session"]["wrote_als"], house["session"])
            self.assertTrue(any(str(path).endswith(".als") for path in house["files"]))

    def test_publish_drops_only_dumps_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            dumps = Path(tmp) / "Dumps"
            os.environ["CONTEXT_DUMPS_DIR"] = str(dumps)
            result = publish_drops("melody loop")
            wav = Path(result["wav"])
            self.assertTrue(str(wav).startswith(str(dumps)))
            self.assertEqual(wav.parent, dumps)
            self.assertTrue(wav.name.startswith("pedalboard-"))
            del os.environ["CONTEXT_DUMPS_DIR"]

    def test_bar_count_controls_wav_length(self):
        with tempfile.TemporaryDirectory() as tmp:
            two = compose_to_folder("2 bar melody loop at 120 bpm", tmp)
            eight = compose_to_folder("8 bar melody loop at 120 bpm", tmp)
            self.assertEqual(two["bars"], 2)
            self.assertEqual(eight["bars"], 8)

            def seconds(path: str) -> float:
                with wave.open(path, "rb") as handle:
                    return handle.getnframes() / handle.getframerate()

            self.assertAlmostEqual(seconds(two["wav"]), 4.0, delta=0.8)
            self.assertAlmostEqual(seconds(eight["wav"]), 16.0, delta=0.8)

    def test_knobs_are_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            faithful = compose_to_folder(
                "melody loop",
                str(Path(tmp) / "faithful"),
                knobs={"reverence": 0.95, "abstraction": 0.05},
            )
            abstract = compose_to_folder(
                "melody loop",
                str(Path(tmp) / "abstract"),
                knobs={"reverence": 0.05, "abstraction": 0.95},
            )
            self.assertEqual(faithful["knobs"]["reverence"], 0.95)
            self.assertEqual(abstract["knobs"]["abstraction"], 0.95)
            self.assertNotEqual(Path(faithful["wav"]).read_bytes(), Path(abstract["wav"]).read_bytes())
            plan = parse_prompt("melody loop")
            clean = apply_knobs(dict(plan), [dict(note) for note in notes_for(plan)], {"reverence": 0.9, "abstraction": 0.1})
            wild = apply_knobs(dict(plan), [dict(note) for note in notes_for(plan)], {"reverence": 0.1, "abstraction": 0.9})
            self.assertNotEqual([note["pitch"] for note in clean], [note["pitch"] for note in wild])
            self.assertGreater(len(wild), len(clean))


if __name__ == "__main__":
    unittest.main()
