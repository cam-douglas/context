---
document: final_implementation_checklist
status: open
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Final Implementation Checklist

## 1. Completion declaration

- [ ] All planned agent-executable phases are implemented.
- [ ] All available automated validation passes.
- [ ] Any unverified result is listed below.

## 2. Outstanding defects or unverified items

| Item | Impact | Evidence/status | Required action | Owner |
|---|---|---|---|---|

## 3. Role and stage-gate closure

| Role ID | Required or skipped | Final verdict or skip reason | Handoff/evidence |
|---|---|---|---|

- [ ] All `BLOCKED` verdicts have been remediated and independently re-verified.
- [ ] The project-lead owner handoff links every required gate and residual risk.

## 4. Environment variables and secrets still required

Never include secret values.

| Variable name | Provider/source | Destination/environment | Why required | Value supplied? | Validation after supply |
|---|---|---|---|---|---|

## 5. Human-only account, permission, billing, or legal actions

| Action | Platform | Reason agent cannot perform | Exact completion evidence |
|---|---|---|---|

## 6. Production integrations and dashboard actions

### Deployment

### DNS and domains

### OAuth and identity providers

### Database and storage

### APIs, webhooks, email, payments, analytics, and other providers

## 7. Final smoke tests after manual actions

- [ ] Application health and primary user journey
- [ ] Authentication and authorization
- [ ] Data persistence and migrations
- [ ] External integrations and webhooks
- [ ] Error handling, logs, alerts, and rollback
- [ ] Security, privacy, accessibility, and performance acceptance

## 8. Owner decision

- [ ] Owner approved the handoff.
- [ ] Conditions or requested remediation are recorded in the active workstream.

## 9. Final evidence

List the exact plans, test commands, build/deployment evidence, and documentation proving all other work is complete.
