---
schema_version: 1
task_id: 20260901-musicgen-musicbench-lora
role_id: software-engineer-subagent
status: active
revision: 2
created_at: 2026-09-01T18:10:00Z
updated_at: 2026-09-01T18:10:00Z
---

# Role Plan: software-engineer-subagent

## 1. Entry criteria and inherited evidence

Control-plane read complete. Preflight READY. Bootstrap complete. Prior unpinned wrapper and seven Job failure modes are known. Persist uses `facebook/musicgen-small`. This VM has no `HF_TOKEN` at plan time (`token_len 0`, `hf` not on PATH).

## 2. Scope, non-goals, and requirement coverage

| Requirement ID | Planned disposition | Expected evidence |
|---|---|---|
| SE-1 | submit script a10g-large 16h; STOP on 402 | script text + submit attempt |
| SE-2 | BASE_MODEL constant | source inspect |
| SE-3 | bulk refuses tar until PREFLIGHT_OK | unittest |
| SE-4 | private repo create + hub_model_id | source + Hub if token |
| SE-5 | no token print; no weights in git | grep + git inspect |
| SE-6 | caps + flavor | source |
| SE-7 | exact `--with` pins | unittest vs submit + wrapper |
| SE-8 | `preflight()` then `bulk()` | source + unittest |
| SE-9 | shims only; hash dreamboothing file | source + unittest |
| SE-10 | `_assert_stack` | unittest with mocks |
| SE-11 | argv builder omits forbidden flags | unittest |
| SE-12 | Job COMPLETED + adapter files | inspect if token; else BLOCKED |

## 3. Dependencies

Pinned uv packages on the Job. `ylacombe/musicgen-dreamboothing` cloned inside the Job only. Hub write token for submit.

## 4. Files, interfaces, data, and external systems

- Wrapper: `train/scripts/musicgen-lora-musicbench.py`
- Submit: `train/remote/submit-musicgen-lora.sh`
- Notes: `train/remote/hf-jobs-musicgen-lora.md`
- Tests: `train/tests/test_musicgen_lora_wrapper.py`
- Hub: Jobs + `cam-douglas/context-musicgen-small-musicbench-lora`
- Data: MusicBench JSON metadata (this VM ok) + tar (Job after PREFLIGHT_OK only)

## 5. Ownership and concurrency

Sole writer of `train/` and this role directory for the assignment window.

## 6. Ordered tasks

1. Write charter/plan (this file). Paths: workstream. Method: role templates. Output: planning artifacts.
2. Implement wrapper: `_assert_stack`, load_dataset shim, serial map/filter shim, `preflight()` (clone, ast+compile, import, HfArgumentParser, 2 sines, decode, 1-step smoke, no push), `bulk()` after `PREFLIGHT_OK`, unique output dirs, no forbidden flags, dreamboothing sha256 unchanged. Never `write_text` the trainer.
3. Implement submit script with exact `--with` pins. Never print `HF_TOKEN`. Flavor a10g-large, timeout 16h, STOP on 402.
4. Local tests for pins, PREFLIGHT_OK gate, no in-place patch, forbidden flags, `_assert_stack`.
5. Commit, push, open draft PR, then run tests.
6. If `hf auth whoami` works, submit one Job, watch PREFLIGHT_OK then COMPLETED/ERROR, fix wrapper (keep pins) on ERROR. If no token, handoff BLOCKED.
7. Confirm adapter files on Hub if Job completes. Do not apply to persist.

## 7. Tool and modality plan

Local: Python unittest, source inspect. Remote: `hf jobs` when authenticated. No browser. No sidecar venv.

## 8. Horizontal full-stack checklist

See charter section 8. All rows assessed.

## 9. Risk controls, rollback, and recovery

- Pins stay exact on retry.
- One resubmit per distinct root cause.
- 402: STOP.
- Git rollback is revert of this branch. Job spend is not reversible; timeout caps it.
- Persist untouched so product rollback is none.

## 10. Validation steps and expected evidence

```text
python3 -m unittest train.tests.test_musicgen_lora_wrapper
# if token:
bash train/remote/submit-musicgen-lora.sh
hf jobs inspect <id>
# Hub file list for adapter weights
```

## 11. Outputs and storage paths

Listed in charter section 3.

## 12. Gate criteria and downstream handoff

Engineering PASS requires COMPLETED Job + adapter weights. Missing token after local verification is BLOCKED, not PASS.

## 13. Deviations and plan change log

- 2026-09-01 r2: remediating unpinned wrapper; COMPLETED is now the success bar (was SCHEDULING).
