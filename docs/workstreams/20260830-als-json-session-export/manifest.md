---
schema_version: 1
task_id: 20260830-als-json-session-export
title: als-json + DawDreamer session export
source_request: wire in als-json and dawdreamer to export arrangements into a user's DAW with complete session integrity
status: owner_handoff
created_at: 2026-08-30T00:12:00Z
updated_at: 2026-08-30T00:26:00Z
revision: 1
owner: user-operator
---

# Workstream Manifest: als-json session export

## 1. Objective

Export Context arrangements into a cloned Ableton Live Set via als-json, and render the same plan offline with DawDreamer, without overwriting the user's source set.

## 3. Scope and non-goals

In scope: sidecar codec, merge, `/export`, compose `.als` write, DawDreamer worker, tests.
Non-goals: plugin chrome, Logic/FL project rewrite, in-place `.als` overwrite, Live File → Open verification.

## 4. Risk classification

- Impacted domains: sidecar export, user session files, unofficial Ableton format
- Reversibility: high (new files only)
- Selected tier: **Tier 2** (user-visible contract change, local file write). Security trigger applies because we write DAW projects.

## 5. Role routing matrix

| Role ID | Required or skipped | Reason/evidence | Status | Verdict |
|---|---|---|---|---|
| `product-manager-subagent` | required | Owner reversed no-`.als`-write product lock | complete | PASS |
| `ui-ux-developer-subagent` | skipped | No plugin chrome; File → Open of a written set | skipped | n/a |
| `software-engineer-subagent` | required | Sidecar implementation | complete | PASS |
| `security-engineer-subagent` | required | Writes user session files; path safety | complete | CONDITIONAL |
| `growth-marketing-subagent` | skipped | No launch, claims, or measurement change | skipped | n/a |
| `project-lead-subagent` | required | Tier 2 reconciliation | complete | CONDITIONAL |

## 6. Requirement traceability

| ID | Requirement | Evidence |
|---|---|---|
| SE-1 | Lossless als-json round-trip | `tests.test_session_export.AlsJsonTests` |
| SE-2 | Never overwrite source `.als` | `test_merge_keeps_user_tracks_and_does_not_overwrite_source` |
| SE-3 | Preserve user tracks; add Context tracks | same |
| SE-4 | `/export` writes `.als` | `test_post_export_writes_als` |
| SE-5 | DawDreamer renders arrangement | `DawDreamerRenderTests` |
| SE-6 | Compose emits a set | `test_writes_audible_non_house_wav` |

## 10. Decisions

Owner 2026-08-30 authorized `.als` export. Recorded in `docs/decisions/2026-08-30-als-json-session-export.md`.

## 13. Residual risks

Live 11 may show a repair dialog on unofficial clip XML. Owner smoke required.

## 15. Closure

Awaiting owner File → Open of a written `Context.als`.
