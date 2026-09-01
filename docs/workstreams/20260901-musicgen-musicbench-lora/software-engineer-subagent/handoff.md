---
schema_version: 1
task_id: 20260901-musicgen-musicbench-lora
role_id: software-engineer-subagent
status: blocked
revision: 2
started_at: 2026-09-01T17:56:00Z
completed_at: 2026-09-01T18:25:00Z
charter: docs/workstreams/20260901-musicgen-musicbench-lora/software-engineer-subagent/charter.md
plan: docs/workstreams/20260901-musicgen-musicbench-lora/software-engineer-subagent/plan.md
predecessor_handoffs: []
verdict: BLOCKED
downstream_role: security-engineer-subagent
---

# Engineering handoff

## 1. Outcome

Implemented and locally verified the pinned MusicGen MusicBench LoRA Job wrapper. **Did not submit a Job and did not train.** This Cloud VM has no Hugging Face login (`HF_TOKEN` unset; `hf auth whoami` -> Not logged in). Verdict **BLOCKED on token**.

Training is **not** claimed succeeded. Persist remains stock `facebook/musicgen-small`. The adapter was not applied. `MusicBench.tar.gz` was not downloaded on this VM.

## 2. Scope completed and not completed

Completed: wrapper, submit pins, preflight/bulk gate, shims, local tests, workstream artifacts, draft PR.

Not completed: HF Job create, PREFLIGHT_OK on a Job, COMPLETED inspect, Hub adapter weights.

## 3. Charter, plan, and predecessor handoffs

Charter and plan revision 2. Predecessor PR 1 wrapper was unpinned and string-patched dreamboothing; this branch replaces that approach.

## 4. Outputs, changed paths, and external changes

- `train/scripts/musicgen-lora-musicbench.py`
- `train/remote/submit-musicgen-lora.sh`
- `train/remote/hf-jobs-musicgen-lora.md`
- `train/tests/test_musicgen_lora_wrapper.py`
- `docs/decisions/2026-09-01-musicgen-musicbench-lora-hf-job.md`
- this workstream

External changes: none. No HF Job. No Hub model files written by this run.

PR: https://github.com/cam-douglas/context/pull/2

## 5. Requirement and horizontal-checklist coverage

| Requirement ID | Result | Evidence |
|---|---|---|
| SE-1 | BLOCKED | No token; submit not reached |
| SE-2 | implemented | `BASE_MODEL=facebook/musicgen-small` |
| SE-3 | implemented | PREFLIGHT_OK gate; tar not fetched here |
| SE-4 | pending | Intended `cam-douglas/context-musicgen-small-musicbench-lora` |
| SE-5 | PASS | No secrets/weights in git |
| SE-6 | designed | a10g-large, 16h, ~$24; 20k/2500 |
| SE-7 | PASS | exact `--with` pins in submit + `UV_WITH` |
| SE-8 | PASS (local) | preflight then bulk; gate tests |
| SE-9 | PASS (local) | shims only; no in-place patch |
| SE-10 | PASS (local) | `_assert_stack` unit tests |
| SE-11 | PASS | argv builder omits forbidden flags |
| SE-12 | BLOCKED | No Job COMPLETED; no Hub adapter files |

Horizontal: Experience/client/server/growth not_applicable. Integrations/identity blocked on token. Persist/sidecar/plugin not modified.

## 6. Validation and evidence

```text
python3 -m unittest train.tests.test_musicgen_lora_wrapper -v
# 16 tests OK on first run; re-run after submit whoami harden

HF_TOKEN unset
hf (temp /tmp/hf-cli-pkgs, not sidecar/.venv) auth whoami -> Not logged in
huggingface_hub.whoami() -> LocalTokenNotFoundError
git diff origin/main -- sidecar plugin -> empty
```

Failed Job root cause addressed in source: pins + no `--overwrite_output_dir` + no `--preprocessing_num_workers` + serial map shim + no string-patch.

## 7. Tools, skills, modalities, and MCP evidence

- No Hugging Face MCP in this session.
- `hf` was not on the default PATH. A throwaway `pip install --target /tmp/hf-cli-pkgs huggingface_hub` was used only for whoami. Not `sidecar/.venv`.
- GitHub MCP used to inspect predecessor branch/PR 1.

## 8. Assumptions, decisions, and deviations

Assumptions: MusicBench remains JSONL + tar with `main_caption` / `location`; shims are sufficient; unique output dirs replace overwrite.

Decisions: exact 4.51.3 pin set; preflight 1-step smoke on the Job; STOP on 402.

Deviations: submit skipped after auth failure, per brief. Full Job preflight was not executed on this VM (would download musicgen-small and is GPU work).

## 9. Findings, severity, risks, and unresolved items

| ID | Severity | Finding |
|---|---|---|
| B-1 | high | Missing `HF_TOKEN` on the Cloud VM. Job cannot be created. |

Unresolved: Job id, PREFLIGHT_OK on Job, COMPLETED, Hub adapter files, Security review of a live `--secrets HF_TOKEN` submit.

Risks: Job spend after a later submit (capped 16h / ~$24). Adapter inherits CC-BY-NC 4.0.

## 10. Remediation and invalidated gates

1. Inject `HF_TOKEN` into the Cloud environment (do not paste it into chat).
2. `hf auth whoami` must not print `Not logged in`.
3. Run `bash train/remote/submit-musicgen-lora.sh` once.
4. On 402, STOP. Else watch `PREFLIGHT_OK`, then COMPLETED or ERROR.
5. On ERROR, fix the wrapper without floating pins; resubmit once per distinct root cause.
6. Confirm `adapter_model.safetensors` (or equivalent) on `cam-douglas/context-musicgen-small-musicbench-lora`.
7. Do not apply the adapter to persist.

Invalidated gates: Security and Project Lead cannot PASS a completed Job until one exists.

## 11. Downstream instructions

Security: review `--secrets HF_TOKEN`, private repo, CC-BY-NC card, pin set, no token in git. Do not treat a Job as running.

## 12. Human actions and production approvals

- Inject a write-scoped Hugging Face token as `HF_TOKEN` (Jobs + private model repo). Do not paste the value into chat.
- After submit: monitor the Job; cancel if it errors or will exceed the credit.
- Do not apply the adapter to persist.

Production approvals: none. Not a production deploy.

## 13. Proposed state and memory updates

- Active workstream: `docs/workstreams/20260901-musicgen-musicbench-lora/manifest.md`
- Active role/gate: software-engineer-subagent BLOCKED on HF_TOKEN
- Next action: inject token, submit once, watch PREFLIGHT_OK then COMPLETED
- Durable: MusicGen LoRA Job wrapper lives under `train/`; pins are transformers==4.51.3 / datasets==3.2.0; dreamboothing is shimmed, not patched; MusicBench tar is Job-only after PREFLIGHT_OK

## 14. Verdict

**BLOCKED** — missing HF_TOKEN. Wrapper and tests are on `cursor/musicgen-lora-pinned-e355`. No Job COMPLETED. Do not claim training succeeded.
