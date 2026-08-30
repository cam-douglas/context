---
schema_version: 1
task_id: YYYYMMDD-short-slug
status: awaiting-owner-decision
revision: 1
created_at: YYYY-MM-DDTHH:MM:SSZ
updated_at: YYYY-MM-DDTHH:MM:SSZ
---

# Owner Handoff: <Task Title>

## 1. Decision requested

State the exact approval, rejection, selection, credential, permission, or manual action required from the owner.

## 2. Delivered outcome

## 3. Scope and requirement traceability

## 4. Role and stage-gate summary

List required/skipped roles, final verdicts, handoff links, and skip reasoning.

## 5. Verification evidence

## 6. Changed paths and external changes

## 7. Integrated security and production status

Distinguish `implemented`, `verified`, `ready for production`, `deployed`, and `owner-approved`.

## 8. Residual risks and accepted limitations

Do not hide `CONDITIONAL` items. High or critical security findings cannot be silently accepted or waived by an agent.

## 9. Rollback, recovery, and operational ownership

## 10. Environment variables and credentials still required

List names, providers, destinations, and validation steps only. Never include values.

## 11. Human-only or production actions

## 12. Owner response

Record exactly one owner choice:

- `APPROVE`
- `REQUEST_CHANGES`
- `DO_NOT_PROCEED`

Agents prepare these choices but never select one for the owner. The task remains open until the owner response is recorded.
