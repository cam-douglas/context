---
schema_version: 1
task_id: YYYYMMDD-short-slug
role_id: canonical-role-id
status: complete
revision: 1
verdict: BLOCKED
started_at: YYYY-MM-DDTHH:MM:SSZ
completed_at: YYYY-MM-DDTHH:MM:SSZ
downstream_role: none
---

# Role Handoff: <Canonical Role ID>

## 1. Outcome

State what was delivered and whether the role objective was met.

## 2. Scope completed and not completed

## 3. Charter, plan, and predecessor handoffs

## 4. Outputs, changed paths, and external changes

## 5. Requirement and horizontal-checklist coverage

| Requirement ID | Result | Evidence |
|---|---|---|

## 6. Validation and evidence

List exact commands, inspections, research sources, test results, and artifact links. Distinguish executed evidence from recommendations.

## 7. Tools, skills, modalities, and MCP evidence

Record actual use, availability/authentication checks, access limitations, and relevant versions when material.

## 8. Assumptions, decisions, and deviations

## 9. Findings, severity, risks, and unresolved items

Include severity, owner, required remediation, and re-verification method.

## 10. Remediation and invalidated gates

## 11. Downstream instructions

- Next role:
- Required inputs:
- Constraints that remain binding:
- Checks that must be repeated:

## 12. Human actions and production approvals

List names, destinations, and owner actions only; never secret values.

## 13. Proposed state and memory updates

Read-only roles return proposed deltas for orchestrating-lead verification and materialization.

## 14. Verdict

Use exactly one:

- `PASS` — all blocking criteria are satisfied with evidence.
- `CONDITIONAL` — only explicit, bounded, non-blocking items remain with owners and deadlines.
- `BLOCKED` — a blocking criterion failed or required evidence is missing.

Unsupported completion claims default to `BLOCKED`. A handoff is not complete until it is linked from the workstream manifest.
