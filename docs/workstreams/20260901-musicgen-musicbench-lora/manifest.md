---
schema_version: 1
task_id: 20260901-musicgen-musicbench-lora
title: MusicGen-small LoRA on MusicBench via Hugging Face Jobs
source_request: SETUP and SUBMIT a Hugging Face Job that fine-tunes facebook/musicgen-small with LoRA on amaai-lab/MusicBench. GPU work on HF Jobs only.
owner: user-operator
status: engineering
created_at: 2026-09-01T11:45:00Z
updated_at: 2026-09-01T11:45:00Z
revision: 1
objective: Submit a detached HF Job that trains a private LoRA adapter for facebook/musicgen-small on MusicBench, without downloading the 17 GB archive or training on this Cloud VM or the owner Mac.
scope: train/ job wrapper and launch notes; workstream evidence; one HF Jobs submit --detach
non_goals: sidecar infer changes; plugin; persist apply; ACE-Step/Parler/AudioLDM training; waiting for COMPLETED; merging to main
risk_tier: 3
risk_reasons: remote paid GPU job, Hub token forwarding, private adapter publish, CC-BY-NC 4.0 base weights
impacted_domains: remote training, Hub repos, billing
reversibility: high for git; Job spend is one-way up to timeout
requirements:
  - SE-1 Submit HF Job --detach on authorized credit
  - SE-2 Host facebook/musicgen-small LoRA, not melody/medium/large
  - SE-3 Dataset amaai-lab/MusicBench prepared only inside the Job
  - SE-4 Private adapter under logged-in user
  - SE-5 No secrets in git; no weights in git
  - SE-6 Budget cap under $30 (prefer <= $24)
acceptance_criteria:
  - Job SCHEDULING or RUNNING, or a clear provider error / missing-token block
  - Evidence records job id, flavor, timeout, adapter id, redacted command
required_roles:
  - software-engineer-subagent
skipped_roles:
  - product-manager-subagent
  - ui-ux-developer-subagent
  - growth-marketing-subagent
pipeline_order:
  - software-engineer-subagent
current_stage: software-engineer-subagent
current_gate: engineering
---

# Workstream Manifest: MusicGen MusicBench LoRA (HF Jobs)

## 1. Objective

Submit a detached Hugging Face Job that LoRA-tunes `facebook/musicgen-small` on `amaai-lab/MusicBench` and pushes a **private** adapter. GPU work runs on HF Jobs only.

## 3. Scope and non-goals

In scope: `train/scripts/`, `train/remote/` notes, this workstream, optional decision record, one `hf jobs` create.

Non-goals: download MusicBench on this VM or the owner Mac; train here; sidecar/.venv; persist apply; other generators; `hf jobs wait`; force-push or merge to main.

## 4. Risk classification

- Selected tier: **Tier 3** (paid remote job, credential forwarding, Hub write, license).
- Reversibility: git is reversible; Job spend is not.
- Data: MusicBench cc-by-sa-3.0 captions/audio; MusicGen weights CC-BY-NC 4.0.

## 5. Role routing matrix

| Role ID | Required or skipped | Reason/evidence | Status | Verdict |
|---|---|---|---|---|
| `product-manager-subagent` | skipped | Owner already decided host, dataset, method, budget, and adapter naming | skipped | n/a |
| `ui-ux-developer-subagent` | skipped | No UI | skipped | n/a |
| `software-engineer-subagent` | required | Job script + submit | in_progress | |
| `security-engineer-subagent` | required by Tier 3 | Token forwarding + private Hub write; lead must run after this handoff | pending | |
| `growth-marketing-subagent` | skipped | No launch or claims | skipped | n/a |
| `project-lead-subagent` | required by Tier 3 | Reconciliation after Security | pending | |

Routing decision owner: software-engineer-subagent (delegated start; owner authorized 2026-09-01).

## 6. Requirement traceability

| ID | Requirement | Evidence |
|---|---|---|
| SE-1 | Detached HF Job submit | `software-engineer-subagent/evidence.md` |
| SE-2 | musicgen-small LoRA | `train/scripts/musicgen-lora-musicbench.py` |
| SE-3 | MusicBench only inside Job | same script; no tar on this VM |
| SE-4 | Private adapter repo | script `create_repo(..., private=True)` + `--hub_private_repo` |
| SE-5 | No secrets/weights in git | inspection of added paths |
| SE-6 | Budget cap | flavor + 16h timeout documented |

## 10. Decisions

- Host: `facebook/musicgen-small` (matches persist).
- Method: `ylacombe/musicgen-dreamboothing --use_lora` inside the Job.
- Flavor: `a10g-large` at $1.50/h, timeout 16h, max ~$24. Chosen over `l4x1` ($0.80/h, also 24 GB) because the Job extracts a 16.7 GB tar and maps audio; 46 GB RAM is safer than 30 GB.
- Sample cap: 20 000 train rows and `max_steps` 2500 so preprocess+train stay under 16h (full 52 768 rows at batch 1 / accum 8 is 6596 steps plus full-set EnCodec map).
- Audio column: `location` (relative wav path inside `MusicBench.tar.gz`). Caption: `main_caption`.

## 13. Residual risks

- Missing `HF_TOKEN` on this Cloud VM blocks submit.
- First `hf jobs` 402 must not be retried on other flavors.
- MusicGen adapter inherits CC-BY-NC 4.0 from the base checkpoint.

## 15. Closure

Engineering completes when the Job is SCHEDULING/RUNNING or the block/error is evidenced. Do not wait for COMPLETED.
