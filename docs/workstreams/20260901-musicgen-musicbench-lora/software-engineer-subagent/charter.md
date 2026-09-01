---
schema_version: 1
task_id: 20260901-musicgen-musicbench-lora
role_id: software-engineer-subagent
status: active
revision: 1
created_at: 2026-09-01T11:45:00Z
updated_at: 2026-09-01T11:45:00Z
predecessor_handoffs: []
mission: Submit a detached HF Job that LoRA-tunes facebook/musicgen-small on MusicBench and records evidence.
objective: Job SCHEDULING or RUNNING, or BLOCKED/ERROR with provider body; never train on this VM.
scope: train/scripts, train/remote, this role directory, optional docs/decisions job record
non_goals: sidecar, plugin, persist, other models, full-run wait, merge to main
---

# Role Charter: software-engineer-subagent

## 1. Role objective

### Mission

Create the Job wrapper, submit `--detach` on Hugging Face Jobs, and leave reproducible evidence. GPU work must not run on this Cloud VM or the owner Mac.

## 2. Inherited request and evidence

Owner authorized this start and added a $30 one-off HF Jobs credit. Persist already uses `facebook/musicgen-small` (`sidecar/src/context_sidecar/generation.py`). Remote `main` has no `train/` tree.

## 3. Scope, non-goals, and ownership

Owned write paths:

- `train/scripts/musicgen-lora-musicbench.py`
- `train/remote/*` (no secrets)
- `docs/workstreams/20260901-musicgen-musicbench-lora/**`
- `docs/decisions/` one-page job record if needed

Prohibited: `sidecar/.venv` and sidecar infer; `plugin/`; `.env` / tokens; persist / generation-rotate; ACE-Step, Parler, AudioLDM training; `hf jobs wait` for the full run; force-push; writing `HF_TOKEN` to a file.

## 4. Inherited requirements and vertical responsibilities

SE-1 through SE-6 in the manifest. Horizontal: integrations (HF Jobs + Hub), reliability (timeout/budget), quality (inspect + job status), performance/cost (flavor + step cap).

## 5. Assumptions, open questions, and clarification decisions

| Assumption | Confidence | If wrong | Validation |
|---|---|---|---|
| MusicBench Hub card is JSON + `MusicBench.tar.gz`; `location` is a relative wav path; must extract inside the Job | high | Job fails on missing audio | metadata JSON + Hub siblings |
| `main_caption` is the text column | high | dreamboothing column error | JSON keys |
| `a10g-large` + 20k/2500 steps stays under 16h and $24 | medium | Job times out; adapter may still push last checkpoint | inspect logs later |
| Adapter id is `<whoami>/context-musicgen-small-musicbench-lora` | high | resolved at Job runtime | `whoami` inside Job |
| This VM has no `HF_TOKEN` | observed | submit blocked | `hf auth whoami` |

## 6. Skills, tools, and evidence sources

- `hf-cli` skill (`~/.agents/skills/hf-cli/SKILL.md`), installed with the CLI.
- Commands: `hf auth whoami`, `hf jobs hardware`, `hf jobs uv run --detach`, `hf jobs list`, `hf jobs inspect`, `hf jobs logs`, `hf datasets info`.
- Do not use `hf auth token` (prints the secret).

## 7. Outputs and storage paths

Charter, plan, evidence, handoff; train script; launch notes.

## 8. Horizontal quality coverage

| Area | Disposition | Rationale |
|---|---|---|
| Product value | reviewed | Owner-fixed scope |
| Experience | not_applicable | No UI |
| Client | not_applicable | No client |
| Server and APIs | not_applicable | No sidecar API change |
| Data | owned | MusicBench columns; no local archive |
| Identity and access | reviewed | `--secrets HF_TOKEN`; private repo |
| Integrations | owned | HF Jobs + Hub push |
| Security and privacy | reviewed | no secrets in files; Security role still required |
| Reliability | owned | 16h timeout; no wait |
| Quality | owned | whoami/hardware/columns/job inspect |
| Performance and cost | owned | a10g-large, caps |
| Observability | owned | Job logs on Hub |
| Measurement and growth | not_applicable | |
| Delivery | reviewed | detached Job |
| Documentation and operations | owned | launch notes + evidence |

## 9. Validation plan and gate criteria

PASS only if Job is SCHEDULING or RUNNING. BLOCKED if `HF_TOKEN` missing or 402. ERROR for other provider failures. Do not claim COMPLETED.

## 10. Risks, blockers, and escalation triggers

Missing token; 402 payment; MusicBench tar extract failure; dreamboothing API drift; CC-BY-NC 4.0 on adapter card.

## 11. Failure handling and recovery

If first create returns 402, stop. Do not retry other flavors. Record the body. Cancel is owner/lead later; this role does not wait.

## 12. Downstream role and handoff conditions

Hand off to `security-engineer-subagent` with job id, redacted command, adapter id, and secret-handling evidence.
