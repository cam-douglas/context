---
schema_version: 1
task_id: 20260901-musicgen-musicbench-lora
role_id: software-engineer-subagent
status: blocked
revision: 1
started_at: 2026-09-01T11:40:00Z
completed_at: 2026-09-01T11:50:00Z
charter: docs/workstreams/20260901-musicgen-musicbench-lora/software-engineer-subagent/charter.md
plan: docs/workstreams/20260901-musicgen-musicbench-lora/software-engineer-subagent/plan.md
predecessor_handoffs: []
verdict: BLOCKED
downstream_role: security-engineer-subagent
---

# Engineering handoff

## Summary

Prepared the HF Jobs wrapper and launch notes for a LoRA tune of `facebook/musicgen-small` on `amaai-lab/MusicBench`. **Did not submit a Job.** `hf auth whoami` on this Cloud VM returned `Not logged in`. Verdict **BLOCKED: missing HF_TOKEN**.

GPU work was not started on this VM or the owner Mac. MusicBench's 16.7 GB tar was not downloaded.

## Outputs

- `train/scripts/musicgen-lora-musicbench.py`
- `train/remote/hf-jobs-musicgen-lora.md`
- `train/remote/submit-musicgen-lora.sh`
- `docs/decisions/2026-09-01-musicgen-musicbench-lora-hf-job.md`
- this workstream

## Changed paths

- `train/scripts/musicgen-lora-musicbench.py`
- `train/remote/hf-jobs-musicgen-lora.md`
- `train/remote/submit-musicgen-lora.sh`
- `docs/workstreams/20260901-musicgen-musicbench-lora/**`
- `docs/decisions/2026-09-01-musicgen-musicbench-lora-hf-job.md`

## External changes

None. No HF Job. No Hub model repo.

## Requirement coverage

| ID | Status | Notes |
|---|---|---|
| SE-1 | BLOCKED | No token; submit not reached |
| SE-2 | implemented | Wrapper ready; unrun on HF |
| SE-3 | implemented | Columns confirmed; extract only in Job |
| SE-4 | pending | Intended `<user>/context-musicgen-small-musicbench-lora` |
| SE-5 | PASS | No secrets/weights in git |
| SE-6 | designed | a10g-large, 16h, ~$24; 20k/2500 cap |

## Horizontal checklist

See charter. Integrations/identity remain blocked on missing token.

## Validation

- `hf` 1.29.0 installed (needed `python3.12-venv` first). hf-cli skill loaded.
- `hf auth whoami` → not logged in.
- `hf jobs hardware` → a10g-large $1.50/h.
- MusicBench metadata/JSON columns verified; tar not fetched.
- `python3 -m py_compile train/scripts/musicgen-lora-musicbench.py` OK.
- `bash train/remote/submit-musicgen-lora.sh` → `BLOCKED: missing HF_TOKEN`.
- Raw `hf jobs uv run --detach ...` → `Error: Not logged in.`

## Evidence links

`docs/workstreams/20260901-musicgen-musicbench-lora/software-engineer-subagent/evidence.md`

## Tool and MCP evidence

hf-cli skill at `~/.agents/skills/hf-cli/SKILL.md`. No Hugging Face MCP used.

## Assumptions

- MusicBench must be extracted inside the Job (`location` + tar), not streamed as Audio parquet.
- 20 000 rows / 2500 steps keep a 16h a10g-large Job under ~$24.
- Adapter name uses the logged-in Hub user, resolved at Job runtime.

## Decisions

Host, dataset, LoRA/dreamboothing, guidance 1.0, a10g-large, private adapter, CC-BY-NC 4.0 card note — as authorized.

## Deviations

Submit skipped after auth failure, per brief. No flavor retry (402 never reached).

## Findings and severity

| ID | Severity | Finding |
|---|---|---|
| B-1 | high | Missing `HF_TOKEN` on the Cloud VM. Job cannot be created. |

## Risks

- Job spend after a later submit (capped by 16h / ~$24).
- Adapter inherits MusicGen CC-BY-NC 4.0.
- Dreamboothing upstream may change `load_dataset` shape; wrapper patches `save_to_disk`.

## Unresolved items

- Hub username
- Job id / status / logs
- Adapter repo creation
- Security review of token forwarding (required for Tier 3; no Job was sent)

## Remediation required

1. Provide `HF_TOKEN` to the Cloud environment through the secret path (not chat).
2. `hf auth whoami` must print a username.
3. Run `bash train/remote/submit-musicgen-lora.sh` once.
4. On 402, stop. Else record id and confirm SCHEDULING/RUNNING.

Invalidated gates: Security and Project Lead cannot PASS until a Job exists or the owner accepts this block.

## Verdict

**BLOCKED** — missing HF_TOKEN. Implementation for submit is in-tree; remote mutation did not occur.

## Downstream instructions

Security: review `--secrets HF_TOKEN`, private repo, CC-BY-NC card, and that no token was written to git. Do not treat a Job as running.

## Human actions

- Inject a write-scoped Hugging Face token into the Cloud Agent environment as `HF_TOKEN` (Jobs + create private model repo). Do not paste the value into chat.
- After submit: monitor the Job on the Hub; cancel if it errors or will exceed the $30 credit.
- Do not apply the adapter to persist until a later authorized task.

## Production approvals

None requested. Not a production deploy.

## Proposed state updates

- Active workstream: `docs/workstreams/20260901-musicgen-musicbench-lora/manifest.md`
- Active role/gate: software-engineer-subagent BLOCKED on HF_TOKEN
- Next action: inject token, resubmit once

## Proposed memory updates

- Durable: MusicGen LoRA Job wrapper lives under `train/`; MusicBench audio is tar+`location`, not Hub Audio parquet.
- Continuation: 2026-09-01 submit blocked; no Job id.
