import unittest

from context_sidecar.intent import empty_intent, validate_intent
from context_sidecar.schema import SchemaError


class IntentSchemaTests(unittest.TestCase):
    def test_track_follow_intent_is_valid(self):
        intent = empty_intent(prompt="add a bridge")
        self.assertEqual(validate_intent(intent)["prompt"], "add a bridge")

    def test_drop_in_requires_path(self):
        intent = empty_intent(mode="drop_in", prompt="remove a layer")
        validate_intent(intent)
        del intent["drop_in"]
        with self.assertRaises(SchemaError):
            validate_intent(intent)

    def test_reference_requires_path(self):
        intent = empty_intent(mode="reference", prompt="inspired by this")
        validate_intent(intent)
        intent["reference"]["file_path"] = "   "
        with self.assertRaises(SchemaError):
            validate_intent(intent)

    def test_rejects_empty_prompt(self):
        intent = empty_intent()
        intent["prompt"] = "  "
        with self.assertRaises(SchemaError):
            validate_intent(intent)

    def test_rejects_abstraction_out_of_range(self):
        intent = empty_intent()
        intent["knobs"]["abstraction"] = 1.5
        with self.assertRaises(SchemaError):
            validate_intent(intent)

    def test_rejects_reference_payload_on_track_mode(self):
        intent = empty_intent()
        intent["reference"] = {"file_path": "/tmp/reference.wav"}
        with self.assertRaises(SchemaError):
            validate_intent(intent)


if __name__ == "__main__":
    unittest.main()
