import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ["CONTEXT_ENABLE_DEMUCS"] = "0"
os.environ["CONTEXT_ENABLE_CLAP"] = "0"
os.environ["CONTEXT_ENABLE_GENERATION"] = "0"

from context_sidecar.adapters import synthesize_texture
from context_sidecar.analysis import analyze_audio
from context_sidecar.arrange import loop_to_song
from context_sidecar.dsp import dawdreamer_rehearse, ducking_plan, room_curve
from context_sidecar.export import export_session
from context_sidecar.http import handle_intent
from context_sidecar.intent import empty_intent, validate_intent
from context_sidecar.midi_symbolic import counter_melody, ghost_notes, humanize_notes, parse_empty_or_notes
from context_sidecar.mix_audit import audit_stems
from context_sidecar.schema import validate_arrangement
from context_sidecar.search import search_local
from context_sidecar.stems import split_stems
from context_sidecar.writer import arrangement_write_actions

ROOT = Path(__file__).resolve().parents[2]
SILENCE = ROOT / "fixtures" / "silence.wav"
EMPTY_MID = ROOT / "fixtures" / "empty.mid"


class Phase2Tests(unittest.TestCase):
    def test_analyze_fixture(self):
        report = analyze_audio(str(SILENCE))
        self.assertEqual(report["backend"], "wave-stdlib")
        self.assertFalse(report.get("wrote"))
        self.assertIn("build", [item["label"] for item in report["section_candidates"]])

    def test_mix_audit_named_stems(self):
        result = audit_stems({"kick": str(SILENCE), "bass": str(SILENCE)})
        self.assertFalse(result["wrote"])
        self.assertTrue(result["hits"])
        self.assertEqual(result["hits"][0]["hz"], 250)

    def test_genre_target_optional(self):
        intent = empty_intent(prompt="build a 3-minute Melodic Techno arrangement from this loop")
        intent["genre_target"] = "Melodic Techno"
        validate_intent(intent)

    def test_midi_parse_and_variation(self):
        parsed = parse_empty_or_notes(str(EMPTY_MID))
        self.assertEqual(parsed["notes"], [])
        notes = [{"pitch": 36, "start": 0.0, "duration": 0.25, "velocity": 100}]
        self.assertTrue(ghost_notes(notes)[-1]["ghost"])
        self.assertTrue(counter_melody(notes)[0]["counter"])
        self.assertNotEqual(humanize_notes(notes, 0.5)[0]["start"], 0.0)


class Phase3Tests(unittest.TestCase):
    def test_loop_to_song_validates(self):
        plan = loop_to_song(genre_target="Melodic Techno", source_path=str(SILENCE))
        validate_arrangement(
            {
                "schema_version": plan["schema_version"],
                "tempo_bpm": plan["tempo_bpm"],
                "musical_key": plan["musical_key"],
                "time_signature": plan["time_signature"],
                "sections": plan["sections"],
                "tracks": plan["tracks"],
            }
        )
        labels = [section["label"] for section in plan["sections"]]
        self.assertIn("intro", labels)
        self.assertIn("build", labels)
        self.assertIn("drop", labels)
        actions = arrangement_write_actions(plan, locks=[])
        methods = {action["method"] for action in actions}
        self.assertIn("set_or_create_locator", methods)
        self.assertIn("set_track_color", methods)


class Phase4Tests(unittest.TestCase):
    def test_blocks_audioldm2(self):
        result = synthesize_texture("riser", backend="audioldm2")
        self.assertEqual(result["error"], "blocked_backend")

    def test_musicgen_stays_gated(self):
        result = synthesize_texture("riser", backend="musicgen")
        self.assertEqual(result["error"], "generation_disabled")

    def test_generation_off_by_default(self):
        result = synthesize_texture("gritty vinyl ambient rumble in F minor")
        self.assertEqual(result["error"], "generation_disabled")

    def test_demucs_disabled(self):
        result = split_stems(str(SILENCE))
        self.assertEqual(result["error"], "demucs_disabled")

    def test_local_search(self):
        result = search_local("dark punchy snare", str(ROOT / "fixtures"))
        self.assertTrue(result["ok"])
        self.assertEqual(result["backend"], "filename-tokens")
        self.assertTrue(result["hits"])

    def test_unmatched_query_still_lists_files(self):
        result = search_local("zzzz-not-a-filename-token", str(ROOT / "fixtures"))
        self.assertTrue(result["ok"])
        self.assertTrue(result["hits"])
        self.assertTrue(any("silence.wav" in item["file_path"] for item in result["hits"]))

    def test_empty_query_browses_library(self):
        result = search_local("", str(ROOT / "fixtures"), limit=20)
        self.assertTrue(result["ok"])
        self.assertEqual(result["backend"], "browse")
        self.assertTrue(any("silence.wav" in item["file_path"] for item in result["hits"]))
        self.assertIn("name", result["hits"][0])


class Phase5Tests(unittest.TestCase):
    def test_ducking_and_room_do_not_write(self):
        duck = ducking_plan([{"hz": 250, "stems": ["kick", "bass"]}])
        room = room_curve({"low": 1.4, "high": 0.8})
        self.assertFalse(duck["wrote"])
        self.assertTrue(room["apply_explicit"])
        self.assertTrue(room["curve"])

    def test_dawdreamer_engine_is_offline_only(self):
        result = dawdreamer_rehearse("example.vst3", [])
        self.assertFalse(result["wrote"])
        if result.get("ok"):
            self.assertEqual(result["backend"], "dawdreamer")
            self.assertIsNotNone(result.get("session_state"))
        else:
            self.assertEqual(result["error"], "dawdreamer_unavailable")


class Phase6Tests(unittest.TestCase):
    def test_export_writes_cloned_als(self):
        with tempfile.TemporaryDirectory() as dest:
            result = export_session(dest, midi_path=str(EMPTY_MID), stem_paths=[str(SILENCE)])
            self.assertTrue(result["wrote_als"], result)
            self.assertTrue(any(str(path).endswith(".als") for path in result["files"]))
            self.assertGreaterEqual(len(result["files"]), 2)
            self.assertFalse(result["session"].get("overwrote_source"))


class IntentStillWorks(unittest.TestCase):
    def test_handle_intent(self):
        status, payload = handle_intent(empty_intent())
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])


if __name__ == "__main__":
    unittest.main()
