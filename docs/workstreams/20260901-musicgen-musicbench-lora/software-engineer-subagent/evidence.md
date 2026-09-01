---
schema_version: 1
task_id: 20260901-musicgen-musicbench-lora
role_id: software-engineer-subagent
revision: 2
updated_at: 2026-09-01T18:25:00Z
---

# Role Evidence: software-engineer-subagent

## Evidence record

- Requirement ID: SE-7
- Claim: Submit script and wrapper carry the exact required pins
- Evidence state: `VERIFIED`
- Method: unittest + source inspect
- Exact command or tool: `python3 -m unittest train.tests.test_musicgen_lora_wrapper -v`
- Artifact, path, source, or stable reference: `train/remote/submit-musicgen-lora.sh`, `train/scripts/musicgen-lora-musicbench.py` `UV_WITH`
- Sanitized result and exit status: 16 tests OK after submit whoami harden
- Timestamp: 2026-09-01T18:26:00Z
- Environment: Cursor Cloud VM, Python 3.12.3, branch `cursor/musicgen-lora-pinned-e355`
- Limitations: Pins are source-verified, not installed on this VM
- Required follow-up: Job image must install the same `--with` list

## Evidence record

- Requirement ID: SE-8 / SE-3
- Claim: `bulk()` and `_download_musicbench()` refuse `MusicBench.tar.gz` until `PREFLIGHT_OK`
- Evidence state: `VERIFIED`
- Method: unittest calling `_refuse_tar_until_preflight`, `_download_musicbench`, `bulk` with `PREFLIGHT_OK=False`
- Exact command or tool: `test_refuse_tar_until_preflight_ok`, `test_bulk_refuses_before_tar_without_preflight`
- Artifact, path, source, or stable reference: `train/scripts/musicgen-lora-musicbench.py`
- Sanitized result and exit status: SystemExit contains `PREFLIGHT_OK` and `MusicBench.tar.gz`
- Timestamp: 2026-09-01T18:20:00Z
- Environment: same Cloud VM
- Limitations: Full Job preflight (clone + 1-step smoke) was not run here
- Required follow-up: Watch Job logs for the line `PREFLIGHT_OK` before tar download

## Evidence record

- Requirement ID: SE-9
- Claim: Wrapper does not edit or string-patch dreamboothing
- Evidence state: `VERIFIED`
- Method: source inspect for banned patch tokens; runtime sha256 check exists
- Exact command or tool: `test_no_in_place_dreamboothing_patch`
- Artifact, path, source, or stable reference: wrapper source
- Sanitized result and exit status: no `script.write_text`, `_patch_local_dataset_load`, or `replace(needle`; shims present
- Timestamp: 2026-09-01T18:20:00Z
- Environment: same
- Limitations: Job-time sha256 compare runs only on HF Jobs
- Required follow-up: none if Job logs show `shims_installed` and no trainer write

## Evidence record

- Requirement ID: SE-10 / SE-11
- Claim: `_assert_stack` rejects transformers 5 and missing `tokenizer=`; argv omits forbidden flags
- Evidence state: `VERIFIED`
- Method: mocked modules + `_trainer_argv` unit tests
- Exact command or tool: `test_assert_stack_*`, `test_trainer_argv_*`
- Artifact, path, source, or stable reference: wrapper
- Sanitized result and exit status: major>=5 and missing tokenizer SystemExit; no `--overwrite_output_dir` / `--preprocessing_num_workers`
- Timestamp: 2026-09-01T18:20:00Z
- Environment: same
- Limitations: mocks, not a real transformers 4.51.3 install on this VM
- Required follow-up: Job `_assert_stack` log `stack_ok transformers=4.51.3`

## Evidence record

- Requirement ID: SE-5
- Claim: No secrets or adapter weights in git; persist / sidecar / plugin untouched
- Evidence state: `VERIFIED`
- Method: `git diff origin/main -- sidecar plugin` line count 0; submit script never echoes token
- Exact command or tool: git diff; `test_submit_flavor_and_timeout`
- Artifact, path, source, or stable reference: this branch vs `origin/main`
- Sanitized result and exit status: sidecar/plugin diff empty; no `hf auth token`
- Timestamp: 2026-09-01T18:22:00Z
- Environment: same
- Limitations: none
- Required follow-up: none

## Evidence record

- Requirement ID: SE-1 / SE-12
- Claim: A Hugging Face Job COMPLETED and Hub adapter weights exist
- Evidence state: `UNVERIFIED`
- Method: env inspect; temp `huggingface_hub` whoami; no Job create
- Exact command or tool: `echo token_len`; `hf auth whoami` via `/tmp/hf-cli-pkgs` (not sidecar/.venv)
- Artifact, path, source, or stable reference: this file
- Sanitized result and exit status: `HF_TOKEN` unset; `hf auth whoami` -> `Not logged in`; `huggingface_hub.whoami()` -> `LocalTokenNotFoundError`. `PATH=/tmp/hf-cli-pkgs/bin bash train/remote/submit-musicgen-lora.sh` -> `BLOCKED: missing HF_TOKEN` exit 2. No Job id.
- Timestamp: 2026-09-01T18:24:00Z
- Environment: Cursor Cloud VM `bc-e013bf6c-d9f3-4a7f-a17c-d4232193e355`
- Limitations: Cannot submit, inspect, or confirm Hub files without a token
- Required follow-up: Inject `HF_TOKEN`, run `bash train/remote/submit-musicgen-lora.sh` once, inspect to COMPLETED, confirm `adapter_model.safetensors` on `cam-douglas/context-musicgen-small-musicbench-lora`

## Evidence record

- Requirement ID: SE-2 / SE-4 / SE-6
- Claim: Host is musicgen-small; private adapter id; a10g-large 16h ~$24 with 20k/2500 caps
- Evidence state: `VERIFIED` (source) / `UNVERIFIED` (remote create)
- Method: source inspect
- Exact command or tool: read wrapper + submit
- Artifact, path, source, or stable reference: `BASE_MODEL`, `ADAPTER_REPO`, submit `--flavor` / `--timeout`
- Sanitized result and exit status: constants match the brief
- Timestamp: 2026-09-01T18:20:00Z
- Environment: same
- Limitations: Job not created
- Required follow-up: submit when token exists; STOP on 402
