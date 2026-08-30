import unittest

from context_sidecar.intent import validate_project_snapshot
from context_sidecar.roles import infer_role
from context_sidecar.snapshot import build_project_snapshot


class RoleTests(unittest.TestCase):
    def test_drums_from_name(self):
        self.assertEqual(infer_role("Drums"), "drums")
        self.assertEqual(infer_role("808 Kick"), "drums")

    def test_other_when_unknown(self):
        self.assertEqual(infer_role("Track 12"), "other")


class SnapshotTests(unittest.TestCase):
    def test_builds_host_and_project(self):
        live_set = {
            "tempo_bpm": 124,
            "musical_key": "F#m",
            "playhead_beats": 8,
            "tracks": [
                {
                    "id": "1",
                    "name": "Drums",
                    "kind": "midi",
                    "clips": [
                        {
                            "id": "c1",
                            "start_beats": 0,
                            "length_beats": 8,
                            "notes": [],
                        }
                    ],
                },
                {
                    "id": "2",
                    "name": "Bass",
                    "kind": "audio",
                    "clips": [
                        {
                            "id": "c2",
                            "start_beats": 0,
                            "length_beats": 8,
                            "file_path": "/tmp/bass.wav",
                        }
                    ],
                },
            ],
        }
        built = build_project_snapshot(live_set, host_track_id="1")
        validate_project_snapshot(built["project"])
        self.assertEqual(built["host_track"]["inferred_role"], "drums")
        self.assertEqual(built["project"]["tracks"][1]["inferred_role"], "bass")
        self.assertEqual(len(built["project"]["tracks"]), 2)


if __name__ == "__main__":
    unittest.main()
