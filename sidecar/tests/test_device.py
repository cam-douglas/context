import unittest

from context_sidecar.device import (
    CHROME_ROWS,
    STATUS,
    can_apply,
    can_audition,
    can_run,
    default_chrome_state,
    reference_knobs_enabled,
    status_for,
)
from context_sidecar.writer import apply_plan


class DeviceChromeTests(unittest.TestCase):
    def test_ten_rows(self):
        self.assertEqual(len(CHROME_ROWS), 10)

    def test_fail_closed_without_sidecar(self):
        self.assertFalse(can_run(health=None, prompt="add a bridge"))
        self.assertFalse(can_apply(health={"ok": False}, has_preview=True))
        self.assertEqual(status_for(health=None, prompt="x", has_preview=False), STATUS["sidecar_down"])

    def test_empty_prompt_blocks_run(self):
        health = {"ok": True}
        self.assertFalse(can_run(health=health, prompt="  "))
        self.assertEqual(status_for(health=health, prompt="", has_preview=False), STATUS["empty_prompt"])

    def test_run_and_apply_when_ready(self):
        health = {"ok": True}
        self.assertTrue(can_run(health=health, prompt="add a bridge"))
        self.assertTrue(can_apply(health=health, has_preview=True))
        self.assertTrue(can_audition(has_preview=True))

    def test_audition_never_writes(self):
        self.assertFalse(default_chrome_state()["audition_writes"])

    def test_reference_knobs_disabled_until_path(self):
        self.assertFalse(reference_knobs_enabled(""))
        self.assertTrue(reference_knobs_enabled("/tmp/ref.wav"))


class WriterGuardTests(unittest.TestCase):
    def test_refuses_when_sidecar_down(self):
        result = apply_plan(
            sidecar_ok=False,
            prompt="add a bridge",
            tracks=[{"id": "a", "kind": "audio"}, {"id": "m", "kind": "midi"}],
            audio_path="/tmp/silence.wav",
        )
        self.assertFalse(result["wrote"])

    def test_creates_one_audio_and_one_midi(self):
        result = apply_plan(
            sidecar_ok=True,
            prompt="add a bridge",
            tracks=[
                {"id": "a", "kind": "audio", "frozen": False},
                {"id": "m", "kind": "midi", "locked": False},
            ],
            audio_path="/tmp/silence.wav",
        )
        self.assertTrue(result["wrote"])
        methods = [action["method"] for action in result["actions"]]
        self.assertEqual(methods, ["create_audio_clip", "create_midi_clip"])
        self.assertIn("Undo", result["undo_hint"])

    def test_skips_frozen_tracks(self):
        result = apply_plan(
            sidecar_ok=True,
            prompt="add a bridge",
            tracks=[
                {"id": "a", "kind": "audio", "frozen": True},
                {"id": "m", "kind": "midi"},
            ],
            audio_path="/tmp/silence.wav",
        )
        self.assertFalse(result["wrote"])


if __name__ == "__main__":
    unittest.main()
