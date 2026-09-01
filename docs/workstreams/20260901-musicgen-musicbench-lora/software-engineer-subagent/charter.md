---
schema_version: 1
task_id: 20260901-musicgen-musicbench-lora
role_id: software-engineer-subagent
status: planning
revision: 2
created_at: 2026-09-01T17:56:00Z
updated_at: 2026-09-01T18:10:00Z
predecessor_handoffs: []
mission: Pin the 4.51.3 stack, wrap dreamboothing without editing it, preflight then bulk, and obtain a COMPLETED HF Job with private adapter files. Persist stays stock.
---

# Role Charter: software-engineer-subagent

## 1. Role objective

### Mission

Design and implement the smallest complete `train/` change that (1) pins the 2024 dreamboothing trainer to transformers 4.51.3 / datasets 3.2.0, (2) never edits or string-patches dreamboothing, (3) refuses `MusicBench.tar.gz` until `PREFLIGHT_OK`, and (4) submits one a10g-large Job when this VM has Hub auth. Persist remains stock `facebook/musicgen-small`. Do not apply the adapter.

## 2. Inherited request and evidence

- Workstream manifest: `docs/workstreams/20260901-musicgen-musicbench-lora/manifest.md`
- Active plan: this role `plan.md`
- Predecessor: PR 1 unpinned wrapper; seven failed Job ids in the user brief
- Decision: `docs/decisions/2026-09-01-musicgen-musicbench-lora-hf-job.md` (to be revised)
- Launch notes: `train/remote/hf-jobs-musicgen-lora.md`

## 3. Scope, non-goals, and ownership

Owned write paths:

- `train/scripts/musicgen-lora-musicbench.py`
- `train/remote/submit-musicgen-lora.sh`
- `train/remote/hf-jobs-musicgen-lora.md`
- `train/tests/`
- `docs/workstreams/20260901-musicgen-musicbench-lora/**`
- `docs/decisions/2026-09-01-musicgen-musicbench-lora-hf-job.md`

Read-only: `.cursor/AGENTS.md`, persist `generation.py` (confirm stock host only), sidecar, plugin.

External-system scope: Hugging Face Jobs + Hub private model repo when `HF_TOKEN` is present.

Prohibited actions: edit dreamboothing; string-patch it; install into `sidecar/.venv`; start ACE-Step; apply adapter to persist; download `MusicBench.tar.gz` on this VM or describe doing so on the owner Mac; print `HF_TOKEN`; pass `--overwrite_output_dir` or `--preprocessing_num_workers`; float to latest libs; plugin/UI copy.

## 4. Inherited requirements and vertical responsibilities

SE-1 through SE-12 in the manifest. Horizontal: integrations (HF Jobs + Hub), reliability (preflight gate), quality (local tests + Job inspect), performance/cost (flavor + caps), documentation.

## 5. Assumptions, open questions, and clarification decisions

| Assumption | Label | If wrong | Validation |
|---|---|---|---|
| MusicBench Hub is JSONL + `MusicBench.tar.gz`; caption `main_caption`; audio `location` | verified | Job cannot resolve wavs | metadata-only Hub inspect (no tar on this VM) |
| `load_dataset` shim + serial `map` shim are enough; no source edit | provisional | Job ERROR names a new trainer API | read logs; fix wrapper only; keep pins |
| Unique empty output dirs replace `--overwrite_output_dir` | verified (4.x trainer) | leftover dir error | timestamped dirs |
| Serial map avoids `num_proc=1` EOFError on GPU | provisional | still EOF | inspect Job logs |
| This Cloud VM may lack `HF_TOKEN` | blocking if submit required | cannot create Job | `hf auth whoami`; handoff BLOCKED |
| Adapter id is `cam-douglas/context-musicgen-small-musicbench-lora` | verified (owner) | whoami differs | Job `whoami` |

## 6. Skills, tools, and evidence sources

- Hugging Face Jobs via `hf` CLI when installed; `--secrets HF_TOKEN`.
- Local unittest in `train/tests/` (stdlib + wrapper import; no sidecar venv).
- No Hugging Face MCP in this session.
- Do not use `hf auth token` (prints the secret).

## 7. Outputs and storage paths

Charter, plan, evidence, handoff; wrapper; submit script; launch notes; tests; decision revision.

## 8. Horizontal quality coverage

| Area | Disposition | Rationale |
|---|---|---|
| Product value | reviewed | Owner-fixed host/dataset/persist-stock |
| Experience | not_applicable | No UI |
| Client | not_applicable | No client |
| Server and APIs | not_applicable | No sidecar API change |
| Data | owned | MusicBench columns; tar gated by PREFLIGHT_OK |
| Identity and access | reviewed | `--secrets HF_TOKEN`; private repo |
| Integrations | owned | HF Jobs + Hub push |
| Security and privacy | reviewed | no secrets in files; Security role still required |
| Reliability | owned | preflight then bulk; 16h timeout |
| Quality | owned | local pin/gate/patch tests; Job inspect |
| Performance and cost | owned | a10g-large, 20k/2500, STOP on 402 |
| Observability | owned | PREFLIGHT_OK log + Hub Job logs |
| Measurement and growth | not_applicable | |
| Delivery | owned | detached Job + Hub adapter |
| Documentation and operations | owned | launch notes + evidence |
| Ethics and communications | reviewed | CC-BY-NC 4.0 on adapter card; no commercial claim |

## 9. Validation plan and gate criteria

PASS only when: local tests pass; Job inspect stage is COMPLETED; Hub repo has `adapter_model.safetensors` or equivalent; persist was not modified.

BLOCKED when this VM has no `HF_TOKEN` after wrapper+tests are pushed. Do not claim training succeeded.

CONDITIONAL is not used for a missing Job.

## 10. Risks, blockers, and escalation triggers

Missing token; 402 payment; preflight smoke failure; dreamboothing API drift; CC-BY-NC 4.0.

## 11. Failure handling and recovery

On Job ERROR: read logs, fix the wrapper (keep pins), resubmit once per distinct root cause. Do not float libs. On 402, STOP. Do not download the tar locally as a workaround.

## 12. Downstream role and handoff conditions

Hand off to `security-engineer-subagent` with pin evidence, no-patch evidence, redacted submit command, Job id if any, adapter id, and token-handling evidence.
