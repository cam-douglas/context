# USER.md

Store durable user-specific instructions and preferences here. Add new durable items near the top without duplicating existing meaning.

## Standing directives

- Preserve the user's operational intent and all materially relevant requirements when improving instructions or files.
- Prefer direct execution over asking the user to perform agent-capable work.
- Operate autonomously unless blocked by credentials, permissions, a consequential design decision, destructive risk, or a material safety/security/privacy concern.
- For new projects and major implementations, use sequential phase planning beginning with `docs/plans/phase_0_foundations_plan.md`.
- Use `/launch-pipeline` and `/instructions/LAUCH.md` as the single practical entry point for raw ideas, major changes, workstream resumption, remediation, and final closure.
- Require `/launch-pipeline` to run read-only preflight first. Every pre-Build Cursor plan must close by suggesting `bash .cursor/scripts/bootstrap.sh` as the first post-Build action, then run that command after Build or explicit Agent-mode implementation authorization.
- Use the adaptive gated role pipeline for substantive multi-domain work: require exhaustive role planning before action, document required and skipped roles, and preserve evidence-backed handoffs under `docs/workstreams/`.
- Require independent security re-verification after blocking remediation and a project-lead owner handoff for consequential product or release work.
- Defer non-blocking manual actions, credentials, provider dashboard work, production DNS, and similar user-only tasks to the final phase and consolidate them into `docs/plans/final_implementation_checklist.md`.
- Keep instructions machine-readable, structured, copyable, and directly usable.
- Avoid context bloat: keep indexes concise and load detailed files only when activated or relevant.
- Preserve exact file paths, unresolved blockers, attempts, validation evidence, and decisions needed for reliable continuation.
- Do not store secret values in markdown, plans, memory, logs, or examples.

## Platform preferences

- Plugin and UI copy must be ASCII only: no em dashes, ellipsis characters, middle dots, curly quotes, or non-English letters. Use hyphen, three dots, and plain quotes.

- Prefer macOS-compatible commands and workflows.
- Vercel workflow: use `/skills/vercel-deploy-workflow/SKILL.md`; prefer Git/CLI/dashboard when MCP is unavailable.
- Supabase workflow: use `/skills/supabase-linked-migrations/SKILL.md`; on macOS, use the documented `npx` fallback when a native binary is blocked.
