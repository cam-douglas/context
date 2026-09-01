---
schema_version: 1
task_id: 20260901-musicgen-musicbench-lora
title: MusicGen-small LoRA on MusicBench via Hugging Face Jobs
source_request: Persist stock musicgen-small. Submit a pinned HF Job that trains a private LoRA adapter on MusicBench. Do not apply the adapter. Do not download MusicBench.tar.gz on the Cloud VM or owner Mac.
owner: user-operator
status: in_progress
created_at: 2026-09-01T11:45:00Z
updated_at: 2026-09-01T18:10:00Z
revision: 2
objective: A Hugging Face Job COMPLETED successfully and private adapter files exist at cam-douglas/context-musicgen-small-musicbench-lora. Persist stays stock facebook/musicgen-small.
scope: train/ job wrapper, pinned uv deps, preflight-then-bulk, local tests, workstream evidence, one HF Jobs submit when HF_TOKEN is present
non_goals: sidecar infer; sidecar/.venv; plugin/UI; persist apply; ACE-Step; in-place dreamboothing edits; string-patches; floating latest transformers/datasets; downloading MusicBench.tar.gz on this VM or the owner Mac
risk_tier: 3
risk_reasons: remote paid GPU job, Hub token forwarding, private adapter publish, CC-BY-NC 4.0 base weights
impacted_domains: remote training, Hub repos, billing
reversibility: high for git; Job spend is one-way up to timeout
---

# Workstream Manifest: MusicGen MusicBench LoRA (HF Jobs)

## 1. Objective and requested outcome

Train a **private** LoRA adapter for stock `facebook/musicgen-small` on `amaai-lab/MusicBench` using Hugging Face Jobs. Persist must stay stock. Do not apply the adapter.

Seven prior Jobs failed because `ylacombe/musicgen-dreamboothing` (2024, `check_min_version` 4.40) ran against latest transformers 5 / datasets 4. Root fix is a pinned 4.51.3 stack plus load_dataset/serial-map shims, not latest-lib whack-a-mole.

## 2. Source request and project context

- Predecessor branch `cursor/musicgen-musicbench-lora-a3c5` / PR 1 shipped an unpinned wrapper that string-patched dreamboothing and was BLOCKED on missing `HF_TOKEN`.
- Failed Job ids: `6a96bba221c5aa7c8364b62c`, `6a96ca5d21c5aa7c8364b7e9`, `6a96d1830718b0f6d890cc2c`, `6a96d2aa21c5aa7c8364b91d`, `6a96d3be0718b0f6d890cc93`, `6a96d56e21c5aa7c8364b9a5`, `6a96d63f0718b0f6d890cd1f`.
- Persist host: `sidecar/src/context_sidecar/generation.py` (`facebook/musicgen-small`).

## 3. Scope and non-goals

In: `train/scripts/`, `train/remote/`, `train/tests/`, this workstream, decision record, one `hf jobs` create when authenticated.

Out: MusicBench tar on this VM or owner Mac; sidecar/.venv; persist apply; ACE-Step; editing or string-patching dreamboothing; `--overwrite_output_dir`; `--preprocessing_num_workers`.

## 4. Risk classification

- Selected tier: **Tier 3** (paid remote job, credential forwarding, Hub write, license).
- Reversibility: git is reversible; Job spend is not.
- Data: MusicBench cc-by-sa-3.0; MusicGen weights CC-BY-NC 4.0.

## 5. Role routing matrix

| Role ID | Required or skipped | Reason/evidence | Status | Verdict |
|---|---|---|---|---|
| `product-manager-subagent` | skipped | Owner already decided host, dataset, method, budget, adapter naming, persist-stock | skipped | n/a |
| `ui-ux-developer-subagent` | skipped | train/ only; ASCII plugin/UI rule does not apply here | skipped | n/a |
| `software-engineer-subagent` | required | Wrapper, pins, tests, Job submit | in_progress | |
| `security-engineer-subagent` | required by Tier 3 | Token forwarding + private Hub write | pending | |
| `growth-marketing-subagent` | skipped | No launch or claims | skipped | n/a |
| `project-lead-subagent` | required by Tier 3 | Reconciliation after Security | pending | |

