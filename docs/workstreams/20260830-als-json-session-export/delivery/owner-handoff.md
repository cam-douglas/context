---
schema_version: 1
task_id: 20260830-als-json-session-export
status: awaiting-owner-decision
revision: 1
created_at: 2026-08-30T00:26:00Z
---

# Owner Handoff: als-json session export

## 1. Decision requested

Open one written `*.als` in Live 11 Suite (File → Open). Choose `APPROVE` if clips/tracks look right, `REQUEST_CHANGES` if Live refuses the set.

## 2. Delivered outcome

Compose and `/export` now write a cloned Live Set plus lossless `*.als.json`. User tracks are preserved. Source `.als` is never overwritten. DawDreamer 0.9.0 renders an offline mix when `/export` is called with `render` true (default).

## 4. Role summary

PM PASS. Engineering PASS. Security CONDITIONAL (Live smoke). UI/UX and Growth skipped. Project Lead CONDITIONAL pending owner open.

## 5. Verification evidence

46 sidecar tests OK. DawDreamer installed in `sidecar/.venv`.

## 8. Residual risks

Unofficial clip XML may prompt Live to repair the set. Logic/GarageBand/FL still get WAV/MIDI only.

## 11. Human-only actions

File → Open a set from `~/Library/Application Support/Context/Plugin` or the `/export` dest folder.

## 12. Owner response

- `APPROVE`
- `REQUEST_CHANGES`
- `DO_NOT_PROCEED`
