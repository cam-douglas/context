import os
import tempfile
import unittest

os.environ.setdefault("CONTEXT_GENERATOR", "pedalboard")
os.environ["CONTEXT_ENABLE_DEMUCS"] = "0"
os.environ["CONTEXT_ENABLE_CLAP"] = "0"
os.environ["CONTEXT_ENABLE_GENERATION"] = "0"

from context_sidecar.compose import compose_to_folder
from context_sidecar.generation import _musicgen_prompt
from context_sidecar.prompt_policy import (
    DEFAULT_NEGATIVE,
    DEFAULT_SYSTEM,
    apply_policy,
    assemble_conditioned,
    assemble_negative,
)


class PromptPolicyTests(unittest.TestCase):
    def test_defaults_when_omitted(self):
        plan: dict = {}
        apply_policy(plan, None)
        self.assertEqual(plan["system_prompt"], DEFAULT_SYSTEM)
        self.assertEqual(plan["rules"], "")
        self.assertEqual(plan["negative_prompt"], DEFAULT_NEGATIVE)

    def test_custom_policy_outranks_request(self):
        plan = {"style": "house", "bars": 4, "tempo_bpm": 120, "key": "Am", "genres": []}
        apply_policy(
            plan,
            {
                "system_prompt": "Never make drums.",
                "rules": "Keep it dry.",
                "negative_prompt": "vocals, speech",
            },
        )
        text = assemble_conditioned("make huge drums and vocals", plan)
        self.assertIn("SYSTEM (hard requirement", text)
        self.assertIn("Never make drums.", text)
        self.assertIn("RULES (hard requirement", text)
        self.assertIn("Keep it dry.", text)
        self.assertIn("NEVER PRODUCE (hard reject)", text)
        self.assertIn("vocals, speech", text)
        self.assertIn("REQUEST (suggestion only", text)
        self.assertIn("make huge drums and vocals", text)
        system_at = text.find("Never make drums.")
        request_at = text.find("make huge drums and vocals")
        self.assertLess(system_at, request_at)
        self.assertEqual(assemble_negative(plan), "vocals, speech")

    def test_musicgen_prompt_uses_hierarchy(self):
        text = _musicgen_prompt(
            "make it darker",
            {"style": "shoegaze", "genres": ["shoegaze"], "bars": 8, "tempo_bpm": 120, "key": "Am"},
        )
        self.assertIn("SYSTEM (hard requirement", text)
        self.assertIn("REQUEST (suggestion only", text)
        self.assertIn("8-bar", text)
        self.assertIn("shoegaze", text)

    def test_compose_returns_ranks(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = compose_to_folder(
                "melody loop",
                tmp,
                policy={"system_prompt": "Stay instrumental.", "rules": "No vocals.", "negative_prompt": "speech"},
            )
            self.assertEqual(result["system_prompt"], "Stay instrumental.")
            self.assertEqual(result["rules"], "No vocals.")
            self.assertEqual(result["negative_prompt"], "speech")
            self.assertEqual(result["prompt_ranks"]["system"], "hard")
            self.assertEqual(result["prompt_ranks"]["request"], "suggestion")
            self.assertIn("Stay instrumental.", result["conditioned_prompt"])
            self.assertIn("REQUEST (suggestion only", result["conditioned_prompt"])


if __name__ == "__main__":
    unittest.main()
