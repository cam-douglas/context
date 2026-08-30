import unittest

from context_sidecar.schema import (
    SchemaError,
    empty_arrangement,
    validate_arrangement,
)


class ArrangementSchemaTests(unittest.TestCase):
    def test_empty_arrangement_is_valid(self):
        plan = empty_arrangement()
        self.assertEqual(validate_arrangement(plan), plan)

    def test_rejects_musicgen_era_missing_sections(self):
        plan = empty_arrangement()
        del plan["sections"]
        with self.assertRaises(SchemaError):
            validate_arrangement(plan)

    def test_rejects_audio_clip_without_path(self):
        plan = empty_arrangement()
        plan["tracks"] = [
            {
                "id": "ref",
                "name": "Reference",
                "kind": "audio",
                "clips": [
                    {
                        "id": "ref-1",
                        "kind": "audio",
                        "start_beats": 0,
                        "length_beats": 16,
                    }
                ],
            }
        ]
        with self.assertRaises(SchemaError):
            validate_arrangement(plan)

    def test_accepts_audio_clip_with_path(self):
        plan = empty_arrangement()
        plan["tracks"] = [
            {
                "id": "ref",
                "name": "Reference",
                "kind": "audio",
                "clips": [
                    {
                        "id": "ref-1",
                        "kind": "audio",
                        "start_beats": 0,
                        "length_beats": 16,
                        "file_path": "/tmp/fixture.wav",
                    }
                ],
            }
        ]
        validate_arrangement(plan)


if __name__ == "__main__":
    unittest.main()
