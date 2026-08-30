import gzip
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from context_sidecar.als_json import parse_als, write_als
from context_sidecar.dsp import dawdreamer_render_arrangement
from context_sidecar.export import arrangement_from_assets, export_session, parse_als_readonly
from context_sidecar.session_export import _minimal_live_set, export_live_set

ROOT = Path(__file__).resolve().parents[2]
SILENCE = ROOT / "fixtures" / "silence.wav"
EMPTY_MID = ROOT / "fixtures" / "empty.mid"


class AlsJsonTests(unittest.TestCase):
    def test_round_trip_preserves_tracks(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "in.als"
            dest = Path(tmp) / "out.als"
            write_als(source, _minimal_live_set())
            payload = parse_als(source)
            write_als(dest, payload)
            again = parse_als(dest)
            self.assertEqual(payload["root"]["tag"], "Ableton")
            names = [
                child.get("attrib", {}).get("Value")
                for node in payload["root"]["children"]
                for child in (node.get("children") or [])
            ]
            self.assertEqual(again["root"]["tag"], payload["root"]["tag"])
            with gzip.open(dest, "rb") as handle:
                root = ET.fromstring(handle.read())
            self.assertEqual(root.tag, "Ableton")
            self.assertEqual(
                [el.attrib.get("Value") for el in root.findall("LiveSet/Tracks/*/Name/EffectiveName")],
                ["1-MIDI", "2-Audio"],
            )
            self.assertTrue(names)


class SessionIntegrityTests(unittest.TestCase):
    def test_merge_keeps_user_tracks_and_does_not_overwrite_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "user.als"
            dest_dir = Path(tmp) / "out"
            write_als(source, _minimal_live_set())
            before = source.read_bytes()
            plan = arrangement_from_assets(
                tempo_bpm=128,
                musical_key="Am",
                midi_path=str(EMPTY_MID),
                stem_paths=[str(SILENCE)],
                notes=[{"pitch": 60, "start": 0, "length": 1, "velocity": 100}],
                bars=4,
                slug="Export",
            )
            result = export_live_set(str(dest_dir), plan, source_als=str(source), slug="Export")
            self.assertTrue(result["ok"], result)
            self.assertTrue(result["wrote_als"])
            self.assertFalse(result["overwrote_source"])
            self.assertEqual(source.read_bytes(), before)
            self.assertNotEqual(result["source_sha256"], result["dest_sha256"])
            self.assertIn("1-MIDI", result["integrity"]["preserved_user_tracks"])
            self.assertIn("2-Audio", result["integrity"]["preserved_user_tracks"])
            self.assertTrue(any(name.startswith("Context ") for name in result["integrity"]["added_tracks"]))
            self.assertGreaterEqual(result["integrity"]["added_clips"], 1)
            self.assertTrue(result["integrity"]["intact"])
            parsed = parse_als_readonly(result["als_path"])
            self.assertTrue(parsed["ok"])
            self.assertIn("1-MIDI", parsed["tracks"])
            self.assertGreaterEqual(parsed["clip_count"], 1)

    def test_export_session_renders_and_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = export_session(
                tmp,
                midi_path=str(EMPTY_MID),
                stem_paths=[str(SILENCE)],
                tempo_bpm=100,
                musical_key="C",
                slug="Mix",
            )
            self.assertTrue(result["wrote_als"], result)
            als = Path(result["session"]["als_path"])
            tree = Path(result["session"]["als_json_path"])
            self.assertTrue(als.is_file())
            self.assertTrue(tree.is_file())
            self.assertIn("als_json_version", tree.read_text())
            render = result["render"]
            if render.get("ok"):
                self.assertEqual(render["backend"], "dawdreamer")
                self.assertTrue(Path(render["path"]).is_file())
            else:
                self.assertEqual(render["error"], "dawdreamer_unavailable")


class DawDreamerRenderTests(unittest.TestCase):
    def test_render_places_audio_on_timeline(self):
        plan = arrangement_from_assets(stem_paths=[str(SILENCE)], bars=2, slug="Render")
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "mix.wav"
            result = dawdreamer_render_arrangement(plan, dest)
            if not result.get("ok"):
                self.assertEqual(result["error"], "dawdreamer_unavailable")
                return
            self.assertTrue(dest.is_file())
            self.assertGreater(dest.stat().st_size, 100)


if __name__ == "__main__":
    unittest.main()
