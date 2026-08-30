# TOOLS.md

This file is the canonical workspace registry of tools, capabilities, and resources the agent may use or should consider using.

Its purpose is to keep the agent aware of its full available operating surface so it does not underuse available capabilities.

## Purpose

Use this file to list all tools that may be relevant to work in this workspace, including:

- local terminal capabilities
- package managers
- language runtimes
- linters
- formatters
- test runners
- debuggers
- build tools
- deployment tools
- plugins and extensions
- local services
- external integrations
- online documentation sources
- internal reference files
- browser-based tools
- APIs and SDKs
- search tools
- database clients
- infrastructure tooling

This file is for awareness and selection, not for historical execution logging.

Do not use this file for:

- exact historical fixes
- blocker tracking
- session notes
- user preferences
- live task state

---

## Update rules

Update `TOOLS.md` whenever:

- a new tool becomes available in the workspace
- a plugin or extension is installed or removed
- a relevant integration is configured
- a recurring online reference source becomes important
- a terminal command family or utility becomes part of the normal workflow
- the user explicitly requests tool additions or removals

Keep this file current enough that the agent can always reason from the broadest realistic set of available capabilities.

---

## Entry format

### Tool: <name>

**Category**

- terminal / runtime / package manager / linter / formatter / test runner / debugger / plugin / integration / online resource / internal file / service / infrastructure / database / API / other

**Purpose**

- What the tool is for

**When to use**

- Typical triggers or relevant situations

**How to access**

- Command, path, extension name, service location, URL label, or integration point

**Common operations**

- Most relevant commands, actions, or usage patterns

**Constraints**

- Safety limits, permission requirements, environmental assumptions, rate limits, or known caveats

**Related files**

- Exact paths to configs, scripts, wrappers, or reference docs

---

## Tool selection rule

Before defaulting to a narrow approach, consider whether a better tool already exists in:

- the terminal
- installed plugins
- configured integrations
- project scripts
- language-native tooling
- test tooling
- linting / formatting tooling
- internal reference files
- online official documentation

Prefer the most direct, verifiable tool for the task.

Prefer built-in project scripts and official tooling over improvised alternatives when available.

---

### Tool: Supabase CLI

**Category**

- database / infrastructure / terminal

**Purpose**

- Manage Supabase projects from the terminal: migrations, `db push` to remote, linking, auth, and local development when configured.

**When to use**

- Applying schema changes, checking migration history, pushing migrations to the linked remote project, or any `supabase` subcommand.

**How to access**

- **On this Mac:** the shell function `supabase` runs `npx --yes supabase@<pinned>` (see `~/.zshrc` / `~/.zlogin`). Raw `~/.local/bin/supabase` from GitHub may be **killed by Gatekeeper** (`zsh: killed`); do not rely on it.
- **Homebrew** `/opt/homebrew/bin/supabase` may be outdated or not upgradable without admin write access to the prefix.

**Common operations**

- `supabase --help`; `supabase migration new <name>`; `supabase migration list --linked`; `supabase db push --linked --yes`; `supabase migration fetch --linked` (when remote history must be pulled into files); `supabase link --project-ref <ref> --yes`; `supabase login`.

**Constraints**

- Prefer **CLI** over Supabase MCP if MCP is unregistered or unauthorized.
- CLI must be discoverable (`supabase --version` should work via `npx`).

**Related files**

- `/skills/supabase-linked-migrations/SKILL.md`
- `/memory/runbooks/supabase-cli-macos.md` — macOS CLI / Gatekeeper notes.

---

### Tool: Supabase migrations (repo)

**Category**

- database / internal file / terminal

**Purpose**

- Versioned SQL under `supabase/migrations/` is the **source of truth** for remote schema history when using the Supabase CLI.

**When to use**

- Any DDL change that must apply to the hosted project: new tables, RLS, policies, functions, indexes.

**How to access**

