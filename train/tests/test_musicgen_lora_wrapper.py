#!/usr/bin/env python3
"""Pins, PREFLIGHT_OK gate, and no in-place dreamboothing patch."""

from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "train/scripts/musicgen-lora-musicbench.py"
SUBMIT = ROOT / "train/remote/submit-musicgen-lora.sh"

REQUIRED_WITH = [
    "transformers==4.51.3",
    "huggingface_hub>=0.26.0,<1.0",
    "datasets==3.2.0",
    "peft==0.14.0",
    "accelerate==1.6.0",
    "evaluate",
    "sentencepiece",
    "librosa",
    "soundfile",
    "torchaudio",
]


def load_wrapper():
    spec = importlib.util.spec_from_file_location("musicgen_lora_musicbench", WRAPPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load wrapper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_wrapper()
        cls.src = WRAPPER.read_text(encoding="utf-8")
        cls.submit = SUBMIT.read_text(encoding="utf-8")

    def test_required_pins_in_wrapper_uv_with(self):
        joined = " ".join(self.mod.UV_WITH)
        for pin in REQUIRED_WITH:
            self.assertIn(pin, joined)

    def test_required_pins_in_submit_script(self):
        for pin in REQUIRED_WITH:
            self.assertIn(f'--with "{pin}"', self.submit)

    def test_submit_flavor_and_timeout(self):
        self.assertIn("--flavor a10g-large", self.submit)
        self.assertIn("--timeout 16h", self.submit)
        self.assertIn("STOP: hf jobs create returned 402", self.submit)
        self.assertIn("BLOCKED: missing HF_TOKEN", self.submit)
        self.assertIn("not logged in", self.submit)
        self.assertNotIn("echo \"$HF_TOKEN\"", self.submit)
        self.assertNotIn("print(HF_TOKEN)", self.submit)
        self.assertNotIn("hf auth token", self.submit)

    def test_no_in_place_dreamboothing_patch(self):
        banned = (
            "script.write_text",
            "_patch_local_dataset_load",
            "replace(needle",
            "text.replace(",
        )
        for token in banned:
            self.assertNotIn(token, self.src, token)
        self.assertIn("_load_dataset_shim", self.src)
        self.assertIn("_serial_call", self.src)
        self.assertIn("_assert_dreamboothing_untouched", self.src)
        self.assertIn("Never edit", self.src)

    def test_preflight_then_bulk_in_main(self):
        self.assertIn("def preflight(", self.src)
        self.assertIn("def bulk(", self.src)
        self.assertRegex(self.src, r"preflight\(\)\s*\n\s*bulk\(\)")

    def test_refuse_tar_until_preflight_ok(self):
        self.mod.PREFLIGHT_OK = False
        with self.assertRaises(SystemExit) as ctx:
            self.mod._refuse_tar_until_preflight()
        self.assertIn("PREFLIGHT_OK", str(ctx.exception))
        with self.assertRaises(SystemExit) as ctx:
            self.mod._download_musicbench()
        self.assertIn("MusicBench.tar.gz", str(ctx.exception))
        self.assertIn("PREFLIGHT_OK", str(ctx.exception))

    def test_bulk_refuses_before_tar_without_preflight(self):
        self.mod.PREFLIGHT_OK = False
        with self.assertRaises(SystemExit) as ctx:
            self.mod.bulk()
        self.assertIn("PREFLIGHT_OK", str(ctx.exception))

    def test_trainer_argv_omits_forbidden_flags(self):
        argv = self.mod._trainer_argv(
            dataset_name="/tmp/ds",
            output_dir="/tmp/out",
            max_steps=1,
            max_train_samples=2,
            push_to_hub=False,
        )
        for flag in self.mod.FORBIDDEN_FLAGS:
            self.assertNotIn(flag, argv)
        joined = " ".join(argv)
        self.assertNotIn("overwrite_output_dir", joined)
        self.assertNotIn("preprocessing_num_workers", joined)
        self.assertIn("--use_lora", argv)
        self.assertIn("facebook/musicgen-small", argv)

    def test_trainer_argv_push_omits_forbidden_flags(self):
        argv = self.mod._trainer_argv(
            dataset_name="/tmp/ds",
            output_dir="/tmp/out",
            max_steps=2500,
            max_train_samples=20000,
            push_to_hub=True,
            hub_model_id="cam-douglas/context-musicgen-small-musicbench-lora",
        )
        self.assertIn("--push_to_hub", argv)
        self.assertIn("cam-douglas/context-musicgen-small-musicbench-lora", argv)
        for flag in ("--overwrite_output_dir", "--preprocessing_num_workers"):
            self.assertNotIn(flag, argv)

    def test_assert_stack_rejects_transformers_major_5(self):
        fake = types.ModuleType("transformers")
        fake.__version__ = "5.0.0"

        class Trainer:
            def __init__(self, tokenizer=None):
                self.tokenizer = tokenizer

        fake.Seq2SeqTrainer = Trainer
        old = sys.modules.get("transformers")
        sys.modules["transformers"] = fake
        try:
            with self.assertRaises(SystemExit) as ctx:
                self.mod._assert_stack()
            self.assertIn("major>=5", str(ctx.exception))
        finally:
            if old is None:
                sys.modules.pop("transformers", None)
            else:
                sys.modules["transformers"] = old

    def test_assert_stack_rejects_missing_tokenizer(self):
        fake = types.ModuleType("transformers")
        fake.__version__ = "4.51.3"

        class Trainer:
            def __init__(self, processing_class=None):
                self.processing_class = processing_class

        fake.Seq2SeqTrainer = Trainer
        old = sys.modules.get("transformers")
        sys.modules["transformers"] = fake
        try:
            with self.assertRaises(SystemExit) as ctx:
                self.mod._assert_stack()
            self.assertIn("tokenizer=", str(ctx.exception))
        finally:
            if old is None:
                sys.modules.pop("transformers", None)
            else:
                sys.modules["transformers"] = old

    def test_assert_stack_accepts_4_51_with_tokenizer(self):
        fake = types.ModuleType("transformers")
        fake.__version__ = "4.51.3"

        class Trainer:
            def __init__(self, tokenizer=None):
                self.tokenizer = tokenizer

        fake.Seq2SeqTrainer = Trainer
        old_tf = sys.modules.get("transformers")
        old_ds = sys.modules.get("datasets")
        fake_ds = types.ModuleType("datasets")
        fake_ds.__version__ = "3.2.0"
        sys.modules["transformers"] = fake
        sys.modules["datasets"] = fake_ds
        try:
            self.mod._assert_stack()
        finally:
            if old_tf is None:
                sys.modules.pop("transformers", None)
            else:
                sys.modules["transformers"] = old_tf
            if old_ds is None:
                sys.modules.pop("datasets", None)
            else:
                sys.modules["datasets"] = old_ds

    def test_serial_call_strips_num_proc(self):
        seen = {}

        def original(*args, **kwargs):
            seen["kwargs"] = kwargs
            return "ok"

        wrapped = self.mod._serial_call(original)
        result = wrapped("ds", num_proc=1, desc="x")
        self.assertEqual(result, "ok")
        self.assertNotIn("num_proc", seen["kwargs"])
        self.assertEqual(seen["kwargs"]["desc"], "x")

    def test_sine_write_and_decode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sine.wav"
            self.mod._write_sine(path, seconds=0.25, freq=440.0)
            rate, nframes = self.mod._decode_wav(path)
            self.assertEqual(rate, 32000)
            self.assertGreater(nframes, 100)

    def test_assert_stack_function_exists(self):
        self.assertTrue(inspect.isfunction(self.mod._assert_stack))
        self.assertIn("major >= 5", self.src)
        self.assertIn('if "tokenizer" not in params', self.src)

    def test_persist_not_touched_by_wrapper(self):
        self.assertIn("persist=stock-no-apply", self.src)
        self.assertNotIn("sidecar/.venv", self.src)


if __name__ == "__main__":
    unittest.main()