Routing decision owner: software-engineer-subagent (owner authorized 2026-09-01; remediating failed Jobs).

## 6. Requirement traceability

| ID | Requirement | Evidence |
|---|---|---|
| SE-1 | Detached HF Job on a10g-large, 16h; STOP on 402 | submit script + evidence |
| SE-2 | Host facebook/musicgen-small LoRA | wrapper constants |
| SE-3 | MusicBench extract only after PREFLIGHT_OK, only inside the Job | wrapper `bulk()` gate |
| SE-4 | Private adapter `cam-douglas/context-musicgen-small-musicbench-lora` | wrapper + Hub inspect |
| SE-5 | No secrets/weights in git; never print HF_TOKEN | inspection |
| SE-6 | Budget cap: a10g-large, 16h, ~$24; 20k/2500 | submit + wrapper caps |
| SE-7 | Exact pins: transformers==4.51.3; huggingface_hub>=0.26.0,<1.0; datasets==3.2.0; peft==0.14.0; accelerate==1.6.0; evaluate; sentencepiece; librosa; soundfile; torchaudio | submit `--with` + tests |
| SE-8 | preflight() then bulk(); refuse tar until PREFLIGHT_OK | wrapper + tests |
| SE-9 | No dreamboothing edit or string-patch; load_dataset + serial map shims only | wrapper + tests |
| SE-10 | `_assert_stack()` exits on transformers major>=5 or Seq2SeqTrainer lacking tokenizer= | wrapper + tests |
| SE-11 | Do not pass `--overwrite_output_dir` or `--preprocessing_num_workers` | wrapper + tests |
| SE-12 | Job inspect stage COMPLETED and Hub adapter weights exist | Job/Hub evidence or BLOCKED on token |

## 7. Dependency and gate order

software-engineer-subagent -> security-engineer-subagent -> project-lead-subagent.

## 8. Path and external-system ownership

| Path or system | Writer | Allowed operation |
|---|---|---|
| `train/scripts/` `train/remote/` `train/tests/` | software-engineer-subagent | create/update |
| `docs/workstreams/20260901-musicgen-musicbench-lora/software-engineer-subagent/` | software-engineer-subagent | create/update |
| `docs/decisions/2026-09-01-musicgen-musicbench-lora-hf-job.md` | software-engineer-subagent | update pins/preflight |
| Hugging Face Jobs + Hub adapter repo | software-engineer-subagent | create Job / private repo when token present |
| `sidecar/` `plugin/` persist apply | none | prohibited |

## 9. Tool and MCP constraints

- `hf` CLI + `--secrets HF_TOKEN`. Never print the token.
- No Hugging Face MCP in this environment.
- Do not install into `sidecar/.venv`.
- Do not start ACE-Step.

## 10. Decisions, clarifications, and provisional assumptions

- Pins are the root-cause fix. Do not float to latest libs on Job ERROR.
- Unique output dirs replace `--overwrite_output_dir`.
- Serial map shim strips `num_proc` because dreamboothing hardcodes `num_proc=1` on GPU (prior EOFError).
- If this VM has no `HF_TOKEN`, implement/verify locally and hand off BLOCKED. Do not claim training succeeded.

## 11. Active blockers and remediation loops

| Finding | Owner | Status |
|---|---|---|
| Seven Jobs failed on unpinned latest stack | software-engineer-subagent | remediating via pins + preflight |
| Cloud VM `HF_TOKEN` may be absent | software-engineer-subagent | check at submit time |

## 12. Artifact and evidence index

- Charter/plan/evidence/handoff under `software-engineer-subagent/`
- Launch notes: `train/remote/hf-jobs-musicgen-lora.md`

## 13. Residual risks and human actions

- Job spend after submit (capped 16h / ~$24). STOP on 402.
- Adapter inherits CC-BY-NC 4.0. Do not apply to persist.
- Inject `HF_TOKEN` via the secret path if this VM is not logged in.

## 14. Owner decisions and approvals

Owner authorized HF Jobs LoRA on MusicBench (2026-09-01). Persist apply is not authorized.

## 15. Closure

Open until Job COMPLETED + Hub adapter weights, or an evidenced token/402 block.