- Files: `supabase/migrations/YYYYMMDDHHMMSS_*.sql` only (CLI naming); reference dump: `supabase/schema.sql` (not a substitute for migration history).
- Remote table: `supabase_migrations.schema_migrations`.

**Common operations**

- Create migration with CLI; edit SQL; `supabase db push --linked --yes`; verify with `supabase migration list --linked`.

**Constraints**

- Avoid `CREATE POLICY IF NOT EXISTS` if Postgres rejects it; use `DROP POLICY IF EXISTS` + `CREATE POLICY` (see existing migrations).

**Related files**

- `supabase/migrations/`

---

### Tool: Vercel CLI (`vercel` / `vc`)

**Category**

- deployment / infrastructure / terminal

**Purpose**

- Deploy a Next.js project to Vercel, link the local directory to a Vercel project, manage env vars from the terminal, inspect deployments and logs.

**When to use**

- Preview or production deploy from the dev machine; linking a new clone; pulling env for local dev; debugging deployment IDs and logs when the dashboard is not enough.

**How to access**

- **Global:** `npm i -g vercel` then `vercel` (or `vc`).
- **No global install:** `npx vercel <command>` from **repo root**.
- Requires **network**; first-time **`vercel login`** may open a browser.

**Common operations**

- `vercel login`; `vercel whoami`; `vercel link` / `vercel link --repo` (monorepos); `vercel pull`; `vercel` (preview deploy); `vercel --prod`; `vercel env ls`; `vercel env pull .env.local`; `vercel logs`, `vercel inspect` (see `vercel --help` for current subcommands).

**Constraints**

- Run CLI from the directory that contains (or should contain) **`.vercel/`** after linking — usually **repo root** for the app.
- Do not commit secrets; env files like `.env.local` stay local.

**Related files**

- `/skills/vercel-deploy-workflow/SKILL.md`
- `/memory/runbooks/vercel-workflow.md` — short runbook.

---

### Tool: Vercel platform (Dashboard + Git + optional MCP)

**Category**

- deployment / integration / online resource / MCP

**Purpose**

- **Production/Preview** deployments driven by **Git push** when the repo is connected in the Vercel project; env and domain configuration in the dashboard.

**When to use**

- Explaining how pushes map to deployments; changing env vars, domains, or build settings; when the user needs preview URLs for branches/PRs.

**How to access**

