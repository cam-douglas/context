---
schema_version: 1
task_id: 20260901-musicgen-musicbench-lora
role_id: software-engineer-subagent
status: active
revision: 1
created_at: 2026-09-01T11:45:00Z
updated_at: 2026-09-01T11:45:00Z
entry_criteria: Owner authorized start; $30 HF Jobs credit; persist host is musicgen-small
---

# Role Plan: software-engineer-subagent

## 1. Entry criteria and inherited evidence

Owner authorized HF Jobs (not this VM, not the owner Mac). Persist uses `facebook/musicgen-small`. No `train/` on remote main.

## 2. Scope, non-goals, and requirement coverage

| Requirement ID | Planned disposition | Expected evidence |
|---|---|---|
| SE-1 | `hf jobs uv run --detach` | job id + status |
| SE-2 | wrapper execs dreamboothing `--use_lora` on musicgen-small | script + logs |
| SE-3 | Job downloads/extracts MusicBench tar only on HF | script; no tar in repo/VM cache as a train run |
| SE-4 | `create_repo(private=True)` + `--hub_private_repo` | intended repo id |
| SE-5 | no token/weights in added files | path inspection |
| SE-6 | a10g-large, 16h, 20k/2500 cap | hardware snippet + notes |

## 3. Dependencies

- `hf` CLI on this VM (install if missing).
- Logged-in Hub token for submit (`--secrets HF_TOKEN`).
- Public Hub access for dataset metadata (no audio tar here).

## 4. Files, interfaces, data, and external systems

- `train/scripts/musicgen-lora-musicbench.py` — Job entry (clone dreamboothing, prepare MusicBench, train, push).
- `train/remote/hf-jobs-musicgen-lora.md` — launch notes, no secrets.
- `train/remote/submit-musicgen-lora.sh` — exact submit command.
- External: Hugging Face Jobs, Hub model repo, `amaai-lab/MusicBench`, `ylacombe/musicgen-dreamboothing`.

## 5. Ownership and concurrency

Sole writer for the paths above during this task.

## 6. Ordered tasks

1. Install `hf` CLI; read hf-cli skill.
2. `hf auth whoami` (username only). Stop with BLOCKED if missing token.
3. `hf jobs hardware`; choose flavor.
4. Discover MusicBench columns from Hub metadata + train JSON only (not the 16.7 GB tar).
5. Write wrapper + launch notes.
6. Submit `--detach` once. On 402, stop.
7. `hf jobs inspect` + first log lines if any.
8. Evidence + handoff.

## 7. Tool and modality plan

hf-cli only for Hub/Jobs. No sidecar pip. No local torch train. Do not print tokens.

## 8. Horizontal full-stack checklist

See charter. Owned rows: data, integrations, reliability, quality, cost, observability, docs.

## 9. Risk controls, rollback, and recovery

- Timeout 16h is the spend cap (~$24 at $1.50/h).
- Private adapter only; cancel Job from Hub if needed (owner/lead).
- Do not retry flavors after 402.
- Git rollback is revert of `train/` + docs only.

## 10. Validation steps and expected evidence

whoami; hardware snippet; column keys; exact command; job id/status; first logs or error body; adapter repo id.

## 11. Outputs and storage paths

Charter, plan, evidence, handoff; train script; remote notes.

## 12. Gate criteria and downstream handoff

Engineering PASS if SCHEDULING/RUNNING. Otherwise BLOCKED or ERROR. Next: Security.

## 13. Deviations and plan change log

- MusicBench is not a streaming audio Hub dataset; Job extracts `MusicBench.tar.gz` and casts `location`.
- Full 52 768-row epoch capped to 20 000 rows / 2500 steps.