- Browser: [vercel.com](https://vercel.com) → Project / Team.
- **Git:** push to connected remote; default branch → Production; other branches → Preview.
- **MCP integration:** use any available Vercel-compatible MCP integration exposed by the current agent environment. Tool names and authentication methods vary by host; inspect the available tool descriptors first. If no authenticated integration is available, use the Vercel CLI in the terminal.

**Common operations**

- Connect Git repo to project; inspect deployment list and build logs; promote/rollback from dashboard (per current Vercel UI).

**Constraints**

- MCP availability varies by session; do not assume OAuth/MCP works without checking tool descriptors and auth.

**Related files**

- `/skills/vercel-deploy-workflow/SKILL.md`

---

### Tool: Product lifecycle launcher

**Category**

- agent orchestration / skill / internal file

**Purpose**

- Start, resume, remediate, or close the complete linked product pipeline from one parent Agent.

**When to use**

- Raw ideas, new products, major features, migrations, active-workstream resumption, failed-gate remediation, release closure, or explicit `/launch-pipeline` invocation.

**How to access**

- Invoke `/launch-pipeline` in Cursor Agent, or ask the parent Agent to follow `/instructions/LAUCH.md`.

**Common operations**

- Run read-only preflight; classify the lifecycle mode and risk; ask only for unresolved consequential decisions; present the activation summary; include `bash .cursor/scripts/bootstrap.sh` as the closing first post-Build action in the pre-Build plan; after Build or explicit Agent-mode authorization, run that bootstrap command as the first mutation; activate Strategy, Project Planning, Subagents, and Roles as needed; create/resume workstream artifacts; launch required roles directly; reconcile gates; prepare the owner handoff.
- Run preflight with `node .cursor/skills/launch-pipeline/scripts/preflight.mjs`.
- Validate linkage with `node .cursor/skills/launch-pipeline/scripts/validate-launch.mjs`.

**Constraints**

- Keep one parent Agent responsible for orchestration. Build approval and role identity do not authorize production or external mutation.

**Related files**

- `/skills/launch-pipeline/SKILL.md`
- `/instructions/LAUCH.md`
- `/INSTRUCTIONS.md`
- `/instructions/ROLES.md`
- `/STATE.md`

---

### Tool: Sub-agents / task delegation

**Category**

- agent orchestration / review / research

**Purpose**

- Delegate bounded independent investigations, implementation slices, or verification passes while the lead agent retains integration ownership.

**When to use**

- Parallel repository audits, strategy research, test design, security review, or disjoint implementation work.

**How to access**

- Use the available task or sub-agent capability for the current environment; follow `/instructions/SUBAGENTS.md` and select canonical role IDs through `/instructions/ROLES.md`.

**Constraints**

- Do not assume a sub-agent has read project context. Provide required paths and prevent overlapping writes.

**Related files**

- `/instructions/SUBAGENTS.md`
- `/instructions/ROLES.md`
- `/agents/`
- `/AGENTS.md`

---

### Tool: Agent bootstrap script

**Category**

- terminal / workspace automation

**Purpose**

- Serve as the cornerstone first mutating gate after launch planning: idempotently create root documentation and agent-system directories, seed missing indexes, maintain memory directories, repair the settings compatibility link, and validate required agent files.

**When to use**

- After Build or explicit Agent-mode implementation authorization in `/launch-pipeline`, at authorized new-session materialization, and after installing or moving the agent configuration tree. Use read-only preflight before mutation.

**How to access**

- Run the resolved `/scripts/bootstrap.sh`; from the agent configuration root, use `bash scripts/bootstrap.sh`.

**Constraints**

- Must not overwrite non-empty project content or introduce secrets.

**Related files**

- `/BOOTSTRAP.md`
- `/scripts/bootstrap.sh`
- `/memory/runbooks/agent-config-bootstrap.md`
- `/memory/runbooks/agent-workspace.md`

---

### Tool: Figma and visual design tooling

**Category**

- plugin / integration / MCP / browser

**Purpose**

- Inspect product visuals, Figma files, screenshots, flows, components, and design-system evidence for UI/UX planning.

**When to use**

- The `ui-ux-developer-subagent` charter includes interface, usability, accessibility, responsive, interaction, or visual-system work.

**How to access**

- Inspect the current session's tool descriptors before use. The workspace enables the Figma plugin in `/config/settings.json`, but configuration does not prove authentication, file access, or write permission.

**Constraints**

- UI/UX work remains plan/design-only unless source implementation is explicitly delegated to `software-engineer-subagent`.
- Never claim a Figma inspection, edit, screenshot, or usability result that was not actually performed.
- External mutations require explicit scope and remain subject to hooks, provider permissions, and owner approval.

**Related files**

- `/config/settings.json`
- `/instructions/ROLES.md`

---

### Tool: Analytics warehouse / BigQuery-class integration

**Category**

- database / analytics / MCP / API

**Purpose**

- Query approved product analytics for baselines, funnels, cohorts, retention, attribution, and experiment evaluation.

**When to use**

- A product or growth charter requires evidence that exists in an authorized analytics source.

**How to access**

- Discover the current session's available MCP/API tools and inspect their schemas before invocation. Treat BigQuery or equivalent access as unavailable until authentication and dataset scope are verified.

**Constraints**

- Default to read-only, aggregate, privacy-preserving queries.
- Do not query unnecessary personal or sensitive data, fabricate unavailable metrics, write datasets, launch campaigns, or change production analytics without explicit owner authorization.
- Record query scope, time range, caveats, and evidence location in the role handoff; never copy credentials or raw sensitive rows into markdown.

**Related files**

- `/instructions/ROLES.md`
- `docs/workstreams/`

---

### Tool: Agent policy hooks and security review

**Category**

- security / automation / policy / test

**Purpose**

- Deterministically block secret access, destructive Git, protected-policy mutation, delegated production mutation, and state-changing production operations; independently review security-sensitive changes.

**When to use**

- Hooks run automatically on configured events. Use policy tests and the agent-config validator after governance changes; activate the security role when the routing matrix requires it.

**How to access**

- Project hooks: `/hooks.json` and `/hooks/policy.mjs`.
- Tests: `node --test .cursor/hooks/policy.test.mjs`.
- Config validation: `node .cursor/scripts/validate-agent-config.mjs`.
- Security scanners/plugins: discover what is actually installed and select stack-appropriate tools from verified descriptors and project scripts.

**Constraints**

- Hook role identity is not an authorization signal. Production credentials must remain owner/CI-only.
- Fail-closed project hooks require a trusted workspace and Node on `PATH`.
- Repo-local controls can be changed by a human with write access; protected branches, required review, scoped credentials, and organization/provider policy are required for stronger enforcement.

**Related files**

- `/hooks.json`
- `/hooks/policy.mjs`
- `/cli.json`
- `/sandbox.json`
- `/permissions.json`
- `/instructions/ROLES.md`
- `docs/handover/agent-governance-operator-setup.md`

---

### Tool: CMake + JUCE 8 (Context plug-in)

**Category**

- build / desktop audio

**Purpose**

- Build the Context AU, VST3, and standalone host.

**When to use**

- After changing `plugin/src/` or when the owner needs a fresh plug-in install.

**How to access**

- `bash scripts/build-plugin.sh`

**Common operations**

- Clones JUCE 8.0.8 into `plugin/third_party/JUCE` if missing; Release arm64 build; copies AU/VST3 into `~/Library/Audio/Plug-Ins/`.

**Constraints**

- JUCE is AGPLv3 unless commercially licensed. Do not distribute VST3 without Steinberg terms. Source stays in the repo.

**Related files**

- `plugin/README.md`
- `docs/runbooks/context-juce-host.md`

---

### Tool: als-json (Context sidecar)

**Category**

- integration / internal file

**Purpose**

- Lossless Ableton `.als` (gzip XML) ↔ JSON tree, then additive arrangement merge.

**When to use**

- Exporting a Context arrangement into a Live Set, or parsing a user `.als` without overwriting it.

**How to access**

- `context_sidecar.als_json` and `context_sidecar.export.export_session`. HTTP `POST /export`.

**Common operations**

- `export_session(dest_dir, arrangement=..., source_als=...)`
- `parse_als_readonly(path)`

**Constraints**

- Never overwrite `source_als`. Unofficial format; Live may repair the set.

**Related files**

- `sidecar/src/context_sidecar/als_json.py`
- `sidecar/src/context_sidecar/session_export.py`
- `docs/decisions/2026-08-30-als-json-session-export.md`

---

### Tool: DawDreamer

**Category**

- runtime / integration

**Purpose**

- Headless offline render of a Context arrangement (stems on a timeline). Not a DAW.

**When to use**

- `/export` with `render` true, or `/dsp` `kind=dawdreamer`.

**How to access**

- Installed in `sidecar/.venv` as `dawdreamer` 0.9.0. Worker: `python -m context_sidecar.dawdreamer_worker`.

**Constraints**

- JUCE render must not run on the HTTP thread; the worker is a subprocess with a 90s timeout.

**Related files**

- `sidecar/src/context_sidecar/dsp.py`
- `sidecar/src/context_sidecar/dawdreamer_worker.py`

